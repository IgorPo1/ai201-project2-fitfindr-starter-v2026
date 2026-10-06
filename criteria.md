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
