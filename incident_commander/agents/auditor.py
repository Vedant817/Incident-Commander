from typing import Dict, Any
from ..config import RISK_THRESHOLD, REQUIRE_APPROVAL


class AuditorAgent:
    def __init__(self, risk_threshold: float = None, require_approval: bool = None):
        self.risk_threshold = risk_threshold or RISK_THRESHOLD
        self.require_approval = require_approval if require_approval is not None else REQUIRE_APPROVAL
    
    def audit_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        audit_result = {
            "approved": False,
            "warnings": [],
            "errors": [],
            "recommendations": [],
            "risk_assessment": {},
            "requires_manual_approval": False
        }
        
        total_risk = plan.get("total_risk_score", 1.0)
        audit_result["risk_assessment"]["total_risk"] = total_risk
        
        if total_risk > self.risk_threshold:
            audit_result["warnings"].append(
                f"Total risk score ({total_risk:.2f}) exceeds threshold ({self.risk_threshold:.2f})"
            )
            audit_result["requires_manual_approval"] = True
        
        steps = plan.get("steps", [])
        high_risk_steps = []
        
        for step in steps:
            step_risk = step.get("risk_score", 0.5)
            if step_risk > self.risk_threshold:
                high_risk_steps.append({
                    "step_id": step.get("id"),
                    "action": step.get("action"),
                    "risk_score": step_risk
                })
        
        if high_risk_steps:
            audit_result["warnings"].append(
                f"Found {len(high_risk_steps)} high-risk steps requiring review"
            )
            audit_result["risk_assessment"]["high_risk_steps"] = high_risk_steps
            audit_result["requires_manual_approval"] = True
        
        steps_without_rollback = [
            step for step in steps
            if step.get("risk_score", 0) > 0.3 and not step.get("rollback")
        ]
        
        if steps_without_rollback:
            audit_result["recommendations"].append(
                f"Consider adding rollback instructions for {len(steps_without_rollback)} risky steps"
            )
        
        if not steps:
            audit_result["errors"].append("Plan contains no steps")
            return audit_result
        
        destructive_ops = ["delete", "kill", "terminate", "destroy", "drop"]
        destructive_steps = []
        
        for step in steps:
            action = step.get("action", "").lower()
            if any(op in action for op in destructive_ops):
                destructive_steps.append(step.get("id"))
        
        if destructive_steps:
            audit_result["warnings"].append(
                f"Plan contains potentially destructive operations in steps: {destructive_steps}"
            )
            audit_result["requires_manual_approval"] = True
        
        # Final approval decision
        if self.require_approval:
            audit_result["requires_manual_approval"] = True
        
        if not audit_result["errors"] and not audit_result["requires_manual_approval"]:
            audit_result["approved"] = True
        elif not audit_result["errors"]:
            audit_result["approved"] = False  # Requires manual approval
        else:
            audit_result["approved"] = False
        
        return audit_result
    
    def validate_role(self, user_role: str, plan: Dict[str, Any]) -> bool:
        allowed_roles = {
            "admin": ["all"],
            "sre": ["all"],
            "engineer": ["low_risk", "medium_risk"],
            "viewer": []
        }
        
        permissions = allowed_roles.get(user_role, [])
        
        if "all" in permissions:
            return True
        
        total_risk = plan.get("total_risk_score", 1.0)
        
        if total_risk < 0.3 and "low_risk" in permissions:
            return True
        if total_risk < 0.7 and "medium_risk" in permissions:
            return True
        
        return False
