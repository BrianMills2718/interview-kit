---
schema_version: "1.0"
artifact_type: design_plan
id: kit-v3-live-run
status: proposed
method_conformance_receipt: docs/plans/kit-v3-live-run.receipt.json
trace_review_criteria:
  - criterion_id: outcome
    expected_outcome: pass
goal:
  outcome: "The kit's three model-calling examples (raw API loop on both providers' shapes, hardened LangChain agent, embedding search) are run once against live models, and the kit says what worked, through which route, with the recorded trace."
  canonical_example: "`uv run python scripts/live_run.py` with an OpenRouter key writes docs/plans/kit-v3-live-run.trace.jsonl; in it the OpenAI-shape run shows a function_call for lookup_order with order_id A-100, a function_call_output with the same call_id, and a final answer naming the order status; skills/raw-api-agent/SKILL.md then states which shapes were run live and on what date."
  forbidden_substitutes: "the offline stub tests passing; a run whose trace shows no tool call; a final answer read without the request and response bodies; a claim for a provider shape that was not actually run"
  boundaries: "files listed under Vertical and reset, in worktree ~/code/interview-kit-c5c on branch c5-live-run; code-c7's files untouched; spend under 1 US dollar on the owner's OpenRouter key; one irreversible action: the push of main after checks"
  done_when: "docs/plans/kit-v3-live-run.trace.jsonl holds the full request and response bodies (no key or headers) of each live run, and docs/plans/kit-v3-live-run.check.txt shows, per run, the tool call, its id echoed back, the final answer, or the exact error; the skill note and wiki Evidence state the result per shape; full pytest suite passes with exit 0; privacy scan 0 hits"
  do_not_gate_on: "a shape the route does not offer (recorded as not run, with the error); a direct-provider key; the owner's own practice run"
---

# Kit v3: one live run of the model-calling examples

Each section below answers the checklist items quoted in it.

## Actor and result

> **CORE-ACTOR-RESULT-EXAMPLE** (blocking): The plan names the actor it serves, the desired result, and one stable, concrete, user-visible example of that result.

**Actor:** a candidate in a timed agentic-AI take-home who copies the kit's examples into their project. **Result:** they know which of the kit's examples have run against a real model, through which route, and what the real responses looked like, instead of only offline stubs. **Example:** the candidate opens `skills/raw-api-agent/SKILL.md` and reads "run live on 2026-10-11 through OpenRouter: OpenAI Responses shape worked (tool call, result, answer); Anthropic Messages shape: <result>", and can open the recorded trace to see a real `function_call` item.

## Requirements

> **CORE-REQUIREMENTS-TRACED** (blocking): The plan lists its requirements: what was asked for, and what the delivered work's own claims imply. A claim here is what the work is presented as being or doing to its users, for example work presented as following a standard, schema or contract (which implies conformance to it) or an output labelled as showing something (which implies it shows it correctly); the plan's own format and front matter are not such claims, and the details a check examines (what a trace must show) belong to that check rather than being separate requirements. Each requirement names the check that verifies it (a test, script, gate step, or named review of a run) and its status: passing, failing, planned and not yet run, or deferred with a stated reason; deferred requirements are carried onto every release or completion record the plan names. A plan fails this item if it has no requirements list, if any requirement has neither a check nor an explicit deferral with its reason, or if the plan presents the work as following a named standard, schema or contract, or as having another property its users rely on, that its requirements list omits.

