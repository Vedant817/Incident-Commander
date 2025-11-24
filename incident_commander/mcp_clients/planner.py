import json
from typing import Dict, List, Any
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import HuggingFaceHub
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from ..config import LLM_PROVIDER, LLM_MODEL, OLLAMA_BASE_URL, HUGGINGFACE_API_KEY

class MCPPlanner:
    def __init__(self):
        self.model = self._init_model()
        self.parser = JsonOutputParser()
        self.prompt = self._init_prompt()
        self.chain = self.prompt | self.model | self.parser

    def _init_model(self):
        if LLM_PROVIDER == "ollama":
            return ChatOllama(
                base_url=OLLAMA_BASE_URL,
                model=LLM_MODEL,
                temperature=0.1,
            )
        elif LLM_PROVIDER == "huggingface":
            return HuggingFaceHub(
                repo_id=LLM_MODEL,
                huggingfacehub_api_token=HUGGINGFACE_API_KEY,
                task="text-generation",
                model_kwargs={
                    "temperature": 0.1,
                    "max_new_tokens": 1024,
                    "top_p": 0.9,
                }
            )
        else:
            # Default to mock generator if no valid provider is found
            return None

    def _init_prompt(self):
        return PromptTemplate(
            template="""
            You are a Site Reliability Engineer creating a remediation plan for an infrastructure alert.
            Based on the provided alert context and relevant runbook snippets, generate a structured JSON plan.

            **Alert Context:**
            {alert_context}

            **Runbook Snippets:**
            {runbook_snippets}

            **Instructions:**
            1.  Analyze the alert and runbooks to identify the likely root cause.
            2.  Create a `summary` of the plan.
            3.  Define a list of `steps`, where each step is an action to be taken.
            4.  For each step, provide:
                - `id`: A unique integer for the step.
                - `action`: A clear, concise description of the action.
                - `tool`: The MCP tool to use (e.g., `shell-command`).
                - `parameters`: The parameters for the tool (e.g., the shell command).
                - `rollback`: A command or description of how to undo the step.
                - `risk_score`: A float between 0.0 and 1.0, where 1.0 is highest risk.
                - `dependencies`: A list of step IDs that must be completed before this one.
            5.  Calculate a `total_risk_score` for the entire plan (the maximum risk score of any single step).
            6.  Set `requires_approval` to `true` if the `total_risk_score` exceeds 0.5, otherwise `false`.
            7.  Ensure the output is a valid JSON object.

            **JSON Output Format:**
            {{
                "summary": "Brief description of the plan.",
                "steps": [
                    {{
                        "id": 1,
                        "action": "Example: Check service status",
                        "tool": "shell-command",
                        "parameters": {{"command": "kubectl get pods -l app=<service>"}},
                        "rollback": "None",
                        "risk_score": 0.1,
                        "dependencies": []
                    }}
                ],
                "total_risk_score": 0.1,
                "requires_approval": false
            }}

            **Generate the plan:**
            """,
            input_variables=["alert_context", "runbook_snippets"],
        )

    def create_plan(self, alert_context: Dict[str, Any], runbook_snippets: List[str]) -> Dict[str, Any]:
        if self.model is None:
            return self._generate_mock_plan(alert_context, runbook_snippets)

        try:
            plan_json = self.chain.invoke({
                "alert_context": json.dumps(alert_context),
                "runbook_snippets": "\n---\n".join(runbook_snippets)
            })
            return self._validate_plan(plan_json)
        except Exception as e:
            print(f"LLM plan generation failed: {e}")
            return self._generate_mock_plan(alert_context, runbook_snippets)

    def _generate_mock_plan(self, alert_context: Dict, runbook_snippets: List[str]) -> Dict:
        service = alert_context.get('service', 'unknown-service')
        return {
            "summary": f"Fallback mock plan for {service}.",
            "steps": [{
                "id": 1,
                "action": f"Diagnose issue for {service} by checking status.",
                "tool": "shell-command",
                "parameters": {"command": f"echo 'Checking status for {service}... Service is reporting errors.'"},
                "rollback": "None",
                "risk_score": 0.1,
                "dependencies": [],
            }],
            "total_risk_score": 0.1,
            "requires_approval": False
        }

    def _validate_plan(self, plan: Dict) -> Dict:
        if not isinstance(plan, dict) or "steps" not in plan:
            return self._generate_mock_plan({}, []) # Return a minimal mock plan on validation failure

        plan.setdefault("summary", "Remediation plan")
        plan.setdefault("total_risk_score", max([s.get("risk_score", 0.0) for s in plan.get("steps", [])], default=0.0))

        for i, step in enumerate(plan["steps"]):
            step.setdefault("id", i + 1)
            step.setdefault("risk_score", 0.5)
            step.setdefault("dependencies", [])

        return plan