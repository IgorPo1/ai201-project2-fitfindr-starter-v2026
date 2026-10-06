"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # TODO: replace this with your implementation
    listings = load_listings()

    # --- price filter ---
    if max_price is not None:
        listings = [l for l in listings if l["price"] <= max_price]

    # --- size filter (whole-token match only) ---
    if size is not None:
        size_lower = size.lower().strip()

        def _size_matches(listing_size: str) -> bool:
            # Split the listing size into tokens, e.g. "S/M" → ["s", "m"]
            tokens = re.split(r"[/\s,]+", listing_size.lower())
            return size_lower in tokens

        listings = [l for l in listings if _size_matches(str(l.get("size", "")))]

    # --- keyword scoring ---
    if not description or not description.strip():
        return listings[: config.SEARCH_RESULT_LIMIT]

    keywords = re.sub(r"[^\w\s]", " ", description.lower()).split()

    def _score(listing: dict) -> int:
        # Build a searchable blob from every text field
        blob = " ".join([
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            " ".join(listing.get("style_tags", [])),
            listing.get("brand", "") or "",
        ]).lower()
        return sum(1 for kw in keywords if kw in blob)

    scored = [(l, _score(l)) for l in listings]
    scored = [(l, s) for l, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [l for l, _ in scored][: config.SEARCH_RESULT_LIMIT]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    # TODO: replace this with your implementation
    title = new_item.get("title", "this item")
    description = new_item.get("description", "")
    category = new_item.get("category", "")
    style_tags = ", ".join(new_item.get("style_tags", []))
    colors = ", ".join(new_item.get("colors", []))

    item_summary = (
        f"Item: {title}\n"
        f"Category: {category}\n"
        f"Style tags: {style_tags}\n"
        f"Colors: {colors}\n"
        f"Description: {description}"
    )

    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        prompt = (
            f"A thrift shopper is considering buying this item:\n\n"
            f"{item_summary}\n\n"
            f"They have no saved wardrobe. Suggest two general outfit ideas "
            f"that would work with this item, naming specific clothing types "
            f"and explaining the vibe. Keep it concise — two to four sentences."
        )
    else:
        wardrobe_text = "\n".join(
            f"- {w.get('name', 'unknown')} ({w.get('color', '')} {w.get('type', '')})"
            for w in wardrobe_items
        )
        prompt = (
            f"A thrift shopper is considering buying this item:\n\n"
            f"{item_summary}\n\n"
            f"Their current wardrobe includes:\n{wardrobe_text}\n\n"
            f"Suggest one or two specific outfits using pieces from their "
            f"wardrobe above. Name the exact pieces and explain why they work "
            f"together. Keep it concise — two to four sentences."
        )

    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    # TODO: replace this with your implementation
    if not outfit or not outfit.strip():
        return "No outfit suggestion available — cannot generate a fit card."

    title = new_item.get("title", "this thrift find")
    raw_price = new_item.get("price", 0)
    # Format price cleanly: drop the decimal if it is a whole number
    # so $18.0 becomes $18, but $18.50 stays $18.50.
    if isinstance(raw_price, (int, float)) and float(raw_price) == int(float(raw_price)):
        price_str = f"${int(float(raw_price))}"
    else:
        price_str = f"${float(raw_price):.2f}"
    platform = new_item.get("platform", "a thrift platform")
    style_tags = ", ".join(new_item.get("style_tags", []))

    prompt = (
        f"Write a short social-media caption (2–4 sentences) for a thrift find.\n\n"
        f"Item: {title}\n"
        f"Price: {price_str}\n"
        f"Platform: {platform}\n"
        f"Vibe/style: {style_tags}\n\n"
        f"Outfit idea: {outfit}\n\n"
        f"The caption should sound like a real post — casual, enthusiastic, "
        f"specific about the vibe. Mention the item, its exact price ({price_str}), "
        f"and the platform once each. Do not use generic phrases like "
        f"'thrift find of the century'. Do not alter the price — use {price_str} exactly."
    )

    return generate(prompt)
