"""Offline tests for the raw-API agent loops: stub clients replay replies in each API's shape."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from raw_api_agent import run_anthropic, run_openai  # noqa: E402


class Stub:
    """Fake client: records each request and returns the next scripted response."""

    def __init__(self, *responses):
        self.queue, self.requests = list(responses), []
        self.messages = self.responses = self  # serves client.messages.create and client.responses.create

    def create(self, **kwargs):
        self.requests.append(json.loads(json.dumps(kwargs, default=vars)))  # snapshot, not a live ref
        return self.queue.pop(0)


def anthropic_reply(stop, *blocks):
    return NS(stop_reason=stop, content=list(blocks))


def test_anthropic_loop_runs_the_requested_tool_and_returns_its_result():
    use = NS(type="tool_use", id="tu_1", name="lookup_order", input={"order_id": "A-101"})
    client = Stub(
        anthropic_reply("tool_use", use),
        anthropic_reply("end_turn", NS(type="text", text="A-101 is processing.")),
    )
    answer, messages = run_anthropic(client, "Where is A-101?", model="m")
    assert answer == "A-101 is processing."
    result = messages[2]["content"][0]  # user turn after the assistant's tool_use
    assert result == {
        "type": "tool_result",
        "tool_use_id": "tu_1",
        "content": "Order A-101: processing",
        "is_error": False,
    }
    # the second request carried the tool result back to the model
    assert client.requests[1]["messages"][2]["content"][0]["tool_use_id"] == "tu_1"


def test_anthropic_tool_error_goes_back_to_the_model_flagged():
    use = NS(type="tool_use", id="tu_9", name="lookup_order", input={"order_id": "Z-1"})
    client = Stub(
        anthropic_reply("tool_use", use),
        anthropic_reply("end_turn", NS(type="text", text="I could not find Z-1.")),
    )
    _, messages = run_anthropic(client, "Where is Z-1?", model="m")
    result = messages[2]["content"][0]
    assert result["is_error"] is True and "Unknown order id 'Z-1'" in result["content"]


def test_anthropic_loop_stops_at_the_turn_limit():
    use = NS(type="tool_use", id="tu", name="lookup_order", input={"order_id": "A-100"})
    client = Stub(*[anthropic_reply("tool_use", use) for _ in range(3)])
    with pytest.raises(RuntimeError, match="after 3 turns"):
        run_anthropic(client, "loop forever", model="m", max_turns=3)


def test_openai_loop_sends_function_call_output_with_the_same_call_id():
    call = NS(type="function_call", call_id="call_1", name="lookup_order", arguments='{"order_id": "A-100"}')
    client = Stub(
        NS(output=[call], output_text=""),
        NS(output=[NS(type="message")], output_text="A-100 has shipped."),
    )
    answer, items = run_openai(client, "Where is A-100?", model="m")
    assert answer == "A-100 has shipped."
    sent = [i for i in items if isinstance(i, dict) and i.get("type") == "function_call_output"]
    assert sent == [{"type": "function_call_output", "call_id": "call_1", "output": "Order A-100: shipped"}]
