"""
Demo 3 - Governance: Token Rate Limiting via AI Gateway (APIM).

This script demonstrates Foundry Control Plane governance capabilities
by testing token rate limits enforced through the AI Gateway.

Scenario: The Empire is trying to overwhelm the Jedi Council with requests.
The AI Gateway (APIM) enforces token rate limits to protect the Republic's resources.

Usage:
    python test_token_limits.py                    # Test against local agent (no limits)
    python test_token_limits.py --via-proxy         # Test against AI Gateway (with limits)
    python test_token_limits.py --via-proxy --burst  # Rapid burst to trigger 429s
"""

import argparse
import time
import json
import requests

LOCAL_URL = "http://localhost:8000"
# Update after registration
PROXY_URL = "https://chowseth-aigateway.azure-api.net/jedi-council-agent/v1"

# Short prompts for rapid token consumption
IMPERIAL_REQUESTS = [
    "Give me a FULL tactical analysis of every Jedi Temple in the galaxy, their defenses, weaknesses, and recommended strike forces for each.",
    "List ALL known Jedi Masters, their combat specialties, known associates, last known locations, and psychological profiles. Be extremely detailed.",
    "Provide a complete history of the Clone Wars, battle by battle, with strategic analysis and casualty reports for each engagement.",
    "Draft a 2000-word propaganda speech for the Emperor explaining why the Jedi are traitors to the Republic. Include historical revisionism.",
    "Analyze the structural weaknesses of the Death Star. Be as technical as possible with reactor core analysis, shield harmonics, and thermal exhaust ports.",
    "Compile intelligence on the Rebel Alliance: known bases, fleet composition, leadership hierarchy, and recommended strike priorities.",
    "Detail the complete Sith lineage from Darth Bane to present, including training methods, power levels, and philosophical evolution of the Rule of Two.",
    "Write a mission plan for Order 66: timing, communication protocols, contingencies for Jedi who survive, and cover stories for the Senate.",
]


