---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v3-additions-c5
status: proposed
method_conformance_receipt: docs/plans/kit-v3-additions-c5.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "A candidate who clones the kit gets notes on how AI use is graded, a debugging method, a raw-API agent loop, retries/limits/cost/guardrails, document search with embeddings, a workflow-vs-agent decision table and a pre-submit requirement check, each code pattern tested offline."
  canonical_example: "In a fresh clone, `uv run pytest -v` runs tests/test_raw_api_agent.py, tests/test_rag_embeddings.py and tests/test_hardening.py and they pass; `bash build_kit.sh` writes KIT.md of at most 600 lines that contains the AI-use red flags, the decision table and the pre-submit check but not the three standalone skills; README lists every new file."
  forbidden_substitutes: "notes without a test for their code snippets; tests that pass with the pattern removed; a KIT.md under 600 lines achieved by dropping existing content; copied third-party text beyond what its license allows"
  boundaries: "only the files named under Vertical and reset, in worktree ~/code/interview-kit-c5b on branch c5-additions; AGENTS.md, method/, PLAN.template.md, agents/planner.md and check.sh belong to session code-c7 and are not touched; one irreversible action: the push of main to the public repo after checks pass"
  done_when: "docs/plans/kit-v3-additions-c5.check.txt, the saved output of the success check run once at the commit to be pushed, shows: every new test by name PASSED and the full suite passed with exit 0; mutation results showing each new test fails when its pattern is broken; KIT.md line count <= 600 and grep results for the included and excluded sections; privacy scan with 0 hits"
  do_not_gate_on: "a live-model run (none is claimed); code-c7's method/ lane; a human dry run in the hosted IDE"
---

# Kit v3: additions from skill and pattern research

Each section below answers the checklist items quoted in it; the gate judges only that
section's text. Replace every `TODO(answer ...)` line before running `cli.py check`. Quote
values in the front matter: an unquoted ` #` starts a YAML comment and cuts the value.

## Actor and result

> **CORE-ACTOR-RESULT-EXAMPLE** (blocking): The plan names the actor it serves, the desired result, and one stable, concrete, user-visible example of that result.

**Actor:** a candidate in a timed agentic-AI take-home in a hosted browser IDE, where only the IDE's built-in AI chat may be used; they read the kit's markdown and copy its examples. **Result:** the kit covers what research on 2026-10-11 found missing: how the platform marks down AI use, a debugging method, an agent loop on the raw provider APIs, production hardening (retries, call limits, cost, guardrails), document search with embeddings, a decision table for workflow vs agent, and a requirement-by-requirement check before submitting. **Example:** the candidate is asked to "build an agent with raw API calls that answers from these documents"; they open `skills/raw-api-agent/SKILL.md` and `examples/raw_api_agent.py`, copy the loop, swap in `examples/rag_embeddings.py`'s retriever as a tool, and the copied code's tests run green offline in their project.

## Requirements

