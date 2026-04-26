"""
Jedi Council Agent - A Star Wars themed AI agent for Microsoft Foundry Control Plane demo.

This agent acts as the Jedi Council's mission briefing assistant.
It uses Azure OpenAI (GPT-4.1) to answer questions about Star Wars missions,
with full OpenTelemetry instrumentation for Foundry observability.

Usage:
    1. Set environment variables (see .env.example)
    2. Run: python jedi_council_agent.py
    3. Agent will be available at http://localhost:8000
    4. Register this endpoint in Foundry Control Plane
"""

import os
import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from openai import AzureOpenAI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
APP_INSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
AGENT_ID = os.getenv("AGENT_ID", "jedi-council-agent")
PORT = int(os.getenv("PORT", "8000"))

# ---------------------------------------------------------------------------
# OpenTelemetry Setup (for Foundry Control Plane observability)
# ---------------------------------------------------------------------------
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "jedi-council-agent",
    "gen_ai.system": "az.ai.foundry",
})

provider = TracerProvider(resource=resource)

# If App Insights is configured, export traces there
if APP_INSIGHTS_CONNECTION_STRING:
    try:
        from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
        exporter = AzureMonitorTraceExporter(connection_string=APP_INSIGHTS_CONNECTION_STRING)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        print("[OTel] Azure Monitor exporter configured")
    except ImportError:
        print("[OTel] azure-monitor-opentelemetry-exporter not installed, traces will be local only")

trace.set_tracer_provider(provider)
tracer = trace.get_tracer("jedi-council-agent", "1.0.0")

# ---------------------------------------------------------------------------
# Azure OpenAI Client
# ---------------------------------------------------------------------------
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
)

SYSTEM_PROMPT = """You are the Jedi Council's Mission Briefing Assistant.
You speak with the wisdom and gravitas of Master Yoda and the strategic mind of Mace Windu.

Your role:
- Brief Jedi Knights on their missions across the galaxy
- Provide strategic analysis of threats (Sith, Separatists, Empire)
- Recommend which Jedi should be assigned to which mission
- Assess risk levels (Youngling-safe, Padawan-level, Knight-level, Master-level, Council-only)
- Reference Star Wars lore accurately

Style: Speak formally but with occasional Yoda-isms. Use Star Wars terminology.
Always end mission briefings with "May the Force be with you."

Important: You are an AI demo agent for Microsoft Foundry Control Plane. If asked about
your architecture, explain that you run as a FastAPI service registered in Foundry via the
AI Gateway (APIM), with OpenTelemetry tracing for full observability.
"""

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Jedi Council Agent",
    description="Star Wars themed AI agent for Foundry Control Plane demo",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    messages: list[dict] = Field(..., description="Chat messages")
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, ge=1, le=4096)


class ChatResponse(BaseModel):
    """OpenAI-compatible chat completion response."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[dict]
    usage: dict


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "operational", "agent": "jedi-council", "side": "light"}


@app.get("/.well-known/agent-card.json")
async def agent_card():
    """A2A Agent Card for Foundry discovery."""
    return {
        "name": "Jedi Council Agent",
        "description": "The Jedi Council's Mission Briefing Assistant. "
                       "Provides strategic analysis, mission assignments, and threat assessments "
                       "across the Star Wars galaxy.",
        "version": "1.0.0",
        "protocol": "http",
        "capabilities": [
            "mission-briefing",
            "threat-assessment",
            "jedi-assignment",
            "risk-evaluation",
        ],
        "author": "Manue & Adil",
        "tags": ["star-wars", "demo", "foundry-control-plane"],
    }


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest):
    """
    OpenAI-compatible chat completions endpoint.
    This is what Foundry AI Gateway proxies to.
    """
    request_id = f"jedi-{uuid.uuid4().hex[:12]}"

    # --- OpenTelemetry: root span for the agent run ---
    with tracer.start_as_current_span(
        "create_agent_run",
        attributes={
            "gen_ai.system": "az.ai.foundry",
            "gen_ai.agent.id": AGENT_ID,
            "gen_ai.request.model": AZURE_OPENAI_DEPLOYMENT,
            "gen_ai.operation.name": "chat",
        },
    ) as agent_span:

        # --- OpenTelemetry: LLM call span ---
        with tracer.start_as_current_span(
            "gen_ai.chat",
            attributes={
                "gen_ai.system": "az.ai.openai",
                "gen_ai.request.model": AZURE_OPENAI_DEPLOYMENT,
                "gen_ai.request.temperature": request.temperature,
                "gen_ai.request.max_tokens": request.max_tokens,
            },
        ) as llm_span:
            try:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}] + request.messages

                start = time.time()
                response = client.chat.completions.create(
                    model=AZURE_OPENAI_DEPLOYMENT,
                    messages=messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                )
                latency_ms = (time.time() - start) * 1000

                # Record OTel attributes
                llm_span.set_attribute("gen_ai.response.model", response.model)
                llm_span.set_attribute("gen_ai.usage.prompt_tokens", response.usage.prompt_tokens)
                llm_span.set_attribute("gen_ai.usage.completion_tokens", response.usage.completion_tokens)
                llm_span.set_attribute("gen_ai.response.finish_reason", response.choices[0].finish_reason)
                llm_span.set_attribute("latency_ms", latency_ms)

            except Exception as e:
                llm_span.set_attribute("error", True)
                llm_span.set_attribute("error.message", str(e))
                raise HTTPException(status_code=500, detail=f"The Dark Side clouds everything: {e}")

        # Set agent-level attributes
        agent_span.set_attribute("gen_ai.usage.total_tokens",
                                response.usage.prompt_tokens + response.usage.completion_tokens)

        return ChatResponse(
            id=request_id,
            created=int(time.time()),
            model=response.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response.choices[0].message.content,
                },
                "finish_reason": response.choices[0].finish_reason,
            }],
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("  JEDI COUNCIL AGENT - Foundry Control Plane Demo")
    print("=" * 60)
    print(f"  Endpoint:    http://localhost:{PORT}")
    print(f"  Health:      http://localhost:{PORT}/health")
    print(f"  Agent Card:  http://localhost:{PORT}/.well-known/agent-card.json")
    print(f"  Chat API:    http://localhost:{PORT}/v1/chat/completions")
    print(f"  Model:       {AZURE_OPENAI_DEPLOYMENT}")
    print(f"  Agent ID:    {AGENT_ID}")
    print("=" * 60)
    print("  May the Force be with you.")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=PORT)
