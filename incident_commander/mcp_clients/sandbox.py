import time
import random
from typing import Dict, Any


class MCPSandbox:
    def __init__(self):
        self.services = {
            "auth-service": {"status": "healthy", "pods": 3, "cpu": 45, "memory": 60},
            "api-service": {"status": "healthy", "pods": 5, "cpu": 30, "memory": 50},
            "db-service": {"status": "healthy", "pods": 2, "cpu": 20, "memory": 40},
            "cache-service": {"status": "degraded", "pods": 2, "cpu": 80, "memory": 90},
        }
        self.incidents = []
    
    def get_service_state(self, service_name: str) -> Dict[str, Any]:
        return self.services.get(service_name, {
            "status": "unknown",
            "pods": 0,
            "cpu": 0,
            "memory": 0
        })
    
    def simulate_incident(self, service_name: str, incident_type: str = "pod_failure") -> Dict[str, Any]:
        if service_name not in self.services:
            self.services[service_name] = {"status": "healthy", "pods": 1, "cpu": 0, "memory": 0}
        
        incident = {
            "service": service_name,
            "type": incident_type,
            "timestamp": time.time(),
            "severity": random.choice(["high", "medium", "low"]),
            "description": self._generate_incident_description(service_name, incident_type)
        }
        
        if incident_type == "pod_failure":
            self.services[service_name]["status"] = "degraded"
            self.services[service_name]["pods"] = max(1, self.services[service_name]["pods"] - 1)
        elif incident_type == "high_cpu":
            self.services[service_name]["cpu"] = 95
            self.services[service_name]["status"] = "degraded"
        elif incident_type == "memory_leak":
            self.services[service_name]["memory"] = 98
            self.services[service_name]["status"] = "critical"
        
        self.incidents.append(incident)
        return incident
    
    def _generate_incident_description(self, service: str, incident_type: str) -> str:
        descriptions = {
            "pod_failure": f"{service} pod crashed due to OOM (Out of Memory)",
            "high_cpu": f"{service} experiencing high CPU usage (95%+)",
            "memory_leak": f"{service} memory usage at 98%, potential memory leak",
            "network_error": f"{service} network connectivity issues",
            "database_timeout": f"{service} database connection timeouts"
        }
        return descriptions.get(incident_type, f"{service} incident detected")
    
    def apply_remediation(self, service_name: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if service_name not in self.services:
            return {"status": "error", "message": f"Service {service_name} not found"}
        
        if action == "restart_pod":
            self.services[service_name]["status"] = "healthy"
            self.services[service_name]["pods"] = params.get("target_pods", self.services[service_name]["pods"])
        elif action == "scale_up":
            self.services[service_name]["pods"] += params.get("replicas", 1)
            self.services[service_name]["cpu"] = max(0, self.services[service_name]["cpu"] - 20)
        elif action == "clear_cache":
            self.services[service_name]["memory"] = max(0, self.services[service_name]["memory"] - 30)
        elif action == "restart_service":
            self.services[service_name]["status"] = "healthy"
            self.services[service_name]["cpu"] = 30
            self.services[service_name]["memory"] = 40
        
        return {
            "status": "success",
            "service": service_name,
            "action": action,
            "new_state": self.services[service_name]
        }
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Get state of all services"""
        return self.services
    
    def reset(self):
        self.services = {
            "auth-service": {"status": "healthy", "pods": 3, "cpu": 45, "memory": 60},
            "api-service": {"status": "healthy", "pods": 5, "cpu": 30, "memory": 50},
            "db-service": {"status": "healthy", "pods": 2, "cpu": 20, "memory": 40},
            "cache-service": {"status": "healthy", "pods": 2, "cpu": 50, "memory": 60},
        }
        self.incidents = []
