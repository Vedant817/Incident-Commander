from typing import Dict, Any
from ..mcp_clients.planner import MCPPlanner


class CommanderAgent:
    def __init__(self, planner: MCPPlanner = None):
        self.planner = planner or MCPPlanner()
    
    def create_plan(self, context_bundle: Dict[str, Any]) -> Dict[str, Any]:
        alert = context_bundle.get("alert", {})
        runbook_snippets = context_bundle.get("runbook_snippets", [])
        
        runbook_texts = [snippet.get("content", "") for snippet in runbook_snippets]
        
        plan = self.planner.create_plan(alert, runbook_texts)
        
        plan["alert_summary"] = context_bundle.get("summary", "")
        plan["root_causes"] = context_bundle.get("root_causes", [])
        plan["service"] = context_bundle.get("service", "unknown")
        
        plan["reasoning"] = self._generate_reasoning(context_bundle, plan)
        
        return plan
    
    def _generate_reasoning(self, context_bundle: Dict[str, Any], plan: Dict[str, Any]) -> str:
        root_causes = context_bundle.get("root_causes", [])
        steps = plan.get("steps", [])
        
        reasoning = f"Plan generated based on {len(root_causes)} identified root causes:\n"
        for i, cause in enumerate(root_causes, 1):
            reasoning += f"{i}. {cause}\n"
        
        reasoning += f"\nRemediation plan consists of {len(steps)} steps:\n"
        for step in steps:
            reasoning += f"- Step {step.get('id')}: {step.get('action')} (Risk: {step.get('risk_score', 0.5):.2f})\n"
        
        return reasoning
