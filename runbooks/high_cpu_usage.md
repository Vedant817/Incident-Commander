# Runbook: High CPU Usage on `auth-service`

## 1. Symptom

Alerts indicate that the `auth-service` is experiencing sustained CPU usage above 90%.
This can lead to slow response times, request timeouts, and potential service outages.

## 2. Diagnosis

### Step 1: Check running processes
Connect to the pod and check for any processes consuming high CPU.
```bash
# Example command to be run by the executor
ps aux --sort=-%cpu | head -n 5
```

### Step 2: Look for recent code changes
Check the deployment history for recent changes to the `auth-service` that might have introduced a performance regression.

## 3. Remediation

### Short-term: Restart the service
The most immediate way to resolve the issue is to restart the affected pod. This can clear any bad state or infinite loops.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Simulating restart for auth-service... Pod terminated and a new one is starting.' && sleep 2"}`
- **Risk:** Low. Kubernetes will automatically restart the pod.

### Mid-term: Increase replicas
If the high CPU is due to high traffic, scaling up the number of replicas can distribute the load.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Simulating scaling up auth-service to 3 replicas.' && sleep 1"}`
- **Risk:** Medium.

## 4. Rollback

If restarting the service causes further issues, the rollback procedure is to revert the deployment to the previous stable version. This is a high-risk operation and requires manual approval.
