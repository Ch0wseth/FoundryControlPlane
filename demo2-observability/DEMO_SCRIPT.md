# Demo 2 – Observability in Foundry Control Plane
## "Monitoring the Jedi Order"

> **Speaker: Manue** | ~8 min

---

## What This Demo Shows

1. **Trace generation** – Sending varied Star Wars missions to produce rich telemetry
2. **Viewing traces** in Foundry Control Plane (span waterfall, LLM calls, tokens)
3. **Continuous evaluation** setup (Groundedness, Safety, Task Adherence)
4. **Fleet overview dashboard** – health scores, cost trends, anomalies

---

## Pre-Demo Setup

### 1. Agent Must Be Running & Registered (from Demo 1)
Ensure the Jedi Council Agent is:
- Running locally (`python jedi_council_agent.py`)
- Exposed via devtunnel
- Registered in Foundry Control Plane

### 2. Generate Traces (run ~5 min before the demo)
```bash
cd demo2-observability

# Generate 10 diverse Star Wars missions (direct)
python generate_traces.py --count 1

# Or through the Foundry AI Gateway proxy (recommended for demo)
python generate_traces.py --via-proxy --count 1

# With chaos scenarios (errors for interesting dashboards)
python generate_traces.py --via-proxy --chaos --count 1
```

This creates ~10-13 traces with varied:
- Token counts (short vs long missions)
- Latencies
- Temperatures (creativity levels)
- Error cases (if --chaos)

---

## Live Demo Script

### Step 1: Show Trace Generation (1 min)
Run a quick burst live:
```bash
python generate_traces.py --via-proxy --count 1
```

**Say:** *"We're sending 10 different Star Wars missions to our Jedi Council Agent – through the Foundry AI Gateway. Each request generates a full OpenTelemetry trace."*

Show the terminal output with token counts and latencies.

### Step 2: Fleet Overview Dashboard (1.5 min)
1. Open **ai.azure.com** → **Operate** → **Overview**
2. Point out:
   - **Active agents** count
   - **Run completion rate** (should be ~90% if chaos was used)
   - **Cost trends** chart
   - **Prevented behaviors** counter (will be 0 for now, comes alive in Demo 3)

**Say:** *"This is your mission control. One dashboard for ALL agents across ALL projects in your subscription. If the Death Star is draining your token budget, you'll see it here."*

### Step 3: Agent Traces (3 min) ⭐ Main event
1. Go to **Operate** → **Assets** → **Agents**
2. Click on `jedi-council-agent`
3. Open the **Traces** tab

**Show:**
- List of all calls with **Trace ID** and **Conversation ID**
- Click on a Trace ID to open the **span waterfall**:
  - Root span: `create_agent_run` (the full agent execution)
  - Child span: `gen_ai.chat` (the LLM call to GPT-4.1)
  - Attributes: `gen_ai.usage.prompt_tokens`, `gen_ai.usage.completion_tokens`
  - Latency per span

**Say:** *"Every single action of every agent is traced. You can see exactly what the agent did: which model it called, how many tokens it consumed, how long it took. If Master Yoda's responses are getting slower, you'll know exactly where the bottleneck is."*

### Step 4: Metrics Overview (1 min)
Back on the agent detail page, show:
- **Error rate** column
- **Token usage** (monthly)
- **Estimated cost**
- **Runs** count

**Say:** *"These metrics are computed automatically from the traces. No extra code needed – just configure Application Insights and Foundry does the rest."*

### Step 5: Continuous Evaluation (1.5 min)
1. On the agent, open the **Evaluation** tab (or **Monitoring** tab)
2. Show how to enable evaluators:
   - **Groundedness** – Is the agent's response grounded in its context?
   - **Relevance** – Is the response relevant to the question?
   - **Task Adherence** – Does the agent follow its instructions?
   - **Safety** – Detect harmful content, PII leakage, jailbreak attempts

**Say:** *"This is continuous evaluation – it runs on PRODUCTION traffic, not just in dev. If the Jedi Council starts hallucinating about Star Trek, Foundry will catch it."*

---

## Key Talking Points

- **Application Insights is the backend** – configure it per project, or share across projects
- **OpenTelemetry gen_ai conventions** – standard attributes (`gen_ai.agent.id`, `gen_ai.usage.*`)
- **No code changes for Foundry agents** – built-in instrumentation
- **Custom agents need OTel** – like our FastAPI agent with the `tracer` setup
- **AI Red Teaming Agent** – can automatically probe your agents for vulnerabilities
- **Cluster Analysis** – groups similar errors to find root causes faster
