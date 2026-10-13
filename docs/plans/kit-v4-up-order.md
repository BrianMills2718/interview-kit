---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v4-up-order
status: proposed
method_conformance_receipt: docs/plans/kit-v4-up-order.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "A candidate who types the kit's memory sheet in order works in the Unified Process order (rules, intent, questions, use cases with failures and ranked risks, domain model and state machine, off-the-shelf parts, shape as ADRs, the riskiest use case as a sequence diagram, plan, build with one test per state arrow) and produces docs/PRD.md, docs/MODEL.md and docs/DECISIONS.md, which the kit's own check.sh (its helper check_docs.py, inside this one standalone repository; no other repository calls it) accepts only when each required section is filled and every state transition and forbidden transition has a test row"
  canonical_example: "Running bash kit/check.sh on a project whose docs/MODEL.md state machine has the arrow 'Paused --> Refunded' but whose 'Tests from the model' table lacks that arrow prints a FAIL naming 'Paused --> Refunded'; with the row added it prints 0 failed"
  forbidden_substitutes: "claiming success from a check's last line or exit status alone; a change outside the listed files; a commit without the saved check output; a test that passes against the pre-change checker"
  boundaries: "only the files listed under Vertical and reset, in the worktree on branch c5-up-order; no push, no irreversible action and no spend; the owner's request as quoted is the scope"
  done_when: "tests/test_check_docs.py: a complete package passes; missing PRD section, no failure use case, missing state machine without 'No states:', a state transition absent from the Tests table, a forbidden line absent from the Tests table, a sequence heading naming an unknown UC, a missing **Answer:** line, no '| ADR-1 |' row, and an invented function or test name under --final each fail with their own message; tests/test_memory_sheet.py finds every required heading and row id (read from check_docs.py constants) in MEMORY_SHEET.md and its 14 prompts in the spec's order; the full kit suite passes. The disproof run (new tests against the pre-change check_docs.py and MEMORY_SHEET.md) and the full suite on the change are saved as docs/plans/kit-v4-up-order.check.txt, and the commit is tagged [Goal kit-v4-up-order] with an Asked: line quoting the request."
  do_not_gate_on: "the owner's review of the plan page; the fresh-agent practice2 dry run, which the coordinating session runs after this commit"
---

# Planning package and memory sheet follow the Unified Process order

## Actor and result

> **CORE-ACTOR-RESULT-EXAMPLE** (blocking): The plan names the actor it serves, the desired result, and one stable, concrete, user-visible example of that result.

**Actor:** the owner, who asked for this change, and the candidates who use the kit in a timed take-home test.

**Request (verbatim):** the owner 2026-10-13 "yes", approving this proposal: rewrite the interview script to follow the standard Unified Process order from his modelling research (intent, use cases including failures, domain diagram, state diagram, hardest case as a sequence diagram, off-the-shelf parts and shape, plan, build with one test per state-diagram arrow), standard names (PRD, ADR, use cases), only diagrams that answer a question; and rewrite the kit's checker to match.

**Desired result:** A candidate who types the kit's memory sheet in order works in the Unified Process order (rules, intent, questions, use cases with failures and ranked risks, domain model and state machine, off-the-shelf parts, shape as ADRs, the riskiest use case as a sequence diagram, plan, build with one test per state arrow) and produces docs/PRD.md, docs/MODEL.md and docs/DECISIONS.md, which the kit's own check.sh (its helper check_docs.py, inside this one standalone repository; no other repository calls it) accepts only when each required section is filled and every state transition and forbidden transition has a test row.

**Stable example:** Running bash kit/check.sh on a project whose docs/MODEL.md state machine has the arrow 'Paused --> Refunded' but whose 'Tests from the model' table lacks that arrow prints a FAIL naming 'Paused --> Refunded'; with the row added it prints 0 failed.

## Requirements

