---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v3-dryrun-flow
plan_id: kit-v3-dryrun-flow
status: proposed
planning_path: requested
method_conformance_receipt: docs/plans/kit-v3-dryrun-flow.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "practice/PROBLEM.md removes the reference with a portable Python command that a test runs; it installs with uv or pip; AGENTS.md says what to do when no person is present to approve the plan; PLAN.template.md has a Shape section and failure modes under Risks that check.sh accepts once filled; KIT.md rebuilt"
  canonical_example: "An agent in a pre-made folder runs practice/PROBLEM.md's removal command and kit/practice/reference is gone, with no 'rm -rf' for a host to block"
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output"
  boundaries: "only these files: practice/PROBLEM.md, AGENTS.md, PLAN.template.md, KIT.md, tests/test_practice.py; no irreversible action and no spend; the owner's request as quoted is the scope"
  done_when: "uv run pytest -v tests/test_practice.py tests/test_check_sh.py tests/test_model.py: test_problem_removal_command_deletes_the_reference (runs the command quoted in PROBLEM.md on a copied kit and asserts reference/ no longer exists while grade.py still does) and test_filled_template_passes_check (fills every template placeholder, runs check.sh, expects exit 0) PASSED, KIT.md tests PASSED, exit 0; both new tests fail on 8d6de8f The check's full output on the parent commit and on the change commit is committed as docs/plans/kit-v3-dryrun-flow.check.txt, and the commit is tagged [Goal kit-v3-dryrun-flow] with an Asked: line quoting the request."
  do_not_gate_on: "the owner's review of the plan page; work outside the listed files"
---

# Make the practice steps and plan rules work for an agent run

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

**Request (verbatim):** The owner 2026-10-11 "what i want is the planning mehtodology all the models and stuff"

**Desired result:** practice/PROBLEM.md removes the reference with a portable Python command that a test runs; it installs with uv or pip; AGENTS.md says what to do when no person is present to approve the plan; PLAN.template.md has a Shape section and failure modes under Risks that check.sh accepts once filled; KIT.md rebuilt

**Stable example:** An agent in a pre-made folder runs practice/PROBLEM.md's removal command and kit/practice/reference is gone, with no 'rm -rf' for a host to block

## Authority and non-goals

**Authority:** the owner asked for this change in his own repository; one agent makes it.

**Non-goals:** nothing outside the files listed under Vertical and reset. No irreversible action and no spend.

## Requirements

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | practice/PROBLEM.md removes the reference with a portable Python command that a test runs; it installs with uv or pip; AGENTS.md says what to do when no person is present to approve the plan; PLAN.template.md has a Shape section and failure modes under Risks that check.sh accepts once filled; KIT.md rebuilt | asked: The owner 2026-10-11 "what i want is the planning mehtodology all the models and stuff" | the success check under Success and disproof, its output saved as `docs/plans/kit-v3-dryrun-flow.check.txt` | planned, not yet run |

Requirements the change's own claims imply: none beyond R1; the change presents nothing as following a standard, schema or contract.

## Success and disproof

**Success evidence:** uv run pytest -v tests/test_practice.py tests/test_check_sh.py tests/test_model.py: test_problem_removal_command_deletes_the_reference (runs the command quoted in PROBLEM.md on a copied kit and asserts reference/ no longer exists while grade.py still does) and test_filled_template_passes_check (fills every template placeholder, runs check.sh, expects exit 0) PASSED, KIT.md tests PASSED, exit 0; both new tests fail on 8d6de8f

**Trace review:** two runs of the success check above are judged from their full output: one on the parent commit before the change (the disproof run: it must show the defect or the check failing, which proves the check can fail) and one on the commit that makes the change (the success run); no model, agent or LLM pipeline runs under this plan. Where the trace lives: the check's complete output, with the exact command and its exit status, is saved as `docs/plans/kit-v3-dryrun-flow.check.txt` and committed with the change. What must be seen in it beyond the final result: the command ran against the files listed under Vertical and reset at that commit, each check or test it reports appears by name with its result and none is skipped, and the exit status matches; for each model element listed under System model, the output shows what that line says. Both runs are saved in that one file, each headed by its commit: the disproof condition is judged from both (it holds if the success run still shows the defect, or if the before run already passes, meaning the check cannot detect it), and success from the success run.

**Disproof:** either new test passes on 8d6de8f (it cannot see the old rm -rf step or the template gap) or fails after the change

## System model

**System model:** `docs/model/ARCHITECTURE.md`, a file in this repository describing this repository only (not a shared model). Reachable from the documentation entry point `wiki/index.md`, which links `docs/model/ARCHITECTURE.md`.

**Model elements this change adds, changes or relies on, and what the saved check output must show of each:**

- B4 is an entity (practice problem): the run must show test_problem_removal_command_deletes_the_reference FAILED before and PASSED after. B1 is an entity (notes: AGENTS.md, PLAN.template.md): the run must show test_filled_template_passes_check and test_planner_notes_name_every_section_check_sh_requires PASSED after. B5 is an entity (KIT.md): the run must show test_kit_md_matches_its_sources PASSED after

**Views, freshness and reconciliation:** the applicable view is the requirement-to-verification link in the Requirements table (each requirement and the check that shows it, the check being source-linked by its command); no other view applies because the change adds, changes or relies on no entity, process, record, event or view beyond the elements listed above. Freshness: the model's drift test (`tests/test_model.py`, `tests/test_check_sh.py`, `tests/test_practice.py`, `tests/test_wiki_map.py`) runs inside the success check and its output is in the saved check file. If an element above is added, removed or renamed, the model, its view coverage and the saved check output are reconciled in the same commit, and otherwise the model needs no update because the elements keep their meaning.

## Capability reuse

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because this is content inside a standalone public interview kit, not a cross-project mechanism
- What the work needs that no entry provides: edits to this repository's own files (`practice/PROBLEM.md`, `AGENTS.md`, `PLAN.template.md`, `KIT.md`, `tests/test_practice.py`); catalogue entries are cross-project capabilities, and none edits a repository's own source.

## Uncertainties

Material uncertainties. This one is the complete set; it is material because a file outside the list would
make the change exceed this plan's scope.

| Material uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether the change needs files beyond the list below; if so it is out of scope for this plan | Resolved before editing: git status --short lists only: practice/PROBLEM.md AGENTS.md PLAN.template.md KIT.md tests/test_practice.py |

## Vertical and reset

One vertical over these files (and the saved check output, `docs/plans/kit-v3-dryrun-flow.check.txt`):

- `practice/PROBLEM.md`
- `AGENTS.md`
- `PLAN.template.md`
- `KIT.md`
- `tests/test_practice.py`

The vertical delivers: practice/PROBLEM.md removes the reference with a portable Python command that a test runs; it installs with uv or pip; AGENTS.md says what to do when no person is present to approve the plan; PLAN.template.md has a Shape section and failure modes under Risks that check.sh accepts once filled; KIT.md rebuilt It is done when this holds: uv run pytest -v tests/test_practice.py tests/test_check_sh.py tests/test_model.py: test_problem_removal_command_deletes_the_reference (runs the command quoted in PROBLEM.md on a copied kit and asserts reference/ no longer exists while grade.py still does) and test_filled_template_passes_check (fills every template placeholder, runs check.sh, expects exit 0) PASSED, KIT.md tests PASSED, exit 0; both new tests fail on 8d6de8f

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

