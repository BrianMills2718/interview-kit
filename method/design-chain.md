# Design chain: from the task to the first test

Work down this chain once, briefly, before code. Each line depends on the one above; skipping a
line usually means a later surprise.

The first five lines are `docs/PRD.md` (from `templates/PRD.md`); the rest feed `docs/MODEL.md`.

1. **Goal**: who does what, and what they see when it works. One sentence, plus one
   concrete example (input, then the exact expected result).
2. **Requirements**: quote the task text, as rows R1, R2...
3. **Use cases**: the normal path first, then every failure and alternative (wrong tool chosen,
   loop never stops, bad input accepted, model output invalid, a human says no). Rows UC1...
   with Kind normal, failure or alternative.
   **Assumptions** (A1...) record each reading of something ambiguous; **risks** (K1...) are
   ranked riskiest first, and the riskiest use case is drawn and built first.
4. **Controls**: the least code that prevents, detects or recovers from each failure mode
   (validation, a step limit, a retry with the error, a human approval step). Every control
   traces to a failure mode; a control with no failure mode is gold-plating.
5. **Boundaries**: where data crosses between parts (user to agent, agent to tool, tool to data,
   agent to model). Each crossing gets a typed contract.
6. **Domain rules**: the business rules, in the order they are checked.
7. **Contracts and schema**: function signatures, tool signatures, Pydantic models, state.
8. **Fixtures**: for each boundary that matters, one good input and one smallest bad input.
9. **Thin slices**: the order to build in (below).

Depth: a take-home is "small". Write lines 1, 2, 3 and 9 in full; 4 to 8 as short lists or in the model. Do not
invent security, compliance or scaling requirements the task did not ask for; name them as
"would add with more time" in the README instead.

## Pick the path

| Situation | Path | What it needs | What it skips |
|---|---|---|---|
| You do not know if an approach works (an API, a model's behavior) | probe | one question, the cheapest real test, a stop rule | tests beyond the probe, polish |
| You know the shape; build it | prototype | outcome example, first vertical slice, focused tests | hardening |
| Something broke | repair | reproduce it first, a failing test, then the fix | redesign |

Switch path when the evidence changes: a probe that answered its question becomes a prototype;
two steps with no visible progress, or three failures at the same boundary, mean stop and rethink
the approach rather than retry.

## Slices: judge first

A slice is one end-to-end path through the system (input to visible result), not one layer.
Build the thinnest one that reaches the real outcome first, then widen.

Each slice has four things, written before its code:

- **Outcome**: what changes for the user.
- **Success check**: the property that shows it works, plus how it could fail (the disproof).
- **Watchlist**: the failure use cases from step 3 this slice could trigger.
- **Judge**: representative inputs and the check that grades them, usually a test with a fake
  model. Write the judge first and see it fail.

A test that the trivial answer would pass proves nothing: include an input where a wrong
implementation gives a different result. A count that lands on the expected number is not proof
the right things were counted; assert which items, not how many.

## When a run fails or surprises you

Read the whole trace (inputs, each tool call and its result, the model's output) before
changing code. Say which it is: the needed data never reached the model, it arrived and was
ignored, or the expected answer was wrong. Fix that, then re-run and keep the failing case as a
test.
