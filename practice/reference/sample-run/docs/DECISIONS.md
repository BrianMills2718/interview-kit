# Decisions

One row per real choice, written when it was made. The README links here.

| ID | Decision | Why | Rejected alternative | What would show it wrong |
|---|---|---|---|---|
| D1 | `create_agent` with `response_format=ToolStrategy(Reply)` | the grader's scripted model answers by calling a tool named `Reply`; ToolStrategy registers exactly that tool, validates it, sends errors back for a retry and fills `structured_response` | hand-built `StateGraph` with a final `with_structured_output` node: more code, and the scripted model never makes a separate final call | a grader case with no `structured_response`, or an invalid Reply that ends the run instead of retrying |
| D2 | Approval pause is `interrupt()` inside the `request_refund` tool, after every rule check and before the write | keeps all six rules in one function in the stated order; the refund is appended only after the pause returns, so the tool's re-run on resume cannot double-refund | a separate approval node: needs extra state to carry order id and amount out of the tool and back | a declined case with the id in `shop["refunds"]`, or an approved case with it twice |
| D3 | Tools are closures over `shop` built inside `build_agent()` | the grader passes a fresh `shop` per case and reads `shop["refunds"]`; a closure writes that exact dict | module-level global shop: cases would leak into each other | refunds from one case appearing in the next |
| D4 | Word-overlap scoring for `search_policy` | three short policies; no embeddings or extra dependency needed | embeddings / BM25 library: a new dependency for three documents | a grader policy case returning the wrong policy first |
| D5 | Step limit set at build time with `.with_config({"recursion_limit": 12})` | the grader calls `invoke`, so the limit must travel with the graph | relying on the default (10007): a looping model runs on | a scripted loop that does not stop with `GraphRecursionError` |
