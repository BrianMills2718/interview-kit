---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v3-practice2
status: proposed
method_conformance_receipt: docs/plans/kit-v3-practice2.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "The kit has a second timed practice problem whose grading cases are hidden from the candidate: a failing hidden case shows its name and the kind of check that failed, never the expected value, and the reference solution passes every case."
  canonical_example: "A candidate's solution that forgets rule 2 (refuse 10.x addresses) runs `python kit/practice2/grade.py solution.py` and sees `FAIL hidden: internal-ip-refused` / `failed check: approval pause, tool output text` and exit 1, with no expected tool text printed; the reference prints `== grade: 13 passed, 0 failed of 13 cases (10 hidden)` and exits 0."
  forbidden_substitutes: "the reference passing alone (a grader that passes everything also passes it); a leak check never shown to fail on a leaking grader; hidden cases that test rules PROBLEM.md does not state; a dry run summarized without reading its first grade output"
  boundaries: "files listed under Vertical and reset, in worktree ~/code/interview-kit-c5d on branch c5-practice2; code-c7's files untouched; one dry-run subagent in ~/code/.scratch/practice2-dryrun; one irreversible action: the push of main after checks"
  done_when: "tests/test_practice2.py passes (reference passes all 13 cases; six broken copies each fail exactly the intended hidden case; a deliberately leaking report fails the leak check, recorded in check.txt); the dry run's first grade output and its hidden failures are read and recorded in check.txt and the wiki Evidence; full pytest suite exit 0; privacy scan 0 hits"
  do_not_gate_on: "the owner's own timed practice run; a human's pace; the docs/ package line beyond stating it (check.sh owns that check)"
---

# Kit v3: a second practice problem with hidden test cases

Each section below answers the checklist items quoted in it.

## Actor and result

> **CORE-ACTOR-RESULT-EXAMPLE** (blocking): The plan names the actor it serves, the desired result, and one stable, concrete, user-visible example of that result.

**Actor:** a candidate rehearsing for a timed agentic-AI take-home with only an IDE's built-in AI chat. **Result:** a second rehearsal in which, as in a real take-home, most grading cases are hidden, so they must turn a stated spec into their own tests rather than fit visible cases. **Example:** their solution forgets to refuse internal addresses; `grade.py` prints `FAIL hidden: internal-ip-refused` and `failed check: approval pause, tool output text`, no expected text; they find rule 2 in PROBLEM.md, write a test for it, fix it, and the grade reaches `12 passed`.

## Requirements

> **CORE-REQUIREMENTS-TRACED** (blocking): The plan lists its requirements: what was asked for, and what the delivered work's own claims imply. A claim here is what the work is presented as being or doing to its users, for example work presented as following a standard, schema or contract (which implies conformance to it) or an output labelled as showing something (which implies it shows it correctly); the plan's own format and front matter are not such claims, and the details a check examines (what a trace must show) belong to that check rather than being separate requirements. Each requirement names the check that verifies it (a test, script, gate step, or named review of a run) and its status: passing, failing, planned and not yet run, or deferred with a stated reason; deferred requirements are carried onto every release or completion record the plan names. A plan fails this item if it has no requirements list, if any requirement has neither a check nor an explicit deferral with its reason, or if the plan presents the work as following a named standard, schema or contract, or as having another property its users rely on, that its requirements list omits.

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | A second practice problem in a new domain, with a stated spec, shown examples and hidden cases | asked: the owner 2026-10-11 "i approve" (a second practice problem whose test cases are hidden from the candidate) | practice2/PROBLEM.md, examples.json, hidden.b64; tests/test_practice2.py::test_reference_passes_every_case | passing: see check.txt |
| R2 | The grader fails solutions that break a stated rule, each on the intended hidden case | the work's own claim (it grades) | test_grader_fails_a_broken_solution, six broken copies | passing: see check.txt |
| R3 | Hidden failures never print expected values | the work's own claim ("hidden") | test_hidden_failures_print_no_expected_values, plus the same test run against a leaking report (must fail) | passing: see check.txt |
| R4 | Every hidden case tests a rule PROBLEM.md states | the work's own claim (a fair hidden suite) | the rule-to-case table under Success and disproof, checked by reading each case | passing: see check.txt |
| R5 | The removal command deletes only the reference, and the grader still runs without it | the work's own claim (step 2) | test_problem_removal_command_deletes_the_reference | passing: see check.txt |
| R6 | PROBLEM.md asks for the docs/ planning package | session code-c7, 2026-10-11 message | "Graded on" paragraph; check.sh enforces it | passing: see check.txt |
| R7 | One dry run by a fresh agent, first grade output kept, hidden failures read | the work's claim that the hidden cases catch a first attempt | check.txt sections 5-7 | passing as a check (two runs, traces read); the claim is not supported: both runs passed every hidden case first time, so the kit says so |
| R8 | No secret or private data | workspace rule on public content | gitleaks and the name grep in check.txt | passing: see check.txt |

