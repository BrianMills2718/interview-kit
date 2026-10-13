# Method: how to plan and design in a timed test

The kit's rules (`AGENTS.md`) say *what* to do: plan, small steps, tests, review. These notes
say *how to think* at each stage. They are adapted from a fuller planning method; everything
that needs a team (claims, worktrees, coordination) is left out.

| Stage of the test | Read | You produce |
|---|---|---|
| First 20 minutes: understand the task | [design-chain.md](design-chain.md) | `docs/PRD.md` from `templates/`: goal, quoted requirements, use cases with failures, assumptions, risks |
| Before code: the shape of the solution | [system-model.md](system-model.md) | `docs/MODEL.md` from `templates/`: domain model, state machine, the riskiest use case as a sequence, tests from the model |
| When another picture would help | [architecture-views.md](architecture-views.md), [representation.md](representation.md) | a diagram only if it answers a question, under a heading that asks it |
| Any choice (library, structure, scope) | [decisions.md](decisions.md) | an ADR row in `docs/DECISIONS.md`: context, decision, consequences, what would show it wrong |
| Each step | [design-chain.md](design-chain.md#slices-judge-first) | the test (the judge) first, then the code |
| Optional: machine-checked plan | [aes.md](aes.md) | `aes` records outcome to criterion to test, and says what is unproven |

**Read first:** `AGENTS.md`, `PLAN.template.md`, the skill for the task (usually
`skills/langgraph-agent`), then this page. Open the other method notes only when their row above
applies.

**Skip in a timed test:** the design chain's steps when the prompt already fixes the inputs,
outputs and rules (quote it in `docs/PRD.md` instead); the model's drift test (it pays off over
days, not hours; `check.sh --final` already checks every named function exists); `aes` under
3 hours. Never skip the package itself: `check.sh` requires it.

Time budget for a 4-hour test: about 25 minutes on design-chain plus model before any code,
5 minutes per decision row, and the last 20 minutes on the README. In a 2-hour test, halve the
first number. If design takes longer, the task is bigger than one test: cut scope and say so.
