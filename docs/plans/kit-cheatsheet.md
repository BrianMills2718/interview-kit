---
schema_version: "1.0"
artifact_type: design_plan
id: kit-cheatsheet
plan_id: kit-cheatsheet
status: proposed
planning_path: requested
method_conformance_receipt: docs/plans/kit-cheatsheet.receipt.json
conflict_surfaces:
  - {kind: repository_path, repository: "<owner>/interview-kit", target: "CHEATSHEET.md", access: write}
  - {kind: repository_path, repository: "<owner>/interview-kit", target: "README.md", access: write}
  - {kind: repository_path, repository: "<owner>/interview-kit", target: "wiki/index.md", access: write}
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "CHEATSHEET.md on main gives one short prompt per stage and nine models chosen by question, linked from README and wiki/index.md"
  canonical_example: "Section 5 row 'What is in the data?' gives the data-dictionary prompt"
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output"
  boundaries: "only these files: CHEATSHEET.md, README.md, wiki/index.md; no irreversible action and no spend; the owner's request as quoted is the scope"
  done_when: "tests/test_wiki_map.py asserts every linked page exists and is reachable from wiki/index.md; full suite exits 0 The check's full output on the parent commit and on the change commit is committed as docs/plans/kit-cheatsheet.check.txt, and the commit is tagged [Goal kit-cheatsheet] with an Asked: line quoting the request."
  do_not_gate_on: "the owner's review of the plan page; work outside the listed files"
---

# Cheat sheet: short prompts per stage with the full model set

## When a run fails or surprises us

This procedure is separate from the anticipated failure named in the disproof
under Success and disproof: it applies to any run that fails or surprises us.
Preserve the failed run itself: keep its complete output (command, every
line, exit status) and its execution trace id, never overwritten by a rerun.
Before selecting a fix,
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

**Request (verbatim):** the owner 2026-10-13 "iw ant like concise terse helper prompts about settting up the normative docuemtnation, planning. modeling data analysis etc" and "is there a github link where i have htat? ... the only thing you ahve ais a state diagram?"

**Desired result:** CHEATSHEET.md on main gives one short prompt per stage and nine models chosen by question, linked from README and wiki/index.md

**Stable example:** Section 5 row 'What is in the data?' gives the data-dictionary prompt

## Authority and non-goals

**Authority:** the owner asked for this change in his own repository; one agent makes it.

**Non-goals:** nothing outside the files listed under Vertical and reset. No irreversible action and no spend.

## Requirements

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | CHEATSHEET.md on main gives one short prompt per stage and nine models chosen by question, linked from README and wiki/index.md | asked: the owner 2026-10-13 "iw ant like concise terse helper prompts about settting up the normative docuemtnation, planning. modeling data analysis etc" and "is there a github link where i have htat? ... the only thing you ahve ais a state diagram?" | the success check under Success and disproof, its output saved as `docs/plans/kit-cheatsheet.check.txt` | planned, not yet run |

Requirements the change's own claims imply: none beyond R1; the change presents nothing as following a standard, schema or contract.

## Success and disproof

**Success evidence:** tests/test_wiki_map.py asserts every linked page exists and is reachable from wiki/index.md; full suite exits 0

**Trace review:** two runs of the success check above are judged from their full output: one on the parent commit before the change (the disproof run: it must show the defect or the check failing, which proves the check can fail) and one on the commit that makes the change (the success run); no model, agent or LLM pipeline runs under this plan. Where the trace lives: the check's complete output, with the exact command and its exit status, is saved as `docs/plans/kit-cheatsheet.check.txt` and committed with the change. What must be seen in it beyond the final result: the command ran against the files listed under Vertical and reset at that commit, each check or test it reports appears by name with its result and none is skipped, and the exit status matches; for each model element listed under System model, the output shows what that line says. Both runs are saved in that one file, each headed by its commit: the disproof condition is judged from both (it holds if the success run still shows the defect, or if the before run already passes, meaning the check cannot detect it), and success from the success run.

**Disproof:** the wiki map test fails, or the file lacks the nine model rows

## System model

**System model:** `method/system-model.md`, a file in this repository describing this repository only (not a shared model). No documentation entry point links `method/system-model.md` yet; that is a visible adoption gap this change does not close.

**Model elements this change adds, changes or relies on, and what the saved check output must show of each:**

- none -- documentation page; no model element added or changed

**Views, freshness and reconciliation:** the applicable view is the requirement-to-verification link in the Requirements table (each requirement and the check that shows it, the check being source-linked by its command); no other view applies because the change adds, changes or relies on no entity, process, record, event or view beyond the elements listed above. Freshness: the model's drift test (`tests/test_model.py`) runs inside the success check and its output is in the saved check file. If an element above is added, removed or renamed, the model, its view coverage and the saved check output are reconciled in the same commit, and otherwise the model needs no update because the elements keep their meaning.

## Capability reuse

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because this is a page of prompts inside one public kit
- What the work needs that no entry provides: edits to this repository's own files (`CHEATSHEET.md`, `README.md`, `wiki/index.md`); catalogue entries are cross-project capabilities, and none edits a repository's own source.

## Uncertainties

Material uncertainties. This one is the complete set; it is material because a file outside the list would
make the change exceed this plan's scope.

| Material uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether the change needs files beyond the list below; if so it is out of scope for this plan | Resolved before editing: 3 files: CHEATSHEET.md new, one row each in README.md and wiki/index.md; no code. System model entry point: wiki/index.md links method/README.md, whose row 'Before code: the shape of the solution' links method/system-model.md |

## Vertical and reset

One vertical over these files (and the saved check output, `docs/plans/kit-cheatsheet.check.txt`):

- `CHEATSHEET.md`
- `README.md`
- `wiki/index.md`

The vertical delivers: CHEATSHEET.md on main gives one short prompt per stage and nine models chosen by question, linked from README and wiki/index.md It is done when this holds: tests/test_wiki_map.py asserts every linked page exists and is reachable from wiki/index.md; full suite exits 0

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
