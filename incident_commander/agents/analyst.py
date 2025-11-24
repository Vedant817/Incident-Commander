from typing import Dict, Any, List
from ..mcp_clients.rag import MCPRAG


class AnalystAgent:
    def __init__(self, rag_tool: MCPRAG = None):
        self.rag_tool = rag_tool or MCPRAG()
    
    def analyze(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        service = alert.get("service", "unknown")
        description = alert.get("description", "")
        severity = alert.get("severity", "medium")
        metrics = alert.get("metrics", {})
        
        query = self._build_search_query(alert)
        
        runbook_snippets = self.rag_tool.retrieve(query, top_k=5)
        
        summary = self._generate_summary(alert, runbook_snippets)
        
        root_causes = self._identify_root_causes(alert, runbook_snippets)
        
        return {
            "alert": alert,
            "summary": summary,
            "runbook_snippets": runbook_snippets,
            "root_causes": root_causes,
            "service": service,
            "severity": severity,
            "recommendations": self._generate_recommendations(runbook_snippets)
        }
    
    def _build_search_query(self, alert: Dict[str, Any]) -> str:
        """Build search query from alert information"""
        service = alert.get("service", "")
        description = alert.get("description", "")
        alert_type = alert.get("type", "")
        
        query_parts = [service, description, alert_type]
        
        metrics = alert.get("metrics", {})
        if "cpu" in str(metrics).lower():
            query_parts.append("high CPU usage")
        if "memory" in str(metrics).lower() or "mem" in str(metrics).lower():
            query_parts.append("memory leak")
        if "error_rate" in metrics or "errors" in str(metrics).lower():
            query_parts.append("error rate")
        
        return " ".join(filter(None, query_parts))
    
    def _generate_summary(self, alert: Dict[str, Any], runbook_snippets: List[Dict]) -> str:
        service = alert.get("service", "unknown service")
        description = alert.get("description", "No description")
        severity = alert.get("severity", "medium")
        
        summary = f"Alert for {service} ({severity} severity): {description}"
        
        if runbook_snippets:
            summary += f"\n\nFound {len(runbook_snippets)} relevant runbook sections."
        
        return summary
    
    def _identify_root_causes(self, alert: Dict[str, Any], runbook_snippets: List[Dict]) -> List[str]:
        causes = []
        
        description = alert.get("description", "").lower()
        metrics = alert.get("metrics", {})
        
        if "pod" in description and ("crash" in description or "failure" in description):
            causes.append("Pod crash or OOM kill")
        
        if "cpu" in description.lower() or metrics.get("cpu", 0) > 90:
            causes.append("High CPU usage - possible resource exhaustion")
        
        if "memory" in description.lower() or metrics.get("memory", 0) > 90:
            causes.append("Memory leak or insufficient memory allocation")
        
        if "timeout" in description.lower():
            causes.append("Network or database timeout")
        
        if "error" in description.lower() or "exception" in description.lower():
            causes.append("Application error or exception")
        
        for snippet in runbook_snippets:
            content = snippet.get("content", "").lower()
            if "memory leak" in content:
                causes.append("Memory leak (from runbook)")
            if "cpu" in content and "high" in content:
                causes.append("High CPU usage (from runbook)")
        
        return list(set(causes)) if causes else ["Unknown root cause - requires investigation"]
    
    def _generate_recommendations(self, runbook_snippets: List[Dict]) -> List[str]:
        recommendations = []
        
        for snippet in runbook_snippets[:3]:
            content = snippet.get("content", "")
            if "restart" in content.lower():
                recommendations.append("Consider restarting affected pods")
            if "scale" in content.lower():
                recommendations.append("Consider scaling up resources")
            if "cache" in content.lower():
                recommendations.append("Consider clearing cache")
        
        return list(set(recommendations)) if recommendations else ["Review runbook sections for remediation steps"]