> **CORE-REQUIREMENTS-TRACED** (blocking): The plan lists its requirements: what was asked for, and what the delivered work's own claims imply. A claim here is what the work is presented as being or doing to its users, for example work presented as following a standard, schema or contract (which implies conformance to it) or an output labelled as showing something (which implies it shows it correctly); the plan's own format and front matter are not such claims, and the details a check examines (what a trace must show) belong to that check rather than being separate requirements. Each requirement names the check that verifies it (a test, script, gate step, or named review of a run) and its status: passing, failing, planned and not yet run, or deferred with a stated reason; deferred requirements are carried onto every release or completion record the plan names. A plan fails this item if it has no requirements list, if any requirement has neither a check nor an explicit deferral with its reason, or if the plan presents the work as following a named standard, schema or contract, or as having another property its users rely on, that its requirements list omits.

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | MEMORY_SHEET.md has 14 prompts in the order of the spec (rules, intent, questions, use cases, domain and states, off the shelf, prove imports, shape, sequence, plan, build, review, README, finish), with the candidate's view stated first at intent, riskiest use case and shape | asked: the owner 2026-10-13 "yes" (Unified Process order) | `tests/test_memory_sheet.py::test_prompts_follow_the_up_order` | planned, not yet run |
| R2 | The planning package uses standard names: docs/PRD.md (goal, requirements, use cases with Kind normal/failure/alternative, assumptions, risks), docs/MODEL.md, docs/DECISIONS.md as ADR rows; templates/DESIGN.md is removed | asked: "standard names (PRD, ADR, use cases)" | `tests/test_check_docs.py` (missing PRD section, no failure use case, no ADR row) and `tests/test_practice.py::test_filled_template_passes_check` | planned, not yet run |
| R3 | MODEL.md requires only the diagrams that answer a question: domain model, state machine (or 'No states:'), a sequence of a named use case; other sections optional; every diagram has an **Answer:** line | asked: "only diagrams that answer a question" | `tests/test_check_docs.py` (missing state machine, unknown UC in sequence heading, missing Answer) | planned, not yet run |
| R4 | One test per state-diagram arrow: every transition and every Forbidden line appears in the 'Tests from the model' table; with --final every named test and function exists in the code | asked: "build with one test per state-diagram arrow" | `tests/test_check_docs.py` (transition absent, forbidden line absent, invented name under --final) | planned, not yet run |
| R5 | The memory sheet names every heading and row id the checker requires, read from check_docs.py constants | implied: the sheet is presented as a script that passes check.sh --final when typed verbatim | `tests/test_memory_sheet.py` | planned, not yet run |
| R6 | No kit file outside docs/plans and practice2/reference/dry-runs still describes DESIGN.md or six fixed diagrams as current; KIT.md equals a fresh build | implied: the kit presents one current method | `grep` recorded in the check file and `tests/test_model.py` (KIT.md equals a fresh build) | planned, not yet run |
| R7 | The recorded practice sample run is in the new format and still passes check_docs.py | implied: the sample run is presented as a passing example | `python3 check_docs.py practice/reference/sample-run --final`, output in the check file | planned, not yet run |

| R8 | Conformance to the claimed method: the prompts put use cases (with failures) before the domain model and state machine, those before the sequence of the riskiest use case, and the build prompt asks for one test per state-machine arrow including forbidden ones; DECISIONS.md uses the Nygard ADR columns (Context, Decision, Consequences) | implied: the work is presented as following the Unified Process order and standard PRD/ADR/use-case names | `tests/test_memory_sheet.py::test_prompts_follow_the_up_order` and `tests/test_check_docs.py` (ADR row, use case kinds) | planned, not yet run |

Requirements the change's own claims imply: R5, R6, R7 and R8 above.

## Success and disproof

> **CORE-SUCCESS-DISPROOF** (blocking): The plan defines the evidence that would show success and a concrete condition that would disprove the approach. Each success measure is the property the plan claims, or a check that directly tests that property, not a stand-in for it: a count, a picture, a readability judgment, or the pipeline agreeing with itself (hashes, labels, byte equality) does not show correctness or conformance it does not test. A plan fails this item if it has no disproof condition, or if a success measure is such a stand-in for the claimed property and the plan names no direct check of that property.

