"""
Demo 2 - Observability: Generate traces & telemetry for the Jedi Council Agent.

This script sends a series of varied Star Wars missions to the agent,
generating rich telemetry data visible in Foundry Control Plane.

Run AFTER Demo 1 (agent must be registered and running).

Usage:
    python generate_traces.py                      # Standard trace generation
    python generate_traces.py --via-proxy           # Through Foundry AI Gateway
    python generate_traces.py --via-proxy --chaos   # Include error scenarios
"""

import argparse
import json
import random
import time
import requests

LOCAL_URL = "http://localhost:8000"
# Update this after registering the agent in Foundry
PROXY_URL = "https://chowseth-aigateway.azure-api.net/jedi-council-agent/v1"

# ---------------------------------------------------------------------------
# Star Wars Missions - varied scenarios to create diverse traces
# ---------------------------------------------------------------------------
MISSIONS = [
    # Normal missions (should succeed)
    {
        "name": "Operation Endor Shield",
        "messages": [{"role": "user", "content":
            "The Rebel Alliance is planning an assault on the second Death Star's shield generator "
            "on the forest moon of Endor. We need a small strike team. Recommend the team composition, "
            "risk assessment, and extraction plan."}],
        "temperature": 0.7,
    },
    {
        "name": "Kamino Investigation",
        "messages": [{"role": "user", "content":
            "Master Kenobi has discovered a secret clone army on Kamino commissioned 10 years ago. "
            "Assess the implications for the Republic and recommend next steps for the Council."}],
        "temperature": 0.5,
    },
    {
        "name": "Naboo Blockade Response",
        "messages": [{"role": "user", "content":
            "The Trade Federation has blockaded Naboo. Queen Amidala requests Jedi intervention. "
            "What team should we send? Consider the diplomatic implications."}],
        "temperature": 0.7,
    },
    {
        "name": "Mandalore Peace Talks",
        "messages": [{"role": "user", "content":
            "Duchess Satine of Mandalore has requested Jedi protection during peace negotiations. "
            "Death Watch is threatening to disrupt the talks. Assign a Jedi and provide security assessment."}],
        "temperature": 0.6,
    },
    {
        "name": "Geonosis Arena Rescue",
        "messages": [{"role": "user", "content":
            "Obi-Wan, Anakin, and Senator Amidala are captured on Geonosis. Count Dooku is present. "
            "This is a full-scale military operation. Mobilize all available Jedi. Give me the battle plan."}],
        "temperature": 0.8,
    },
    {
        "name": "Ahsoka's Trial",
        "messages": [{"role": "user", "content":
            "Padawan Ahsoka Tano is accused of bombing the Jedi Temple. Review the evidence, "
            "assess her innocence probability, and recommend whether the Council should intervene."}],
        "temperature": 0.4,
    },
    {
        "name": "Order 66 Contingency",
        "messages": [{"role": "user", "content":
            "CLASSIFIED: We've intercepted communications suggesting the clone army has hidden "
            "behavioral programming. If activated, clones would turn on Jedi. Assess this threat "
            "and propose countermeasures. Priority: COUNCIL-ONLY."}],
        "temperature": 0.3,
    },
    {
        "name": "Scarif Recon",
        "messages": [{"role": "user", "content":
            "Intelligence reports a heavily fortified Imperial data vault on Scarif containing "
            "Death Star technical readouts. A volunteer team wants to extract the plans. "
            "What is the probability of success and acceptable casualty threshold?"}],
        "temperature": 0.7,
    },
    {
        "name": "Dagobah Anomaly",
        "messages": [{"role": "user", "content":
            "We're detecting unusually strong Force readings from the Dagobah system. "
            "No known civilizations. The Dark Side signature is... confusing. It's both "
            "dark and light. Should we investigate? What precautions?"}],
        "temperature": 0.8,
    },
    {
        "name": "Youngling Training Schedule",
        "messages": [{"role": "user", "content":
            "Simple request: draft next week's Youngling training schedule. Include lightsaber "
            "basics, Force meditation, and galactic history. Keep it appropriate for ages 5-10."}],
        "temperature": 0.9,
    },
]

