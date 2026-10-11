"""Tool-calling agent loop on the raw provider APIs, no framework: a template to copy and adapt.

The loop: call the model, run every tool it asks for, send the results back, repeat until it
answers without asking for a tool (or the turn limit is hit). Two versions, one per API shape:
  run_anthropic(client, ...)  Anthropic Messages API  (pip install anthropic)
  run_openai(client, ...)     OpenAI Responses API    (pip install openai)

Run live:  ANTHROPIC_API_KEY=... python examples/raw_api_agent.py anthropic "Where is order A-100?"
           OPENAI_API_KEY=...    python examples/raw_api_agent.py openai    "Where is order A-100?"
Test:      pytest tests/test_raw_api_agent.py -v  (offline: a stub client replays scripted replies
           in the documented message shapes; it does not prove the live SDKs still match them)
"""

import json
import logging
import os
import sys

log = logging.getLogger("raw_agent")

ORDERS = {"A-100": "shipped", "A-101": "processing"}  # stand-in for a real data source


def lookup_order(order_id: str) -> str:
    """Return the status of an order given its ID, e.g. 'A-100'."""
    if order_id not in ORDERS:
        raise ValueError(f"Unknown order id {order_id!r}; known ids look like 'A-100'.")
    return f"Order {order_id}: {ORDERS[order_id]}"


# One registry drives both APIs: name -> (function, description, JSON schema of its arguments).
# The description is the prompt the model reads: say what it does, when to use it, what it returns.
TOOLS = {
    "lookup_order": (
        lookup_order,
        "Look up an order's shipping status by order ID. Use for any question about a "
        "specific order. Returns one line like 'Order A-100: shipped'.",
        {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "e.g. 'A-100'"}},
            "required": ["order_id"],
        },
    ),
}
SYSTEM = "You are a support agent. Use tools for facts; never guess. Say so if you cannot find it."


def run_tool(name: str, args: dict) -> tuple[str, bool]:
    """Run one requested tool; return (result text, is_error). Errors go back to the model."""
    if name not in TOOLS:
        return f"Unknown tool {name!r}; available: {sorted(TOOLS)}", True
    try:
        out = TOOLS[name][0](**args)
    except Exception as e:  # the model sees the message and can retry; nothing is hidden
        log.warning("tool %s(%s) failed: %s", name, args, e)
        return f"{type(e).__name__}: {e}", True
    log.info("tool %s(%s) -> %d chars", name, args, len(out))
    return out, False


def run_anthropic(client, question: str, model: str, max_turns: int = 8) -> tuple[str, list]:
    """Agent loop on the Anthropic Messages API; returns (final answer, full message list)."""
    tools = [{"name": n, "description": d, "input_schema": s} for n, (_, d, s) in TOOLS.items()]
    messages = [{"role": "user", "content": question}]
    for turn in range(max_turns):
        resp = client.messages.create(
            model=model, max_tokens=1024, system=SYSTEM, tools=tools, messages=messages
        )
        messages.append({"role": "assistant", "content": resp.content})
        calls = [b for b in resp.content if b.type == "tool_use"]
        log.info("turn %d: stop_reason=%s tools=%s", turn, resp.stop_reason, [c.name for c in calls])
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text"), messages
        results = []  # one tool_result per tool_use, same id, all in a single user message
        for c in calls:
            text, is_error = run_tool(c.name, c.input)
            results.append(
                {"type": "tool_result", "tool_use_id": c.id, "content": text, "is_error": is_error}
            )
        messages.append({"role": "user", "content": results})
    raise RuntimeError(f"no final answer after {max_turns} turns")


def run_openai(client, question: str, model: str, max_turns: int = 8) -> tuple[str, list]:
    """Agent loop on the OpenAI Responses API; returns (final answer, full input list)."""
    tools = [
        {"type": "function", "name": n, "description": d, "parameters": s}
        for n, (_, d, s) in TOOLS.items()
    ]
    items: list = [{"role": "user", "content": question}]
    for turn in range(max_turns):
        resp = client.responses.create(model=model, instructions=SYSTEM, tools=tools, input=items)
        items += resp.output  # keep the model's own items (incl. its function calls) in history
        calls = [i for i in resp.output if i.type == "function_call"]
        log.info("turn %d: tools=%s", turn, [c.name for c in calls])
        if not calls:
            return resp.output_text, items
        for c in calls:
            text, _ = run_tool(c.name, json.loads(c.arguments))
            items.append({"type": "function_call_output", "call_id": c.call_id, "output": text})
    raise RuntimeError(f"no final answer after {max_turns} turns")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    provider, question = sys.argv[1], " ".join(sys.argv[2:]) or "Where is order A-100?"
    if provider == "anthropic":
        import anthropic

        answer, _ = run_anthropic(
            anthropic.Anthropic(), question, os.environ.get("MODEL", "claude-sonnet-5-5")
        )
    else:
        import openai

        answer, _ = run_openai(openai.OpenAI(), question, os.environ.get("MODEL", "gpt-5-mini"))
    print(answer)
