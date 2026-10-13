---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v3-practice3
status: proposed
method_conformance_receipt: docs/plans/kit-v3-practice3.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "The kit has a third timed practice problem that rehearses the data-analysis half of a data-science agentic take-home: an agent whose tools do anomaly detection, coordinated-behaviour detection, a Welch t-test and reply-network counting over multilingual synthetic posts, a human approval step, and a classifier evaluation with per-topic precision, recall and a confusion matrix, graded offline by shown and hidden cases."
  canonical_example: "A solution whose daily_volume_anomalies compares with > instead of >= runs `python kit/practice3/grade.py solution.py evaluate.py` and sees `FAIL hidden: z-threshold-is-inclusive` / `failed check: tool output text` and exit 1, with no expected text printed; the reference prints `== grade: N passed, 0 failed of N cases (H hidden)` and exits 0."
  forbidden_substitutes: "the reference passing alone (a grader that passes everything also passes it); hidden cases that test rules PROBLEM.md does not state; metric checks on a prediction set where all-zero or all-one answers would also pass; data whose planted signals are asserted only by count, not by which posts and accounts"
  boundaries: "files listed under Vertical and reset, on branch practice3-data-analysis in this session's isolated worktree off origin/main d40bf1c; not pushed; MEMORY_SHEET.md, method/, templates/, check.sh, check_docs.py, KIT.md and the existing reference solutions untouched (another session owns them)"
  done_when: "tests/test_practice3.py passes (reference passes every shown and hidden case; each single-rule broken copy fails exactly its intended hidden case; hidden failures print no expected value; make_data.py reproduces posts.csv and labels.csv byte for byte; the removal command deletes practice3/reference and the grader still runs); full pytest suite exit 0; privacy grep 0 hits; results in docs/plans/kit-v3-practice3.check.txt"
  do_not_gate_on: "a timed human run; a dry run by a fresh agent (not asked for in this lane); a live-model evaluation"
---

# Kit v3: a third practice problem for the data-analysis side

Each section below answers the checklist items quoted in it.

## Actor and result

> **CORE-ACTOR-RESULT-EXAMPLE** (blocking): The plan names the actor it serves, the desired result, and one stable, concrete, user-visible example of that result.

**Actor:** a candidate rehearsing for a 4-hour data-science agentic take-home in a hosted Python IDE, graded on solution quality, AI use and explanations, for a role that asks for LLMs inside analytical pipelines, evaluating agentic systems, anomaly detection, statistical tests, multilingual text analytics and network analysis. **Result:** a third rehearsal that exercises exactly those analysis skills (the first two rehearse only agent and tool mechanics). **Example:** their `daily_volume_anomalies` uses `>`; `grade.py` prints `FAIL hidden: z-threshold-is-inclusive` / `failed check: tool output text`; they find "at or above" in PROBLEM.md, write a test at the boundary, fix it, and the case passes.

## Requirements