> **CORE-TRACE-REVIEW** (blocking): Every success or acceptance criterion in the plan is judged from the full trace of a run, not only its final outcome: it names the run whose full trace is examined (for example the session, its tool and LLM calls, commits, check output, or messages), where that trace lives, and what must be seen in that trace beyond the final outcome. A criterion that names only an outcome, such as tests passing, a PR merged, a test fixture reproducing the journey, or a status reading succeeded, fails this item. A criterion for which no run exists, such as a pure document edit, passes only when the plan states that exemption and its reason explicitly.

**Success evidence:** tests/test_check_docs.py: a complete package passes; missing PRD section, no failure use case, missing state machine without 'No states:', a state transition absent from the Tests table, a forbidden line absent from the Tests table, a sequence heading naming an unknown UC, a missing **Answer:** line, no '| ADR-1 |' row, and an invented function or test name under --final each fail with their own message; tests/test_memory_sheet.py finds every required heading and row id (read from check_docs.py constants) in MEMORY_SHEET.md and its 14 prompts in the spec's order; the full kit suite passes. Each check tests the claimed property directly: a fixture package is edited to remove exactly one required element and the checker's own message for that element must appear.

**Disproof:** the new tests pass against the pre-change check_docs.py or MEMORY_SHEET.md (so they cannot detect the old format), or check.sh accepts a MODEL.md whose state machine has an arrow with no test row.

**Trace review:** two runs are judged from their full output: the disproof run (the new tests/test_check_docs.py and tests/test_memory_sheet.py against the pre-change check_docs.py and MEMORY_SHEET.md from commit d40bf1c; it must show those tests failing by name) and the success run (the full suite `uv run python -m pytest tests/ -v -p no:cacheprovider` on the changed tree). No model, agent or LLM pipeline runs under this plan. Where the trace lives: both runs, each with the exact command, every test by name with its result, the summary counts and the exit status, are saved in `docs/plans/kit-v4-up-order.check.txt` and committed with the change. What must be seen beyond the final result: each new failure-mode test appears by name and passes on the change and fails on the old checker; no test is skipped; the exit status matches the counts; the sample-run check_docs.py output shows every PASS line.

## When a run fails or surprises us

> **CORE-TRACE-DEBUGGING** (blocking): The plan includes a separate When a run fails or surprises us procedure, distinct from anticipated failure modes. It requires preserving the failed run and its trace id; reading full inputs, prompts, each tool call arguments/results, intermediate stages and final output before selecting a fix; citing the observed divergence; classifying evidence absent, evidence returned but unused or contradicted, invalid expectation, or unresolved; and linking a targeted repair to a new traced verification run while retaining the original failure. Unresolved diagnoses permit investigation but cannot authorize a causal repair. Review completeness is separate from the run verdict.

This procedure is separate from the anticipated failure named in the disproof
under Success and disproof: it applies to any run that fails or surprises us.
Preserve the failed check and its execution trace id (the check file entry: command, commit and
timestamp). Before selecting a fix, read the complete inputs, prompts, tool arguments/results,
intermediate stages and final output, including the full check command/output, each failing
test's assertion and the changed files. Cite the observed divergence and classify evidence
absent, returned but unused or contradicted, invalid expectation, or unresolved. An unresolved
diagnosis cannot authorize a causal repair; it permits only further investigation. Bind the
targeted repair to a new traced verification run; retain the failed original. Review every
failing or surprising item and a sample of passes. A complete review is distinct from a
passing run. Criterion `outcome` covers the entire requested success check.

## Standard conformance

**Standards the work claims to follow:** the Unified Process / RUP ordering as taught in Larman's *Applying UML and Patterns* (use cases, then domain model, then interaction diagrams; riskiest case first); model-based testing from a state machine (one test per transition, including forbidden ones); Nygard's Architecture Decision Record (Context, Decision, Consequences); the PRD and use-case names. None publishes machine-readable rules, so the check encodes these written rules instead:

