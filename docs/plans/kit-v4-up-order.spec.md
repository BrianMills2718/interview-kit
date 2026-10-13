# Spec: planning package and memory sheet in the Unified Process order

Source of the method: the owner's own research chat (2026-10-13, an outside-model conversation on
software modelling; not committed because it is a private chat). Its established references:
the Unified Process / RUP (iterate, riskiest case first), Larman's *Applying UML and Patterns*
(use cases -> domain model -> interactions -> responsibilities), and model-based testing (the
state diagram is the test oracle: one test per arrow, including forbidden ones). Its rule:
draw only the models that answer a question.

## Order the candidate works in (and the chat prompts follow)

1. Rules. 2. Intent, candidate states their reading first. 3. Questions -> assumptions.
4. Use cases (normal, then failures and alternatives) and ranked risks; candidate names the
   riskiest; then `docs/PRD.md` is written.
5. Domain model (classDiagram + rules/invariants) and state machine (stateDiagram-v2, with the
   human pause and the forbidden transitions) in `docs/MODEL.md`; candidate questions it.
6. Off-the-shelf research. 7. Prove the imports (`check_imports.py`).
8. Shape: candidate proposes, AI argues against; then `docs/DECISIONS.md` as ADRs.
9. Sequence diagram of the riskiest use case, plus the "Tests from the model" table.
10. Plan (PLAN.md, unchanged headings). 11. Build one step (keep d40bf1c's wording: test what the
    diagrams forbid; never change a diagram or test just to pass). 12. Review. 13. README.
14. Finish (tick done-when with real results).

## Package (replaces DESIGN.md + six fixed diagrams)

### docs/PRD.md (new template `templates/PRD.md`; `templates/DESIGN.md` is removed)
- `## Goal`: one-line thesis (who, what, why this shape) and `Example: <input> -> <result>`.
- `## Requirements`: table rows `| R1 |` quoting the task.
- `## Use cases`: table `| ID | Kind | Actor | Trigger | Steps | Expected result |`, rows `| UC1 |`;
  Kind is one of `normal`, `failure`, `alternative`. Check: at least one `normal` row and at
  least one `failure` or `alternative` row (cell value match, structural).
- `## Assumptions`: rows `| A1 |`.
- `## Risks`: rows `| K1 |` ranked, riskiest first, each with how it is tested early.

### docs/MODEL.md (rewritten `templates/MODEL.md`)
Required sections (heading starts with the name; case-insensitive):
- `## Domain model`: a ```mermaid classDiagram (or erDiagram) block, a `**Answer:**` line, and a
  `Rules:` list (invariants).
- `## State machine`: a ```mermaid stateDiagram-v2 block and `**Answer:**`, plus a
  `Forbidden:` list; OR the line `No states: <reason>` (as today's diagram 5 exemption).
- `## Sequence`: (heading `## Sequence: UCn <name>`) a ```mermaid sequenceDiagram block and
  `**Answer:**`; the heading names a UC id that exists in docs/PRD.md.
- `## Tests from the model`: table `| Claim | From | Test |` with backticked `test_x` names.
  Check: every `A --> B` transition in the state machine block (including `[*]` arrows) appears
  verbatim (`A --> B`) in this table; every line of the `Forbidden:` list appears too; at least
  one row. With `--final`, every backticked test exists (existing defined_names logic) and every
  backticked `name()` in MODEL.md is defined (existing logic).
Optional sections, each needing a mermaid block and `**Answer:**` if present: `## Context`,
`## Agent loop`, `## Components`. Any other `##` section with a mermaid block also needs
`**Answer:**`. The Runtime, Contracts, Quality and Unknowns tables are dropped.

### docs/DECISIONS.md (rewritten template)
ADR log, Nygard columns: `| ID | Context | Decision | Consequences | Rejected alternative | What would show it wrong |`, rows `| ADR-1 |`. Check: at least one `| ADR-\d` row.

### Unchanged
PLAN.md headings and checks in check.sh (`## Goal`, `## Done when`, `## Steps`,
`## System model`, ticked items with real results); README sections; compile and test checks.
check.sh messages that mention DESIGN.md / "six diagrams" are updated.

## Files to change
check_docs.py; check.sh (messages only); templates/PRD.md (new), templates/DESIGN.md (delete),
templates/MODEL.md, templates/DECISIONS.md; MEMORY_SHEET.md (14 prompts above); AGENTS.md;
PLAN.template.md; method/README.md, method/system-model.md, method/design-chain.md,
method/representation.md, method/decisions.md, method/architecture-views.md (only where they
describe the package; keep them short); skills/plan/SKILL.md; skills/explain-your-work/SKILL.md;
agents/planner.md; practice2/PROBLEM.md; practice/reference/sample-run (bring its package to the
new format so it still passes); wiki/index.md; README.md (rows); KIT.md (regenerate with
build_kit.sh); tests/test_check_docs.py, tests/test_check_sh.py, tests/test_practice.py,
tests/test_memory_sheet.py (read the required names from check_docs.py constants);
tests/fixtures as needed. practice2/reference/dry-runs keep their old MODEL.md files as history;
their README says they use the earlier six-diagram format.

## Checks that must pass
- tests/test_check_docs.py: a complete package passes; each of these fails with its own message:
  missing PRD section, no failure use case, missing state machine without `No states:`, a state
  transition absent from the Tests table, a forbidden line absent from the Tests table, sequence
  heading naming an unknown UC, missing `**Answer:**`, no `| ADR-1 |` row, invented function or
  test name under --final.
- Full suite `uv run python -m pytest tests/ -v` exits 0.
- A fresh agent running MEMORY_SHEET.md verbatim on practice2 passes `check.sh --final` and the
  grader (run by the coordinating session after the builder finishes).
