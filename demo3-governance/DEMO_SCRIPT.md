# Demo 3 – Governance: Token Rate Limiting & Compliance
## "The Empire vs The AI Gateway"

> **Speaker: Adil** | ~10 min

---

## What This Demo Shows

1. **Token rate limiting** via AI Gateway (APIM) – the `llm-token-limit` policy
2. **Burst attack** – The Empire tries to overwhelm the Jedi Council Agent
3. **429 responses** – AI Gateway protects the Republic's resources
4. **Compliance dashboard** – viewing policy enforcement in Foundry Control Plane
5. **Bonus**: Blocking an agent from the Compliance pane

---

## Pre-Demo Setup

### 1. Apply the APIM Token Limit Policy

**Option A: Via Azure Portal**
1. Go to portal.azure.com > API Management > `chowseth-aigateway`
2. APIs > select the `jedi-council-agent` API (created when you registered the agent)
3. **Design** tab > All operations > **Inbound processing** > `</>` Code editor
4. Paste the content from `apim-token-limit-policy.xml`
5. Click **Save**

**Option B: Via Azure CLI**
```bash
# Export current policy, modify, and re-import
az apim api operation policy show \
  --resource-group chowseth-ai-rg \
  --service-name chowseth-aigateway \
  --api-id jedi-council-agent \
  --operation-id <operation-id> \
  --format xml
```

### 2. Key Policy Settings
```xml
<llm-token-limit
    tokens-per-minute="2000"
    counter-key="@(context.Subscription.Id)"
    estimate-prompt-tokens="true" />
```
- **2000 TPM** is intentionally LOW for the demo
- Counter is per subscription (so all clients under one sub share the limit)
- `estimate-prompt-tokens="true"` counts tokens BEFORE sending to backend

### 3. Agent Must Be Running (from Demo 1)

---

## Live Demo Script

### Step 1: Explain the Setup (1 min)
Show the APIM policy XML on screen.

**Say:** *"The AI Gateway sits in front of every agent, model, and tool in Foundry. We've configured a token rate limit of 2000 tokens per minute. This is like the Jedi Temple's shield generator – it protects our resources from being overwhelmed."*

**Say:** *"Notice the `llm-token-limit` policy. Unlike traditional rate limiting that counts requests, this counts TOKENS. A short question costs fewer tokens than asking for a full galactic history. Smart rate limiting for the AI era."*

### Step 2: Normal Pace – Should Succeed (2 min)
```bash
cd demo3-governance
python test_token_limits.py --via-proxy
```

Show 4 requests going through normally, with token counts.

**Say:** *"At normal pace, the Jedi Council responds to all missions. Notice the token count per request – we're tracking prompt + completion tokens."*

### Step 3: Burst Attack – The Empire Strikes Back (3 min) ⭐
```bash
python test_token_limits.py --via-proxy --burst
```

Watch as the first few requests succeed, then 429s start appearing:
```
  [1/8] 200 OK - 850 tokens
  [2/8] 200 OK - 920 tokens
  [3/8] 429 RATE LIMITED - Retry-After: 42s
       The AI Gateway is protecting the Republic's resources!
  [4/8] 429 RATE LIMITED - Retry-After: 38s
  ...
```

**Say:** *"The Empire tried to overwhelm our Jedi Council with rapid-fire requests. But the AI Gateway caught it – after ~2000 tokens in a minute, it starts returning 429 Too Many Requests. The Retry-After header tells the client when to try again."*

**Say:** *"This is CRITICAL for enterprise governance. Without this, one rogue application could consume your entire Azure OpenAI quota and impact every other team."*

### Step 4: Show in Foundry Control Plane (2 min)
1. Go to **Operate** → **Overview**
   - Point out **"Prevented behaviors"** counter (should have increased)
   - Show **cost trends** (token consumption capped)

2. Go to **Operate** → **Assets** → `jedi-council-agent` → **Traces**
   - Show the 429 traces alongside successful ones
   - Point out the difference in token consumption

3. Go to **Operate** → **Compliance**
   - Show policy assignments
   - Show compliance posture across agents

**Say:** *"Everything is visible in one place. Which agents are compliant, which are hitting limits, which need attention. This is fleet governance – not per-project firefighting."*

### Step 5: Bonus – Other Governance Capabilities (1 min)
Quickly mention/show:
- **Quota management**: Operate → Quota → adjust model quotas
- **Block an agent**: Assets → select agent → Update Status → Block
- **Bulk remediation**: Compliance → select non-compliant agents → remediate

**Say:** *"Token rate limiting is just one governance lever. You can also enforce content safety, manage quotas, block misbehaving agents, and apply policies across your entire fleet from this single Control Plane."*

---

## Key Talking Points

- **`llm-token-limit` vs classic rate limit**: Token-aware, not just request-count
- **Granularity**: Per subscription, per deployment, per client, per project
- **`llm-emit-token-metric`**: Feeds dashboards and cost attribution
- **Rolling window**: 60-second rolling window for TPM
- **Response headers**: `x-ratelimit-remaining-tokens` tells clients their budget
- **Content Safety**: Can also be enforced at gateway level (separate policy)
- **No code changes**: Governance is applied at the infrastructure layer

---

## Policy Reference

| Policy | What It Does |
|--------|-------------|
| `llm-token-limit` | Enforce TPM limits, returns 429 when exceeded |
| `llm-emit-token-metric` | Emit token usage metrics for dashboards |
| `llm-content-safety` | Content filtering at gateway level |
| `llm-semantic-cache-lookup` | Cache similar prompts to save tokens |
| `rate-limit-by-key` | Classic request-count rate limiting |
| `ip-filter` | Restrict access by IP range |
