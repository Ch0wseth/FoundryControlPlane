# Demo 1 – Register a Custom Agent in Foundry Control Plane
## "The Jedi Council Agent"

> **Speaker: Adil** | ~10 min

---

## What This Demo Shows

1. **A custom agent** (FastAPI + Azure OpenAI) running locally
2. **Registering it** in Foundry Control Plane via the portal
3. **The AI Gateway (APIM)** acting as a proxy – clients use the NEW Foundry URL
4. **Agent lifecycle** – viewing the agent in inventory, blocking/unblocking

---

## Pre-Demo Setup (do this BEFORE the session)

### 1. Configure Environment
```bash
cd demo1-register-agent
copy .env.example .env
# Edit .env with your Azure OpenAI key and App Insights connection string
```

### 2. Get your Azure OpenAI key
```bash
az cognitiveservices account keys list \
  --name chowseth-aiproj-1-resource \
  --resource-group chowseth-ai-rg \
  --query key1 -o tsv
```

### 3. Get App Insights connection string
```bash
az monitor app-insights component show \
  --app chowseth-appinsight \
  --resource-group chowseth-ai-rg \
  --query connectionString -o tsv
```

### 4. Start the agent
```bash
python jedi_council_agent.py
```
You should see:
```
============================================================
  JEDI COUNCIL AGENT - Foundry Control Plane Demo
============================================================
  Endpoint:    http://localhost:8000
  Health:      http://localhost:8000/health
  Agent Card:  http://localhost:8000/.well-known/agent-card.json
  Chat API:    http://localhost:8000/v1/chat/completions
============================================================
  May the Force be with you.
============================================================
```

### 5. Expose locally with devtunnel
```bash
devtunnel host -p 8000 --allow-anonymous
```
Note the public URL (e.g., `https://xxxxx.devtunnels.ms`)

---

## Live Demo Script

### Step 1: Show the Agent Running (30 sec)
- Show the terminal with the agent running
- Open browser: `http://localhost:8000/health` → `{"status": "operational", "agent": "jedi-council", "side": "light"}`
- Open: `http://localhost:8000/.well-known/agent-card.json` → show the agent card

**Say:** *"This is our Jedi Council Agent – a simple FastAPI app using Azure OpenAI. It could be built with ANY framework: LangChain, Semantic Kernel, LangGraph... Foundry doesn't care."*

### Step 2: Quick Test Locally (30 sec)
```bash
python test_agent.py --scenario mission_briefing
```
**Say:** *"Let's ask the Jedi Council for a mission briefing on the Battle of Coruscant..."*

### Step 3: Register in Foundry Control Plane (2 min)
1. Open **ai.azure.com** (New Foundry portal)
2. Click **Operate** (top-right toolbar)
3. Click **Overview** → **Register Asset**
4. Fill in:
   - **Agent URL**: `https://xxxxx.devtunnels.ms/v1/` (your tunnel URL)
   - **Protocol**: HTTP
   - **Project**: `chowseth-aiproj-1`
   - **Agent Name**: `jedi-council-agent`
   - **Description**: "The Jedi Council's Mission Briefing Assistant"
   - **OpenTelemetry Agent ID**: `jedi-council-agent`
5. Click **Save**

**Say:** *"Notice Foundry uses APIM as a proxy. It generates a NEW URL – all clients must use THIS url from now on. This is how Foundry gets visibility and control."*

### Step 4: Show the New Proxy URL (30 sec)
1. Go to **Assets** → **Agents**
2. Filter **Source = Custom**
3. Click on `jedi-council-agent`
4. Copy the **Agent URL** (the APIM proxy URL)

**Say:** *"The proxy URL looks like `https://chowseth-aigateway.azure-api.net/jedi-council-agent/v1/`. All traffic now goes through the AI Gateway."*

### Step 5: Test via the Proxy (1 min)
Update `test_agent.py` FOUNDRY_PROXY_URL with the new URL:
```bash
python test_agent.py --proxy --scenario threat_assessment
```

**Say:** *"Same request, same response – but now it's going through the AI Gateway. Foundry is logging everything: tokens, latency, cost."*

### Step 6: Block the Agent (30 sec)
1. In **Assets**, select `jedi-council-agent`
2. Click **Update Status** → **Block**
3. Try calling again:
```bash
python test_agent.py --proxy --scenario jedi_assignment
```
→ Shows the agent is blocked (requests rejected)

**Say:** *"If an agent misbehaves – maybe it's been compromised by the Dark Side – an admin can block it instantly. No need to touch the infrastructure."*

4. **Unblock** the agent to restore access

---

## Key Talking Points

- **Any framework works**: FastAPI, LangChain, Semantic Kernel, LangGraph, Flask...
- **APIM as proxy**: This is what gives Foundry control – auth, rate limiting, monitoring
- **Agent card** (`.well-known/agent-card.json`): Optional but useful for A2A discovery
- **OpenTelemetry**: The `gen_ai.agent.id` attribute links traces to this agent in Foundry
- **Block/Unblock**: Only lifecycle operation for custom agents (no start/stop since Foundry doesn't own the infra)
