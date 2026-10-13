# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listings database for items matching a description with optional size and price filters; scores results by keyword overlap and returns the best matches
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" --> description (str) — keywords describing the item; size (str | None) — size token to filter by (e.g. "M"), or None to skip size filtering; max_price (float | None) — inclusive price ceiling in dollars, or None to skip price filtering
- **Returns:**A list of listing dicts, each containing id (str), title (str), description (str), category (str), style_tags (list[str]), size (str), condition (str), price (float), colors (list[str]), brand (str | None), platform (str); sorted by keyword-overlap score, best match first, at most config.SEARCH_RESULT_LIMIT items
- **When it has nothing:**Returns an empty list [] — never None, never raises. The loop branches on this

### `suggest_outfit`

- **What it does:**Given the item the user is considering and their saved wardrobe, asks the model to suggest one or two specific outfits
- **Inputs:**new_item (dict) — a listing dict from search_listings; wardrobe (dict) — a wardrobe dict with an "items" key holding a list of wardrobe item dicts (may be empty)
- **Returns:**A non-empty string of outfit suggestions, two to four sentences, naming specific pieces from the wardrobe when available
- **When it has nothing:**When wardrobe["items"] is empty, returns general styling advice for the item type rather than raising or returning an empty string.

### `create_fit_card`

- **What it does:**Writes a short social-media caption for the thrift find, mentioning the item, price, and platform, styled to read like a real post
- **Inputs:**outfit (str) — the outfit suggestion from suggest_outfit; new_item (dict) — the listing dict for the item being captioned
- **Returns:**A two-to-four sentence caption string that mentions the item's title, its price as a number, and the platform name exactly once
- **When it has nothing:**if outfit is empty or whitespace, returns the string "No outfit suggestion available — cannot generate a fit card."

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:**

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->

**What moves through the session:** <!-- which fields, in what order -->

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] select_item
      in:  dict with keys: from
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Pair the Y2K baby tee with the **baggy dark wash straight-leg jeans** and **chunky white sneakers** foran eff…
[5] create_fit_card
      in:  dict with keys: item
      out: Obsessed with the dreamy butterfly print on this little Y2K baby tee. It’s the ultimate early-2000s staple, pe…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair the Y2K baby tee with the **baggy dark wash straight-leg jeans** and **chunky white sneakers** for an effortless, authentic early-2000s silhouette. Throw the **black cropped zip hoodie** over top for an easy layering piece that balances the fitted, cropped cut of the tee with a relaxed street-style edge.

  Fit card: Obsessed with the dreamy butterfly print on this little Y2K baby tee. It’s the ultimate early-2000s staple, perfect for pairing with baggy denim and chunky sneakers. Grab it on my depop right now for just $18 before it's gone!

0 model calls this session, 2 served from cache

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee withbutterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors':['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id':'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khakicolor, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags':['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```

$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"


**Outfit:** Vintage Levi's 501 Jeans + White ribbed tank top + Black combat boots + Black cropped zip hoodie

**Why it works:** This combination balances the classic, structured fit of the mid-wash denim with edgy, modern streetwear staples. The white tank provides a clean, minimalist base that lets the vintage fade of the jeans stand out, while the cropped hoodie and combat boots anchor the look with attitude and proportion.


```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Nothing beats the fit of broken-in vintage denim. These classic medium wash Levi's 501s bring that effortless streetwear energy and are ready to be your neweveryday go-to. Style them with crisp white sneakers for an instant off-duty look, available now on my Depop for just $38.

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Help me fix the issue with MCP server
- *What came back:* AI identify that function need to be registered
- *What I changed:* I tested and it worked as expected

**Moment 2**

- *What I asked for:* critique this criteria
- *What came back:* critique
- *What I changed:* Adjusted criteria to be life ready

**Moment 3**

- *What I asked for:* Why does `python app.py ask 'bmw i8 0-60'` return an answer when nothing should match?
- *What came back:* Claude traced it to `search_listings`: keyword scoring used substring matching, so the `0` and `60` tokens matched prices and "90s"-style text, and any score above zero passed.
- *What I changed:* I checked the claim by running the keywords one at a time against the listings before changing anything. Then I made the scoring drop keywords with no letters and match whole words. The `bmw` query now returns 0 results.

**Moment 4**

- *What I asked for:* Add handlers for the failures that crashed or went silent, and a trace.
- *What came back:* Claude reproduced three failures (MCP server unreachable, empty outfit from the model, session budget exceeded) and wrote a handler for each. The trace steps were already in `agent.py`, so it only added one for the empty-outfit stop.
- *What I changed:* I re-ran each failure and read the messages. Claude's first draft of the MCP line claimed a full-agent comparison that hadn't been run, so I had it removed.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item matches the item passed to suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions the item's price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe gives a non-empty outfit and fit card | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function that produced it: `results/run_2026-10-12_1940_before.md`, scenario "matching query completes", try 1 (`run_eval.py::run_once` → `agent.py::run_agent`):

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Outfit suggestion:

```
Pair the Y2K baby tee with the baggy dark wash jeans and chunky white sneakers for an effortless, authentic early-2000s silhouette. Throw the black cropped zip hoodie on top for a balanced contrast of fitted and oversized shapes while keeping the color palette cohesive.
```

Fit card:

```
Serving major early-2000s energy with this dreamy butterfly print baby tee. Style it with baggy low-rise denim and chunky sneakers for the ultimate off-duty pop star vibe. Snag this little gem for just $18 over on my Depop before it's gone!
```

