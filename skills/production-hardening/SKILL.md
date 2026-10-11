---
name: production-hardening
description: Add retries, call limits, cost tracking and input/output guardrails to a LangChain agent using LangChain's own middleware. Use once the agent works, when the task mentions reliability, cost, safety or production readiness.
---

# Skill: harden the agent with built-in middleware

Runnable, offline-tested version: `examples/hardening.py` (`tests/test_hardening.py`), langchain
1.4 / langchain-core 1.6. Each piece is LangChain's own, passed to
`create_agent(llm, tools, middleware=[...])`; don't hand-write retry loops or regex filters.

| Need | Use | Note |
|---|---|---|
| transient model errors (503, rate limit) | `ModelRetryMiddleware(max_retries=2, initial_delay=1.0, on_failure="error")` | `on_failure="continue"` (default) hides a final failure; prefer `"error"` |
| runaway tool loops | `ModelCallLimitMiddleware(run_limit=6, exit_behavior="end")` | also `ToolCallLimitMiddleware(run_limit=5)` |
| a node in your own StateGraph | `g.add_node("x", fn, retry_policy=RetryPolicy(max_attempts=3))` | `from langgraph.types import RetryPolicy` |
| rate limiting | `ChatOpenAI(..., rate_limiter=InMemoryRateLimiter(requests_per_second=1))` | `langchain_core.rate_limiters` |
| personal data | `PIIMiddleware("email", strategy="redact", apply_to_input=True)` | strategies: redact, mask, hash, block |
| reject bad input before spending a call | `@before_agent(can_jump_to=["end"])` returning `{"messages": [...], "jump_to": "end"}` | `@after_agent` checks the output |
| cost | `with get_usage_metadata_callback() as cb:` then tokens x price | counts only replies whose `response_metadata` has `model_name` (real providers set it; fakes in tests must) |

Also:

- **Tool output is untrusted input** (prompt injection): never let a tool result change the
  system prompt or call a destructive tool without a check or a human-approval interrupt
  (`examples/patterns.py`).
- **Validate tool arguments** with typed parameters or a Pydantic schema, and raise a clear error.
- **Report cost and limits in the README**: tokens and estimated cost per question, and what
  happens when a limit is hit. Graders look for this.

Test each guard on a case where it must act: an email that must not reach the model, a model
that fails once, a model that asks for tools forever (see the example's tests).
