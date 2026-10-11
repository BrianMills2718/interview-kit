---
name: raw-api-agent
description: Build a tool-calling agent directly on the Anthropic or OpenAI API, no framework - the loop, tool definitions, error handling. Use when the task says raw API calls or forbids LangChain, or a framework would be overkill.
---

# Skill: an agent loop on the raw API

Runnable, offline-tested version: `examples/raw_api_agent.py` (`tests/test_raw_api_agent.py`).
The tests replay replies in the documented message shapes with a stub client. Both loops also
ran once live on 2026-10-11 through OpenRouter (`scripts/live_run.py`, trace in
`docs/plans/kit-v3-live-run.trace.jsonl`): `openai/gpt-5-mini` on the Responses shape and
`anthropic/claude-haiku-5.5` on the Messages shape each called the tool, got the result back
under the same id and answered from it, unchanged. Live details the stubs do not show:

- reasoning models put `reasoning` items in `resp.output`; sending them back as-is
  (`items += resp.output`) works;
- through OpenRouter: `OpenAI(base_url="https://openrouter.ai/api/v1", api_key=KEY)` and
  `Anthropic(base_url="https://openrouter.ai/api", auth_token=KEY)` (bearer auth), model ids like
  `openai/gpt-5-mini`;
- anthropic 1.13+ is built on `httpx2`: a custom `http_client=` must be an `httpx2.Client`,
  an `httpx.Client` raises "Invalid `http_client` argument".

## The loop (both providers)

```
messages = [user question]
repeat at most N turns:
    reply = model(messages, tools)
    append reply to messages            # keep the model's own tool-call items
    if reply asks for no tool: return its text
    for each tool call: run it, append its result with the SAME call id
raise "no answer after N turns"
```

| | Anthropic Messages API | OpenAI Responses API |
|---|---|---|
| call | `client.messages.create(model, max_tokens, system, tools, messages)` | `client.responses.create(model, instructions, tools, input)` |
| tool def | `{"name", "description", "input_schema"}` | `{"type": "function", "name", "description", "parameters"}` |
| more tools wanted when | `resp.stop_reason == "tool_use"` | any `item.type == "function_call"` in `resp.output` |
| call fields | block `.id`, `.name`, `.input` (dict) | item `.call_id`, `.name`, `.arguments` (JSON string) |
| send result | user message of `{"type": "tool_result", "tool_use_id", "content", "is_error"}` blocks, all results in one message | append `{"type": "function_call_output", "call_id", "output"}` |
| final text | text blocks of `resp.content` | `resp.output_text` |

## Design rules (from the providers' guides and 12-factor-agents, paraphrased)

- **You own the control flow**: the loop, the turn limit and the stop condition are plain code
  you can read and test, which is easy to explain to a grader.
- **Tool descriptions are prompts**: say what it does, when to use it, and what it returns.
  Return only the fields the model needs.
- **Errors go back to the model, compactly**: catch the tool's exception, send its message as the
  result with `is_error: true`, and let the model retry or explain. Unknown tool names too.
  Never crash the loop, and never hide the error.
- **Bound everything**: `max_turns`, and `max_tokens` on Anthropic (required there).
- **Log each turn**: tool name, arguments, result size; return the whole message list so a test
  can assert on it.

When to prefer this over LangGraph: the prompt says raw API calls, one provider is fixed, or the
loop is all you need. Say so in the README's design decisions.
