---
name: mcp-and-a2a
description: What MCP (agent-to-tool) and A2A (agent-to-agent) are, when to use each, and a tested MCP server. Use when a task mentions tools over a protocol, tool servers, or agents talking to agents.
---

# Skill: MCP and A2A in one page

Checked 2026-10-11 against the MCP spec 2026-07-28 (modelcontextprotocol.io/specification),
the `mcp` Python SDK 2.3.0, and the A2A spec 1.0.0 (a2a-protocol.org/latest/specification).

## Which one

| | MCP (Model Context Protocol) | A2A (Agent2Agent) |
|---|---|---|
| Connects | an AI app to **tools and data** | an agent to **another agent** |
| The other side is | a server exposing functions | an opaque agent doing a task |
| Use when | the model needs to call a function or read a resource | work is handed to an agent you do not control |

In a take-home, plain LangChain `@tool` functions are usually enough. Use MCP if the task asks
for it or the tools must be shared across apps; mention A2A as the next step, not the core.

## MCP: the facts that matter

- JSON-RPC 2.0 messages. Roles: **host** (the app), **client** (one connector per server),
  **server**.
- Servers offer **tools** (functions the model calls), **resources** (data to read) and
  **prompts** (templates). Clients may offer **elicitation** (asking the user for input).
- Standard transports: **stdio** (client launches the server as a subprocess) and **Streamable
  HTTP** (one HTTP endpoint; replies as JSON or an SSE stream).
- Security: tools are arbitrary code; the host must get user consent before calling one, and
  tool descriptions from an untrusted server are untrusted input.

Tested server (`examples/mcp_server.py`, `tests/test_mcp_server.py`):

```python
from mcp.server import MCPServer                     # mcp 2.x; 1.x called it FastMCP
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("orders")

@mcp.tool()
def lookup_order(order_id: str) -> str:
    """Return the status of an order given its ID, e.g. 'A-100'."""   # the model reads this
    if order_id not in ORDERS:
        raise ToolError(f"Unknown order id {order_id!r}")   # message reaches the model
    return f"Order {order_id}: {ORDERS[order_id]}"
```

- Raise `ToolError` for expected failures: any other exception reaches the client only as
  `Error executing tool lookup_order` (found by the test, not in most tutorials).
- Test without a network: `async with mcp.Client(server) as c: await c.call_tool(...)`;
  results use `is_error` and `input_schema` (snake_case in 2.x).
- Into LangGraph: the `langchain-mcp-adapters` package (`MultiServerMCPClient`, then
  `await client.get_tools()`) turns server tools into LangChain tools. Untested here: check
  the installed version's docs before using it.

## A2A: the facts that matter

- An agent publishes an **Agent Card** (JSON: identity, skills, endpoint, auth) at
  `https://{domain}/.well-known/agent-card.json`.
- Work is a **Task** with states such as submitted, working, input-required, completed,
  failed. **Messages** (role user or agent) carry **Parts** (text, file, data); results come
  back as **Artifacts**.
- Bindings: JSON-RPC (`SendMessage`, `SendStreamingMessage`), gRPC, and HTTP+JSON. Streaming
  uses Server-Sent Events.
- Python SDK: `a2a-sdk`. Untested here.

## Say this in the README

Name which protocol you used and why, what you would expose over MCP or A2A with more time,
and the security point: tool servers run code, so calls need consent and tool text is untrusted.
