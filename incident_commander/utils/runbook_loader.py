import os
from typing import List, Tuple, Dict, Any
from ..config import RUNBOOKS_PATH


def load_runbooks() -> Tuple[List[str], List[Dict[str, Any]]]:
    documents = []
    metadata = []
    
    runbooks = [
        {
            "name": "runbook-k8s-restart-pod.md",
            "content": """
# Kubernetes Pod Restart Runbook

## Overview
This runbook describes the procedure for restarting a Kubernetes pod when it becomes unresponsive or crashes.

## Prerequisites
- kubectl access to the cluster
- Pod name and namespace

## Steps

### 1. Identify the Pod
```bash
kubectl get pods -n <namespace>
```

### 2. Check Pod Status
```bash
kubectl describe pod <pod-name> -n <namespace>
```

### 3. Restart the Pod
```bash
kubectl delete pod <pod-name> -n <namespace>
```

Kubernetes will automatically recreate the pod with the same configuration.

### 4. Verify Pod Status
```bash
kubectl get pods <pod-name> -n <namespace>
```

Wait until the pod status is "Running".

## Rollback
If the restart causes issues, check the deployment history:
```bash
kubectl rollout history deployment/<deployment-name>
kubectl rollout undo deployment/<deployment-name>
```

## Risk Level
Low - Pod restart is a safe operation as Kubernetes will recreate it automatically.
""",
            "category": "kubernetes",
            "tags": ["restart", "pod", "k8s"]
        },
        {
            "name": "runbook-high-cpu.md",
            "content": """
# High CPU Usage Remediation Runbook

## Overview
This runbook addresses high CPU usage in services, which can lead to performance degradation and timeouts.

## Symptoms
- CPU usage above 80%
- Increased response times
- Timeout errors
- Service degradation

## Diagnosis Steps

### 1. Check Current CPU Usage
```bash
kubectl top pods -n <namespace>
```

### 2. Identify Resource Limits
```bash
kubectl describe pod <pod-name> -n <namespace>
```

### 3. Check Application Logs
```bash
kubectl logs <pod-name> -n <namespace> --tail=100
```

## Remediation Steps

### Option 1: Scale Horizontally
Increase the number of replicas to distribute load:
```bash
kubectl scale deployment <deployment-name> --replicas=<new-count> -n <namespace>
```

### Option 2: Increase CPU Limits
Update the deployment to increase CPU limits:
```yaml
resources:
  limits:
    cpu: "2000m"
  requests:
    cpu: "1000m"
```

### Option 3: Restart Pods
If scaling doesn't help, restart pods to clear stuck processes:
```bash
kubectl delete pod <pod-name> -n <namespace>
```

## Verification
Monitor CPU usage after remediation:
```bash
kubectl top pods -n <namespace>
```

## Risk Level
Medium - Scaling and resource changes can affect service availability.
""",
            "category": "performance",
            "tags": ["cpu", "performance", "scaling"]
        },
        {
            "name": "runbook-memory-leak.md",
            "content": """
# Memory Leak Remediation Runbook

## Overview
This runbook addresses memory leaks that cause pods to be OOM (Out of Memory) killed.

## Symptoms
- Memory usage continuously increasing
- Pods being OOM killed
- Frequent pod restarts
- Application errors related to memory

## Diagnosis Steps

### 1. Check Memory Usage
```bash
kubectl top pods -n <namespace>
```

### 2. Check Pod Events
```bash
kubectl describe pod <pod-name> -n <namespace>
```

Look for "OOMKilled" events.

### 3. Check Application Logs
```bash
kubectl logs <pod-name> -n <namespace> --previous
```

## Remediation Steps

### Immediate Actions

1. **Restart Affected Pods**
```bash
kubectl delete pod <pod-name> -n <namespace>
```

2. **Increase Memory Limits (Temporary)**
Update deployment to increase memory limits:
```yaml
resources:
  limits:
    memory: "4Gi"
  requests:
    memory: "2Gi"
```

### Long-term Fixes

1. **Identify Memory Leak Source**
   - Review application code
   - Use memory profiling tools
   - Check for unclosed connections, file handles, or caches

2. **Implement Memory Limits**
   - Set appropriate memory limits
   - Monitor memory usage trends

3. **Add Health Checks**
   - Implement memory-based health checks
   - Automatically restart pods before OOM

## Rollback
If increasing memory limits causes issues:
```bash
kubectl rollout undo deployment/<deployment-name> -n <namespace>
```

## Risk Level
High - Memory issues can cause service outages if not addressed promptly.
""",
            "category": "memory",
            "tags": ["memory", "oom", "leak"]
        },
        {
            "name": "runbook-scale-deployment.md",
            "content": """
# Scale Deployment Runbook

## Overview
This runbook describes how to scale Kubernetes deployments up or down.

## When to Scale

### Scale Up
- High CPU or memory usage
- Increased traffic
- Performance degradation

### Scale Down
- Low resource usage
- Cost optimization
- Maintenance

## Steps

### 1. Check Current Replica Count
```bash
kubectl get deployment <deployment-name> -n <namespace>
```

### 2. Scale Deployment
```bash
kubectl scale deployment <deployment-name> --replicas=<count> -n <namespace>
```

### 3. Verify Scaling
```bash
kubectl get pods -n <namespace> -l app=<app-label>
```

Wait for all pods to be in "Running" state.

### 4. Monitor Resource Usage
```bash
kubectl top pods -n <namespace>
```

## Rollback
To revert to previous replica count:
```bash
kubectl scale deployment <deployment-name> --replicas=<previous-count> -n <namespace>
```

## Risk Level
Low to Medium - Scaling is generally safe but can affect service availability during transition.
""",
            "category": "kubernetes",
            "tags": ["scale", "deployment", "replicas"]
        },
        {
            "name": "runbook-clear-cache.md",
            "content": """
# Clear Cache Runbook

## Overview
This runbook describes how to clear application caches when they become stale or corrupted.

## When to Clear Cache
- Stale data being served
- Cache corruption
- Memory pressure from cache
- Performance issues

## Steps

### For Redis Cache

1. **Connect to Redis**
```bash
kubectl exec -it <redis-pod> -n <namespace> -- redis-cli
```

2. **Clear All Keys**
```bash
FLUSHALL
```

3. **Clear Specific Pattern**
```bash
KEYS <pattern>
DEL <key>
```

### For Application Cache

1. **Restart Cache Service**
```bash
kubectl delete pod <cache-pod> -n <namespace>
```

2. **Clear via API (if available)**
```bash
curl -X POST https://<service>/api/cache/clear
```

## Verification
- Check cache hit rates
- Monitor memory usage
- Verify data freshness

## Risk Level
Low - Cache clearing is generally safe but may cause temporary performance impact.
""",
            "category": "cache",
            "tags": ["cache", "redis", "clear"]
        },
        {
            "name": "runbook-health-check.md",
            "content": """
# Health Check Runbook

## Overview
This runbook describes how to perform health checks on services.

## HTTP Health Check

### Basic Check
```bash
curl https://<service-url>/health
```

### Detailed Check
```bash
curl -v https://<service-url>/health
```

Expected response: HTTP 200 with JSON body containing service status.

## Kubernetes Health Checks

### Check Pod Status
```bash
kubectl get pods -n <namespace>
```

### Check Pod Health
```bash
kubectl describe pod <pod-name> -n <namespace>
```

Look for:
- Readiness probe status
- Liveness probe status
- Container status

## Application Health Checks

### Check Logs
```bash
kubectl logs <pod-name> -n <namespace> --tail=50
```

### Check Metrics
```bash
kubectl top pod <pod-name> -n <namespace>
```

## Risk Level
Low - Health checks are read-only operations.
""",
            "category": "monitoring",
            "tags": ["health", "check", "monitoring"]
        },
        {
            "name": "runbook-database-timeout.md",
            "content": """
# Database Timeout Remediation Runbook

## Overview
This runbook addresses database connection timeouts and query performance issues.

## Symptoms
- Database connection timeouts
- Slow query responses
- Connection pool exhaustion
- Application errors related to database

## Diagnosis Steps

### 1. Check Database Connections
```bash
# For PostgreSQL
kubectl exec -it <db-pod> -n <namespace> -- psql -c "SELECT count(*) FROM pg_stat_activity;"
```

### 2. Check Query Performance
```bash
# Check slow queries
kubectl exec -it <db-pod> -n <namespace> -- psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### 3. Check Connection Pool
Review application configuration for connection pool settings.

## Remediation Steps

### Immediate Actions

1. **Restart Database Connections**
   - Restart application pods to reset connection pools
   ```bash
   kubectl delete pod <app-pod> -n <namespace>
   ```

2. **Increase Connection Pool Size**
   - Update application configuration
   - Restart application

### Long-term Fixes

1. **Optimize Queries**
   - Add database indexes
   - Review slow queries
   - Optimize application queries

2. **Scale Database**
   - Increase database resources
   - Add read replicas

3. **Implement Connection Pooling**
   - Use connection pooler (PgBouncer, etc.)
   - Configure appropriate pool sizes

## Risk Level
Medium - Database issues can affect multiple services.
""",
            "category": "database",
            "tags": ["database", "timeout", "connection"]
        },
        {
            "name": "runbook-network-error.md",
            "content": """
# Network Error Remediation Runbook

## Overview
This runbook addresses network connectivity issues between services.

## Symptoms
- Connection refused errors
- Timeout errors
- Network unreachable
- Service discovery failures

## Diagnosis Steps

### 1. Check Service Endpoints
```bash
kubectl get endpoints -n <namespace>
```

### 2. Check Service Configuration
```bash
kubectl describe service <service-name> -n <namespace>
```

### 3. Test Connectivity
```bash
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup <service-name>
```

### 4. Check Network Policies
```bash
kubectl get networkpolicies -n <namespace>
```

## Remediation Steps

### 1. Restart Services
```bash
kubectl delete pod <pod-name> -n <namespace>
```

### 2. Check Service Selectors
Ensure service selectors match pod labels:
```bash
kubectl get pods --show-labels -n <namespace>
kubectl describe service <service-name> -n <namespace>
```

### 3. Verify Network Policies
Review and update network policies if they're blocking traffic.

### 4. Check DNS
```bash
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default
```

## Risk Level
Medium - Network issues can cause service outages.
""",
            "category": "network",
            "tags": ["network", "connectivity", "dns"]
        },
        {
            "name": "runbook-error-rate-spike.md",
            "content": """
# High Error Rate Remediation Runbook

## Overview
This runbook addresses sudden spikes in application error rates.

## Symptoms
- Error rate above 5%
- Increased 5xx HTTP status codes
- Application exceptions
- User complaints

## Diagnosis Steps

### 1. Check Error Logs
```bash
kubectl logs <pod-name> -n <namespace> --tail=100 | grep -i error
```

### 2. Check Metrics
- Review error rate metrics
- Check response time metrics
- Review resource usage

### 3. Identify Error Patterns
- Group errors by type
- Identify affected endpoints
- Check error timestamps

## Remediation Steps

### Immediate Actions

1. **Restart Affected Pods**
```bash
kubectl delete pod <pod-name> -n <namespace>
```

2. **Scale Up Services**
```bash
kubectl scale deployment <deployment-name> --replicas=<new-count> -n <namespace>
```

3. **Enable Circuit Breakers**
   - If available, enable circuit breakers
   - Isolate failing services

### Investigation

1. **Review Recent Deployments**
```bash
kubectl rollout history deployment/<deployment-name> -n <namespace>
```

2. **Check Dependencies**
   - Verify database connectivity
   - Check external API availability
   - Review cache status

3. **Analyze Error Patterns**
   - Common error messages
   - Affected user segments
   - Geographic patterns

## Rollback
If errors started after a deployment:
```bash
kubectl rollout undo deployment/<deployment-name> -n <namespace>
```

## Risk Level
High - High error rates directly impact users.
""",
            "category": "errors",
            "tags": ["error", "rate", "5xx"]
        },
        {
            "name": "runbook-disk-space.md",
            "content": """
# Disk Space Remediation Runbook

## Overview
This runbook addresses disk space issues in pods and nodes.

## Symptoms
- Disk usage above 80%
- Pod evictions
- Write failures
- Log rotation issues

## Diagnosis Steps

### 1. Check Pod Disk Usage
```bash
kubectl exec <pod-name> -n <namespace> -- df -h
```

### 2. Check Node Disk Usage
```bash
kubectl top nodes
```

### 3. Check Logs Size
```bash
kubectl exec <pod-name> -n <namespace> -- du -sh /var/log
```

## Remediation Steps

### Immediate Actions

1. **Clean Up Logs**
```bash
kubectl exec <pod-name> -n <namespace> -- find /var/log -type f -mtime +7 -delete
```

2. **Clean Up Temporary Files**
```bash
kubectl exec <pod-name> -n <namespace> -- rm -rf /tmp/*
```

3. **Restart Pods**
```bash
kubectl delete pod <pod-name> -n <namespace>
```

### Long-term Fixes

1. **Implement Log Rotation**
   - Configure log rotation policies
   - Set log retention periods

2. **Add Disk Monitoring**
   - Set up disk usage alerts
   - Monitor disk growth trends

3. **Increase Disk Size**
   - Update PVC sizes
   - Add persistent volume storage

## Risk Level
Medium - Disk space issues can cause pod evictions and service outages.
""",
            "category": "storage",
            "tags": ["disk", "storage", "space"]
        }
    ]
    
    for runbook in runbooks:
        content = runbook["content"]
        sections = content.split("\n##")
        
        for i, section in enumerate(sections):
            if section.strip():
                if i > 0:
                    section = "##" + section
                
                documents.append(section.strip())
                metadata.append({
                    "source": runbook["name"],
                    "category": runbook.get("category", "general"),
                    "tags": runbook.get("tags", []),
                    "section": i
                })
    
    return documents, metadata