# Chaos scenarios (for error trace generation)
CHAOS_SCENARIOS = [
    {
        "name": "[CHAOS] Empty message",
        "messages": [],
        "temperature": 0.7,
        "expect_error": True,
    },
    {
        "name": "[CHAOS] Extremely long prompt",
        "messages": [{"role": "user", "content": "Tell me everything " * 500}],
        "temperature": 0.7,
        "expect_error": True,
    },
    {
        "name": "[CHAOS] Invalid temperature",
        "messages": [{"role": "user", "content": "Hello there!"}],
        "temperature": 5.0,
        "expect_error": True,
    },
]


def send_mission(url: str, mission: dict, index: int, total: int):
    """Send a single mission and report results."""
    name = mission["name"]
    print(f"  [{index}/{total}] {name}...", end=" ", flush=True)

    payload = {
        "messages": mission["messages"],
        "temperature": mission.get("temperature", 0.7),
        "max_tokens": 512,
    }

    try:
        start = time.time()
        resp = requests.post(f"{url}/v1/chat/completions", json=payload, timeout=120)
        latency = (time.time() - start) * 1000

        if resp.status_code == 200:
            data = resp.json()
            tokens = data["usage"]["total_tokens"]
            print(f"OK ({tokens} tokens, {latency:.0f}ms)")
            return {"status": "success", "tokens": tokens, "latency": latency}
        else:
            print(f"HTTP {resp.status_code} ({latency:.0f}ms)")
            return {"status": "error", "code": resp.status_code, "latency": latency}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "exception", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Generate traces for Foundry observability demo")
    parser.add_argument("--via-proxy", action="store_true", help="Route through Foundry AI Gateway")
    parser.add_argument("--chaos", action="store_true", help="Include error/chaos scenarios")
    parser.add_argument("--count", type=int, default=1, help="Number of full cycles to run")
    args = parser.parse_args()

    url = PROXY_URL if args.via_proxy else LOCAL_URL
    missions = MISSIONS.copy()
    if args.chaos:
        missions.extend(CHAOS_SCENARIOS)

    total = len(missions) * args.count

    print("\n" + "=" * 60)
    print("  FOUNDRY OBSERVABILITY - Trace Generator")
    print("  Theme: Star Wars Jedi Council Missions")
    print(f"  Target: {url}")
    print(f"  Missions: {len(missions)} x {args.count} cycle(s) = {total} requests")
    print(f"  Chaos mode: {'ON' if args.chaos else 'OFF'}")
    print("=" * 60 + "\n")

    # Health check
    try:
        base = url.rstrip("/").rsplit("/v1", 1)[0]
        health = requests.get(f"{base}/health", timeout=5)
        print(f"  Agent health: {health.json()}\n")
    except Exception:
        print(f"  Agent health: checking via {url}...")

    stats = {"success": 0, "error": 0, "total_tokens": 0, "total_latency": 0}

    for cycle in range(args.count):
        if args.count > 1:
            print(f"\n  --- Cycle {cycle+1}/{args.count} ---")
        random.shuffle(missions)

        for i, mission in enumerate(missions):
            result = send_mission(url, mission, (cycle * len(missions)) + i + 1, total)
            if result["status"] == "success":
                stats["success"] += 1
                stats["total_tokens"] += result["tokens"]
                stats["total_latency"] += result["latency"]
            else:
                stats["error"] += 1
            time.sleep(2)  # Space out requests for cleaner traces

    # Summary
    print("\n" + "=" * 60)
    print("  TRACE GENERATION COMPLETE")
    print(f"  Successful: {stats['success']}")
    print(f"  Errors:     {stats['error']}")
    print(f"  Total tokens: {stats['total_tokens']}")
    if stats["success"] > 0:
        print(f"  Avg latency: {stats['total_latency']/stats['success']:.0f}ms")
    print("=" * 60)
    print("\n  Now go to Foundry Portal:")
    print("  1. Operate > Assets > select 'jedi-council-agent'")
    print("  2. Open 'Traces' tab to see all calls")
    print("  3. Click a Trace ID to see the span waterfall")
    print("  4. Check Overview dashboard for fleet metrics\n")


if __name__ == "__main__":
    main()