Claims implied: "hidden" (R3), "grades" (R2), "fair" (R4). No external standard is claimed.

## Success and disproof

> **CORE-SUCCESS-DISPROOF** (blocking): The plan defines the evidence that would show success and a concrete condition that would disprove the approach. Each success measure is the property the plan claims, or a check that directly tests that property, not a stand-in for it: a count, a picture, a readability judgment, or the pipeline agreeing with itself (hashes, labels, byte equality) does not show correctness or conformance it does not test. A plan fails this item if it has no disproof condition, or if a success measure is such a stand-in for the claimed property and the plan names no direct check of that property.

> **CORE-TRACE-REVIEW** (blocking): Every success or acceptance criterion in the plan is judged from the full trace of a run, not only its final outcome: it names the run whose full trace is examined (for example the session, its tool and LLM calls, commits, check output, or messages), where that trace lives, and what must be seen in that trace beyond the final outcome. A criterion that names only an outcome, such as tests passing, a PR merged, a test fixture reproducing the journey, or a status reading succeeded, fails this item. A criterion for which no run exists, such as a pure document edit, passes only when the plan states that exemption and its reason explicitly.

**Success evidence:** the reference passes all 13 cases; each of six single-rule breakages fails exactly its hidden case (membership, not count); a report changed to print details fails the leak test with the leaked strings named.

**Rule-to-case table (R4):** block-declined-by-reviewer = block rule 5 "Otherwise"; internal-ip-refused = rule 2; invalid-ip-rejected = rule 1; second-block-is-a-no-op = rule 3; host-names-ignore-case = get_host and search_logs "case does not matter", "newest first, at most 3"; search-limit-enforced = "at most 4 times per agent"; high-without-evidence-is-retried = "High or critical needs at least one evidence id"; unknown-severity-is-retried = severity values and "goes back to the model to retry"; parallel-tool-calls = "sometimes several in one turn"; two-pauses-in-one-turn = "Several blocks asked for in one model turn may pause together".

**Disproof:** a broken copy that passes, a hidden case that fails for a rule not on the page, or the dry-run agent finding PROBLEM.md contradicting the grader.