Trace:

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] select_item
      in:  dict with keys: from
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Pair the Y2K baby tee with the baggy dark wash jeans and chunky white sneakers for an effortless, authentic ea…
[5] create_fit_card
      in:  dict with keys: item
      out: Serving major early-2000s energy with this dreamy butterfly print baby tee. Style it with baggy low-rise denim…
```
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | MET (5/5) | Counted tries where the run had no error, selected an item, and returned a non-empty fit card. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET (5/5) | Counted tries that stopped at the empty-results branch with `suggest_outfit` never called. The query matches nothing because of the price and size filters, not keyword scoring. |
| 3 | Selected item matches the item passed to suggest_outfit | 5 of 5 | MET (5/5) | Counted tries where the outfit contains a word from the selected item's title. This is a weak check; it doesn't prove the same item object reached the tool. |
| 4 | Fit card mentions the item's price and platform | 5 of 5 | MET (5/5) | Counted tries where the card contains the exact price (for example `$18`) and the platform name. The five cards differed. |
| 5 | Empty wardrobe gives a non-empty outfit and fit card | 5 of 5 | MET (5/5) | Counted tries where the outfit is at least 20 characters and the fit card is non-empty. |

**Diagnoses**

No criterion missed in the Before run, so there is no miss to diagnose.

One gap the run did not catch: criterion 2 passed on its chosen query, but `bmw i8 0-60` is also a query nothing should match, and it returns 10 unrelated listings. The place is a tool, `search_listings` in `tools.py`. The mechanism is substring scoring: `kw in blob` matches the `0` and `60` tokens inside prices and "90s"-style text, so any stray hit passes the score filter. The criterion didn't test this because its scenario relied on the price and size filters to empty the list first. The fix is either to match whole words or to make criterion 2's scenario a query with no numeric keywords. Fixing it is the planned improvement.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] select_item
      in:  dict with keys: from
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Pair the Y2K baby tee with the **baggy dark wash straight-leg jeans** and **chunky white sneakers** for an eff…
[5] create_fit_card
      in:  dict with keys: item
      out: Obsessed with the dreamy butterfly print on this little Y2K baby tee. It’s the ultimate early-2000s staple, pe…
```

**Empty search**

```
$ python app.py ask 'zzqx widget under $30' --trace
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch: empty results
      →    stopping early — No listings matched 'zzqx widget'. To find something, you could: raise the price ceiling above $30.
```

The empty path stops after three steps, as the branch should. `bmw i8 0-60` doesn't take this path: it returns 10 unrelated listings, which is the documented failure below.

**On the MCP move:** `run_agent()` now gets `search_listings` results through `mcp_client.call_tool` instead of a direct call. Nothing I tested behaved differently: for the same inputs the MCP result is identical to the direct call (`identical: True`, 7 results for `graphic tee`, `max_price=30`). The one behaviour change is failure handling: if the server can't start, the agent now stops with a message instead of crashing. Separately, I added handlers for three failures:
- **MCP server unreachable:** it used to crash `run_agent()`. It now sets a message saying to run `python mcp_server.py` on its own and fix the error.
- **Model returns an empty outfit:** it used to succeed silently with a "No outfit suggestion" caption. It now stops with an error asking the user to retry or run with `AI201_CACHE=0`.
- **Session budget exceeded (`QuotaGuard`):** it used to crash. It now stops with a message pointing to `SESSION_REQUEST_BUDGET` in `config.py`.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** In `search_listings` in [tools.py](tools.py), keyword scoring now does two things. It drops keywords that contain no letters, so the `0` and `60` in `0-60` no longer count. It also matches whole words in the listing text instead of substrings, so a keyword can't hit inside a price, a "90s", or a longer word. Nothing else changed: the tool signature, the return shape, and the empty-list behaviour are the same.

**Which failure it was meant to fix:** The diagnosis in Verdicts and Diagnoses. `bmw i8 0-60` returned 10 unrelated listings instead of stopping at the empty-results branch. The cause was substring matching in `search_listings`, not the loop or the model. Before the fix this query returned 10 listings; after it, 0, and the run stops with the "nothing found" message (`python app.py ask 'bmw i8 0-60' --trace`, 0 model calls).

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected item matches the item passed to suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions the item's price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe gives a non-empty outfit and fit card | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Before and after, side by side:**

| Criterion | Target | Before | After | Changed? |
|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | 5 of 5 MET | 5 of 5 MET | no |
| 2. An impossible query stops before the second tool | 5 of 5 | 5 of 5 MET | 5 of 5 MET | no |
| 3. Selected item matches the item passed to suggest_outfit | 5 of 5 | 5 of 5 MET | 5 of 5 MET | no |
| 4. Fit card mentions the item's price and platform | 5 of 5 | 5 of 5 MET | 5 of 5 MET | no |
| 5. Empty wardrobe gives a non-empty outfit and fit card | 5 of 5 | 5 of 5 MET | 5 of 5 MET | no |
| _Diagnostic: `bmw i8 0-60` (not one of the five)_ | _none_ | 10 unrelated listings, ran through `suggest_outfit` | 0 listings, stops at the empty-results branch | **yes, fixed** |

**Did it help, and how do I know:** It fixed the query I diagnosed, and it didn't break the five scenarios. The After run (`results/run_2026-10-12_2321_after.md`, caching off, five tries each) passes every try, the same as Before. That run can't show a gain, though. All five criteria already passed on their chosen scenarios, and the one scenario that exposed the bug is not in the suite. The evidence of the fix is the single `bmw` query above. Whole-word matching could also miss plurals such as "tees" for "tee", and none of the 25 After tries hit that case. I didn't test it.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