| Id | Requirement | Source | Check | Status |
| --- | --- | --- | --- | --- |
| R1 | Run `run_openai` live (Responses shape) and record request/response bodies | asked: the owner 2026-10-11 "i approve" (to: one real run of the new examples through the OpenRouter account) | trace.jsonl + check.txt section openai | passing: see check.txt |
| R2 | Run `run_anthropic` live (Messages shape), or record why the route cannot | same approval | trace.jsonl + check.txt section anthropic | passing: see check.txt |
| R3 | Run `examples/hardening.py` agent live and record usage/cost | same approval | trace.jsonl + check.txt section hardening | passing: see check.txt |
| R4 | Run `examples/rag_embeddings.py` with live embeddings | same approval | check.txt section rag (refund question returns the refunds doc first) | passing: see check.txt |
| R5 | Kit notes state what was run live, how, and the result, without overclaiming | the work's own claim | grep of skills/raw-api-agent/SKILL.md and wiki/index.md in check.txt | passing: see check.txt |
| R6 | Any defect found in an example is fixed with an offline test that fails before the fix | same approval (goal: retire the stub-only concern) | pytest output in check.txt | passing: see check.txt |
| R7 | No secret or private data in committed traces | workspace rule on public content | gitleaks + grep for the key prefix, emails, names in check.txt | passing: see check.txt |

Claims implied: the notes will say an example "ran live"; R1-R4 check exactly that, per shape. No external standard is claimed.

## Success and disproof

> **CORE-SUCCESS-DISPROOF** (blocking): The plan defines the evidence that would show success and a concrete condition that would disprove the approach. Each success measure is the property the plan claims, or a check that directly tests that property, not a stand-in for it: a count, a picture, a readability judgment, or the pipeline agreeing with itself (hashes, labels, byte equality) does not show correctness or conformance it does not test. A plan fails this item if it has no disproof condition, or if a success measure is such a stand-in for the claimed property and the plan names no direct check of that property.

> **CORE-TRACE-REVIEW** (blocking): Every success or acceptance criterion in the plan is judged from the full trace of a run, not only its final outcome: it names the run whose full trace is examined (for example the session, its tool and LLM calls, commits, check output, or messages), where that trace lives, and what must be seen in that trace beyond the final outcome. A criterion that names only an outcome, such as tests passing, a PR merged, a test fixture reproducing the journey, or a status reading succeeded, fails this item. A criterion for which no run exists, such as a pure document edit, passes only when the plan states that exemption and its reason explicitly.