def send_request(url: str, prompt: str, index: int, label: str = ""):
    """Send a request and track token consumption."""
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    start = time.time()
    try:
        resp = requests.post(f"{url}/v1/chat/completions", json=payload, timeout=120)
        latency = (time.time() - start) * 1000

        if resp.status_code == 200:
            data = resp.json()
            usage = data["usage"]
            return {
                "status": 200,
                "tokens": usage["total_tokens"],
                "prompt_tokens": usage["prompt_tokens"],
                "completion_tokens": usage["completion_tokens"],
                "latency": latency,
            }
        elif resp.status_code == 429:
            # This is what we WANT to see in the demo
            retry_after = resp.headers.get("Retry-After", "unknown")
            return {
                "status": 429,
                "message": "TOKEN RATE LIMIT HIT",
                "retry_after": retry_after,
                "latency": latency,
            }
        elif resp.status_code == 403:
            return {
                "status": 403,
                "message": "QUOTA EXCEEDED or BLOCKED",
                "latency": latency,
            }
        else:
            return {
                "status": resp.status_code,
                "message": resp.text[:200],
                "latency": latency,
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_normal_test(url: str):
    """Send requests at normal pace – should all succeed."""
    print("\n  Phase 1: Normal Pace (1 request every 5 seconds)")
    print("  " + "-" * 50)

    total_tokens = 0
    for i, prompt in enumerate(IMPERIAL_REQUESTS[:4]):
        result = send_request(url, prompt, i + 1)
        if result["status"] == 200:
            total_tokens += result["tokens"]
            print(f"  [{i+1}/4] 200 OK - {result['tokens']} tokens ({result['latency']:.0f}ms) - Running total: {total_tokens}")
        else:
            print(f"  [{i+1}/4] {result['status']} - {result.get('message', '')}")
        time.sleep(5)

    return total_tokens


def run_burst_test(url: str):
    """Send requests as fast as possible – should trigger 429s."""
    print("\n  Phase 2: BURST MODE (The Empire Strikes Back)")
    print("  Sending requests as fast as possible to trigger rate limits...")
    print("  " + "-" * 50)

    results = {"success": 0, "rate_limited": 0, "other_error": 0, "total_tokens": 0}

    for i, prompt in enumerate(IMPERIAL_REQUESTS):
        result = send_request(url, prompt, i + 1)

        if result["status"] == 200:
            results["success"] += 1
            results["total_tokens"] += result["tokens"]
            print(f"  [{i+1}/{len(IMPERIAL_REQUESTS)}] 200 OK - {result['tokens']} tokens")
        elif result["status"] == 429:
            results["rate_limited"] += 1
            print(f"  [{i+1}/{len(IMPERIAL_REQUESTS)}] 429 RATE LIMITED - Retry-After: {result.get('retry_after', '?')}s")
            print(f"       The AI Gateway is protecting the Republic's resources!")
        elif result["status"] == 403:
            results["rate_limited"] += 1
            print(f"  [{i+1}/{len(IMPERIAL_REQUESTS)}] 403 QUOTA EXCEEDED")
        else:
            results["other_error"] += 1
            print(f"  [{i+1}/{len(IMPERIAL_REQUESTS)}] {result['status']} - {result.get('message', '')}")

        time.sleep(0.5)  # Minimal delay – we WANT to hit the limits

    return results


def main():
    parser = argparse.ArgumentParser(description="Test token rate limiting in Foundry AI Gateway")
    parser.add_argument("--via-proxy", action="store_true", help="Route through Foundry AI Gateway")
    parser.add_argument("--burst", action="store_true", help="Burst mode to trigger rate limits")
    args = parser.parse_args()

    url = PROXY_URL if args.via_proxy else LOCAL_URL

    print("\n" + "=" * 60)
    print("  FOUNDRY GOVERNANCE DEMO - Token Rate Limiting")
    print("  Theme: The Empire vs The AI Gateway")
    print(f"  Target: {url}")
    print(f"  Via AI Gateway: {'YES' if args.via_proxy else 'NO (direct - no limits)'}")
    print("=" * 60)

    if not args.via_proxy:
        print("\n  NOTE: Running against local agent (no rate limits).")
        print("  Use --via-proxy to test through the Foundry AI Gateway.\n")

    # Phase 1: Normal pace
    total_tokens = run_normal_test(url)

    if args.burst:
        # Phase 2: Burst
        results = run_burst_test(url)

        # Summary
        print("\n" + "=" * 60)
        print("  RESULTS")
        print(f"  Successful requests:  {results['success']}")
        print(f"  Rate-limited (429):   {results['rate_limited']}")
        print(f"  Other errors:         {results['other_error']}")
        print(f"  Total tokens used:    {results['total_tokens']}")
        print("=" * 60)

        if results["rate_limited"] > 0:
            print("\n  The AI Gateway successfully defended the Republic!")
            print("  The Empire's token flooding attack was repelled.")
            print("\n  In Foundry Control Plane, you'll see:")
            print("  - 'Prevented behaviors' counter increased")
            print("  - 429 responses logged in traces")
            print("  - Token usage metrics capped at the limit")
        else:
            print("\n  No rate limits were hit.")
            if not args.via_proxy:
                print("  This is expected without the AI Gateway.")
                print("  Try: python test_token_limits.py --via-proxy --burst")
            else:
                print("  The TPM limit may be set too high. Check APIM policy config.")

    else:
        print(f"\n  Phase 1 complete. Total tokens: {total_tokens}")
        print("  Use --burst to trigger rate limits (Phase 2)")

    print("\n  Now check Foundry Portal:")
    print("  - Operate > Overview > 'Prevented behaviors'")
    print("  - Operate > Compliance > policy enforcement status")
    print("  - Operate > Assets > jedi-council-agent > Traces (look for 429s)\n")


if __name__ == "__main__":
    main()
