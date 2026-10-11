"""Grade a practice solution against the known-answer cases, offline (no API key needed).

usage: python practice/grade.py [path/to/solution.py]     (default: ./solution.py)

Each case replays a scripted model (its tool calls are fixed in cases.json), so what is graded
is your tools, your Reply schema, your approval step and your graph wiring, not the model.
Prints one line per case, the reasons for any failure, and a summary; exits 1 if any case failed.
"""

import copy
import importlib.util
import json
import sys
from pathlib import Path

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.types import Command

HERE = Path(__file__).parent


class ScriptedModel(GenericFakeChatModel):
    """Replays fixed AI messages; bind_tools is a no-op so agents can bind tools to it."""

    def bind_tools(self, tools, **kwargs):
        return self


def script_messages(steps):
    out = []
    for i, s in enumerate(steps):
        calls = [{"name": c["name"], "args": c["args"], "id": f"c{i}_{j}"} for j, c in enumerate(s.get("tool_calls", []))]
        out.append(AIMessage(content=s.get("content", ""), tool_calls=calls))
    return out


def run_case(solution, case, data):
    shop = copy.deepcopy(data)
    shop["refunds"] = []
    llm = ScriptedModel(messages=iter(script_messages(case["script"])))
    graph = solution.build_agent(llm, shop)
    config = {"configurable": {"thread_id": case["name"]}, "recursion_limit": 50}
    out = graph.invoke({"messages": [HumanMessage(case["message"])]}, config)
    interrupts = 0
    while out.get("__interrupt__"):
        interrupts += 1
        if interrupts > 3:
            return ["more than 3 interrupts; resume is not reaching the end"]
        pending = out["__interrupt__"]  # two tool calls that each pause in one turn: answer each by id
        answer = case.get("human")
        resume = answer if len(pending) == 1 else {i.id: answer for i in pending}
        out = graph.invoke(Command(resume=resume), config)

    exp, problems = case["expect"], []
    if shop["refunds"] != exp["refunds"]:
        problems.append(f"refunds issued {shop['refunds']}, expected {exp['refunds']}")
    if (interrupts > 0) != exp["interrupted"]:
        problems.append(f"paused for approval: {interrupts > 0}, expected {exp['interrupted']}")
    tool_text = "\n".join(str(m.content) for m in out["messages"] if isinstance(m, ToolMessage))
    for s in exp.get("tool_output_contains", []):
        if s not in tool_text:
            problems.append(f"no tool output contains {s!r}")
    reply = out.get("structured_response")
    if reply is None:
        problems.append("no structured_response (final answer must be a validated Reply)")
    else:
        for k, v in exp.get("reply", {}).items():
            if getattr(reply, k, None) != v:
                problems.append(f"reply.{k} = {getattr(reply, k, None)!r}, expected {v!r}")
    return problems


def run_all(solution, cases=None, data=None):
    cases = cases or json.loads((HERE / "cases.json").read_text())
    data = data or json.loads((HERE / "data.json").read_text())
    results = []
    for case in cases:
        try:
            problems = run_case(solution, case, data)
        except Exception as e:  # a crash is a failed case, with its reason shown
            problems = [f"crashed: {type(e).__name__}: {e}"]
        results.append((case["name"], problems))
    return results


def load(path):
    spec = importlib.util.spec_from_file_location("solution", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    results = run_all(load(sys.argv[1] if len(sys.argv) > 1 else "solution.py"))
    for name, problems in results:
        print(f"{'PASS' if not problems else 'FAIL'} {name}")
        for p in problems:
            print(f"     {p}")
    failed = sum(bool(p) for _, p in results)
    print(f"== grade: {len(results) - failed} passed, {failed} failed of {len(results)} cases")
    sys.exit(1 if failed else 0)
