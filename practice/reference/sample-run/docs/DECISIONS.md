# Decisions (ADR log)

One row per real choice, written when it was made. The README links here.

| ID | Context | Decision | Consequences | Rejected alternative | What would show it wrong |
|---|---|---|---|---|---|
| ADR-1 | the grader's scripted model answers by calling a tool named `Reply` | `create_agent` with `response_format=ToolStrategy(Reply)` | ToolStrategy registers exactly that tool, validates it, sends errors back for a retry and fills `structured_response` | hand-built `StateGraph` with a final `with_structured_output` node: more code, and the scripted model never makes a separate final call | a grader case with no `structured_response`, or an invalid Reply that ends the run instead of retrying |
| ADR-2 | refunds over $50 need a human yes, and a resumed tool re-runs from its first line | approval pause is `interrupt()` inside the `request_refund` tool, after every rule check and before the write | all six rules stay in one function in the stated order; the refund is appended only after the pause returns, so the re-run cannot double-refund | a separate approval node: needs extra state to carry order id and amount out of the tool and back | a declined case with the id in `shop["refunds"]`, or an approved case with it twice |
| ADR-3 | the grader passes a fresh `shop` per case and reads `shop["refunds"]` | tools are closures over `shop` built inside `build_agent()` | a closure writes that exact dict | module-level global shop: cases would leak into each other | refunds from one case appearing in the next |
| ADR-4 | three short policies to search | word-overlap scoring for `search_policy` | no embeddings or extra dependency | embeddings / BM25 library: a new dependency for three documents | a grader policy case returning the wrong policy first |
| ADR-5 | the grader calls `invoke`, so the limit must travel with the graph | step limit set at build time with `.with_config({"recursion_limit": 12})` | a looping model stops with `GraphRecursionError` | relying on the default (10007): a looping model runs on | a scripted loop that does not stop with `GraphRecursionError` |