> **CORE-REQUIREMENTS-TRACED** (blocking): The plan lists its requirements: what was asked for, and what the delivered work's own claims imply. A claim here is what the work is presented as being or doing to its users, for example work presented as following a standard, schema or contract (which implies conformance to it) or an output labelled as showing something (which implies it shows it correctly); the plan's own format and front matter are not such claims, and the details a check examines (what a trace must show) belong to that check rather than being separate requirements. Each requirement names the check that verifies it (a test, script, gate step, or named review of a run) and its status: passing, failing, planned and not yet run, or deferred with a stated reason; deferred requirements are carried onto every release or completion record the plan names. A plan fails this item if it has no requirements list, if any requirement has neither a check nor an explicit deferral with its reason, or if the plan presents the work as following a named standard, schema or contract, or as having another property its users rely on, that its requirements list omits.

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | AI-use red flags and "treat AI answers as review" in using-ide-ai-chat | asked: the owner 2026-10-11 "i approve" (to: the 8-item shortlist, items 1 and 3) | grep in check.txt (section KIT) | passing: see check.txt |
| R2 | debug skill (root cause before fix) | same approval, item 2 | file exists, linked from README and wiki; grep in check.txt | passing: see check.txt |
| R3 | raw-API agent loop (Anthropic and OpenAI shapes) with offline test | same approval, item 4 | tests/test_raw_api_agent.py; mutation M1 | passing: see check.txt |
| R4 | retries, call limits, cost tracking, guardrails, with offline test | same approval, item 5 | tests/test_hardening.py; mutation M2 | passing: see check.txt |
| R5 | workflow / single call / agent decision table in the plan skill | same approval, item 6 | grep in check.txt | passing: see check.txt |
| R6 | document search with embeddings, offline test | same approval, item 7 | tests/test_rag_embeddings.py; mutation M3 | passing: see check.txt |
| R7 | pre-submit requirement-by-requirement check in the reviewer role | same approval, item 8 | grep in check.txt | passing: see check.txt |
| R8 | KIT.md stays at most 600 lines; standalone skills (debug, raw-api-agent, production-hardening) excluded from it | the split the owner approved: short notes in KIT.md, the rest as separate files | `wc -l KIT.md` and greps in check.txt | passing: see check.txt |
| R9 | public repo: no private data, no employer names; third-party text used within its license (superpowers and awesome-copilot MIT, with attribution; interview-practice pages and 12-factor-agents paraphrased only) | workspace rule on public content; kit wiki decision 5 | gitleaks + grep for emails/phones and the names of employers in check.txt; source line in each adapted file | passing: see check.txt |

Requirements the change's own claims imply: each code snippet is presented as tested, which R3, R4 and R6 check; the work claims conformance to no external standard.

## Success and disproof

> **CORE-SUCCESS-DISPROOF** (blocking): The plan defines the evidence that would show success and a concrete condition that would disprove the approach. Each success measure is the property the plan claims, or a check that directly tests that property, not a stand-in for it: a count, a picture, a readability judgment, or the pipeline agreeing with itself (hashes, labels, byte equality) does not show correctness or conformance it does not test. A plan fails this item if it has no disproof condition, or if a success measure is such a stand-in for the claimed property and the plan names no direct check of that property.

> **CORE-TRACE-REVIEW** (blocking): Every success or acceptance criterion in the plan is judged from the full trace of a run, not only its final outcome: it names the run whose full trace is examined (for example the session, its tool and LLM calls, commits, check output, or messages), where that trace lives, and what must be seen in that trace beyond the final outcome. A criterion that names only an outcome, such as tests passing, a PR merged, a test fixture reproducing the journey, or a status reading succeeded, fails this item. A criterion for which no run exists, such as a pure document edit, passes only when the plan states that exemption and its reason explicitly.

**Success evidence:** check.txt shows the three new test files' tests PASSED by name and the full suite passed with exit 0; R1, R2, R5, R7 greps find the section in the right file; `wc -l KIT.md` <= 600 and KIT.md contains the R1/R5/R7 headings but not the standalone skills' headings; privacy scan 0 hits.

**Direct correctness check (not a stand-in):** the claimed property of each code pattern is that it behaves as the note says, so each test asserts behavior on a case where a wrong implementation gives a different answer: the raw loop must call the tool the stub model asks for with its exact arguments and feed the result back (an implementation that skips the tool or drops the result fails); the retriever must return the matching document first, not the other (a non-searching store fails); the call limit must stop a model that asks for tools forever (a missing limit loops and fails). The mutation check (mutation.txt section of check.txt) breaks each pattern on purpose and shows its test failing; that is the direct evidence the tests test the property. Test counts are a summary on top of that, not the proof.

**Disproof:** any new test passes with its pattern broken; KIT.md exceeds 600 lines without dropping existing content; a snippet in a skill note does not match the tested example; the privacy scan hits.

**Run judged:** the success check, run once at the commit to be pushed. **Where its trace lives:** its complete output, with each command and exit status, saved as docs/plans/kit-v3-additions-c5.check.txt and committed. **What must be seen beyond the final result:** each new test appears by name with PASSED and none is skipped; each mutation appears with the test that failed and its assertion message; the KIT.md greps show which headings are present and absent; the privacy scan prints its patterns and 0 hits; the exit status of pytest matches its summary line. No model runs live, so the offline test output with the scripted stub replies (in the test files) is the whole trace.

