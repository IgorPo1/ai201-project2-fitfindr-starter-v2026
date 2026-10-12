"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""
import re
import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }
# ── query parsing ─────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    """
    Parse a plain-language query into description, size, and max_price.

    Uses regex to extract size tokens (S, M, L, XL, XS, etc.) and price
    ceilings ($N or "under N"). Everything remaining is the description.

    Returns a dict with keys: description (str), size (str|None),
    max_price (float|None).
    """
    text = query.strip()
    size = None
    max_price = None

    # --- extract size FIRST so numeric sizes (e.g. "size 8") are not
    #     consumed by the price regex: "size N", or standalone S/M/L/XL/XS/XXS/XXL ---
    size_match = re.search(
        r"\bsize\s+([A-Za-z0-9]{1,3})\b|(?<![A-Za-z0-9])(XXS|XS|XL|XXL|[SML])(?![A-Za-z0-9])",
        text, re.I
    )
    if size_match:
        size = (size_match.group(1) or size_match.group(2)).upper()
        text = text[:size_match.start()] + text[size_match.end():]

    # --- extract max_price: requires "under N", "$N", or "under $N" ---
    # A bare number like "90s" should NOT match here.
    price_match = re.search(r"(?:under\s+\$?|(?<!\w)\$)(\d+(?:\.\d+)?)", text, re.I)
    if price_match:
        max_price = float(price_match.group(1))
        text = text[:price_match.start()] + text[price_match.end():]

    # --- clean up leftover punctuation / filler words ---
    description = re.sub(r"[,\-]+", " ", text).strip()
    description = re.sub(r"\s+", " ", description)
    # Remove common stopwords that add no search value
    description = re.sub(r"\b(a|an|the|for|and|in|on|at|of|under|over|with|size)\b",
                         " ", description, flags=re.I).strip()
    description = re.sub(r"\s+", " ", description)

    return {
        "description": description,
        "size": size,
        "max_price": max_price,
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """

    from mcp_client import call_tool

    session = new_session(query, wardrobe)
    iteration = 0

    try:
        # ── step 1: parse the query ───────────────────────────────────────────
        iteration += 1
        trace.check_iterations(iteration)
        parsed = _parse_query(query)
        session["parsed"] = parsed
        trace.step(
            "parse_query",
            inputs={"query": query},
            returned=parsed,
        )

        # ── step 2: search listings via MCP ──────────────────────────────────
        iteration += 1
        trace.check_iterations(iteration)
        results = call_tool("search_listings", {
            "description": parsed["description"],
            "size": parsed["size"],
            "max_price": parsed["max_price"],
        })
        session["search_results"] = results
        trace.step(
            "search_listings (via MCP)",
            inputs={
                "description": parsed["description"],
                "size": parsed["size"],
                "max_price": parsed["max_price"],
            },
            returned=results,
        )

        # ── BRANCH: if nothing came back, stop here ───────────────────────────
        if not results:
            desc = parsed["description"] or query
            hints = []
            if parsed["max_price"] is not None:
                hints.append(f"raise the price ceiling above ${parsed['max_price']:.0f}")
            if parsed["size"] is not None:
                hints.append(f"try a different size (searched for '{parsed['size']}')")
            if not hints:
                hints.append("try different keywords")
            session["error"] = (
                f"No listings matched '{desc}'. To find something, you could: "
                + "; or ".join(hints) + "."
            )
            trace.step(
                "branch: empty results",
                note=f"stopping early — {session['error']}",
            )
            return session

        # ── step 3: pick the top result ───────────────────────────────────────
        iteration += 1
        trace.check_iterations(iteration)
        session["selected_item"] = results[0]
        trace.step(
            "select_item",
            inputs={"from": f"{len(results)} results"},
            returned=session["selected_item"],
        )

        # ── step 4: suggest an outfit ─────────────────────────────────────────
        iteration += 1
        trace.check_iterations(iteration)
        outfit = suggest_outfit(
            new_item=session["selected_item"],
            wardrobe=session["wardrobe"],
        )
        session["outfit_suggestion"] = outfit
        trace.step(
            "suggest_outfit",
            inputs={
                "item": session["selected_item"].get("title"),
                "wardrobe_items": len(wardrobe.get("items", [])),
            },
            returned=outfit,
        )

        # ── step 5: create the fit card ───────────────────────────────────────
        iteration += 1
        trace.check_iterations(iteration)
        fit_card = create_fit_card(
            outfit=session["outfit_suggestion"],
            new_item=session["selected_item"],
        )
        session["fit_card"] = fit_card
        trace.step(
            "create_fit_card",
            inputs={"item": session["selected_item"].get("title")},
            returned=fit_card,
        )

    except ModelUnavailable as exc:
        session["error"] = (
            f"The model couldn't be reached: {exc}. "
            "Check your GEMINI_API_KEY in .env and try again."
        )
        trace.step("error", note=str(session["error"]))

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