1. In MEMORY_SHEET.md the use-case prompt comes before the domain-and-states prompt, which comes before the sequence prompt; the sequence prompt targets the riskiest use case.
2. The build prompt asks for a test per state-machine arrow and per forbidden transition.
3. docs/MODEL.md's 'Tests from the model' table contains every `A --> B` arrow of the state machine and every Forbidden line.
4. docs/DECISIONS.md rows are `| ADR-n |` under the columns Context, Decision, Consequences.
5. docs/PRD.md has use cases with Kind normal and at least one failure or alternative.

**Check and gate:** `tests/test_memory_sheet.py` (rules 1-2) and `tests/test_check_docs.py` plus `check_docs.py` itself (rules 3-5), run by the full suite `uv run python -m pytest tests/ -v -p no:cacheprovider`, which is this repository's local merge gate (no hosted CI); check.sh runs check_docs.py on every candidate project as its gate step '1b. Planning package'. The disproof includes: an artifact the kit labels as following these rules (the sample run's package, the fixture package, or the memory sheet) violates one of them while the check passes.

**Extensions beyond the standards, labelled as such:** the `**Answer:**` line under each diagram, the 'No states:' exemption, the 'Rejected alternative' and 'What would show it wrong' ADR columns, and the `| R1 |` / `| A1 |` / `| K1 |` row ids are the kit's own additions; the templates say so in their guidance text.

## System model

> **CORE-SYSTEM-MODEL** (blocking): The plan links the project's system model (a path such as docs/model/ODD.md) or carries the one-line exemption `System model: exempt -- <reason>`, which fits only a project with no stored state and no user-facing view. Unless exempt, the plan names each system-model element (entity, process, record or event, or view) that the work adds, changes, or relies on, and its trace review names, for each such element, what the examined run must show of it (for example an event of that record type with its id, or the view displaying that entity). A plan with neither a model link nor the exemption line fails this item, as does one that lists model elements without saying what the examined run must show of each, or one that names no element without stating that the work touches none and why. For a maintained repository, the plan also cites the documentation entry point from which the model is reachable; a shared model explicitly identifies this repository's scope. It names applicable source-linked views, explains material omissions without imposing a fixed diagram quota, names concrete model freshness or drift checks, and states how the model, view coverage and verification evidence will be reconciled in the same change (or gives a concrete reason each needs no update). A bare model path without these discovery, view, freshness and reconciliation obligations fails this item. Representation Router may render selected views but does not supply planning authority or prove executed behavior.

**System model:** `docs/model/ARCHITECTURE.md`, a file in this repository describing this repository only (not a shared model). Reachable from the documentation entry point `wiki/index.md`, which links `docs/model/ARCHITECTURE.md`.

**Model elements this change adds, changes or relies on, and what the saved check output must show of each:**

- B1 (notes: AGENTS.md, PLAN.template.md, skills, agents, method, MEMORY_SHEET.md) changes to the new order and names; the check file must show tests/test_memory_sheet.py passing on the change and failing on the old sheet, and the grep for DESIGN.md / six diagrams finding nothing outside docs/plans and dry-runs.
- B3 (check.sh, the enforcement gate) changes through its helper check_docs.py; the check file must show each new failure-mode test in tests/test_check_docs.py and tests/test_check_sh.py passing by name.
- B4 (practice problem and its recorded sample run) is brought to the new format; the check file must show check_docs.py --final on practice/reference/sample-run printing only PASS lines and tests/test_practice.py passing.
- V2 (check.sh output) gains new PASS/FAIL messages; the check file must show tests/test_check_sh.py passing, including the counted package results.
- V4 (wiki/index.md map) is updated to name PRD/MODEL/DECISIONS; the check file must show tests/test_wiki_map.py passing.