## When a run fails or surprises us

> **CORE-TRACE-DEBUGGING** (blocking): The plan includes a separate When a run fails or surprises us procedure, distinct from anticipated failure modes. It requires preserving the failed run and its trace id; reading full inputs, prompts, each tool call arguments/results, intermediate stages and final output before selecting a fix; citing the observed divergence; classifying evidence absent, evidence returned but unused or contradicted, invalid expectation, or unresolved; and linking a targeted repair to a new traced verification run while retaining the original failure. Unresolved diagnoses permit investigation but cannot authorize a causal repair. Review completeness is separate from the run verdict.

Keep the failing run: its trace id is the commit hash plus the pytest node id; save its full output, assertion diffs included, in the session notes and read it in full before changing code: the scripted stub replies (the only model inputs offline), the tool call arguments and results, the messages list the loop built, and the final answer. Name where it diverged and classify it: evidence absent (a value never came back), returned but unused or contradicted (e.g. a tool result not appended), invalid expectation (the test is wrong, e.g. an API shape changed: check the installed package source), or unresolved. Unresolved allows more reading but not a fix on a guess. A fix is linked to a new run of the same node id at the fixed commit, saved beside the original failure, which stays recorded.

This procedure is separate from the anticipated failure modes listed under Uncertainties (missing numpy, API shape drift in the provider SDKs, middleware signature changes); those are known risks with their own checks, while this applies to any failure or surprise, including ones not anticipated.

## System model

> **CORE-SYSTEM-MODEL** (blocking): The plan links the project's system model (a path such as docs/model/ODD.md) or carries the one-line exemption `System model: exempt -- <reason>`, which fits only a project with no stored state and no user-facing view. Unless exempt, the plan names each system-model element (entity, process, record or event, or view) that the work adds, changes, or relies on, and its trace review names, for each such element, what the examined run must show of it (for example an event of that record type with its id, or the view displaying that entity). A plan with neither a model link nor the exemption line fails this item, as does one that lists model elements without saying what the examined run must show of each, or one that names no element without stating that the work touches none and why. For a maintained repository, the plan also cites the documentation entry point from which the model is reachable; a shared model explicitly identifies this repository's scope. It names applicable source-linked views, explains material omissions without imposing a fixed diagram quota, names concrete model freshness or drift checks, and states how the model, view coverage and verification evidence will be reconciled in the same change (or gives a concrete reason each needs no update). A bare model path without these discovery, view, freshness and reconciliation obligations fails this item. Representation Router may render selected views but does not supply planning authority or prove executed behavior.

System model: exempt -- documentation and example-code repo with no stored state, no service and no user-facing view, so no source-linked views apply

Documentation entry point: `wiki/index.md` (linked from `README.md`, "Working on this repo"); it maps every file and is where a model would be linked. Freshness and reconciliation: the file map is the wiki's Map table and the README table, both updated in the same commit with the new files; the drift check is the commit rule's wiki-reachability check, which refuses a commit whose new markdown is not reachable from `wiki/index.md` within two links. Session code-c7's lane is adding `docs/model/`; if it lands first, this change rebases onto it and touches no model file.

## Capability reuse

