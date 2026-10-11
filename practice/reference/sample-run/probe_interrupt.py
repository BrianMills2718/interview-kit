"""Probe: how LangGraph's interrupt() inside a create_agent tool pauses and resumes (run, don't trust memory)."""

from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt

ENTRIES: list[str] = []


class Scripted(GenericFakeChatModel):
    """Fake model that replays fixed messages; bind_tools is a no-op."""

    def bind_tools(self, tools, **kw):
        """Return self so create_agent can bind tools to it."""
        return self


@tool
def risky(x: str) -> str:
    """Ask a human before acting on x."""
    ENTRIES.append("enter")
    print(f"  risky() entered (entry #{len(ENTRIES)})")
    answer = interrupt({"question": f"ok to act on {x}?"})
    print(f"  interrupt() returned {answer!r}")
    return f"acted on {x}: {answer}"


def main():
    """Run one pause and one resume, printing what the caller sees."""
    llm = Scripted(messages=iter([
        AIMessage(content="", tool_calls=[{"name": "risky", "args": {"x": "A"}, "id": "c1"}]),
        AIMessage(content="done"),
    ]))
    graph = create_agent(llm, tools=[risky], checkpointer=InMemorySaver())
    cfg = {"configurable": {"thread_id": "t1"}}
    print("invoke #1")
    out = graph.invoke({"messages": [HumanMessage("go")]}, cfg)
    print("caller got __interrupt__:", out.get("__interrupt__"))
    print("next nodes in checkpoint:", graph.get_state(cfg).next)
    print("invoke #2 with Command(resume='yes'), same thread_id")
    out = graph.invoke(Command(resume="yes"), cfg)
    print("caller got __interrupt__:", out.get("__interrupt__"))
    print("last tool message:", [m.content for m in out["messages"] if m.type == "tool"])
    print(f"risky() entered {len(ENTRIES)} times")


if __name__ == "__main__":
    main()
