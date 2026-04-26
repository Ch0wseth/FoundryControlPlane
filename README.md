# Microsoft Foundry Control Plane – Demo Kit
### *"The Jedi Council Edition"* ⚔️

A complete demo kit for presenting **Microsoft Foundry Control Plane** at level 200/300.
Uses a Star Wars themed AI agent to demonstrate real-world governance, observability, and fleet management.

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │   Foundry Control Plane          │
                    │   (Operate > Overview/Assets/    │
                    │    Compliance/Quota/Admin)        │
                    └──────────┬──────────────────────┘
                               │ telemetry + control
                    ┌──────────▼──────────────────────┐
                    │   AI Gateway (APIM)              │
┌──────────┐        │   - Token rate limiting          │        ┌──────────────────┐
│  Client   │──────▶│   - Auth & access control        │──────▶ │  Jedi Council    │
│  (User)   │◀──────│   - Metrics emission             │◀────── │  Agent (FastAPI)  │
└──────────┘        │   - Content safety (optional)    │        │  + Azure OpenAI   │
                    └──────────┬──────────────────────┘        └──────────────────┘
                               │
                    ┌──────────▼──────────────────────┐
                    │   Application Insights           │
                    │   (OpenTelemetry traces)         │
                    └─────────────────────────────────┘
```

---

## 📋 Session Outline

| # | Topic | Speaker | Type |
|---|-------|---------|------|
| 01 | What is Microsoft Foundry? | Manue | Slides |
| 02 | What is the Control Plane & Why? | Manue | Slides |
| 03 | The Agentic Approach | Manue | Slides |
| 04 | Control Plane Key Features | Manue | Slides |
| **05** | **Register & Manage Agents** | **Adil** | **DEMO** |
| 06 | Observability Deep Dive | Adil | Slides |
| **07** | **Observability in Action** | **Manue** | **DEMO** |
| 08 | AI Gateway & MCP Tools | Adil | Slides |
| 09 | Governance & Compliance | Manue | Slides |
| **10** | **Token Limiting & Governance** | **Adil** | **DEMO** |
| 11 | Security (Defender, Purview, Entra) | Manue | Slides |
| 12 | Key Takeaways | Both | Slides |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Azure subscription with:
  - Microsoft Foundry resource + project
  - Azure OpenAI deployment (GPT-4.1)
  - AI Gateway (APIM) configured
  - Application Insights
- `devtunnel` CLI (for exposing local agent)

### Setup
```bash
# Clone the repo
git clone https://github.com/Ch0wseth/FoundryControlPlane.git
cd FoundryControlPlane

# Install dependencies
pip install -r requirements.txt

# Configure the agent
cd demo1-register-agent
cp .env.example .env
# Edit .env with your Azure OpenAI key and App Insights connection string
```

### Run the Jedi Council Agent
```bash
python demo1-register-agent/jedi_council_agent.py
```

### Expose via DevTunnel
```bash
devtunnel host -p 8000 --allow-anonymous
```

---

## 📁 Repository Structure

```
FoundryControlPlane/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .gitignore
│
├── demo1-register-agent/              # Demo 1: Agent Registration
│   ├── DEMO_SCRIPT.md                 #   Step-by-step demo guide
│   ├── jedi_council_agent.py          #   The Star Wars themed agent
│   ├── test_agent.py                  #   Test client with scenarios
│   └── .env.example                   #   Environment variables template
│
├── demo2-observability/               # Demo 2: Tracing & Monitoring
│   ├── DEMO_SCRIPT.md                 #   Step-by-step demo guide
│   └── generate_traces.py             #   Trace generator (10 Star Wars missions)
│
└── demo3-governance/                  # Demo 3: Token Limiting
    ├── DEMO_SCRIPT.md                 #   Step-by-step demo guide
    ├── test_token_limits.py           #   Rate limit test ("Empire attack")
    └── apim-token-limit-policy.xml    #   APIM policy to apply
```

---

## 🎬 Demo Details

### Demo 1: Register a Custom Agent (Adil)
**The Jedi Council Agent** – a FastAPI app using Azure OpenAI that gets registered in Foundry Control Plane.

Key points:
- Agent runs locally, exposed via devtunnel
- Registered in Foundry → gets an APIM proxy URL
- Clients must use the new URL (that's how Foundry gets control)
- Lifecycle: block/unblock the agent from the portal

### Demo 2: Observability (Manue)
**Monitoring the Jedi Order** – generate varied missions to create rich telemetry.

Key points:
- 10 diverse Star Wars missions generate varied traces
- View span waterfall in Foundry (LLM calls, tool calls, tokens)
- Set up continuous evaluation (Groundedness, Safety)
- Fleet overview dashboard with health scores

### Demo 3: Token Rate Limiting (Adil)
**The Empire vs The AI Gateway** – burst attack triggers rate limits.

Key points:
- APIM `llm-token-limit` policy set to 2000 TPM (intentionally low)
- Normal pace: all requests succeed
- Burst mode: 429s start after limit is reached
- Visible in Foundry: prevented behaviors, compliance posture

---

## 🔗 Key Resources

| Resource | URL |
|----------|-----|
| Control Plane Overview | [learn.microsoft.com/azure/foundry/control-plane/overview](https://learn.microsoft.com/en-us/azure/foundry/control-plane/overview) |
| Register Custom Agents | [learn.microsoft.com/azure/foundry/control-plane/register-custom-agent](https://learn.microsoft.com/en-us/azure/foundry/control-plane/register-custom-agent) |
| Manage Agents at Scale | [learn.microsoft.com/azure/foundry/control-plane/how-to-manage-agents](https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-manage-agents) |
| Configure AI Gateway | [learn.microsoft.com/azure/foundry/configuration/enable-ai-api-management-gateway-portal](https://learn.microsoft.com/en-us/azure/foundry/configuration/enable-ai-api-management-gateway-portal) |
| Enforce Token Limits | [learn.microsoft.com/azure/foundry/control-plane/how-to-enforce-limits-models](https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-enforce-limits-models) |
| MCP Tools Governance | [learn.microsoft.com/azure/foundry/agents/how-to/tools/governance](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/governance) |

---

## ⚡ Environment Info

| Resource | Name |
|----------|------|
| Subscription | ChowsethSubscription |
| Resource Group | chowseth-ai-rg |
| Foundry Resource | chowseth-msfoundry |
| Project 1 | chowseth-aiproj-1 |
| Project 2 | chowseth-aiproj-2 |
| AI Gateway (APIM) | chowseth-aigateway |
| App Insights | chowseth-appinsight |
| Key Vault | chowseth-kv |
| OpenAI Deployment | gpt-4.1 (GlobalStandard) |

---

*May the Force be with your Control Plane.* ⚔️