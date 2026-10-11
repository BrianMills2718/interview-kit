"""Expose a tool over MCP (Model Context Protocol) with the official Python SDK (mcp 2.x).

Run:   uv run mcp dev examples/mcp_server.py      (opens the MCP Inspector)
       python examples/mcp_server.py               (stdio, for a desktop or IDE client)
Test:  pytest -v tests/test_mcp_server.py          (in-memory client, no network)
"""

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

ORDERS = {"A-100": "shipped", "A-101": "processing"}

mcp = MCPServer("orders")


@mcp.tool()
def lookup_order(order_id: str) -> str:
    """Return the status of an order given its ID, e.g. 'A-100'."""
    if order_id not in ORDERS:
        # ToolError: the message reaches the model. Any other exception is treated as a crash
        # and the client sees only "Error executing tool lookup_order" (mcp 2.x hides it).
        raise ToolError(f"Unknown order id {order_id!r}")
    return f"Order {order_id}: {ORDERS[order_id]}"


if __name__ == "__main__":
    mcp.run()  # stdio by default
