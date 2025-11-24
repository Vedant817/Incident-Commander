import json
import time
from typing import Any, Dict, Tuple

import gradio as gr

from ..mcp_clients.rag import MCPRAG
from ..mcp_clients.sandbox import MCPSandbox
from ..orchestrator import AgentOrchestrator
from ..rag.vector_store import VectorStore


class IncidentCommanderUI:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.sandbox = MCPSandbox()
        self.current_incident_response = None
        self.current_execution_results = None
        self.current_alert = None

        self._initialize_vector_store()

    def _initialize_vector_store(self):
        try:
            vector_store = VectorStore()

            if not vector_store.load():
                from ..utils.runbook_loader import load_runbooks

                documents, metadata = load_runbooks()
                if documents:
                    vector_store.initialize(documents, metadata)
                    vector_store.save()

            self.orchestrator.rag_tool = MCPRAG(vector_store)
        except Exception as e:
            print(f"Warning: Could not initialize vector store: {e}")

    def create_ui(self) -> gr.Blocks:
        app = gr.Blocks(title="🚨 Incident Commander")
        app.theme = gr.themes.Soft()

        with app:
            gr.Markdown("# 🚨 Incident Commander: Autonomous SRE Agent")
            gr.Markdown(
                "AI-powered incident detection, diagnosis, planning, and execution"
            )

            self.incident_state = gr.State(value=None)
            self.plan_state = gr.State(value=None)
            self.execution_state = gr.State(value=None)
            self.alert_state = gr.State(value=None)

            with gr.Tabs() as tabs:
                # Tab 1: Incident Stream
                with gr.Tab("📊 Alerts"):
                    self._create_alerts_tab()

                # Tab 2: Plan Viewer
                with gr.Tab("📋 Plan"):
                    self._create_plan_tab()

                # Tab 3: Execution Panel
                with gr.Tab("⚙️ Execution"):
                    self._create_execution_tab()

                # Tab 4: Postmortem
                with gr.Tab("📝 Postmortem"):
                    self._create_postmortem_tab()

        return app

    def _create_alerts_tab(self):
        gr.Markdown("## Incident Feed")
        gr.Markdown("Monitor and respond to infrastructure alerts")

        with gr.Row():
            with gr.Column(scale=2):
                alerts_output = gr.JSON(label="Active Alerts", value=[])

                with gr.Row():
                    simulate_btn = gr.Button("🎲 Simulate Incident", variant="primary")
                    refresh_btn = gr.Button("🔄 Refresh")

                with gr.Accordion("Create Custom Alert", open=False):
                    with gr.Row():
                        alert_service = gr.Textbox(
                            label="Service Name", value="auth-service"
                        )
                        alert_severity = gr.Dropdown(
                            choices=["low", "medium", "high", "critical"],
                            value="high",
                            label="Severity",
                        )
                    alert_description = gr.Textbox(
                        label="Description",
                        value="Pod crash detected - OOM kill",
                        lines=3,
                    )
                    alert_metrics = gr.JSON(
                        label="Metrics (JSON)",
                        value={"cpu": 95, "memory": 98, "error_rate": 0.15},
                    )
                    create_alert_btn = gr.Button("Create Alert", variant="secondary")

            with gr.Column(scale=1):
                incident_summary = gr.Markdown("### No active incident")
                analyze_btn = gr.Button(
                    "🔍 Analyze Incident", variant="primary", visible=False
                )

        # Event handlers
        simulate_btn.click(
            fn=self._simulate_incident,
            outputs=[alerts_output, incident_summary, analyze_btn, self.alert_state],
        )

        create_alert_btn.click(
            fn=self._create_custom_alert,
            inputs=[alert_service, alert_severity, alert_description, alert_metrics],
            outputs=[alerts_output, incident_summary, analyze_btn, self.alert_state],
        )

        analyze_btn.click(
            fn=self._analyze_incident,
            inputs=[self.alert_state],
            outputs=[incident_summary, self.incident_state],
        )

        refresh_btn.click(fn=self._refresh_alerts, outputs=[alerts_output])

    def _create_plan_tab(self):
        gr.Markdown("## Remediation Plan")
        gr.Markdown("Review the generated remediation plan before execution")

        with gr.Row():
            with gr.Column(scale=2):
                plan_json = gr.JSON(label="Plan Details")
                plan_reasoning = gr.Markdown("### Reasoning Trace")
                runbook_refs = gr.Markdown("### Runbook References")

            with gr.Column(scale=1):
                plan_summary = gr.Markdown("### Plan Summary")
                risk_score = gr.Markdown("### Risk Assessment")
                audit_result = gr.JSON(label="Audit Result")

                with gr.Row():
                    approve_btn = gr.Button("✅ Approve Plan", variant="primary")
                    reject_btn = gr.Button("❌ Reject Plan", variant="stop")

        # Load plan from state
        self.incident_state.change(
            fn=self._load_plan,
            inputs=[self.incident_state],
            outputs=[
                plan_json,
                plan_summary,
                plan_reasoning,
                runbook_refs,
                risk_score,
                audit_result,
                self.plan_state,
            ],
        )

        approve_btn.click(
            fn=self._approve_plan, inputs=[self.plan_state], outputs=[plan_summary]
        )

    def _create_execution_tab(self):
        gr.Markdown("## Execution Panel")
        gr.Markdown("Execute remediation steps and monitor progress")

        with gr.Row():
            with gr.Column(scale=2):
                execution_log = gr.Textbox(
                    label="Execution Log", lines=15, interactive=False
                )

                with gr.Row():
                    execute_all_btn = gr.Button(
                        "▶️ Execute All Steps", variant="primary"
                    )
                    execute_step_btn = gr.Button(
                        "▶️ Execute Next Step", variant="secondary"
                    )
                    pause_btn = gr.Button("⏸️ Pause", variant="stop")

                step_status = gr.Dataframe(
                    label="Step Status",
                    headers=["Step ID", "Action", "Status", "Risk", "Duration"],
                    interactive=False,
                )

            with gr.Column(scale=1):
                execution_summary = gr.Markdown("### Execution Summary")
                rollback_btn = gr.Button(
                    "🔄 Rollback Last Step", variant="stop", visible=False
                )

        # Event handlers
        execute_all_btn.click(
            fn=self._execute_all_steps,
            inputs=[self.plan_state],
            outputs=[
                execution_log,
                step_status,
                execution_summary,
                rollback_btn,
                self.execution_state,
            ],
        )

        execute_step_btn.click(
            fn=self._execute_next_step,
            inputs=[self.plan_state, self.execution_state],
            outputs=[
                execution_log,
                step_status,
                execution_summary,
                rollback_btn,
                self.execution_state,
            ],
        )

        # Load execution from state
        self.execution_state.change(
            fn=self._update_execution_display,
            inputs=[self.execution_state],
            outputs=[execution_log, step_status, execution_summary],
        )

    def _create_postmortem_tab(self):
        gr.Markdown("## Incident Postmortem")
        gr.Markdown("Automatically generated postmortem document")

        with gr.Row():
            with gr.Column(scale=2):
                postmortem_text = gr.Textbox(
                    label="Postmortem Document", lines=30, interactive=True
                )

            with gr.Column(scale=1):
                generate_btn = gr.Button("📝 Generate Postmortem", variant="primary")
                export_md_btn = gr.Button("💾 Export as Markdown", variant="secondary")
                export_json_btn = gr.Button("💾 Export as JSON", variant="secondary")

        # Generate postmortem when execution completes
        self.execution_state.change(
            fn=self._auto_generate_postmortem,
            inputs=[self.incident_state, self.execution_state],
            outputs=[postmortem_text],
        )

        generate_btn.click(
            fn=self._generate_postmortem,
            inputs=[self.incident_state, self.execution_state],
            outputs=[postmortem_text],
        )

    # Event handler methods
    def _simulate_incident(self) -> Tuple[list, str, gr.Button, Dict]:
        services = ["auth-service", "api-service", "db-service", "cache-service"]
        import random

        service = random.choice(services)
        incident = self.sandbox.simulate_incident(service)

        alert = {
            "service": incident["service"],
            "severity": incident["severity"],
            "description": incident["description"],
            "timestamp": time.time(),
            "type": incident["type"],
            "metrics": {},
        }

        alerts = [alert]
        summary = f"### 🚨 Incident Detected\n**Service:** {service}\n**Severity:** {incident['severity']}\n**Type:** {incident['type']}"

        return alerts, summary, gr.Button(visible=True), alert

    def _create_custom_alert(
        self, service: str, severity: str, description: str, metrics: dict
    ) -> Tuple[list, str, gr.Button, Dict]:
        """Create a custom alert"""
        alert = {
            "service": service,
            "severity": severity,
            "description": description,
            "metrics": metrics,
            "timestamp": time.time(),
            "type": "custom",
        }

        alerts = [alert]
        summary = f"### 🚨 Custom Alert Created\n**Service:** {service}\n**Severity:** {severity}"

        return alerts, summary, gr.Button(visible=True), alert

    def _analyze_incident(self, alert: Dict) -> Tuple[str, Dict]:
        if not alert:
            return (
                "### ❌ No alert available. Please create or simulate an incident first.",
                None,
            )

        incident_response = self.orchestrator.process_incident(alert)
        self.current_incident_response = incident_response
        self.current_alert = alert

        summary = f"""
### ✅ Analysis Complete

**Incident ID:** {incident_response["incident_id"]}

**Root Causes:**
{chr(10).join(f"- {cause}" for cause in incident_response["context_bundle"].get("root_causes", []))}

**Plan Generated:** {len(incident_response["plan"].get("steps", []))} steps
**Risk Score:** {incident_response["plan"].get("total_risk_score", 0.0):.2f}
**Requires Approval:** {incident_response["audit"].get("requires_manual_approval", False)}
"""

        return summary, incident_response

    def _load_plan(
        self, incident_response: Dict
    ) -> Tuple[Dict, str, str, str, str, Dict, Dict]:
        """Load plan details into UI"""
        if not incident_response:
            return {}, "### No plan available", "", "", "", {}, {}

        plan = incident_response.get("plan", {})
        context = incident_response.get("context_bundle", {})
        audit = incident_response.get("audit", {})

        # Format plan summary
        summary = f"""
### Plan Summary

{plan.get("summary", "No summary")}

**Total Steps:** {len(plan.get("steps", []))}
**Total Risk:** {plan.get("total_risk_score", 0.0):.2f}
"""

        # Format reasoning
        reasoning = (
            f"### Reasoning\n\n{plan.get('reasoning', 'No reasoning available')}"
        )

        # Format runbook references
        runbook_snippets = context.get("runbook_snippets", [])
        runbook_text = "### Runbook References\n\n"
        for i, snippet in enumerate(runbook_snippets[:3], 1):
            runbook_text += f"**{i}. {snippet.get('source', 'Unknown')}**\n"
            runbook_text += f"{snippet.get('content', '')[:200]}...\n\n"

        # Format risk assessment
        risk_text = f"""
### Risk Assessment

**Total Risk Score:** {plan.get("total_risk_score", 0.0):.2f}

**High-Risk Steps:**
{len(audit.get("risk_assessment", {}).get("high_risk_steps", []))} steps require attention
"""

        return plan, summary, reasoning, runbook_text, risk_text, audit, plan

    def _approve_plan(self, plan: Dict) -> str:
        """Approve plan for execution"""
        return "### ✅ Plan Approved\n\nReady for execution."

    def _execute_all_steps(self, plan: Dict) -> Tuple[str, list, str, gr.Button, Dict]:
        """Execute all plan steps"""
        if not plan:
            return (
                "No plan available",
                [],
                "### No execution data",
                gr.Button(visible=False),
                {},
            )

        execution_results = self.orchestrator.execute_plan(plan, step_by_step=False)
        self.current_execution_results = execution_results

        # Format execution log
        log_text = self._format_execution_log(execution_results)

        # Format step status
        step_data = self._format_step_status(plan, execution_results)

        # Format summary
        summary = f"""
### Execution Summary

**Status:** {execution_results.get("status", "unknown")}
**Duration:** {execution_results.get("duration_seconds", 0):.2f}s
**Steps Executed:** {len(execution_results.get("steps_executed", []))}
**Steps Failed:** {len(execution_results.get("steps_failed", []))}
"""

        return (
            log_text,
            step_data,
            summary,
            gr.Button(visible=len(execution_results.get("steps_failed", [])) > 0),
            execution_results,
        )

    def _execute_next_step(
        self, plan: Dict, execution_state: Dict
    ) -> Tuple[str, list, str, gr.Button, Dict]:
        """Execute next step in plan"""
        if not plan:
            return (
                "No plan available",
                [],
                "### No execution data",
                gr.Button(visible=False),
                {},
            )

        steps = plan.get("steps", [])
        executed_ids = (
            execution_state.get("steps_executed", []) if execution_state else []
        )

        # Find next step
        next_step = None
        for step in steps:
            if step.get("id") not in executed_ids:
                next_step = step
                break

        if not next_step:
            return (
                "All steps completed",
                [],
                "### Execution Complete",
                gr.Button(visible=False),
                execution_state or {},
            )

        # Execute step
        step_result = self.orchestrator.execute_single_step(next_step)

        # Update execution state
        if not execution_state:
            execution_state = {"steps_executed": [], "steps_failed": [], "logs": []}

        if step_result.get("status") == "success":
            execution_state["steps_executed"].append(next_step.get("id"))
        else:
            execution_state["steps_failed"].append(next_step.get("id"))

        execution_state["logs"].extend(step_result.get("logs", []))

        # Format output
        log_text = self._format_execution_log(execution_state)
        step_data = self._format_step_status(plan, execution_state)
        summary = f"### Step {next_step.get('id')} Executed\n\nStatus: {step_result.get('status', 'unknown')}"

        return (
            log_text,
            step_data,
            summary,
            gr.Button(visible=len(execution_state.get("steps_failed", [])) > 0),
            execution_state,
        )

    def _format_execution_log(self, execution_results: Dict) -> str:
        if not execution_results:
            return "No execution log available"

        logs = execution_results.get("logs", [])
        log_text = ""

        for log in logs[-50:]:  # Last 50 entries
            timestamp = time.strftime(
                "%H:%M:%S", time.localtime(log.get("timestamp", time.time()))
            )
            level = log.get("level", "info")
            message = log.get("message", "")
            log_text += f"[{timestamp}] [{level.upper()}] {message}\n"

        return log_text if log_text else "No logs yet"

    def _format_step_status(self, plan: Dict, execution_results: Dict) -> list:
        """Format step status as dataframe"""
        if not plan or not execution_results:
            return []

        steps = plan.get("steps", [])
        executed = execution_results.get("steps_executed", [])
        failed = execution_results.get("steps_failed", [])

        step_data = []
        for step in steps:
            step_id = step.get("id")
            action = step.get("action", "")
            risk = step.get("risk_score", 0.0)

            if step_id in failed:
                status = "❌ Failed"
            elif step_id in executed:
                status = "✅ Completed"
            else:
                status = "⏳ Pending"

            step_data.append(
                [
                    step_id,
                    action[:50] + "..." if len(action) > 50 else action,
                    status,
                    f"{risk:.2f}",
                    "-",
                ]
            )

        return step_data

    def _update_execution_display(self, execution_state: Dict) -> Tuple[str, list, str]:
        if not execution_state:
            return "No execution data", [], "### No execution data"

        log_text = self._format_execution_log(execution_state)
        summary = f"### Execution Status\n\nSteps Executed: {len(execution_state.get('steps_executed', []))}"

        return log_text, [], summary

    def _generate_postmortem(
        self, incident_response: Dict, execution_results: Dict
    ) -> str:
        """Generate postmortem document"""
        if not incident_response:
            incident_response = self.current_incident_response
        if not execution_results:
            execution_results = self.current_execution_results

        if not incident_response or not execution_results:
            return "No incident or execution data available. Please complete analysis and execution first."

        postmortem = self.orchestrator.generate_postmortem(
            incident_response, execution_results
        )
        return postmortem

    def _auto_generate_postmortem(
        self, incident_response: Dict, execution_results: Dict
    ) -> str:
        """Auto-generate postmortem when execution completes"""
        if not execution_results or execution_results.get("status") not in [
            "completed",
            "partial",
            "failed",
        ]:
            return ""

        return self._generate_postmortem(incident_response, execution_results)

    def _refresh_alerts(self) -> list:
        """Refresh alerts list"""
        return []


def create_app() -> gr.Blocks:
    ui = IncidentCommanderUI()
    return ui.create_ui()