> **CORE-REQUIREMENTS-TRACED** (blocking): The plan lists its requirements: what was asked for, and what the delivered work's own claims imply. A claim here is what the work is presented as being or doing to its users, for example work presented as following a standard, schema or contract (which implies conformance to it) or an output labelled as showing something (which implies it shows it correctly); the plan's own format and front matter are not such claims, and the details a check examines (what a trace must show) belong to that check rather than being separate requirements. Each requirement names the check that verifies it (a test, script, gate step, or named review of a run) and its status: passing, failing, planned and not yet run, or deferred with a stated reason; deferred requirements are carried onto every release or completion record the plan names. A plan fails this item if it has no requirements list, if any requirement has neither a check nor an explicit deferral with its reason, or if the plan presents the work as following a named standard, schema or contract, or as having another property its users rely on, that its requirements list omits.

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | practice3/ mirrors practice2: PROBLEM.md, data, grade.py with hidden cases in hidden.b64, reference/, tests/test_practice3.py, scripted model reused | asked: the owner 2026-10-13 via the coordinating session, "make sure the practice examples test what a data-science agentic take-home will test" | test_reference_passes_every_case; test_hidden_file_matches_its_source | passing: see check.txt |
| R2 | Seeded generator committed with its output: ~400 posts, ~30 days, ~40 accounts, en/es/ru, two volume spikes, a ~5-account coordinated cluster, ~60 gold labels over 4 topics | asked (same) | test_data_is_reproducible (byte equality of a rerun) plus test_planted_signals (the spike days, the cluster's accounts and post ids, by membership) | passing: see check.txt |
| R3 | Five analysis tools with exact return formats stated, plus one approval-gated flag tool where "no" records nothing | asked (same) | the shown and hidden agent cases; flag-declined-records-nothing | passing: see check.txt |
| R4 | Validated Pydantic `Finding` final answer; an invalid one goes back to the model | asked (same) | coordination-finding-needs-evidence (hidden) | passing: see check.txt |
| R5 | evaluate.py: per-topic precision and recall plus confusion matrix; fake model by default, real LLM behind an env var; a note on what the errors show | asked (same) | metric cases on a fixed prediction set where trivial answers fail; zero-division and out-of-topic cases | passing: see check.txt |
| R6 | About 10 hidden cases covering ties, empty filters, z boundary, window just outside, approval "no", zero division; 3 shown examples | asked (same) | test_reference_passes_every_case (counts hidden == 11) plus the rule-to-case table below | passing: see check.txt |
| R7 | The grader fails a solution that breaks a stated rule, each on the intended case; hidden failures never print expected values | the work's own claim (it grades, cases are hidden) | test_grader_fails_a_broken_solution (parametrized); test_hidden_failures_print_no_expected_values | passing: see check.txt |
| R8 | The removal one-liner in all three PROBLEM pages deletes practice3/reference too, and the grader still runs without it | asked (extend the shutil one-liner) | test_problem_removal_command_deletes_the_reference (practice3) | passing: see check.txt |
| R9 | The kit stays public-safe: no employer, team, person, product or interview detail | asked (the kit is public) | privacy grep recorded in check.txt | passing: see check.txt |
| R10 | PROBLEM.md names the planning package as "PRD.md, MODEL.md, DECISIONS.md, as the kit's templates describe" | coordinator message 2026-10-13 (another session is rewriting the package) | read in review; recorded in check.txt | passing: see check.txt |

Claims implied: "hidden" (R7), "grades" (R7), "reproducible data" (R2), "fair" (each hidden case tests a stated rule, R6 table). No external standard is claimed; the Welch t-test is computed by scipy, which is the reference implementation of that statistic.

## Success and disproof

> **CORE-SUCCESS-DISPROOF** (blocking): The plan defines the evidence that would show success and a concrete condition that would disprove the approach. Each success measure is the property the plan claims, or a check that directly tests that property, not a stand-in for it: a count, a picture, a readability judgment, or the pipeline agreeing with itself (hashes, labels, byte equality) does not show correctness or conformance it does not test. A plan fails this item if it has no disproof condition, or if a success measure is such a stand-in for the claimed property and the plan names no direct check of that property.

> **CORE-TRACE-REVIEW** (blocking): Every success or acceptance criterion in the plan is judged from the full trace of a run, not only its final outcome: it names the run whose full trace is examined (for example the session, its tool and LLM calls, commits, check output, or messages), where that trace lives, and what must be seen in that trace beyond the final outcome. A criterion that names only an outcome, such as tests passing, a PR merged, a test fixture reproducing the journey, or a status reading succeeded, fails this item. A criterion for which no run exists, such as a pure document edit, passes only when the plan states that exemption and its reason explicitly.

**Success evidence:** the reference passes every case; each single-rule breakage (at least three: z comparison `>` for `>=`, window exclusive instead of inclusive, flag recorded before the analyst answers) fails exactly its named hidden case (membership, not count); the hidden expected values of the agent cases are recomputed by an independent script (plain arithmetic, not the reference) and match; the byte-equality data test is only a reproducibility check, and the planted signals are checked separately by which days, accounts and post ids they are.

**Rule-to-case table (R6):** count-empty-filter-means-all = "an empty string, meaning no filter", language ignores case; count-range-matches-nothing = "`0 posts.`" (both calls); z-threshold-is-inclusive = "rounded to 2 decimals, at or above z" (z 2.992 drops the day whose z is 2.99297; z 2.99 keeps it); window-boundary = "at most window_minutes after the anchor (inclusive)" (4-minute spread included, 10-minute near miss excluded at 9); same-account-counts-once = "distinct accounts"; flag-declined-records-nothing = flag rule 4 "Otherwise" and "A no records nothing"; flag-input-checked-before-pause = flag rules 1-3; hub-ties-by-account-id = "ties by account id"; self-replies-not-counted = "a reply to one's own post does not count"; coordination-finding-needs-evidence = Finding rule; precision-zero-division = "a topic never predicted has precision 0.0"; prediction-outside-topics-raises = "raises ValueError". Each case was checked by reading it against the rule text; their expected values are recomputed independently in check.txt section 3.

**Disproof:** a broken copy that passes; a hidden case that fails for a rule not on the page; an independent recomputation that disagrees with a hidden expected value; or a metric case that an all-zero implementation passes.

**Runs judged and their traces:** `.venv/bin/python -m pytest tests/test_practice3.py -v` and the full suite, output saved in docs/plans/kit-v3-practice3.check.txt, which must show each parametrized broken copy with its failed case name, the independent recomputation's output beside the hidden expectations, and the reference's grade output line by line.

## When a run fails or surprises us

> **CORE-TRACE-DEBUGGING** (blocking): The plan includes a separate When a run fails or surprises us procedure, distinct from anticipated failure modes. It requires preserving the failed run and its trace id; reading full inputs, prompts, each tool call arguments/results, intermediate stages and final output before selecting a fix; citing the observed divergence; classifying evidence absent, evidence returned but unused or contradicted, invalid expectation, or unresolved; and linking a targeted repair to a new traced verification run while retaining the original failure. Unresolved diagnoses permit investigation but cannot authorize a causal repair. Review completeness is separate from the run verdict.

Keep the failing run before changing anything: its trace id is the pytest node id plus the case name (each grader case runs under `thread_id` = case name), and its full output is copied into check.txt and never overwritten. Before choosing a fix, read the full inputs and prompts (the case's message and the agent's system prompt; for a metric case its gold and predicted lists), every intermediate stage (each scripted AI message, each tool call's arguments and the tool output it got back, each interrupt and resume), and the final output (the Finding, the flagged list, or the returned metrics). Cite the observed divergence (the expected line and the actual tool output or state, side by side in check.txt). Classify: evidence absent (the tool never produced the text), returned but unused (tool text right, Finding or state wrong), invalid expectation (the case or the spec is wrong), or unresolved (read more, no fix; an unresolved diagnosis never authorizes a causal repair). The repair is targeted at the classified cause only. A fix to a case or to PROBLEM.md re-encodes hidden.b64 and is linked to a new traced verification run of the full test file (its trace id is the same node id and case name with the rerun's timestamp) whose full output is saved beside the original failure, which stays in check.txt. Whether the trace review was complete is recorded separately from pass or fail.

## System model

> **CORE-SYSTEM-MODEL** (blocking): The plan links the project's system model (a path such as docs/model/ODD.md) or carries the one-line exemption `System model: exempt -- <reason>`, which fits only a project with no stored state and no user-facing view. Unless exempt, the plan names each system-model element (entity, process, record or event, or view) that the work adds, changes, or relies on, and its trace review names, for each such element, what the examined run must show of it (for example an event of that record type with its id, or the view displaying that entity). A plan with neither a model link nor the exemption line fails this item, as does one that lists model elements without saying what the examined run must show of each, or one that names no element without stating that the work touches none and why. For a maintained repository, the plan also cites the documentation entry point from which the model is reachable; a shared model explicitly identifies this repository's scope. It names applicable source-linked views, explains material omissions without imposing a fixed diagram quota, names concrete model freshness or drift checks, and states how the model, view coverage and verification evidence will be reconciled in the same change (or gives a concrete reason each needs no update). A bare model path without these discovery, view, freshness and reconciliation obligations fails this item. Representation Router may render selected views but does not supply planning authority or prove executed behavior.

System model: exempt -- documentation and example-code repo with no stored state, no service and no user-facing view, so no source-linked views apply

Documentation entry point: `wiki/index.md`. Freshness and reconciliation: a new wiki Map line and README "What is here" line for practice3 land in the same commit; tests/test_wiki_map.py fails if a wiki link does not resolve.

## Capability reuse

> **CORE-CAPABILITY-REUSE** (blocking): The plan answers capability reuse against the capability catalogue in agentic-capability-architecture-canonical, which has two files: `reuse_candidates.yml`, whose entries under `candidates:` are cross-project capabilities with their selected off-the-shelf implementations, each named by its `id` (for example `documents_to_text`) and marked candidate or promoted; and `capability_registry.yml`, whose entries under `capabilities:` are the packages that repository holds, each named by its key (for example `approvals`) with the capability ids it `provides` (for example `approval.resolve`). An entry from either file counts. The plan names each catalogue capability the work reuses, by its id, key or provided id; names each new capability the work adds together with its first consumer (the project, command or workflow in this plan that uses it); and, where no entry covers what the work needs, states `No catalogue entry fits, because <reason>`, the reason saying what the work needs that no entry provides. A plan may give more than one of these answers. A plan fails this item if it gives none of them, if it claims reuse without naming the catalogue entry or id reused (reusing code or a contract that is not a catalogue entry does not count), if it adds a capability without naming its first consumer, or if it says no entry fits without a reason.

- No catalogue entry fits, because the need is a self-contained practice grader and synthetic dataset that run offline in a cloned folder with only langchain, langgraph and scipy installed; catalogue capabilities need workspace services a candidate does not have.
- Catalogue capabilities reused: none, for the reason above.
- New capabilities added: none to the catalogue. `practice3/grade.py` is repo-local; its first consumer is tests/test_practice3.py and a candidate's practice run.

## Authority and non-goals

> **CORE-AUTHORITY-NONGOALS** (blocking): The plan states who holds authority over the work and what it explicitly will not do (non-goals).

**Authority:** the owner, through the coordinating session's task of 2026-10-13 ("make sure the practice examples test what a data-science agentic take-home will test"); commit on a branch, do not push.

**Non-goals:** no push; no edit to MEMORY_SHEET.md, method/, templates/, check.sh, check_docs.py, KIT.md or the existing reference solutions; no live-model grading; no encryption of hidden cases; no dry run by a fresh agent in this lane; pandas not added (the csv module and scipy suffice).

## Irreversible actions and spend

> **CORE-IRREVERSIBLE-SPEND** (blocking): For each irreversible action or spend the plan proposes, it names the boundary, who must authorize it, and how it is contained.

None. No push, no API key, no model spend (the grader and the evaluation default to scripted or stand-in models). Installing scipy into the existing .venv is reversible (`uv pip uninstall scipy`) and passed the storage gate (1 GiB, exit 0).

## Uncertainties

> **CORE-UNCERTAINTIES** (blocking): The plan lists its material uncertainties, and each one has an owner or the evidence that would resolve it.

- **Can a person finish it in the 4-hour real-time budget?** Six tools, one approval step and an evaluation file is more than practice2. Evidence that resolves it: a timed human run (owner: the kit owner, when rehearsing); this lane gives an estimate only.
- **Is the spec exact enough for the hidden cases?** Evidence: the independent recomputation of each hidden expectation from the rule text alone; any rule it had to guess at is tightened in PROBLEM.md. Owner: this session.
- **Will the planning-package names change again?** Owner: the session rewriting the package; PROBLEM.md names only the three files and points at the templates.

## Activation facts

> **CORE-ACTIVATION-FACTS** (blocking): No activation fact that the plan triggers is declared false. Declaring a fact true when the plan does not strictly need it is acceptable, because it only adds checks; judge only facts declared false. empirical_comparison_proposed is triggered when the plan proposes an A/B test, benchmark, bake-off, or other experiment comparing alternative designs, models, or candidates to choose among them; checking the built result against an expected outcome (an acceptance test, fixture replay, or regression check) is verification and does not trigger it. shared_mechanism is triggered by a new shared mechanism, contract, or algorithm; llm_central by behavior that centrally depends on LLM calls; irreversible_or_spend_action by a proposed irreversible action or spend. claims_external_standard is triggered when the plan claims, or presents its work as, following, implementing or conforming to a standard, schema or contract owned outside the repository being changed (for example a model presented as DM2, or output said to match a published schema); conforming to the repository's own contracts does not trigger it; aes_governed_target when the target repository is governed by an AES target (`.aes/target.yaml`), or the plan creates one (for example by running `aes init`). These two facts are optional: an undeclared one is shown as false and is judged like a declared false.

- empirical_comparison_proposed: false. Verification against expected outcomes only.
- shared_mechanism: true. Declared true to be safe: candidates rely on the grader's contract; answered under Prior art and ownership.
- llm_central: true. The graded artifact is an LLM agent (run with a scripted model); see LLM call boundary.
- irreversible_or_spend_action: false. No push, no spend (see above).
- aes_governed_target: false. `.aes/` holds only `commit_rule.yaml`.
- claims_external_standard: not declared (false).

## Prior art and ownership

> **OV-PRIOR-ART-DISPOSITION** (blocking): Existing ownership, internal lineage, and relevant external prior art were searched, and each candidate found is dispositioned as reuse, extend, compose, supersede, or bounded exception.

> **OV-PRIOR-ART-PARALLEL-CHECK** (advisory): The plan names one concrete structural check or consumer-path observation that would detect a silent parallel implementation of the same concern.

External prior art searched (2026-10-13, from what this repo's earlier plans already searched plus the libraries named here): hosted-assessment hidden test suites, scipy's statistical tests, scikit-learn's classification metrics, and the planted-signal approach to synthetic test data. Each is dispositioned below.

- **practice/grade.py and practice2/grade.py** (this repo's graders): **reuse** and **extend**. practice3/grade.py is an **extend** of practice2/grade.py (same case runner and hidden report, plus metric cases); it imports the ScriptedModel and script_messages from practice/grade.py by path, and copies practice2's hidden-case report and `--encode` convention.
- **scipy.stats.ttest_ind(equal_var=False)**: **reuse** for the Welch test (the standard implementation); **sklearn.metrics.precision_recall_fscore_support / confusion_matrix**: **reuse its conventions** (rows are gold, columns predicted; zero_division=0) but not the package, so candidates write the metric functions the grader checks.
- **External prior art (hidden test suites in hosted coding assessments):** reuse the convention practice2 adopted, a few shown examples, hidden failures by name only.
- **Synthetic data with planted signals**: **reuse** of the standard approach, which is the usual way to test anomaly and coordination detectors with known answers; the generator is seeded and committed so the answers are reproducible.

**Existing ownership and internal lineage searched:** this repo's practice/, practice2/, tests/ and docs/plans/ (no data-analysis practice exists). Dispositions: practice2 is **extend** (a third problem beside it, same grader shape); practice/grade.py's scripted model is **reuse**.

**Parallel-implementation check:** `grep -rn "class ScriptedModel" --include=*.py .` must show only practice/grade.py; output in check.txt.

## LLM call boundary

> **OV-LLM-CALL-BOUNDARY** (blocking): The plan describes the model call graph, the structured result boundary each call returns, and how calls are traced.

> **OV-LLM-AUTHORITY-PROMOTION** (blocking): The plan names the provider and spend authority for model calls and one authentic-run condition that must hold before the behavior is promoted.

**Call graph.** The grader makes no model calls: a scripted model replays fixed AI messages for the agent cases; the metric cases call plain functions. The reference evaluate.py classifies each labelled post with one structured call (`with_structured_output(Topic)`); by default the model is a keyword stand-in replayed through the same scripted-model class, and a real model is used only when an environment variable names one.

**Structured result boundary.** The agent's final answer is a validated `Finding` read from `structured_response`; each classifier call returns a validated `Topic`.

**Tracing.** The grader prints per case; the reference agent logs each step through the graph's messages; check.txt keeps the full test output.

**Provider and spend authority:** none used in this lane (no API key). A real-model evaluation is optional for the candidate, on their own key. **Authentic-run condition before promotion:** the kit may claim the evaluation exercises a real model only after one traced run with a real model; this lane does not make that claim.

## Vertical and reset

> **OV-PROTO-VERTICAL-RESET** (blocking): The plan names the minimal vertical result, the reset boundary, and the non-goals, without adding coordinated-work ceremony.

**Minimal vertical:** make_data.py and its output; reference solution and evaluate.py; grade.py passing the reference on shown and hidden cases; then broken copies, leak test, removal test; then PROBLEM.md, README and wiki lines.

**Files (the whole lane):** NEW practice3/ (PROBLEM.md, make_data.py, posts.csv, labels.csv, examples.json, hidden.b64, grade.py, reference/solution.py, reference/evaluate.py, reference/hidden_cases.json), tests/test_practice3.py, docs/plans/kit-v3-practice3.* (plan records, check.txt); EDIT README.md (one new line), wiki/index.md (one new line), practice/PROBLEM.md and practice2/PROBLEM.md (removal one-liner only), pyproject.toml and uv.lock (scipy).

**Reset boundary:** branch practice3-data-analysis off origin/main d40bf1c in this session's worktree; abandoning it means deleting the branch, nothing pushed. **Non-goals:** as under Authority and non-goals. **No coordinated-work ceremony is added:** one writer, one branch.
