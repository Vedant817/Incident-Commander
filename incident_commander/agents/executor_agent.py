import time
from typing import Dict, Any, List
from ..mcp_clients.executor import MCPExecutor


class ExecutorAgent:
    def __init__(self, executor: MCPExecutor = None):
        self.executor = executor or MCPExecutor()
        self.execution_log = []
    
    def execute_plan(self, plan: Dict[str, Any], step_by_step: bool = False) -> Dict[str, Any]:
        steps = plan.get("steps", [])
        execution_results = {
            "plan_id": plan.get("id", f"plan_{int(time.time())}"),
            "status": "in_progress",
            "steps_executed": [],
            "steps_failed": [],
            "rollbacks_performed": [],
            "start_time": time.time(),
            "end_time": None,
            "logs": []
        }
        
        self._log(execution_results, "Starting plan execution", "info")
        
        executed_step_ids = set()
        
        for step in steps:
            step_id = step.get("id")
            
            dependencies = step.get("dependencies", [])
            if not all(dep in executed_step_ids for dep in dependencies):
                self._log(execution_results, f"Step {step_id} waiting for dependencies: {dependencies}", "warning")
                continue
            
            step_result = self._execute_step(step, execution_results)
            
            if step_result["status"] == "success":
                executed_step_ids.add(step_id)
                execution_results["steps_executed"].append(step_id)
                self._log(execution_results, f"Step {step_id} completed successfully", "success")
            else:
                execution_results["steps_failed"].append(step_id)
                self._log(execution_results, f"Step {step_id} failed: {step_result.get('error', 'Unknown error')}", "error")
                
                if step.get("rollback"):
                    rollback_result = self._rollback_step(step, execution_results)
                    if rollback_result["status"] == "success":
                        execution_results["rollbacks_performed"].append(step_id)
                        self._log(execution_results, f"Rollback for step {step_id} completed", "info")
                
                if step_by_step:
                    execution_results["status"] = "paused"
                    break
        
        execution_results["end_time"] = time.time()
        execution_results["duration_seconds"] = execution_results["end_time"] - execution_results["start_time"]
        
        if not execution_results["steps_failed"]:
            execution_results["status"] = "completed"
            self._log(execution_results, "Plan execution completed successfully", "success")
        elif execution_results["steps_executed"]:
            execution_results["status"] = "partial"
            self._log(execution_results, "Plan execution completed with some failures", "warning")
        else:
            execution_results["status"] = "failed"
            self._log(execution_results, "Plan execution failed", "error")
        
        return execution_results
    
    def _execute_step(self, step: Dict[str, Any], execution_results: Dict[str, Any]) -> Dict[str, Any]:
        tool = step.get("tool", "")
        parameters = step.get("parameters", {})
        action = step.get("action", "")
        
        self._log(execution_results, f"Executing: {action}", "info")
        
        try:
            result = self.executor.execute(tool, parameters)
            result["step_id"] = step.get("id")
            result["step_action"] = action
            
            self.execution_log.append(result)
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "step_id": step.get("id"),
                "step_action": action,
                "error": str(e)
            }
            self.execution_log.append(error_result)
            return error_result
    
    def _rollback_step(self, step: Dict[str, Any], execution_results: Dict[str, Any]) -> Dict[str, Any]:
        rollback_instruction = step.get("rollback", "")
        step_id = step.get("id")
        
        self._log(execution_results, f"Rolling back step {step_id}: {rollback_instruction}", "warning")
        
        try:
            rollback_result = self.executor.rollback_step(step_id)
            return rollback_result
        except Exception as e:
            return {
                "status": "error",
                "error": f"Rollback failed: {str(e)}"
            }
    
    def _log(self, execution_results: Dict[str, Any], message: str, level: str = "info"):
        log_entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message
        }
        execution_results["logs"].append(log_entry)
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        return self.execution_log
    
    def execute_single_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        execution_results = {
            "status": "in_progress",
            "logs": [],
            "start_time": time.time()
        }
        
        result = self._execute_step(step, execution_results)
        execution_results.update(result)
        execution_results["end_time"] = time.time()
        execution_results["duration_seconds"] = execution_results["end_time"] - execution_results["start_time"]
        
        return execution_results
