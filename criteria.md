# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

---

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

For 5 of 5 successful runs (runs where search_listings returns at least one result), session["selected_item"] is a dict with a non-empty "title" field, and the outfit suggestion string returned by suggest_outfit contains at least one word from that item's title.

**Why this target:**
State failure is invisible in the final output — if the wrong item reaches suggest_outfit, the fit card is generated for the wrong thing and nothing crashes. The only way to catch it is to compare what the search found against what the outfit tool actually received. if the item changed mid-session the name would no longer appear. 5 of 5, so state passing is either working or broken.


---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->
For 5 of 5 successful runs, session["fit_card"] is a string that contains the item's price (as a number or "affordable") and the platform name (one of "depop", "thredUp", or "poshmark").




**Why this target:**
The fit card prompt explicitly asks the model to mention price and platform once each. These two facts are what make the caption actionable. 5 of 5 because the prompt is explicit.



---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->
When the agent is run with an empty wardrobe (wardrobe["items"] is []), session["outfit_suggestion"] is a non-empty (at least 20 characters) in 5 of 5 tries, and session["fit_card"] is also non-empty.




**Why this target:**
A new user with no saved wardrobe is a realistic case, not an edge case — someone just starting to thrift has nothing saved yet. If the agent crashes or returns an empty string in this case, it is useless for its primary audience. I chose "at least 20 characters" as the observable because an empty string or a single-word fallback would technically be non-empty but would not be useful advice. 5 of 5 because the empty-wardrobe branch in suggest_outfit is a deliberate fallback — if it fails, the code is wrong, not the data.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
## Capstone

# Acceptance criteria — Unit 9 Capstone (Shape B: Harden against failure)

Five criteria for the Unit 9 extension. Written before any results exist.
At least three are about the extension — the new failure-handling layer.

---

## 6. Empty and whitespace queries are rejected with a 400 before reaching run_agent

When `POST /ask` receives a JSON body whose `"query"` field is an empty string
or a string that is only whitespace, the HTTP response status code is 400, the
JSON body contains an `"error"` key, and the log record for that request shows
`"outcome": "invalid_input"` — in all 5 of 5 triggered attempts.

**Why this target:**
The validation is deterministic — either the stripped query is empty and the
branch fires, or it isn't. There is no model call and no variation between runs.
5 of 5 is the right number because an empty check that sometimes passes
something to `run_agent` is a broken guard, not an acceptable miss rate. The
reason the log outcome matters as a check is that a silent rejection (one that
returns 400 but doesn't log) would leave no trace; the whole point of the
failure-hardening is that every bad path is observable after the fact.

---

## 7. Non-string queries are rejected with a 400 and logged before run_agent

When `POST /ask` receives a `"query"` value that is not a string (e.g. an
integer like `12345`, a `null`, or a list), the HTTP response status code is
400, and the log record shows `"outcome": "invalid_input"` with
`"error_message": "query must be a string"` — in all 5 of 5 triggered attempts.

**Why this target:**
Like criterion 6, this branch is deterministic — `isinstance(raw_query, str)`
either returns True or False. The 5 of 5 target is right because anything less
would mean the type check is flaky, which is impossible for a simple isinstance
call. I test this separately from criterion 6 because the two rejection paths
(empty vs. wrong type) are different code branches in `serve.py::ask`; a bug
in one would not necessarily surface as a failure in the other.

---

## 8. Every completed HTTP request appears in the log within 1 second of the response

For 10 of 10 consecutive requests of any kind (happy path, early-stop, or
invalid input), a JSON record appears in `fitfindr_run.log` with a `timestamp`
field, a `query` field matching what was sent, a `duration_s` field, and an
`outcome` field. The record is present when the log file is read within 1 second
of the HTTP response being received.

**Why this target:**
Logging is the whole observability story for Path B — without it, there is no
run record. The check is straightforward: count the lines added to the log file
during a session of 10 requests and confirm they match. I picked 10 of 10
rather than 9 of 10 because a log that sometimes skips entries is worse than no
log at all; it creates the false impression that everything worked. The 1-second
window is generous — the log write is a file append that takes milliseconds —
but it bounds the check to something a person can actually observe rather than
"eventually".

---

## 9. A query that matches no listings completes under 3 seconds via HTTP

When a query that is known to return no listings (e.g. "designer ballgown size
XXS under $5") is sent to `POST /ask`, the HTTP response arrives within 3
seconds, and the log record shows `duration_s` less than 3.0 — in at least 4
of 5 trials.

**Why this target:**
An early-stop run makes no model calls — it only calls `run_agent` which calls
`search_listings` (the MCP tool). The only time cost is the subprocess overhead
of spawning `mcp_server.py`. From the initial session measurements, that
overhead was about 1.9 seconds. I set the target at 3 seconds to give 1+ second
of headroom; if it exceeds 3 seconds that is a sign of unexpected blocking, not
normal variation. I allow 4 of 5 because the MCP subprocess startup time can
vary with system load, and one slow cold start is not a defect.

---

## 10. The 503 retry covers transient overload: a simulated 503 is retried and does not raise ModelUnavailable immediately

When `generate.generate()` encounters an exception whose message contains "503"
or "service unavailable", the function does not immediately raise
`ModelUnavailable`; instead, it backs off and retries up to `config.MAX_RETRIES`
times. This is confirmed by patching the Gemini client to raise a fake 503 once
and observing that (a) the first attempt fails silently, (b) a second attempt
succeeds and returns the model's response, and (c) no `ModelUnavailable` is
raised — in 3 of 3 triggered test runs.

**Why this target:**
The Unit 4 diagnosis identified the exact mechanism: `generate.py::generate`'s
exception handler checked only for 429 patterns and immediately re-raised
anything else as `ModelUnavailable`. A single transient 503 would kill a run
that would have succeeded on a retry. This criterion directly tests the fix —
the change is in the `rate_limited` check, so the criterion exercises exactly
that branch. 3 of 3 is the right number because the patch is deterministic: the
fake exception is controlled code, and a retry that fires sometimes is a bug,
not a quirk.