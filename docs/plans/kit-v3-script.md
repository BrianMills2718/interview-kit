---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v3-script
plan_id: kit-v3-script
status: proposed
planning_path: requested
method_conformance_receipt: docs/plans/kit-v3-script.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "MEMORY_SHEET.md holds thirteen near-verbatim prompts, in order, from intent through off-the-shelf research, diagrams, plan, build, review and finish, and every heading the kit's gate requires is named in a prompt"
  canonical_example: "A fresh agent playing the IDE chat ran prompts 1-12 verbatim on practice2 and found that the plan and README prompts omitted headings check.sh --final requires; after the fix, tests/test_memory_sheet.py reads the required headings from check.sh and check_docs.py and finds each in the sheet"
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output"
  boundaries: "only these files: MEMORY_SHEET.md, README.md, wiki/index.md, tests/test_memory_sheet.py; no irreversible action and no spend; the owner's request as quoted is the scope"
  done_when: "tests/test_memory_sheet.py asserts four properties directly against the file text: (1) the PLAN.md headings parsed from check.sh's 'for sec in \"## Goal\"' line plus '## System model' each appear verbatim in MEMORY_SHEET.md; (2) the README sections parsed from check.sh's 'for sec in \"Run it\"' line each appear, and the exact string '\"## Run it\"' appears; (3) the DESIGN_SECTIONS list parsed from check_docs.py each appear; (4) the finish prompt contains 'Tick each Done when item'. tests/test_wiki_map.py asserts every relative link in wiki/index.md resolves to an existing file. The saved output shows each of these tests passing by name, and running test_memory_sheet.py against the pre-change sheet shows the named assertions failing with the missing headings listed The check's full output on the parent commit and on the change commit is committed as docs/plans/kit-v3-script.check.txt, and the commit is tagged [Goal kit-v3-script] with an Asked: line quoting the request."
  do_not_gate_on: "the owner's review of the plan page; work outside the listed files"
---

# Word-for-word chat script for the take-home

## When a run fails or surprises us

This procedure is separate from the anticipated failure named in the disproof
under Success and disproof: it applies to any run that fails or surprises us.
Preserve the failed check and its execution trace id. Before selecting a fix,
read the complete inputs, prompts, tool arguments/results, intermediate stages
and final output, including the full check command/output and the changed files.
Cite the observed divergence and classify evidence absent, returned but unused
or contradicted, invalid expectation, or unresolved. An unresolved diagnosis
cannot authorize a causal repair; it permits only further investigation. Bind the targeted repair to a new
traced verification run; retain the failed original. Review every failing or
surprising item and a sample of passes. A complete review is distinct from a
passing run. Criterion `outcome` covers the entire requested success check.

## Actor and result

**Actor:** the owner, who asked for this change.

**Request (verbatim):** the owner 2026-10-12 "i want word for word basically what i will type to the xtent we can. the idea is that i cgoin there and engage with diaogue and resarhc with the agent to plan out the intent stuff then find off the shelf solutiosn wherever psossible and diagram it out as far as possible etc"

**Desired result:** MEMORY_SHEET.md holds thirteen near-verbatim prompts, in order, from intent through off-the-shelf research, diagrams, plan, build, review and finish, and every heading the kit's gate requires is named in a prompt

**Stable example:** A fresh agent playing the IDE chat ran prompts 1-12 verbatim on practice2 and found that the plan and README prompts omitted headings check.sh --final requires; after the fix, tests/test_memory_sheet.py reads the required headings from check.sh and check_docs.py and finds each in the sheet

## Authority and non-goals

**Authority:** the owner asked for this change in his own repository; one agent makes it.

**Non-goals:** nothing outside the files listed under Vertical and reset. No irreversible action and no spend.

## Requirements

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | MEMORY_SHEET.md holds thirteen near-verbatim prompts, in order, from intent through off-the-shelf research, diagrams, plan, build, review and finish, and every heading the kit's gate requires is named in a prompt | asked: the owner 2026-10-12 "i want word for word basically what i will type to the xtent we can. the idea is that i cgoin there and engage with diaogue and resarhc with the agent to plan out the intent stuff then find off the shelf solutiosn wherever psossible and diagram it out as far as possible etc" | the success check under Success and disproof, its output saved as `docs/plans/kit-v3-script.check.txt` | planned, not yet run |

Requirements the change's own claims imply: none beyond R1; the change presents nothing as following a standard, schema or contract.

## Success and disproof

**Success evidence:** tests/test_memory_sheet.py asserts four properties directly against the file text: (1) the PLAN.md headings parsed from check.sh's 'for sec in "## Goal"' line plus '## System model' each appear verbatim in MEMORY_SHEET.md; (2) the README sections parsed from check.sh's 'for sec in "Run it"' line each appear, and the exact string '"## Run it"' appears; (3) the DESIGN_SECTIONS list parsed from check_docs.py each appear; (4) the finish prompt contains 'Tick each Done when item'. tests/test_wiki_map.py asserts every relative link in wiki/index.md resolves to an existing file. The saved output shows each of these tests passing by name, and running test_memory_sheet.py against the pre-change sheet shows the named assertions failing with the missing headings listed

