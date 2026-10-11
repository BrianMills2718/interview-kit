"""Grade a practice2 solution, offline (no API key needed): public examples in full, hidden cases by name only.

usage: python practice2/grade.py [path/to/solution.py]     (default: ./solution.py)

Each case replays a scripted model (its tool calls are fixed), so what is graded is your tools,
your Verdict schema, your approval step and your graph wiring, not the model.
For the examples in examples.json every failure shows expected and actual values. For the hidden
cases in hidden.b64 a failure names only the case and which kind of check failed, like a real
hidden test suite. hidden.b64 is zlib+base64: not secret, just not readable by accident.
Exits 1 if any case failed.
"""

import base64
import copy
import importlib.util
import json
import sys
import zlib
from pathlib import Path

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.types import Command

HERE = Path(__file__).parent


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The scripted model is the first practice's; reused, not copied.
_base = _load(HERE.parent / "practice" / "grade.py", "practice_grade")
ScriptedModel, script_messages = _base.ScriptedModel, _base.script_messages


def run_case(solution, case, data):
    """Return a list of (kind, detail) problems; kind is what a hidden case may show."""
    soc = copy.deepcopy(data)
    soc["blocked"] = []
    llm = ScriptedModel(messages=iter(script_messages(case["script"])))
    graph = solution.build_agent(llm, soc)
    config = {"configurable": {"thread_id": case["name"]}, "recursion_limit": 50}
    out = graph.invoke({"messages": [HumanMessage(case["message"])]}, config)
    interrupts = 0
    while out.get("__interrupt__"):
        interrupts += 1
        if interrupts > 3:
            return [("approval", "more than 3 interrupts; resume is not reaching the end")]
        pending = out["__interrupt__"]  # several blocks in one turn pause together: answer each by id
        answer = case.get("human")
        resume = answer if len(pending) == 1 else {i.id: answer for i in pending}
        out = graph.invoke(Command(resume=resume), config)

    exp, problems = case["expect"], []
    if sorted(soc["blocked"]) != sorted(exp["blocked"]):  # order within one turn is not specified
        problems.append(("blocked IPs", f"blocked {soc['blocked']}, expected {exp['blocked']}"))
    if (interrupts > 0) != exp["interrupted"]:
        problems.append(("approval pause", f"paused for approval: {interrupts > 0}, expected {exp['interrupted']}"))
    tool_text = "\n".join(str(m.content) for m in out["messages"] if isinstance(m, ToolMessage))
    for s in exp.get("tool_output_contains", []):
        if s not in tool_text:
            problems.append(("tool output text", f"no tool output contains {s!r}"))
    for s in exp.get("tool_output_absent", []):
        if s in tool_text:
            problems.append(("tool output text", f"a tool output contains {s!r}, which it should not"))
    verdict = out.get("structured_response")
    if verdict is None:
        problems.append(("verdict missing", "no structured_response (final answer must be a validated Verdict)"))
    else:
        for k, v in exp.get("verdict", {}).items():
            if getattr(verdict, k, None) != v:
                problems.append((f"verdict.{k}", f"verdict.{k} = {getattr(verdict, k, None)!r}, expected {v!r}"))
    return problems


def hidden_cases():
    return json.loads(zlib.decompress(base64.b64decode((HERE / "hidden.b64").read_text())))


def run_all(solution, cases, data=None):
    data = data or json.loads((HERE / "data.json").read_text())
    results = []
    for case in cases:
        try:
            problems = run_case(solution, case, data)
        except Exception as e:  # a crash is a failed case
            problems = [("crashed", f"{type(e).__name__}: {e}")]
        results.append((case["name"], problems))
    return results


def report(results, hidden):
    lines = []
    for name, problems in results:
        lines.append(f"{'PASS' if not problems else 'FAIL'} {'hidden: ' if hidden else ''}{name}")
        if hidden:  # kinds only, never expected values
            kinds = sorted({k for k, _ in problems})
            if kinds:
                lines.append(f"     failed check: {', '.join(kinds)}")
        else:
            lines += [f"     {d}" for _, d in problems]
    return lines


def main(path):
    solution = _load(path, "solution")
    shown = run_all(solution, json.loads((HERE / "examples.json").read_text()))
    hidden = run_all(solution, hidden_cases())
    print("\n".join(report(shown, False) + report(hidden, True)))
    failed = sum(bool(p) for _, p in shown + hidden)
    total = len(shown) + len(hidden)
    print(f"== grade: {total - failed} passed, {failed} failed of {total} cases ({len(hidden)} hidden)")
    return 1 if failed else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["--encode"]:  # maintainers: rebuild hidden.b64 from reference/hidden_cases.json
        raw = (HERE / "reference" / "hidden_cases.json").read_bytes()
        (HERE / "hidden.b64").write_text(base64.b64encode(zlib.compress(raw, 9)).decode() + "\n")
        sys.exit(0)
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "solution.py"))
