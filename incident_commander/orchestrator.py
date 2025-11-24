import time
from typing import Dict, Any, Optional
from .agents.analyst import AnalystAgent
from .agents.commander import CommanderAgent
from .agents.executor_agent import ExecutorAgent
from .agents.auditor import AuditorAgent
from .mcp_clients.rag import MCPRAG
from .mcp_clients.planner import MCPPlanner
from .mcp_clients.executor import MCPExecutor
from .config import MCP_MODE


class AgentOrchestrator:
    def __init__(self):
        self.rag_tool = MCPRAG()
        self.planner = MCPPlanner()
        self.executor = MCPExecutor(mode=MCP_MODE)
        
        # Initialize agents
        self.analyst = AnalystAgent(self.rag_tool)
        self.commander = CommanderAgent(self.planner)
        self.executor_agent = ExecutorAgent(self.executor)
        self.auditor = AuditorAgent()
        
        # State management
        self.current_incident = None
        self.current_plan = None
        self.current_execution = None
    
    def process_incident(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        incident_id = f"incident_{int(time.time())}"
        
        # Step 1: Analyst Agent - Understand and retrieve context
        context_bundle = self.analyst.analyze(alert)
        self.current_incident = {
            "id": incident_id,
            "alert": alert,
            "context": context_bundle,
            "timestamp": time.time()
        }
        
        # Step 2: Commander Agent - Create plan
        plan = self.commander.create_plan(context_bundle)
        plan["id"] = f"plan_{incident_id}"
        self.current_plan = plan
        
        # Step 3: Auditor Agent - Validate plan
        audit_result = self.auditor.audit_plan(plan)
        
        return {
            "incident_id": incident_id,
            "alert": alert,
            "context_bundle": context_bundle,
            "plan": plan,
            "audit": audit_result,
            "status": "planned",
            "timestamp": time.time()
        }
    
    def execute_plan(self, plan: Optional[Dict[str, Any]] = None, step_by_step: bool = False) -> Dict[str, Any]:
        plan_to_execute = plan or self.current_plan
        
        if not plan_to_execute:
            return {
                "status": "error",
                "error": "No plan available to execute"
            }
        
        # Execute plan
        execution_results = self.executor_agent.execute_plan(plan_to_execute, step_by_step=step_by_step)
        self.current_execution = execution_results
        
        return execution_results
    
    def execute_single_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        return self.executor_agent.execute_single_step(step)
    
    def generate_postmortem(self, incident_response: Dict[str, Any], execution_results: Dict[str, Any]) -> str:
        alert = incident_response.get("alert", {})
        plan = incident_response.get("plan", {})
        context = incident_response.get("context_bundle", {})
        
        postmortem = f"""# Incident Postmortem

## Incident Summary

**Incident ID:** {incident_response.get('incident_id', 'unknown')}
**Service:** {alert.get('service', 'unknown')}
**Severity:** {alert.get('severity', 'medium')}
**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(incident_response.get('timestamp', time.time())))}

## Alert Description

{alert.get('description', 'No description provided')}

## Root Causes Identified

"""
        
        root_causes = context.get("root_causes", [])
        for i, cause in enumerate(root_causes, 1):
            postmortem += f"{i}. {cause}\n"
        
        postmortem += f"""
## Remediation Plan

**Plan Summary:** {plan.get('summary', 'No summary')}

**Total Risk Score:** {plan.get('total_risk_score', 0.0):.2f}

### Steps Executed

"""
        
        steps = plan.get("steps", [])
        for step in steps:
            step_id = step.get("id")
            action = step.get("action", "")
            risk = step.get("risk_score", 0.0)
            status = "✓" if step_id in execution_results.get("steps_executed", []) else "✗"
            
            postmortem += f"{status} **Step {step_id}:** {action} (Risk: {risk:.2f})\n"
        
        postmortem += f"""
## Execution Results

**Status:** {execution_results.get('status', 'unknown')}
**Duration:** {execution_results.get('duration_seconds', 0):.2f} seconds
**Steps Executed:** {len(execution_results.get('steps_executed', []))}
**Steps Failed:** {len(execution_results.get('steps_failed', []))}
**Rollbacks Performed:** {len(execution_results.get('rollbacks_performed', []))}

### Execution Log

"""
        
        logs = execution_results.get("logs", [])
        for log in logs[-20:]:  # Last 20 log entries
            timestamp = time.strftime('%H:%M:%S', time.localtime(log.get('timestamp', 0)))
            level = log.get('level', 'info')
            message = log.get('message', '')
            postmortem += f"[{timestamp}] [{level.upper()}] {message}\n"
        
        postmortem += f"""
## Long-term Recommendations

1. Monitor {alert.get('service', 'service')} metrics more closely
2. Consider implementing automated scaling policies
3. Review and update runbooks based on this incident
4. Implement preventive measures to avoid similar incidents

## Timeline

- **Alert Received:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(incident_response.get('timestamp', time.time())))}
- **Plan Generated:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(plan.get('timestamp', time.time())))}
- **Execution Started:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(execution_results.get('start_time', time.time())))}
- **Execution Completed:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(execution_results.get('end_time', time.time())))}

---
*Generated automatically by Incident Commander*
"""
        
        return postmortem
    
    def get_current_state(self) -> Dict[str, Any]:
        return {
            "incident": self.current_incident,
            "plan": self.current_plan,
            "execution": self.current_execution
        }
