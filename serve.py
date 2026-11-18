#!/usr/bin/env python3
"""
FitFindr over HTTP. ← UNIT 9

    python serve.py                       run it on your machine
    gunicorn serve:app                    run it the way a host runs it

Everything else in this repo exits after one command. A host has nothing to
keep running, so a command line cannot be deployed. This file is the smallest
thing that can: it starts a web server, waits, and hands each request to the
same `run_agent()` your CLI calls. **No new agent logic lives here.** If your
loop works from `python app.py ask`, it works from here; if it doesn't, fix it
there, not in this file.

Two routes:

    POST /ask       {"query": "vintage graphic tee under $30",
                     "wardrobe": {...}}     ← wardrobe is optional
    GET  /health    is it awake?

`/ask` returns the session dict from `run_agent()` as JSON, unchanged — the
same keys you print from the command line, including `error`. Read
`session["error"]` first, exactly as you do everywhere else.

It runs **one request at a time**, and one route is deliberately slower than a
web server has to be. The reason is worth reading before you deploy: see the
note above `_one_at_a_time` below — it also decides which gunicorn worker you
can use.

Unit 9 extensions (Shape B — Harden against failure):
  - Structured JSON logging: every request writes a record to fitfindr_run.log.
  - Request timeout: agent calls that exceed REQUEST_TIMEOUT_S return a 503
    rather than leaving the caller waiting indefinitely.
  - Input validation: empty, non-string, or oversized queries get a 400 with a
    specific message rather than propagating garbage to run_agent.
"""

import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

# config first, and before anything that talks to the model: it loads your .env
# and fixes the Windows console encoding for every module that imports it.
import config  # noqa: F401

from flask import Flask, jsonify, request

from agent import run_agent
from utils.data_loader import get_example_wardrobe

app = Flask(__name__)

# ── constants ─────────────────────────────────────────────────────────────────

# Wall-clock limit for one agent run via HTTP.  Covers the case where the model
# is unreachable or hanging — without this, POST /ask would hang indefinitely
# and the caller would have no way to tell the difference between "slow" and
# "broken".  30 seconds is generous: a normal run is 4-8 s; a 503-and-retry
# run adds at most ~65 s of backoff per retry.  If the agent hasn't answered in
# 30 s the most likely explanation is a network problem, not a slow model.
REQUEST_TIMEOUT_S = 30

# Hard cap on the query length passed to run_agent.  Keeps the prompt size
# predictable and prevents someone from crafting a query that inflates token
# counts on purpose.
MAX_QUERY_LENGTH = 500

# Log file path — in the project root alongside serve.py.
LOG_FILE = Path(__file__).parent / "fitfindr_run.log"

_log_lock = threading.Lock()


# ── structured logging ────────────────────────────────────────────────────────