> **CORE-CAPABILITY-REUSE** (blocking): The plan answers capability reuse against the capability catalogue in agentic-capability-architecture-canonical, which has two files: `reuse_candidates.yml`, whose entries under `candidates:` are cross-project capabilities with their selected off-the-shelf implementations, each named by its `id` (for example `documents_to_text`) and marked candidate or promoted; and `capability_registry.yml`, whose entries under `capabilities:` are the packages that repository holds, each named by its key (for example `approvals`) with the capability ids it `provides` (for example `approval.resolve`). An entry from either file counts. The plan names each catalogue capability the work reuses, by its id, key or provided id; names each new capability the work adds together with its first consumer (the project, command or workflow in this plan that uses it); and, where no entry covers what the work needs, states `No catalogue entry fits, because <reason>`, the reason saying what the work needs that no entry provides. A plan may give more than one of these answers. A plan fails this item if it gives none of them, if it claims reuse without naming the catalogue entry or id reused (reusing code or a contract that is not a catalogue entry does not count), if it adds a capability without naming its first consumer, or if it says no entry fits without a reason.

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because the need is notes and example code readable by a third-party hosted IDE's assistant with no access to the workspace. The code reuses off-the-shelf libraries only: the `anthropic`/`openai` message shapes (stubbed), LangChain's `InMemoryVectorStore` and `DeterministicFakeEmbedding`, `langchain.agents.middleware` (`ModelRetryMiddleware`, `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware`, `PIIMiddleware`), `langgraph.types.RetryPolicy`, `get_usage_metadata_callback`. Notes adapt MIT-licensed text from obra/superpowers and github/awesome-copilot with attribution.
- Catalogue capabilities reused: none, because none is importable from a hosted IDE with no workspace access.
- New capabilities added: none to the catalogue. The work adds copyable example files (`examples/raw_api_agent.py`, `examples/hardening.py`, `examples/rag_embeddings.py`) and notes, not a package, service or contract. Their first consumer is this repo's own test suite (`tests/test_raw_api_agent.py`, `tests/test_hardening.py`, `tests/test_rag_embeddings.py`), and then a candidate copying them into a take-home project.

## Authority and non-goals

> **CORE-AUTHORITY-NONGOALS** (blocking): The plan states who holds authority over the work and what it explicitly will not do (non-goals).

**Authority:** the owner, who approved the 8 additions on 2026-10-11 ("i approve"). Session code-c7 owns AGENTS.md, method/, PLAN.template.md, agents/planner.md and check.sh by agreement; README, wiki and KIT.md are shared and the second to land rebases.

**Non-goals:** no edit to code-c7's files; no live model call; no LLM-as-judge example (needs a key; next tier); no new dependency beyond numpy; no claim that any pattern works with a live model; no text copied from sources whose license does not allow it.

## Irreversible actions and spend

> **CORE-IRREVERSIBLE-SPEND** (blocking): For each irreversible action or spend the plan proposes, it names the boundary, who must authorize it, and how it is contained.

One irreversible action, no spend.

- **Action and boundary:** `git push origin main` to the public GitHub repo. Before it everything is local and revertible; after it content may be cached.
- **Who authorizes:** the owner, by the standing rule (2026-10-07: "i dont care what is public as long as it doesnt contain private data") and the approval of this work.
- **Containment:** push only after check.txt shows the privacy scan with 0 hits and the suite passing; content is generic notes and example code; if anything private is found after the push, revert at once and tell the owner.

## Uncertainties

> **CORE-UNCERTAINTIES** (blocking): The plan lists its material uncertainties, and each one has an owner or the evidence that would resolve it.

- **numpy needed for the fake embedding** (seen 2026-10-11: `NameError: np`): resolved by adding numpy to pyproject; evidence is test_rag_embeddings passing in a fresh `uv sync`. Owner: this session.
- **Provider API shapes** (Anthropic tool_result blocks, OpenAI Responses `function_call_output`): the example uses stubbed dict shapes taken from the official docs, so the offline test cannot catch drift in the real SDKs. Evidence that would resolve it: one live call per provider; not run (no live claim made, see LLM section). The note says so.
- **Middleware signatures in langchain 1.4.4:** resolved by the test constructing each middleware and running it in `create_agent` with a fake model.
- **KIT.md budget with code-c7 adding method/ files:** owner code-c7 for its own additions; this change keeps its own additions within 600 and reports the line count.

## Activation facts

