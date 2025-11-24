# 🚨 Incident Commander: Autonomous SRE Agent

An AI-powered, autonomous SRE agent designed to **detect**, **diagnose**, **plan**, and **execute** incident remediation actions using **MCP-enabled tool execution**, **RAG-powered runbook retrieval**, and **multi-step reasoning**.

## Features

### Core Autonomy
- ✅ Multi-step reasoning for complex incident resolution
- ✅ Runbook selection via RAG (Retrieval Augmented Generation)
- ✅ Plan decomposition with HTN planning
- ✅ Safe execution with rollback logic

### MCP Features
- ✅ MCP Planner Tool (LLM-based structured planning)
- ✅ MCP Executor Tool (Kubernetes / Cloud APIs / GitHub Actions)
- ✅ MCP Sandbox Tool (for demo mode)
- ✅ MCP Runbook Retrieval Tool (RAG)

### UX Features
- ✅ Incident Feed with severity color coding
- ✅ Plan Visualizer with timeline
- ✅ Approval workflow
- ✅ Step execution logs
- ✅ Real-time status indicators
- ✅ Automatic postmortem generation

### Safety
- ✅ Role-based access control
- ✅ Approval gates
- ✅ Audit logs
- ✅ Strict MCP execution boundaries

## Architecture

```
               ┌───────────────────────────────────────────┐
               │               Gradio UI                   │
               │  - Incident feed                          │
               │  - Plan viewer                            │
               │  - Approval & Execution controls          │
               │  - Logs & Postmortem                      │
               └───────────────────────────────────────────┘
                                │
                                ▼
               ┌───────────────────────────────────────────┐
               │           Agent Orchestrator              │
               │  - Analyst Agent (RAG)                    │
               │  - Commander Agent (Planner)              │
               │  - Executor Agent (Tool caller)           │
               │  - Auditor Agent (Policy)                 │
               └───────────────────────────────────────────┘
                                │
                                ▼
             ┌─────────────────────────────────────────────────┐
             │                   MCP Tools                     │
             │  1. mcp-planner (LLM-based structured planner)  │
             │  2. mcp-executor (K8s, Cloud APIs, GitHub...)   │
             │  3. mcp-sandbox (demo simulator)                │
             │  4. mcp-rag (runbook retriever)                 │
             └─────────────────────────────────────────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │    Vector DB (FAISS)    │
                   │  - Runbooks             │
                   │  - Past incidents       │
                   │  - Deployment history   │
                   └─────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Vedant817/Incident-Commander.git
cd "Incident-Commander"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:


4. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:7860`

## Usage

### 1. Incident Stream Tab

- View active alerts
- Simulate incidents for testing
- Create custom alerts
- Analyze incidents to generate remediation plans

### 2. Plan Tab

- Review generated remediation plans
- View plan reasoning and runbook references
- Check risk assessments
- Approve or reject plans

### 3. Execution Tab

- Execute remediation plans (all steps or step-by-step)
- Monitor execution logs in real-time
- View step status
- Perform rollbacks if needed

### 4. Postmortem Tab

- View automatically generated postmortem documents
- Edit postmortem content
- Export as Markdown or JSON

## Agent System

### 🔍 Analyst Agent
- Understands alerts and retrieves relevant runbook sections
- Identifies potential root causes
- Generates context bundles for planning

### 🧠 Commander Agent
- Converts context into structured remediation plans
- Creates multi-step plans with dependencies
- Adds rollback instructions and risk scores

### ⚙️ Executor Agent
- Executes plan steps via MCP tools
- Handles failures and rollbacks
- Maintains execution logs

### 🛡️ Auditor Agent
- Validates plans for safety and compliance
- Checks risk scores
- Enforces approval requirements
- Validates user roles

## MCP Tools

### mcp-planner
Generates structured remediation plans using LLM reasoning.

### mcp-executor
Executes infrastructure actions:
- Kubernetes pod restarts
- Deployment scaling
- Cache clearing
- HTTP health checks
- Pod termination

### mcp-sandbox
Simulates infrastructure for demo purposes without affecting real systems.

### mcp-rag
Retrieves relevant runbook sections using semantic search over a FAISS vector store.

## Runbooks

The system includes 10+ sample runbooks covering:
- Kubernetes pod restarts
- High CPU usage remediation
- Memory leak fixes
- Deployment scaling
- Cache clearing
- Health checks
- Database timeouts
- Network errors
- Error rate spikes
- Disk space issues

## Configuration

Key configuration options in `.env`:

- `HUGGINGFACE_API_KEY`: Required for calling hosted Qwen models via Hugging Face Inference
- `LLM_PROVIDER`: Set to `huggingface` (default) or `ollama` if you are serving Qwen locally
- `LLM_MODEL`: Defaults to `Qwen/Qwen2.5-7B-Instruct` for reasoning + planning
- `EMBEDDING_MODEL`: Defaults to `BAAI/bge-large-en` for runbook retrieval embeddings
- `MCP_MODE`: Set to `sandbox` for safe demo mode, `real` for actual execution
- `RISK_THRESHOLD`: Maximum acceptable risk score (0.0-1.0)
- `REQUIRE_APPROVAL`: Require manual approval for all plans

## Safety Features

1. **Sandbox Mode**: Default mode simulates all actions without affecting real infrastructure
2. **Risk Assessment**: All plans are scored for risk and require approval if above threshold
3. **Audit Logs**: Complete audit trail of all actions
4. **Rollback Support**: Automatic rollback on step failures
5. **Role-Based Access**: Control who can execute plans

mcp-in-action-track-xx