"""The MCP server example, exercised through the SDK's in-memory client (no network, no model)."""

import asyncio
import sys
from pathlib import Path

from mcp import Client

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from mcp_server import mcp  # noqa: E402


async def _session(fn):
    async with Client(mcp) as client:
        return await fn(client)


def test_mcp_lists_the_tool_with_its_docstring_and_schema():
    tools = asyncio.run(_session(lambda c: c.list_tools())).tools
    (t,) = tools
    assert t.name == "lookup_order"
    assert "status of an order" in t.description
    assert t.input_schema["properties"]["order_id"]["type"] == "string"


def test_mcp_tool_call_returns_result_and_errors_are_flagged():
    ok = asyncio.run(_session(lambda c: c.call_tool("lookup_order", {"order_id": "A-100"})))
    assert not ok.is_error and ok.content[0].text == "Order A-100: shipped"
    bad = asyncio.run(_session(lambda c: c.call_tool("lookup_order", {"order_id": "Z-9"})))
    assert bad.is_error and "Unknown order id 'Z-9'" in bad.content[0].text