> **CORE-ACTIVATION-FACTS** (blocking): No activation fact that the plan triggers is declared false. Declaring a fact true when the plan does not strictly need it is acceptable, because it only adds checks; judge only facts declared false. empirical_comparison_proposed is triggered when the plan proposes an A/B test, benchmark, bake-off, or other experiment comparing alternative designs, models, or candidates to choose among them; checking the built result against an expected outcome (an acceptance test, fixture replay, or regression check) is verification and does not trigger it. shared_mechanism is triggered by a new shared mechanism, contract, or algorithm; llm_central by behavior that centrally depends on LLM calls; irreversible_or_spend_action by a proposed irreversible action or spend. claims_external_standard is triggered when the plan claims, or presents its work as, following, implementing or conforming to a standard, schema or contract owned outside the repository being changed (for example a model presented as DM2, or output said to match a published schema); conforming to the repository's own contracts does not trigger it; aes_governed_target when the target repository is governed by an AES target (`.aes/target.yaml`), or the plan creates one (for example by running `aes init`). These two facts are optional: an undeclared one is shown as false and is judged like a declared false.

- empirical_comparison_proposed: false. No comparison of alternatives; tests check built patterns against expected outcomes.
- shared_mechanism: true. Declared true to be safe: the raw-API loop and the hardening patterns are mechanisms other people (candidates) are expected to copy and rely on, even though no project imports them; the added checks are answered under Shared mechanism.
- llm_central: true. The raw-API loop and hardening patterns are about model calls; call boundary and authority are under LLM call boundary.
- irreversible_or_spend_action: true. The public push; see Irreversible actions and spend.
- aes_governed_target: false. `.aes/` holds only `commit_rule.yaml`, no `target.yaml`.
- claims_external_standard: not declared (false). The kit claims conformance to no externally owned standard, schema or contract: the raw loop is an example modelled on the providers' docs and explicitly labelled as tested offline only against stubs, not as conforming to their APIs; a candidate checks it against the live SDK in their own test.

## Prior art and ownership

Searched on 2026-10-11 by two research agents (public skill collections; agent-building gaps), with every source URL and license re-checked through the GitHub API by this session. Disposition of each candidate:

- **obra/superpowers** systematic-debugging, receiving-code-review, verification-before-completion (MIT): **extend**, trimmed into `skills/debug/SKILL.md`, `skills/using-ide-ai-chat/SKILL.md` and `agents/reviewer.md`, with attribution.
- **github/awesome-copilot** agent-architecture selection table (MIT): **extend**, condensed into `skills/plan/SKILL.md`.
- **Two companies' published pages on how they judge AI use in their own interviews** (copyrighted): **bounded exception**, paraphrased as generic red flags with no company named, because the kit is public and names no employer.
- **humanlayer/12-factor-agents** (text licence not asserted on GitHub): **bounded exception**, ideas paraphrased in `skills/raw-api-agent/SKILL.md`, no text copied.
- **Anthropic and OpenAI tool-use docs**: **reuse**, the loop is modelled on their documented examples; the kit does not present it as conforming to either provider's API contract (the note says it is tested offline only, against stubs, and may drift from the live SDKs).
- **LangChain** `langchain.agents.middleware`, `RetryPolicy`, `get_usage_metadata_callback`, `InMemoryVectorStore`, `DeterministicFakeEmbedding`, and langchain-skills' langchain-middleware skill (MIT): **reuse**, the examples call these rather than reimplementing retry, limits, PII redaction or vector search.
- **This repo's own** `examples/agent_template.py` and `examples/patterns.py` (keyword retrieval): **compose**, the new RAG example sits beside the keyword one and the raw loop reuses the template's order-lookup tool, so a reader can compare like for like.
- **anthropics/skills** `claude-api` (Apache-2.0): **bounded exception**, not used, because it is provider-specific and 616 lines, too large for a pasteable kit; its loop shape is covered by the providers' docs above.
- **awesome-cursorrules** and **awesome-claude-code** entries: **bounded exception**, not used, because they depend on Cursor or Claude Code hooks and commands that a hosted IDE chat cannot run.
- **Third-party interview-prep guides**: **bounded exception**, not used, because they are secondhand with no published rubric; the companies' own pages (above) are the primary sources.

**Existing ownership and internal lineage searched:** this repo's `skills/`, `agents/`, `examples/` and `KIT.md` (grep for 'debug', 'middleware', 'retry', 'embedding', 'raw API' on 2026-10-11: no existing note or example covers them; `middleware` has 0 hits); the kit's own prior plans `docs/plans/kit-v2-*.md`; and session code-c7, the other writer, who confirmed by message on 2026-10-11 that no such research or additions exist and whose lane (method/, AGENTS.md) does not cover these concerns.

