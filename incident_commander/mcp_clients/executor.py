import time
import subprocess
from typing import Dict, Any

class MCPExecutor:
    def __init__(self, mode: str = "sandbox"):
        self.mode = mode
        self.execution_history = []

    def execute(self, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if self.mode == "sandbox":
            return self._execute_sandbox(tool, parameters)
        else:
            return self._execute_real(tool, parameters)

    def _execute_sandbox(self, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(0.5)
        command = parameters.get('command', 'echo "No command specified"')

        result = {
            "status": "success",
            "tool": tool,
            "parameters": parameters,
            "output": {
                "message": f"Simulated execution of: {command}",
                "stdout": f"Fake output for: {command}",
                "stderr": "",
                "return_code": 0,
            },
            "timestamp": time.time(),
            "duration_seconds": 0.5,
            "mode": "sandbox"
        }
        self.execution_history.append(result)
        return result

    def _execute_real(self, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            if tool == "shell-command":
                result = self._shell_command(parameters)
            else:
                result = {
                    "status": "error",
                    "error": f"Unknown tool: {tool}"
                }
            
            result["duration_seconds"] = time.time() - start_time
            result["timestamp"] = time.time()
            result["mode"] = "real"
            
        except Exception as e:
            result = {
                "status": "error",
                "error": str(e),
                "duration_seconds": time.time() - start_time,
                "timestamp": time.time(),
                "mode": "real"
            }
        
        self.execution_history.append(result)
        return result

    def _shell_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        command = params.get("command")
        if not command:
            return {
                "status": "error",
                "error": "No command specified for shell-command tool."
            }

        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            status = "success" if process.returncode == 0 else "error"
            
            return {
                "status": status,
                "tool": "shell-command",
                "parameters": params,
                "output": {
                    "message": f"Command executed with return code {process.returncode}",
                    "stdout": process.stdout.strip(),
                    "stderr": process.stderr.strip(),
                    "return_code": process.returncode,
                }
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "tool": "shell-command",
                "parameters": params,
                "output": { "error": "Command timed out after 60 seconds." }
            }
        except Exception as e:
            return {
                "status": "error",
                "tool": "shell-command",
                "parameters": params,
                "output": { "error": f"An unexpected error occurred: {str(e)}" }
            }

    def get_execution_history(self) -> list:
        """Get execution history"""
        return self.execution_history

    def rollback_step(self, step_id: int) -> Dict[str, Any]:
        return {
            "status": "info",
            "message": f"Rollback for step {step_id} acknowledged. Automatic rollback is not yet implemented. Please perform manual rollback if needed.",
            "step_id": step_id
        }
