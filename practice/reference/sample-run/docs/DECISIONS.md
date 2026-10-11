# Decisions

One row per real choice, written when it was made. The README links here.

| ID | Decision | Why | Rejected alternative | What would show it wrong |
|---|---|---|---|---|
| D1 | Prebuilt `create_agent` with `response_format=ToolStrategy(Reply)` and `checkpointer=InMemorySaver()` | gives the `Reply` tool, retry-on-invalid and `structured_response` the grader reads, with no custom routing | hand-built `StateGraph` with a check node: more code for the same behavior | a grader case needs routing `create_agent` cannot express (e.g. a step between tools) |
| D2 | Approval `interrupt()` inside the `request_refund` tool, after rules 1-4 | the reviewer is only asked when the refund would otherwise go through; one tool keeps the exact messages together | a separate approval node: needs custom graph and state passing the order id | a case where the tool's re-run on resume produces a duplicate refund or a second pause |
| D3 | All refund rules in one pure function `refund_refusal()` | testable without a model or graph; order of checks visible in one place | checks spread in the tool body: order harder to see and test | a rule-order test fails, or a grader case refuses with the wrong message |
| D4 | Policy search by keyword overlap with light stemming, ties in data order | three short policies; offline, deterministic, explainable | embeddings: needs a key or model download for 3 documents | a grader case expects a policy ranked differently than overlap gives |
| D5 | Tools built as closures in `make_tools(shop)` | the grader passes a fresh `shop` per case; no global state between cases | module-level `SHOP` global: cases would share refunds | refunds leaking between test cases |
| D6 | `Reply.order_id` accepts `A-123` or `None`; `action` must be one sentence | the task says "`A-123` form, or none" and "one sentence"; strict schema makes the retry meaningful | free strings: an invalid answer would be accepted silently | a valid scripted Reply is rejected (grader shows "no structured_response") |
| D7 | Step limit `recursion_limit=25` set at build time with `.with_config` | the grader calls `invoke`, so the limit must live on the graph | relying on the caller's config: default is 10007 steps | a legitimate case needs more than 25 steps (hits GraphRecursionError) |