**Parallel-implementation check:** before commit, `grep -rn "def run_tool\|tool_result\|Retry" examples/` must show the raw loop only in `examples/raw_api_agent.py` and retries only via LangChain's own classes in `examples/hardening.py` (no hand-written retry loop anywhere); and `ls skills/` must show one skill per concern (no second debugging or hardening note). The output goes into check.txt.

## LLM call boundary

> **OV-LLM-CALL-BOUNDARY** (blocking): The plan describes the model call graph, the structured result boundary each call returns, and how calls are traced.

> **OV-LLM-AUTHORITY-PROMOTION** (blocking): The plan names the provider and spend authority for model calls and one authentic-run condition that must hold before the behavior is promoted.

**Call graph.** Raw-API loop: one model call per turn (`client.messages.create` or `client.responses.create` shape, stubbed), then each requested tool runs and its result is appended; repeat until the model returns no tool call, bounded by `max_turns`. Hardening example: `create_agent` with a fake model wrapped by retry, call-limit and PII middleware; one model call per agent turn. RAG example makes no model call (embedding only, fake offline).

**Structured result boundary.** The raw loop reads only the provider's structured tool-call blocks (name, id, input/arguments as JSON) and returns `tool_result`/`function_call_output` items keyed by that id; unknown tool names and tool exceptions become error results (`is_error`) instead of crashes. In LangChain, `AIMessage.tool_calls` is validated against each tool's schema.

**Tracing.** The raw loop logs each turn (tool name, arguments, result size) and returns the full message list, which the test asserts on; the hardening example uses `get_usage_metadata_callback` for token counts. In this plan's runs every model is a scripted stub, so the trace is check.txt with the scripted replies in the test files.

**Provider and spend authority:** this plan makes no live call and spends nothing. In a test the candidate's own key and the test's rules are the authority; in this repo the owner's OpenRouter route is the authority for any future live check.

**Authentic-run condition before promotion:** the kit presents these patterns as offline-tested control flow only. Before any note claims the raw loop works against a real provider, one live run per provider must show in its logged trace a real tool_use (Anthropic) or function_call (OpenAI) item, the tool result sent back with the same id, and a final text answer. Until then the note says "tested offline against the documented message shapes".

## Vertical and reset

> **OV-PROTO-VERTICAL-RESET** (blocking): The plan names the minimal vertical result, the reset boundary, and the non-goals, without adding coordinated-work ceremony.

**Minimal vertical:** one new pattern end to end first: `examples/raw_api_agent.py` + `tests/test_raw_api_agent.py` + `skills/raw-api-agent/SKILL.md` + README/wiki rows + build_kit exclusion, checked; then the others in the same shape.

**Files (the whole lane):** NEW skills/debug/SKILL.md, skills/raw-api-agent/SKILL.md, skills/production-hardening/SKILL.md, examples/raw_api_agent.py, examples/rag_embeddings.py, examples/hardening.py, tests/test_raw_api_agent.py, tests/test_rag_embeddings.py, tests/test_hardening.py, docs/plans/kit-v3-additions-c5.*; EDIT skills/using-ide-ai-chat/SKILL.md, skills/plan/SKILL.md, agents/reviewer.md, build_kit.sh, pyproject.toml, uv.lock, README.md, wiki/index.md, KIT.md (generated).

**Reset boundary:** branch c5-additions in worktree ~/code/interview-kit-c5b off origin/main 42c13f6; abandoning it means deleting the branch, with nothing pushed. **Non-goals:** no edit to code-c7's files (AGENTS.md, method/, PLAN.template.md, agents/planner.md, check.sh); no live model call; no LLM-as-judge example; no dependency beyond numpy; no claim that a pattern works with a live model. **No coordinated-work ceremony is added:** one writer on one branch, no claim registry, no handoff documents; the only coordination is a two-message file split with code-c7, already done.
