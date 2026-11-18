"""
Measure the token cost and timing of one agent run.
Run with caching off to get real numbers.
Usage: python measure_cost.py
"""
import os
import time

os.environ["AI201_CACHE"] = "0"

import config  # noqa: E402 — must come after env override
import generate  # noqa: E402

from agent import run_agent  # noqa: E402
from utils.data_loader import get_example_wardrobe  # noqa: E402

wardrobe = get_example_wardrobe()

durations = []
token_totals = []

RUNS = 5
print(f"Running {RUNS} full agent passes (cache off, temperature {config.TEMPERATURE})...\n")

for i in range(RUNS):
    # Reset generate counters between runs by re-importing — but they're
    # module-level globals, so just track the delta instead.
    before_calls = generate.call_count()
    before_tokens = generate.token_counts()["total"]

    t0 = time.monotonic()
    session = run_agent("vintage graphic tee under $30", wardrobe)
    elapsed = time.monotonic() - t0

    after_calls = generate.call_count()
    after_tokens = generate.token_counts()["total"]

    delta_tokens = after_tokens - before_tokens
    durations.append(elapsed)
    token_totals.append(delta_tokens)

    status = "ok" if session.get("fit_card") else f"error: {session.get('error', '?')[:60]}"
    print(f"  Run {i+1}: {elapsed:.2f}s  {delta_tokens} tokens  {status}")
    if i < RUNS - 1:
        # Brief pause between runs to avoid rate limits
        time.sleep(5)

print()
avg_duration = sum(durations) / len(durations)
avg_tokens = sum(token_totals) / len(token_totals)
print(f"Average duration : {avg_duration:.2f}s")
print(f"Average tokens   : {avg_tokens:.0f} total")
print()

# Gemini 1.5 Flash-Lite pricing (free tier has $0 cost up to quota,
# paid tier is $0.075 per 1M input tokens, $0.30 per 1M output tokens).
# Use the total as a worst-case estimate.
cost_per_million = 0.075  # input (conservative single-rate estimate)
cost_per_run = (avg_tokens / 1_000_000) * cost_per_million
cost_100_per_day = cost_per_run * 100

print(f"At paid-tier input rate (${cost_per_million}/1M tokens):")
print(f"  Cost per run       : ${cost_per_run:.6f}")
print(f"  100 users/day      : ${cost_100_per_day:.4f}/day")
print()
print(f"Full usage: {generate.usage()}")