**Success evidence:** for each of R1-R3, the trace shows a model request carrying the tool definitions, a response containing a tool call with name and arguments, the next request carrying the tool result keyed by the same id, and a final text answer that uses the tool result (order A-100's status). For R4, the live embedding search returns the refunds document first for "how long do refunds take?" and the shipping document first for a shipping question.

**Direct correctness check (not a stand-in):** the claimed property is "this loop works against a live model". The trace is the direct evidence: the id equality and the answer containing the tool's returned status are read from the recorded bodies, not inferred from exit status. A model that answered without calling the tool would show no tool call and fails the check.

**Disproof:** the live response shape differs from what the example reads (e.g. the loop crashes or never sees the tool call), or the answer ignores the tool result. Either is a defect to fix (R6), not a pass.

**Run judged:** `scripts/live_run.py` run once. **Where its trace lives:** docs/plans/kit-v3-live-run.trace.jsonl (every HTTP request and response body, headers dropped) and the console output saved as check.txt. **What must be seen beyond the final result:** per run, the request model id, the tool call item and its id, the tool result with the same id, token usage, the final answer; for a failed shape, the HTTP status and error body. For R4 (embeddings), the trace shows each embeddings request (model id and the input texts: the three documents, then each query) and each response (vector count and dimension, token usage), and check.txt prints every document id with its similarity score per query, so the ranking is read from the scores, not only from which document came first.

## When a run fails or surprises us

> **CORE-TRACE-DEBUGGING** (blocking): The plan includes a separate When a run fails or surprises us procedure, distinct from anticipated failure modes. It requires preserving the failed run and its trace id; reading full inputs, prompts, each tool call arguments/results, intermediate stages and final output before selecting a fix; citing the observed divergence; classifying evidence absent, evidence returned but unused or contradicted, invalid expectation, or unresolved; and linking a targeted repair to a new traced verification run while retaining the original failure. Unresolved diagnoses permit investigation but cannot authorize a causal repair. Review completeness is separate from the run verdict.

Keep the failing run: its trace id is the run label plus timestamp in trace.jsonl; keep that file's lines. Read the full request and response bodies before changing anything: the tools sent, the model's output items, the tool call arguments and results, the next request, and the final output. Name where it diverged and classify it: evidence absent (the route returned no tool call or an error), returned but unused or contradicted (tool result sent but the answer ignores it), invalid expectation (the example's shape assumption is wrong for this route: check the provider docs and the installed SDK source), or unresolved. Unresolved allows more reading, not a fix. A fix gets an offline test reproducing the divergence and a new live run, saved beside the original failure, which stays recorded.

This is separate from the anticipated failure modes under Uncertainties (route may not offer a shape; model ids differ on the route).

## System model

> **CORE-SYSTEM-MODEL** (blocking): The plan links the project's system model (a path such as docs/model/ODD.md) or carries the one-line exemption `System model: exempt -- <reason>`, which fits only a project with no stored state and no user-facing view. Unless exempt, the plan names each system-model element (entity, process, record or event, or view) that the work adds, changes, or relies on, and its trace review names, for each such element, what the examined run must show of it (for example an event of that record type with its id, or the view displaying that entity). A plan with neither a model link nor the exemption line fails this item, as does one that lists model elements without saying what the examined run must show of each, or one that names no element without stating that the work touches none and why. For a maintained repository, the plan also cites the documentation entry point from which the model is reachable; a shared model explicitly identifies this repository's scope. It names applicable source-linked views, explains material omissions without imposing a fixed diagram quota, names concrete model freshness or drift checks, and states how the model, view coverage and verification evidence will be reconciled in the same change (or gives a concrete reason each needs no update). A bare model path without these discovery, view, freshness and reconciliation obligations fails this item. Representation Router may render selected views but does not supply planning authority or prove executed behavior.

System model: exempt -- documentation and example-code repo with no stored state, no service and no user-facing view, so no source-linked views apply

Documentation entry point: `wiki/index.md`. Freshness and reconciliation: the wiki Evidence list and the Map row for the new script are updated in the same commit; the commit rule's wiki-reachability check refuses unreachable new markdown.

## Capability reuse

> **CORE-CAPABILITY-REUSE** (blocking): The plan answers capability reuse against the capability catalogue in agentic-capability-architecture-canonical, which has two files: `reuse_candidates.yml`, whose entries under `candidates:` are cross-project capabilities with their selected off-the-shelf implementations, each named by its `id` (for example `documents_to_text`) and marked candidate or promoted; and `capability_registry.yml`, whose entries under `capabilities:` are the packages that repository holds, each named by its key (for example `approvals`) with the capability ids it `provides` (for example `approval.resolve`). An entry from either file counts. The plan names each catalogue capability the work reuses, by its id, key or provided id; names each new capability the work adds together with its first consumer (the project, command or workflow in this plan that uses it); and, where no entry covers what the work needs, states `No catalogue entry fits, because <reason>`, the reason saying what the work needs that no entry provides. A plan may give more than one of these answers. A plan fails this item if it gives none of them, if it claims reuse without naming the catalogue entry or id reused (reusing code or a contract that is not a catalogue entry does not count), if it adds a capability without naming its first consumer, or if it says no entry fits without a reason.

Checked against the capability catalogue in agentic-capability-architecture-canonical (`reuse_candidates.yml` and `capability_registry.yml`):

- No catalogue entry fits, because the need is a one-off live check of example code that must stay copyable into a hosted IDE with only the provider SDKs; the workspace's shared LLM client is not importable there and wrapping the examples in it would test a different code path from the one candidates copy.
- Catalogue capabilities reused: none, for the reason above.
- New capabilities added: none to the catalogue. `scripts/live_run.py` is a repo-local check script; its first consumer is this plan's run, then anyone re-running the live check.

## Authority and non-goals

> **CORE-AUTHORITY-NONGOALS** (blocking): The plan states who holds authority over the work and what it explicitly will not do (non-goals).

**Authority:** the owner, who approved this run on 2026-10-11 ("i approve"). Session code-c7 confirmed by message the same day that this lane does not collide with its own (it is adding practice/reference/sample-run/).

**Non-goals:** no change to code-c7's files; no new dependency in pyproject (the anthropic SDK is used ephemerally via `uv run --with anthropic` for the check); no benchmark or model comparison; no claim beyond the shapes and route actually run.

## Irreversible actions and spend

> **CORE-IRREVERSIBLE-SPEND** (blocking): For each irreversible action or spend the plan proposes, it names the boundary, who must authorize it, and how it is contained.

- **Spend:** a few model calls on the owner's OpenRouter key (OPENROUTER_API_KEY), cheap models, expected well under 0.10 US dollars, hard ceiling 1 US dollar. Boundary: each call is billed when made. Authorized by the owner's approval of this run. Contained by: one run of the script, max 8 turns per loop, no retries beyond the example's own, and the key never printed or written to any file (headers are dropped from the trace).
- **Action:** `git push origin main` to the public repo. Authorized by the owner's standing rule on public content (2026-10-07) and this approval. Contained by: push only after the privacy scan shows 0 hits on the trace; revert at once if anything private is found.

## Uncertainties

> **CORE-UNCERTAINTIES** (blocking): The plan lists its material uncertainties, and each one has an owner or the evidence that would resolve it.

- **Does OpenRouter offer the OpenAI Responses shape and the Anthropic Messages shape?** Evidence that resolves it: the first request of each run in trace.jsonl (status and body). Owner: this session. If a shape is not offered, it is recorded as not run with the error; the kit says so.
- **Model ids on the route** (e.g. `openai/gpt-5-mini`, `anthropic/claude-sonnet-5-5` style): resolved by OpenRouter's model list, fetched before the run.
- **Re-sending SDK output objects as input** (`items += resp.output`): the route may reject extra fields; the trace shows whether the second request succeeded.

## Activation facts

> **CORE-ACTIVATION-FACTS** (blocking): No activation fact that the plan triggers is declared false. Declaring a fact true when the plan does not strictly need it is acceptable, because it only adds checks; judge only facts declared false. empirical_comparison_proposed is triggered when the plan proposes an A/B test, benchmark, bake-off, or other experiment comparing alternative designs, models, or candidates to choose among them; checking the built result against an expected outcome (an acceptance test, fixture replay, or regression check) is verification and does not trigger it. shared_mechanism is triggered by a new shared mechanism, contract, or algorithm; llm_central by behavior that centrally depends on LLM calls; irreversible_or_spend_action by a proposed irreversible action or spend. claims_external_standard is triggered when the plan claims, or presents its work as, following, implementing or conforming to a standard, schema or contract owned outside the repository being changed (for example a model presented as DM2, or output said to match a published schema); conforming to the repository's own contracts does not trigger it; aes_governed_target when the target repository is governed by an AES target (`.aes/target.yaml`), or the plan creates one (for example by running `aes init`). These two facts are optional: an undeclared one is shown as false and is judged like a declared false.

- empirical_comparison_proposed: false. No comparison among alternatives; one verification run.
- shared_mechanism: true. Declared true to be safe: the examples are patterns candidates rely on; answered under Prior art and ownership.
- llm_central: true. The work is live model calls; see LLM call boundary.
- irreversible_or_spend_action: true. OpenRouter spend and the public push; see Irreversible actions and spend.
- aes_governed_target: false. `.aes/` holds only `commit_rule.yaml`.
- claims_external_standard: not declared (false). The note will report what ran on one route on one date; it does not claim conformance to either provider's API contract.

## Prior art and ownership

- **OpenRouter's OpenAI-compatible and Responses endpoints**: **reuse**, the examples point at them through the SDKs' standard base-URL settings, unchanged.
- **httpx event hooks** (the SDKs' HTTP client): **reuse**, to record request and response bodies without changing example code.
- **The kit's own offline tests** (`tests/test_raw_api_agent.py`, `tests/test_hardening.py`, `tests/test_rag_embeddings.py`): **compose**, they stay the regression check; the live run adds evidence beside them.
- **External prior art searched (2026-10-11):** OpenRouter's documentation for its OpenAI-compatible API, its Responses API and its Anthropic-compatible endpoint (openrouter.ai/docs), and the OpenAI and Anthropic SDK READMEs for base-URL configuration and custom httpx clients; LangChain's `ChatOpenAI`/`OpenAIEmbeddings` `base_url` parameters. Disposition: **reuse** all of them as documented; no wrapper or proxy is built. Tools like LangSmith or Helicone tracing: **bounded exception**, not used, because they need another account and would not be available to a candidate in a hosted IDE; an httpx hook records the same bodies with no account.
- **The workspace's shared LLM client and its call logs**: **bounded exception**, not used, because the kit's examples must run with only the provider SDKs in a hosted IDE.

**Existing ownership and internal lineage searched:** this repo's `scripts/`, `examples/` and `docs/plans/` (grep for 'live', 'openrouter', 'base_url' on 2026-10-11: no live-run script or record exists); the previous plan kit-v3-additions-c5 deferred exactly this run; session code-c7 confirmed it has no such lane. Dispositions: the previous plan kit-v3-additions-c5 is **extend** (this plan carries out the live run it deferred, under its authentic-run condition); session code-c7's lane (practice/reference/sample-run/) is **bounded exception**, not touched, because it covers a different concern.

**Parallel-implementation check:** before commit, `grep -rln "openrouter" scripts/ examples/` must show only `scripts/live_run.py` (the examples stay route-agnostic); output in check.txt.

## LLM call boundary

> **OV-LLM-CALL-BOUNDARY** (blocking): The plan describes the model call graph, the structured result boundary each call returns, and how calls are traced.

> **OV-LLM-AUTHORITY-PROMOTION** (blocking): The plan names the provider and spend authority for model calls and one authentic-run condition that must hold before the behavior is promoted.

**Call graph.** `scripts/live_run.py` calls, in order: `run_openai` (Responses shape, one call per turn, max 8), `run_anthropic` (Messages shape, same bound), the hardening agent (`create_agent` with retry and call-limit middleware, ChatOpenAI pointed at OpenRouter), and the embedding search (`OpenAIEmbeddings`, two queries). Each loop ends when the model returns no tool call.

**Structured result boundary.** Unchanged from the examples: the loops read only structured tool-call items (name, id, JSON arguments) and send results keyed by that id; the hardening agent's tool calls are validated by LangChain against the tool schema. The embedding calls return a list of float vectors, one per input text; the script checks the count equals the number of inputs and all vectors share one dimension before searching, and raises with the response body otherwise.

**Tracing.** An httpx event hook records every request body and response body (headers dropped) with a run label and timestamp into docs/plans/kit-v3-live-run.trace.jsonl; console logs go to check.txt.

**Provider and spend authority:** OpenRouter with the owner's key, approved 2026-10-11; ceiling 1 US dollar.

**Authentic-run condition before promotion:** a note may say a shape "ran live" only when trace.jsonl shows, for that shape, a real tool call item, the result sent back with the same id, and a final text answer using it.

## Vertical and reset

> **OV-PROTO-VERTICAL-RESET** (blocking): The plan names the minimal vertical result, the reset boundary, and the non-goals, without adding coordinated-work ceremony.

**Minimal vertical:** the OpenAI Responses run first, end to end with its trace read; then Anthropic, hardening, RAG.

**Files (the whole lane):** NEW scripts/live_run.py, docs/plans/kit-v3-live-run.* (plan records, trace.jsonl, check.txt); EDIT skills/raw-api-agent/SKILL.md, skills/production-hardening/SKILL.md (one line on the live result), wiki/index.md (Map row, Evidence), README.md (one row), KIT.md (generated), and examples/*.py plus their tests only if the run finds a defect (R6).

**Reset boundary:** branch c5-live-run in worktree ~/code/interview-kit-c5c off origin/main 5890683; abandoning it means deleting the branch, nothing pushed. **Non-goals:** as under Authority and non-goals. **No coordinated-work ceremony is added:** one writer, one branch; coordination was one message exchange with code-c7.
