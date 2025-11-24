# Runbook: Database Connection Errors

## 1. Symptom

Multiple services are reporting errors related to database connectivity. This could be due to a database outage, network issues, or configuration problems.

## 2. Diagnosis

### Step 1: Verify database health
Ping the database server to ensure it is online and responsive.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Pinging database host db.internal... Host is reachable.' && sleep 1"}`
- **Risk:** Low.

### Step 2: Check connection pool
The database connection pool might be exhausted. Check the current number of active connections.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Checking database connection pool... Pool is at 98% capacity.' && sleep 1"}`
- **Risk:** Low.

## 3. Remediation

### Action: Flush connection pool
If the connection pool is exhausted with stale connections, flushing it can resolve the issue.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Flushing database connection pool... Connections reset.' && sleep 2"}`
- **Risk:** Medium. This may interrupt active queries.

### Action: Restart application services
If flushing the pool doesn't work, restarting the application services will force them to establish fresh connections.

**Action:**
- **Tool:** `shell-command`
- **Parameters:** `{"command": "echo 'Issuing rolling restart of all application services...' && sleep 3"}`
- **Risk:** High. This can cause a brief service disruption.

## 4. Rollback

There is no direct rollback for these actions. If problems persist, the incident must be escalated to the on-call database administrator.