**Runs judged and their traces:** (1) `uv run pytest tests/test_practice2.py -v` and the leak-mutation run, output in docs/plans/kit-v3-practice2.check.txt, which must show each parametrized case and the leaked-string assertion; (2) the dry-run subagent session (its transcript under the session's task output; first grade output saved verbatim in check.txt), which must show the first grade output, each hidden failure, and how the agent traced it to a rule.

## When a run fails or surprises us

> **CORE-TRACE-DEBUGGING** (blocking): The plan includes a separate When a run fails or surprises us procedure, distinct from anticipated failure modes. It requires preserving the failed run and its trace id; reading full inputs, prompts, each tool call arguments/results, intermediate stages and final output before selecting a fix; citing the observed divergence; classifying evidence absent, evidence returned but unused or contradicted, invalid expectation, or unresolved; and linking a targeted repair to a new traced verification run while retaining the original failure. Unresolved diagnoses permit investigation but cannot authorize a causal repair. Review completeness is separate from the run verdict.

Keep the failing run and its trace id before changing anything: the pytest node id with its full output, or the dry-run session's task id with its first_grade.txt, both copied into check.txt. Before choosing a fix, read the full inputs and prompts (the case's customer message and the agent's system prompt; for the dry run, its instructions), each tool call's arguments and results in order, every intermediate stage (each scripted AI message, each interrupt and resume), and the final output (the verdict and the blocked list). Classify: evidence absent (the solution never produced the tool text), returned but unused (tool text right, verdict or state wrong), invalid expectation (the case or the spec is wrong), or unresolved (read more, no fix). A fix to a case or to PROBLEM.md re-encodes hidden.b64 and is linked to a new traced verification run (the full test file again, output saved beside the original failure, which stays in check.txt). Whether the trace review was complete is recorded separately from the run's pass or fail verdict. Example already met while building: search-limit-enforced first failed on the reference; the case's absent-check was an invalid expectation (it forbade text a correct run produces); the case was rewritten to require the exact 3-line sequence.

## System model

> **CORE-SYSTEM-MODEL** (blocking): The plan links the project's system model (a path such as docs/model/ODD.md) or carries the one-line exemption `System model: exempt -- <reason>`, which fits only a project with no stored state and no user-facing view. Unless exempt, the plan names each system-model element (entity, process, record or event, or view) that the work adds, changes, or relies on, and its trace review names, for each such element, what the examined run must show of it (for example an event of that record type with its id, or the view displaying that entity). A plan with neither a model link nor the exemption line fails this item, as does one that lists model elements without saying what the examined run must show of each, or one that names no element without stating that the work touches none and why. For a maintained repository, the plan also cites the documentation entry point from which the model is reachable; a shared model explicitly identifies this repository's scope. It names applicable source-linked views, explains material omissions without imposing a fixed diagram quota, names concrete model freshness or drift checks, and states how the model, view coverage and verification evidence will be reconciled in the same change (or gives a concrete reason each needs no update). A bare model path without these discovery, view, freshness and reconciliation obligations fails this item. Representation Router may render selected views but does not supply planning authority or prove executed behavior.

System model: exempt -- documentation and example-code repo with no stored state, no service and no user-facing view, so no source-linked views apply

Documentation entry point: `wiki/index.md`. Freshness and reconciliation: the wiki Map row and Evidence entry for practice2 are updated in the same commit; the commit rule's wiki-reachability check refuses unreachable new markdown.

## Capability reuse

> **CORE-CAPABILITY-REUSE** (blocking): The plan answers capability reuse against the capability catalogue in agentic-capability-architecture-canonical, which has two files: `reuse_candidates.yml`, whose entries under `candidates:` are cross-project capabilities with their selected off-the-shelf implementations, each named by its `id` (for example `documents_to_text`) and marked candidate or promoted; and `capability_registry.yml`, whose entries under `capabilities:` are the packages that repository holds, each named by its key (for example `approvals`) with the capability ids it `provides` (for example `approval.resolve`). An entry from either file counts. The plan names each catalogue capability the work reuses, by its id, key or provided id; names each new capability the work adds together with its first consumer (the project, command or workflow in this plan that uses it); and, where no entry covers what the work needs, states `No catalogue entry fits, because <reason>`, the reason saying what the work needs that no entry provides. A plan may give more than one of these answers. A plan fails this item if it gives none of them, if it claims reuse without naming the catalogue entry or id reused (reusing code or a contract that is not a catalogue entry does not count), if it adds a capability without naming its first consumer, or if it says no entry fits without a reason.

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because the need is a self-contained practice grader that runs offline in a hosted IDE with only langchain and langgraph installed; catalogue capabilities need workspace services a candidate does not have.
- Catalogue capabilities reused: none, for the reason above.
- New capabilities added: none to the catalogue. `practice2/grade.py` is repo-local; its first consumer is this plan's dry run.

## Authority and non-goals

> **CORE-AUTHORITY-NONGOALS** (blocking): The plan states who holds authority over the work and what it explicitly will not do (non-goals).

**Authority:** the owner, who approved this on 2026-10-11 ("i approve"). Session code-c7 confirmed by message the same day that practice2/ is this lane's and asked for the docs/ package line.

**Non-goals:** no change to practice/ or any of code-c7's files; no new dependency; no encryption of the hidden cases (they are out of sight, not secret, and the page says so); no live-model grading.

## Irreversible actions and spend

> **CORE-IRREVERSIBLE-SPEND** (blocking): For each irreversible action or spend the plan proposes, it names the boundary, who must authorize it, and how it is contained.

- **Spend:** one dry-run subagent session on the session's own model allowance; no API key spend. Contained by: one run, 60-minute cap in its instructions.
- **Action:** `git push origin main` to the public repo. Authorized by the owner's standing rule on public content (2026-10-07) and this approval. Contained by: push only after gitleaks and the name grep show 0 hits; revert at once if anything private is found.

## Uncertainties

> **CORE-UNCERTAINTIES** (blocking): The plan lists its material uncertainties, and each one has an owner or the evidence that would resolve it.

- **Is it hard enough to rehearse?** Two agent dry runs of practice/ took 12 and 3.5 minutes. Evidence that resolves it: the dry run's first grade (how many hidden cases fail before the agent sees any). Owner: this session.
- **Is the spec complete enough for the hidden cases?** Evidence: the dry-run agent's list of ambiguities; each is fixed in PROBLEM.md or recorded.

## Activation facts

> **CORE-ACTIVATION-FACTS** (blocking): No activation fact that the plan triggers is declared false. Declaring a fact true when the plan does not strictly need it is acceptable, because it only adds checks; judge only facts declared false. empirical_comparison_proposed is triggered when the plan proposes an A/B test, benchmark, bake-off, or other experiment comparing alternative designs, models, or candidates to choose among them; checking the built result against an expected outcome (an acceptance test, fixture replay, or regression check) is verification and does not trigger it. shared_mechanism is triggered by a new shared mechanism, contract, or algorithm; llm_central by behavior that centrally depends on LLM calls; irreversible_or_spend_action by a proposed irreversible action or spend. claims_external_standard is triggered when the plan claims, or presents its work as, following, implementing or conforming to a standard, schema or contract owned outside the repository being changed (for example a model presented as DM2, or output said to match a published schema); conforming to the repository's own contracts does not trigger it; aes_governed_target when the target repository is governed by an AES target (`.aes/target.yaml`), or the plan creates one (for example by running `aes init`). These two facts are optional: an undeclared one is shown as false and is judged like a declared false.

- empirical_comparison_proposed: false. One verification dry run, no comparison among alternatives.
- shared_mechanism: true. Declared true to be safe: candidates rely on the grader's contract; answered under Prior art and ownership.
- llm_central: true. The dry run is an agent session; see LLM call boundary.
- irreversible_or_spend_action: true. The public push and the dry-run session; see Irreversible actions and spend.
- aes_governed_target: false. `.aes/` holds only `commit_rule.yaml`.
- claims_external_standard: not declared (false).

## Prior art and ownership

- **practice/grade.py** (this repo's first grader): **reuse**, practice2/grade.py imports its ScriptedModel and script_messages by path instead of copying them.
- **External prior art searched (2026-10-11):** hidden test suites in hosted coding assessments (HackerRank's and CoderPad's hidden test cases, LeetCode and Codeforces judges): **reuse** their convention as is, show a few examples, report hidden failures by name only. Tools that grade with encrypted or server-side tests: **bounded exception**, not used, because the kit must grade offline in a cloned folder with no server.
- **langchain_core GenericFakeChatModel**: **reuse** through practice/grade.py.

**Existing ownership and internal lineage searched:** this repo's practice/, tests/ and docs/plans/ (no hidden-case grader exists); the wiki's "In progress and next" item 1 asked for exactly this; code-c7 confirmed no overlapping lane. Dispositions: the practice/ problem and grader are **extend** (a second problem beside it, its scripted model imported); the wiki's next-additions item is **extend** (this work carries it out and the item is removed).

**Parallel-implementation check:** `grep -rn "class ScriptedModel" --include=*.py .` must show only practice/grade.py; output in check.txt.

## LLM call boundary

> **OV-LLM-CALL-BOUNDARY** (blocking): The plan describes the model call graph, the structured result boundary each call returns, and how calls are traced.

> **OV-LLM-AUTHORITY-PROMOTION** (blocking): The plan names the provider and spend authority for model calls and one authentic-run condition that must hold before the behavior is promoted.

**Call graph.** The grader makes no model calls: a scripted model replays fixed AI messages. The only model calls are the dry-run subagent's own session, which reads files and runs commands in its scratch folder.

**Structured result boundary.** The graded solution's final answer is a validated `Verdict` (pydantic) read from `structured_response`; the dry run's result is its report plus `first_grade.txt` on disk.

**Tracing.** The subagent's full transcript is kept by the session; its first grade output is copied verbatim into check.txt.

**Provider and spend authority:** provider Anthropic, through this Claude Code session's own subscription (the subagent runs on the session's model); spend authority is the owner's 2026-10-11 approval of this work; no API key is used. **Authentic-run condition before promotion:** the wiki may say the hidden cases catch a first attempt only if the dry run's first_grade.txt shows at least one hidden failure that the agent then traced to a stated rule. Result: neither dry run showed one, so the wiki does not say it.

## Vertical and reset

> **OV-PROTO-VERTICAL-RESET** (blocking): The plan names the minimal vertical result, the reset boundary, and the non-goals, without adding coordinated-work ceremony.

**Minimal vertical:** data, reference and grader passing the reference; then broken copies and the leak test; then PROBLEM.md, the dry run, notes.

**Files (the whole lane):** NEW practice2/ (PROBLEM.md, data.json, examples.json, hidden.b64, grade.py, reference/solution.py, reference/hidden_cases.json), tests/test_practice2.py, docs/plans/kit-v3-practice2.* (plan records, check.txt); EDIT README.md (one row, test count), wiki/index.md (Map row, Evidence, next list), KIT.md (generated, only after pulling).

**Reset boundary:** branch c5-practice2 in worktree ~/code/interview-kit-c5d off origin/main 90caf9f; abandoning it means deleting the branch, nothing pushed. **Non-goals:** no change to practice/ or code-c7's files; no new dependency; no encryption of hidden cases; no live-model grading. **No coordinated-work ceremony is added:** one writer, one branch; coordination was one message exchange with code-c7.