def _log_request(
    query: str,
    duration_s: float,
    outcome: str,
    error_message: str | None = None,
) -> None:
    """
    Append one JSON log record to fitfindr_run.log.

    Fields:
        timestamp    ISO-8601 UTC string — when the request arrived.
        query        The raw query string received (may be empty on bad input).
        duration_s   Seconds from request receipt to response, 2 d.p.
        outcome      "ok" | "error" | "timeout" | "invalid_input"
        error_message  The error string when outcome != "ok", else null.

    Every request is logged, including failures and bad input — that is the
    point: a failure that leaves no record is one you will never diagnose.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "duration_s": round(duration_s, 3),
        "outcome": outcome,
        "error_message": error_message,
    }
    line = json.dumps(record, ensure_ascii=False)
    with _log_lock:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError as exc:
            # Logging must never kill a successful request.
            print(f"  [log] could not write to {LOG_FILE}: {exc}", file=sys.stderr)


# ── one request at a time ─────────────────────────────────────────────────────
# Here's why this exists.
#
# A web server will happily run two requests at once. Two things in this repo
# assume otherwise:
#
#   • If you moved a tool onto MCP in unit 4, `mcp_client.call_tool` starts
#     `mcp_server.py` as a separate process over stdio, one per call. Two
#     overlapping requests means two extra Python interpreters, and the free
#     tier you're deploying to has 512 MB for all of it. That is the reason
#     that would still be here even if everything else were perfect.
#   • `generate.py`'s pacing window and its call counter are plain module
#     globals — deliberately, because that file is teaching pacing and quota,
#     not locking. Two threads sharing them means the per-minute limiter is
#     counting something that isn't true.
#
# What the lock covers is exactly the agent run: the part that spawns
# processes and calls the model. Reading the request, rejecting a bad one, and
# turning the answer into JSON all happen outside it — so a request with a
# malformed body comes straight back with a 400 instead of queueing behind
# somebody else's agent.
#
# Serialising the runs costs you nothing here — this is one user asking one
# question — and it keeps the deployed behaviour identical to the CLI's. When
# that stops being an acceptable trade, the fix is a real queue, not a bigger
# lock.

_one_at_a_time = threading.Lock()


@app.get("/health")
def health():
    """Is the server awake? A host pings something like this to find out."""
    return jsonify({"status": "ok"})


@app.post("/ask")
def ask():
    """
    Run the agent on one query.

    In:   {"query": "...", "wardrobe": {...}}   wardrobe optional — leave it
                                                out and you get the same
                                                example wardrobe the CLI uses.
    Out:  the session dict from run_agent(), as JSON.

    Unit 9 Shape B additions:
      - Validates query before touching run_agent (empty / non-string / too long → 400).
      - Times the agent call and enforces REQUEST_TIMEOUT_S.
      - Logs every request to fitfindr_run.log via _log_request.
    """
    t_start = time.monotonic()
    payload = request.get_json(silent=True) or {}

    # ── input validation (Shape B: bad input path) ────────────────────────────
    raw_query = payload.get("query", "")
    if not isinstance(raw_query, str):
        duration = time.monotonic() - t_start
        _log_request(str(raw_query)[:100], duration, "invalid_input", "query must be a string")
        return jsonify({"error": "query must be a string"}), 400

    query = raw_query.strip()
    if not query:
        duration = time.monotonic() - t_start
        _log_request("", duration, "invalid_input", "query is empty")
        return (
            jsonify({"error": "Send JSON with a 'query' field, e.g. "
                               '{"query": "vintage graphic tee under $30"}'}),
            400,
        )

    if len(query) > MAX_QUERY_LENGTH:
        duration = time.monotonic() - t_start
        msg = f"query exceeds {MAX_QUERY_LENGTH} characters (got {len(query)})"
        _log_request(query[:100], duration, "invalid_input", msg)
        return jsonify({"error": msg}), 400

    wardrobe = payload.get("wardrobe")
    if not isinstance(wardrobe, dict):
        wardrobe = get_example_wardrobe()

    # A queued request should look like a queued request.
    if _one_at_a_time.locked():
        print(
            "  [serve] another request is still running. This one is waiting "
            "its turn — serve.py handles one at a time, on purpose.",
            file=sys.stderr,
            flush=True,
        )

    # ── agent run with timeout (Shape B: timeout path) ────────────────────────
    failure = None
    timed_out = False
    session = None

    result_holder: list = []
    error_holder: list = []

    def _run():
        try:
            result_holder.append(run_agent(query, wardrobe))
        except Exception as exc:  # noqa: BLE001
            error_holder.append(exc)

    with _one_at_a_time:
        worker = threading.Thread(target=_run, daemon=True)
        worker.start()
        worker.join(timeout=REQUEST_TIMEOUT_S)

        if worker.is_alive():
            # The agent did not finish within the timeout window.
            timed_out = True
        elif error_holder:
            failure = f"{type(error_holder[0]).__name__}: {error_holder[0]}"
        else:
            session = result_holder[0] if result_holder else None

    duration = time.monotonic() - t_start

    if timed_out:
        _log_request(query, duration, "timeout",
                     f"agent did not respond within {REQUEST_TIMEOUT_S}s")
        return jsonify({"error": f"Request timed out after {REQUEST_TIMEOUT_S}s"}), 503

    if failure is not None:
        _log_request(query, duration, "error", failure)
        return jsonify({"error": failure}), 500

    # Even a completed session may carry a session-level error (empty search,
    # model unavailable caught inside run_agent) — that is still outcome "ok"
    # from the HTTP layer's perspective: the agent completed and returned a
    # structured response.
    err_msg = session.get("error") if session else None
    _log_request(query, duration, "ok", err_msg)
    return jsonify(session)


if __name__ == "__main__":
    # PORT  and 0.0.0.0 are not decoration. A host tells you which port to
    # listen on through PORT, and it reaches your process from outside the
    # container — bind 127.0.0.1 and nothing but the container itself can
    # connect, which looks exactly like a broken app from the browser.
    port = int(os.getenv("PORT", "5001"))

    # Never on by default. Flask's debugger executes code typed into a browser,
    # and a deployed app with it on is a stranger's shell. Set AI201_DEBUG=1 in
    # your own terminal when you want the reloader.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"\nFitFindr is listening on http://localhost:{port}")
    print(f"Logs: {LOG_FILE}")
    print("It runs one request at a time — a second one waits for the first.")
    print("Ask it something (single quotes, as always):\n")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"query\": \"vintage graphic tee under $30\"}}'\n"
    )
    print("Ctrl-C to stop.\n")

    app.run(host="0.0.0.0", port=port, debug=debug)