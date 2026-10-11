# Method: how to plan and design in a timed test

The kit's rules (`AGENTS.md`) say *what* to do: plan, small steps, tests, review. These notes
say *how to think* at each stage. They are adapted from a fuller planning method; everything
that needs a team (claims, worktrees, coordination) is left out.

| Stage of the test | Read | You produce |
|---|---|---|
| First 10 minutes: understand the task | [design-chain.md](design-chain.md) | outcome, requirements, failure modes, in `PLAN.md` |
| Before code: the shape of the solution | [system-model.md](system-model.md) | a one-page model in `PLAN.md` or `docs/MODEL.md` |
| When a picture would help | [architecture-views.md](architecture-views.md), [representation.md](representation.md) | one or two Mermaid diagrams, each answering one question |
| Any choice (library, structure, scope) | [decisions.md](decisions.md) | a decision row in the README: choice, why, what would show it wrong |
| Each step | [design-chain.md](design-chain.md#slices-judge-first) | the test (the judge) first, then the code |
| Optional: machine-checked plan | [aes.md](aes.md) | `aes` records outcome to criterion to test, and says what is unproven |

Time budget for a 4-hour test: about 25 minutes on design-chain plus model before any code,
5 minutes per decision row, and the last 20 minutes on the README. In a 2-hour test, halve the
first number. If design takes longer, the task is bigger than one test: cut scope and say so.
