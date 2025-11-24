from typing import List, Dict, Any
from ..rag.vector_store import VectorStore


class MCPRAG:
    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store or VectorStore()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.vector_store.is_initialized():
            return self._get_fallback_results(query)
        
        results = self.vector_store.search(query, top_k=top_k)
        
        return [
            {
                "content": result.get("content", ""),
                "source": result.get("source", "unknown"),
                "score": result.get("score", 0.0),
                "metadata": result.get("metadata", {})
            }
            for result in results
        ]
    
    def _get_fallback_results(self, query: str) -> List[Dict[str, Any]]:
        fallback_snippets = [
            {
                "content": "To restart a Kubernetes pod: 1) Identify the pod name using 'kubectl get pods', 2) Delete the pod with 'kubectl delete pod <pod-name>', 3) Kubernetes will automatically recreate the pod.",
                "source": "runbook-k8s-restart.md",
                "score": 0.8,
                "metadata": {"category": "kubernetes", "action": "restart"}
            },
            {
                "content": "For high CPU usage: 1) Check current resource limits, 2) Scale horizontally by increasing replica count, 3) Monitor CPU metrics after scaling.",
                "source": "runbook-high-cpu.md",
                "score": 0.7,
                "metadata": {"category": "performance", "action": "scale"}
            },
            {
                "content": "Memory leak remediation: 1) Identify pods with high memory usage, 2) Restart affected pods, 3) Check application logs for memory leak patterns, 4) Consider increasing memory limits if needed.",
                "source": "runbook-memory-leak.md",
                "score": 0.75,
                "metadata": {"category": "memory", "action": "restart"}
            }
        ]
        
        query_lower = query.lower()
        if "restart" in query_lower or "pod" in query_lower:
            return [fallback_snippets[0]]
        elif "cpu" in query_lower or "performance" in query_lower:
            return [fallback_snippets[1]]
        elif "memory" in query_lower:
            return [fallback_snippets[2]]
        
        return fallback_snippets[:2]