**Views, freshness and reconciliation:** the applicable view is the requirement-to-verification link in the Requirements table (each requirement and the check that shows it, source-linked by its command); no other view applies because the change adds no entity, process, record or event beyond the elements above. Freshness: the model's drift tests (`tests/test_model.py`, `tests/test_check_sh.py`, `tests/test_practice.py`, `tests/test_wiki_map.py`) run inside the success check and their output is in the saved check file. The elements keep their IDs and meaning, so ARCHITECTURE.md needs no update; if an element were added, removed or renamed, the model, view coverage and check output would be reconciled in the same commit.

## Capability reuse

> **CORE-CAPABILITY-REUSE** (blocking): The plan answers capability reuse against the capability catalogue in agentic-capability-architecture-canonical, which has two files: `reuse_candidates.yml`, whose entries under `candidates:` are cross-project capabilities with their selected off-the-shelf implementations, each named by its `id` (for example `documents_to_text`) and marked candidate or promoted; and `capability_registry.yml`, whose entries under `capabilities:` are the packages that repository holds, each named by its key (for example `approvals`) with the capability ids it `provides` (for example `approval.resolve`). An entry from either file counts. The plan names each catalogue capability the work reuses, by its id, key or provided id; names each new capability the work adds together with its first consumer (the project, command or workflow in this plan that uses it); and, where no entry covers what the work needs, states `No catalogue entry fits, because <reason>`, the reason saying what the work needs that no entry provides. A plan may give more than one of these answers. A plan fails this item if it gives none of them, if it claims reuse without naming the catalogue entry or id reused (reusing code or a contract that is not a catalogue entry does not count), if it adds a capability without naming its first consumer, or if it says no entry fits without a reason.

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because this is content inside a standalone public interview kit (its prompt script, templates and its own standard-library checker), not a cross-project mechanism.
- What the work needs that no entry provides: edits to this repository's own files; catalogue entries are cross-project capabilities, and none edits a repository's own source. The method itself is reused prior art (Unified Process, Larman's use case to domain model to interaction order, model-based testing from a state machine, Nygard ADRs), named in the spec.

## Authority and non-goals

> **CORE-AUTHORITY-NONGOALS** (blocking): The plan states who holds authority over the work and what it explicitly will not do (non-goals).

**Authority:** the owner asked for this change in his own repository; one agent makes it in its own worktree.

**Non-goals:** nothing outside the files listed under Vertical and reset; no change to PLAN.md headings, README sections or the compile and test checks in check.sh; no rewrite of the practice2 dry-run history; no push; no irreversible action and no spend.

## Irreversible actions and spend

> **CORE-IRREVERSIBLE-SPEND** (blocking): For each irreversible action or spend the plan proposes, it names the boundary, who must authorize it, and how it is contained.

None proposed. Every edit is a commit on a local branch, undone by `git revert`; nothing is pushed, deleted from history, sent or paid for. The boundary is the worktree; the owner's approval of the task authorizes the local commit.

## Uncertainties

> **CORE-UNCERTAINTIES** (blocking): The plan lists its material uncertainties, and each one has an owner or the evidence that would resolve it.

| Material uncertainty | Owner or resolving evidence |
| --- | --- |
| Whether a fresh agent typing the new sheet verbatim on practice2 passes check.sh --final and the grader | The coordinating session's dry run after this commit (not gated here) |
| Whether files beyond the list need edits so nothing describes the old package as current | Resolved by the grep recorded in the check file before commit |
| Whether the 'A --> B' transition match is too strict for labelled arrows ('A --> B: event') | Resolved by reading: the checker extracts 'A --> B' without the label and the test table must contain that text; covered by a fixture test with a labelled arrow |

## Activation facts

> **CORE-ACTIVATION-FACTS** (blocking): No activation fact that the plan triggers is declared false. Declaring a fact true when the plan does not strictly need it is acceptable, because it only adds checks; judge only facts declared false. empirical_comparison_proposed is triggered when the plan proposes an A/B test, benchmark, bake-off, or other experiment comparing alternative designs, models, or candidates to choose among them; checking the built result against an expected outcome (an acceptance test, fixture replay, or regression check) is verification and does not trigger it. shared_mechanism is triggered by a new shared mechanism, contract, or algorithm; llm_central by behavior that centrally depends on LLM calls; irreversible_or_spend_action by a proposed irreversible action or spend. claims_external_standard is triggered when the plan claims, or presents its work as, following, implementing or conforming to a standard, schema or contract owned outside the repository being changed (for example a model presented as DM2, or output said to match a published schema); conforming to the repository's own contracts does not trigger it; aes_governed_target when the target repository is governed by an AES target (`.aes/target.yaml`), or the plan creates one (for example by running `aes init`). These two facts are optional: an undeclared one is shown as false and is judged like a declared false.

Each fact, with its value and why:

- `shared_mechanism`: false -- check_docs.py is a helper of this standalone repository's check.sh; no other repository calls it, and no contract, algorithm or mechanism other code uses is added.
- `empirical_comparison_proposed`: false -- no alternatives are compared; the success check verifies the one change.
- `llm_central`: false -- the change makes no model call.
- `irreversible_or_spend_action`: false -- the change is reverted by `git revert` and spends nothing.
- `claims_external_standard`: true -- the work presents the memory sheet as following the Unified Process order (use cases, then domain model, then interactions, riskiest case first) and uses the standard names PRD, ADR (Nygard columns) and use cases; requirement R8 states that conformance and names its check.
- `aes_governed_target`: false -- this repository has no `.aes/target.yaml`.

## Vertical and reset

> **OV-PROTO-VERTICAL-RESET** (blocking): The plan names the minimal vertical result, the reset boundary, and the non-goals, without adding coordinated-work ceremony.

One vertical over these files (and the saved check output, `docs/plans/kit-v4-up-order.check.txt`, plus this plan's own records):

- `check_docs.py`
- `check.sh`
- `templates/PRD.md`
- `templates/DESIGN.md`
- `templates/MODEL.md`
- `templates/DECISIONS.md`
- `MEMORY_SHEET.md`
- `AGENTS.md`
- `PLAN.template.md`
- `method/README.md`
- `method/system-model.md`
- `method/design-chain.md`
- `method/representation.md`
- `method/decisions.md`
- `method/architecture-views.md`
- `skills/plan/SKILL.md`
- `skills/explain-your-work/SKILL.md`
- `agents/planner.md`
- `practice/PROBLEM.md`
- `practice2/PROBLEM.md`
- `practice2/reference/dry-runs/README.md`
- `practice/reference/sample-run/README.md`
- `practice/reference/sample-run/docs/PRD.md`
- `practice/reference/sample-run/docs/DESIGN.md`
- `practice/reference/sample-run/docs/MODEL.md`
- `practice/reference/sample-run/docs/DECISIONS.md`
- `wiki/index.md`
- `README.md`
- `KIT.md`
- `tests/test_check_docs.py`
- `tests/test_check_sh.py`
- `tests/test_practice.py`
- `tests/test_memory_sheet.py`
- `tests/fixtures/adder_docs/PRD.md`
- `tests/fixtures/adder_docs/DESIGN.md`
- `tests/fixtures/adder_docs/MODEL.md`
- `tests/fixtures/adder_docs/DECISIONS.md`
- `docs/plans/kit-v4-up-order.spec.md`

The minimal vertical result: a candidate can type the 14 prompts of MEMORY_SHEET.md in order and get docs/PRD.md, docs/MODEL.md (domain model, state machine, riskiest-use-case sequence, a 'Tests from the model' table) and docs/DECISIONS.md (ADR rows), and the kit's check.sh accepts that package only when every state arrow and forbidden transition has a test row. The concrete result in this repository: the rewritten checker, templates, sheet and sample run, with tests/test_check_docs.py and tests/test_memory_sheet.py passing, saved in the check file.

Make the change, run the disproof and success checks, commit once. Reset: `git revert` of the commit. Not pursued: anything outside these files. This plan adds no coordinated-work ceremony: no work-unit graph, no review or release contract, no claim beyond the repository's own rules.