**Trace review:** two runs of the success check above are judged from their full output: one on the parent commit before the change (the disproof run: it must show the defect or the check failing, which proves the check can fail) and one on the commit that makes the change (the success run); no model, agent or LLM pipeline runs under this plan. Where the trace lives: the check's complete output, with the exact command and its exit status, is saved as `docs/plans/kit-v3-script.check.txt` and committed with the change. What must be seen in it beyond the final result: the command ran against the files listed under Vertical and reset at that commit, each check or test it reports appears by name with its result and none is skipped, and the exit status matches; for each model element listed under System model, the output shows what that line says. Both runs are saved in that one file, each headed by its commit: the disproof condition is judged from both (it holds if the success run still shows the defect, or if the before run already passes, meaning the check cannot detect it), and success from the success run.

**Disproof:** tests/test_memory_sheet.py passes against the pre-change MEMORY_SHEET.md (then it cannot detect a missing heading), or any of its four assertions fails against the new sheet

## System model

**System model:** `docs/model/ARCHITECTURE.md`, a file in this repository describing this repository only (not a shared model). Reachable from the documentation entry point `wiki/index.md`, which links `docs/model/ARCHITECTURE.md`.

**Model elements this change adds, changes or relies on, and what the saved check output must show of each:**

- B1 notes (MEMORY_SHEET.md is a note): changes it; the check output must show tests/test_memory_sheet.py with its 4 tests passed by name
- V2 check.sh output: relies on its required headings; the check output must show test_plan_headings_are_named and test_readme_sections_are_named passing, which read those headings from check.sh
- V4 wiki/index.md map: changes one row; the check output must show tests/test_wiki_map.py passing

**Views, freshness and reconciliation:** the applicable view is the requirement-to-verification link in the Requirements table (each requirement and the check that shows it, the check being source-linked by its command); no other view applies because the change adds, changes or relies on no entity, process, record, event or view beyond the elements listed above. Freshness: the model's drift test (`tests/test_model.py`, `tests/test_check_sh.py`, `tests/test_practice.py`, `tests/test_wiki_map.py`) runs inside the success check and its output is in the saved check file. If an element above is added, removed or renamed, the model, its view coverage and the saved check output are reconciled in the same commit, and otherwise the model needs no update because the elements keep their meaning.

## Capability reuse

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because this is interview-prep wording plus a doc drift test, not a reusable capability
- What the work needs that no entry provides: edits to this repository's own files (`MEMORY_SHEET.md`, `README.md`, `wiki/index.md`, `tests/test_memory_sheet.py`); catalogue entries are cross-project capabilities, and none edits a repository's own source.

## Uncertainties

Material uncertainties. This one is the complete set; it is material because a file outside the list would
make the change exceed this plan's scope.

| Material uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether the change needs files beyond the list below; if so it is out of scope for this plan | Resolved before editing: Four files: MEMORY_SHEET.md, one README.md row, one wiki/index.md row, one new drift test; no runtime code |

## Vertical and reset

One vertical over these files (and the saved check output, `docs/plans/kit-v3-script.check.txt`):

- `MEMORY_SHEET.md`
- `README.md`
- `wiki/index.md`
- `tests/test_memory_sheet.py`

The vertical delivers: MEMORY_SHEET.md holds thirteen near-verbatim prompts, in order, from intent through off-the-shelf research, diagrams, plan, build, review and finish, and every heading the kit's gate requires is named in a prompt It is done when this holds: tests/test_memory_sheet.py asserts four properties directly against the file text: (1) the PLAN.md headings parsed from check.sh's 'for sec in "## Goal"' line plus '## System model' each appear verbatim in MEMORY_SHEET.md; (2) the README sections parsed from check.sh's 'for sec in "Run it"' line each appear, and the exact string '"## Run it"' appears; (3) the DESIGN_SECTIONS list parsed from check_docs.py each appear; (4) the finish prompt contains 'Tick each Done when item'. tests/test_wiki_map.py asserts every relative link in wiki/index.md resolves to an existing file. The saved output shows each of these tests passing by name, and running test_memory_sheet.py against the pre-change sheet shows the named assertions failing with the missing headings listed

Make the change, run the success check before and after it, commit. Reset: `git revert` of the commit. Not pursued: anything outside these files. This plan adds no coordinated-work ceremony: no work-unit graph, no review or release contract, no claim beyond the repository's own rules.

## Activation facts

Each fact, with its value and why:

- `shared_mechanism`: false -- the change edits only the listed files and adds no contract, algorithm or mechanism other code uses.
- `empirical_comparison_proposed`: false -- no alternatives are compared; the success check verifies the one change.
- `llm_central`: false -- the change makes no model call.
- `irreversible_or_spend_action`: false -- the change is reverted by `git revert` and spends nothing.
- `claims_external_standard`: false -- the work claims no external standard, schema or contract.
- `aes_governed_target`: false -- this repository has no `.aes/target.yaml` (checked by quick-adopt).
- `durable_documents_declared`: false -- `.agentic/repo.yaml` declares no `durable_documents` (checked by quick-adopt).

