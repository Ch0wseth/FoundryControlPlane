"""
Jedi Council Agent - Test client for demo purposes.

Sends Star Wars themed requests to the Jedi Council Agent
to generate traces and telemetry in Foundry Control Plane.

Usage:
    python test_agent.py                    # Single mission briefing
    python test_agent.py --flood 10         # Send 10 requests (for observability demo)
    python test_agent.py --scenario all     # Run all demo scenarios
"""

import argparse
import json
import time
import requests

AGENT_URL = "http://localhost:8000"
FOUNDRY_PROXY_URL = None  # Set this after registering in Foundry

SCENARIOS = {
    "mission_briefing": {
        "name": "Mission Briefing - Battle of Coruscant",
        "messages": [
            {"role": "user", "content": "Brief me on the situation on Coruscant. "
             "General Grievous has been spotted near the Senate district. "
             "What Jedi team should we deploy and what's the risk level?"}
        ],
    },
    "threat_assessment": {
        "name": "Threat Assessment - Sith Activity",
        "messages": [
            {"role": "user", "content": "We've detected unusual Force disturbances in the Outer Rim, "
             "near Mustafar. Intelligence suggests a Sith training facility. "
             "Assess the threat level and recommend a reconnaissance plan."}
        ],
    },
    "jedi_assignment": {
        "name": "Jedi Assignment - Protect Senator Amidala",
        "messages": [
            {"role": "user", "content": "Senator Amidala has received death threats from a bounty hunter. "
             "We need to assign a protection detail. Which Jedi are available "
             "and who would be the best fit for this diplomatic protection mission?"}
        ],
    },
    "risk_evaluation": {
        "name": "Risk Evaluation - Death Star Plans",
        "messages": [
            {"role": "user", "content": "The Rebel Alliance has intel about a new Imperial superweapon "
             "being constructed in the Scarif system. Evaluate the risk of a "
             "strike mission to steal the plans. What forces would we need?"}
        ],
    },
    "architecture": {
        "name": "Agent Architecture (meta-demo)",
        "messages": [
            {"role": "user", "content": "Explain your technical architecture. "
             "How are you built, how are you registered in Foundry Control Plane, "
             "and how does the observability work?"}
        ],
    },
}


def send_request(url: str, messages: list, label: str = ""):
    """Send a chat completion request and display the result."""
    print(f"\n{'='*60}")
    print(f"  >> {label}")
    print(f"{'='*60}")

    payload = {
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    start = time.time()
    try:
        resp = requests.post(f"{url}/v1/chat/completions", json=payload, timeout=60)
        latency = (time.time() - start) * 1000

        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data["usage"]
            print(f"\n  [Model: {data['model']}]")
            print(f"  [Tokens: {usage['prompt_tokens']} prompt + {usage['completion_tokens']} completion = {usage['total_tokens']} total]")
            print(f"  [Latency: {latency:.0f}ms]")
            print(f"\n  {content[:500]}{'...' if len(content) > 500 else ''}")
        elif resp.status_code == 429:
            print(f"\n  [429 Too Many Requests] Token rate limit exceeded!")
            print(f"  This is expected in Demo 3 (governance). The AI Gateway is doing its job.")
            print(f"  Response: {resp.text[:200]}")
        elif resp.status_code == 403:
            print(f"\n  [403 Forbidden] Agent is blocked or quota exceeded!")
            print(f"  Response: {resp.text[:200]}")
        else:
            print(f"\n  [HTTP {resp.status_code}] {resp.text[:300]}")

    except requests.exceptions.ConnectionError:
        print(f"\n  [Connection Error] Cannot reach {url}")
        print(f"  Is the Jedi Council Agent running?")
    except Exception as e:
        print(f"\n  [Error] {e}")

    print(f"\n{'='*60}\n")


def run_flood(url: str, count: int):
    """Send multiple requests to generate telemetry for observability demo."""
    print(f"\n  Flooding {count} requests to generate traces...")
    print(f"  (For Foundry Control Plane observability demo)\n")

    scenarios = list(SCENARIOS.values())
    for i in range(count):
        scenario = scenarios[i % len(scenarios)]
        print(f"  [{i+1}/{count}] {scenario['name']}...", end=" ", flush=True)
        try:
            resp = requests.post(
                f"{url}/v1/chat/completions",
                json={"messages": scenario["messages"], "temperature": 0.7, "max_tokens": 512},
                timeout=60,
            )
            if resp.status_code == 200:
                tokens = resp.json()["usage"]["total_tokens"]
                print(f"OK ({tokens} tokens)")
            else:
                print(f"HTTP {resp.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)  # Small delay to avoid overwhelming

    print(f"\n  Done! Check Foundry Control Plane > Operate > Assets > Traces")


def main():
    parser = argparse.ArgumentParser(description="Jedi Council Agent - Test Client")
    parser.add_argument("--url", default=AGENT_URL, help="Agent URL (default: localhost:8000)")
    parser.add_argument("--proxy", action="store_true", help="Use Foundry proxy URL instead of direct")
    parser.add_argument("--scenario", default="mission_briefing",
                        choices=list(SCENARIOS.keys()) + ["all"],
                        help="Which scenario to run")
    parser.add_argument("--flood", type=int, default=0, help="Send N requests for telemetry generation")
    args = parser.parse_args()

    url = FOUNDRY_PROXY_URL if args.proxy and FOUNDRY_PROXY_URL else args.url

    print("\n" + "="*60)
    print("  JEDI COUNCIL AGENT - Test Client")
    print(f"  Target: {url}")
    print("="*60)

    # Health check
    try:
        health = requests.get(f"{url}/health", timeout=5)
        print(f"  Health: {health.json()}")
    except Exception:
        print("  Health: UNREACHABLE - is the agent running?")
        return

    if args.flood > 0:
        run_flood(url, args.flood)
        return

    if args.scenario == "all":
        for key, scenario in SCENARIOS.items():
            send_request(url, scenario["messages"], scenario["name"])
            time.sleep(2)
    else:
        scenario = SCENARIOS[args.scenario]
        send_request(url, scenario["messages"], scenario["name"])


if __name__ == "__main__":
    main()
