# Runbook: Service Outage on `api-service`

## 1. Symptom

The `api-service` is not responding to requests. Monitoring systems report a 100% error rate and health checks are failing.

## 2. Diagnosis

### Step 1: Check service status
Verify if the service is running and its current state.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Checking status of api-service... Service is down.' && sleep 1"}`
- **Risk:** Low.

### Step 2: Check logs
Inspect the logs for the `api-service` to identify any critical errors or crash loops.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Fetching logs for api-service... Error: Database connection timeout.' && sleep 2"}`
- **Risk:** Low.

## 3. Remediation

### Primary Action: Restart the service
A restart can often resolve transient issues causing an outage.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Attempting to restart api-service...' && sleep 2"}`
- **Risk:** Medium.

### Secondary Action: Check database health
If the logs indicate a database issue, check the health of the database.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Pinging database... Database is responsive.' && sleep 1"}`
- **Risk:** Low.

## 4. Rollback

If the service does not recover after a restart, roll back to the last known good deployment.
