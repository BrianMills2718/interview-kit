"""Grade a practice3 solution, offline (no API key needed): public examples in full, hidden cases by name only.

usage: python practice3/grade.py [solution.py] [evaluate.py]     (defaults: ./solution.py ./evaluate.py)

Agent cases replay a scripted model (its tool calls are fixed), so what is graded is your tools, your
Finding schema, your approval step and your graph wiring, not the model. Metric cases call your
evaluate.py functions on fixed gold and predicted labels; a classify case also runs classify_topic
with a scripted model. For the examples in examples.json every failure shows expected and actual
values. For the hidden cases in hidden.b64 a failure names only the case and which kind of check
failed, like a real hidden test suite. hidden.b64 is zlib+base64: not secret, just not readable by
accident. Exits 1 if any case failed.
"""

import base64
import csv
import copy
import importlib.util
import json
import sys
import zlib
from pathlib import Path

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.types import Command

HERE = Path(__file__).parent
TOL = 1e-6


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The scripted model is the first practice's; reused, not copied.
_base = _load(HERE.parent / "practice" / "grade.py", "practice_grade")
ScriptedModel, script_messages = _base.ScriptedModel, _base.script_messages


def load_posts():
    """posts.csv as csv.DictReader gives it: a list of dicts, every value a string."""
    with open(HERE / "posts.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_agent_case(solution, case, posts):
    """Return a list of (kind, detail) problems; kind is what a hidden case may show."""
    data = {"posts": copy.deepcopy(posts), "flagged": []}
    llm = ScriptedModel(messages=iter(script_messages(case["script"])))
    graph = solution.build_agent(llm, data)
    config = {"configurable": {"thread_id": case["name"]}, "recursion_limit": 50}
    out = graph.invoke({"messages": [HumanMessage(case["message"])]}, config)
    interrupts = 0
    while out.get("__interrupt__"):
        interrupts += 1
        if interrupts > 3:
            return [("approval", "more than 3 interrupts; resume is not reaching the end")]
        pending = out["__interrupt__"]
        answer = case.get("human")
        resume = answer if len(pending) == 1 else {i.id: answer for i in pending}
        out = graph.invoke(Command(resume=resume), config)

    exp, problems = case["expect"], []
    flagged = sorted(sorted(g) for g in data["flagged"])
    if flagged != sorted(sorted(g) for g in exp["flagged"]):
        problems.append(("flagged groups", f"flagged {data['flagged']}, expected {exp['flagged']}"))
    if (interrupts > 0) != exp["interrupted"]:
        problems.append(("approval pause", f"paused for approval: {interrupts > 0}, expected {exp['interrupted']}"))
    tool_text = "\n".join(str(m.content) for m in out["messages"] if isinstance(m, ToolMessage))
    for s in exp.get("tool_output_contains", []):
        if s not in tool_text:
            problems.append(("tool output text", f"no tool output contains {s!r}"))
    for s in exp.get("tool_output_absent", []):
        if s in tool_text:
            problems.append(("tool output text", f"a tool output contains {s!r}, which it should not"))
    finding = out.get("structured_response")
    if finding is None:
        problems.append(("finding missing", "no structured_response (final answer must be a validated Finding)"))
    else:
        for k, v in exp.get("finding", {}).items():
            if getattr(finding, k, None) != v:
                problems.append((f"finding.{k}", f"finding.{k} = {getattr(finding, k, None)!r}, expected {v!r}"))
    return problems


def _close(a, b):
    return isinstance(a, (int, float)) and abs(a - b) <= TOL


def run_metrics_case(evaluate, case):
    """Check per_topic_metrics and confusion_matrix (and classify_topic when the case scripts a model)."""
    exp, problems = case["expect"], []
    pred = case.get("pred")
    if "script" in case:  # predictions come from the candidate's classify_topic and a scripted model
        llm = ScriptedModel(messages=iter(script_messages(case["script"])))
        pred = [evaluate.classify_topic(llm, t) for t in case["texts"]]
        if pred != exp["predictions"]:
            problems.append(("classify_topic", f"classify_topic gave {pred}, expected {exp['predictions']}"))
            return problems
    args = (case["gold"], pred, case["topics"])
    if "raises" in exp:
        for fn in ("per_topic_metrics", "confusion_matrix"):
            try:
                getattr(evaluate, fn)(*args)
                problems.append(("error raised", f"{fn} returned instead of raising {exp['raises']}"))
            except Exception as e:  # any other exception type is also a failure
                if type(e).__name__ != exp["raises"]:
                    problems.append(("error raised", f"{fn} raised {type(e).__name__}, expected {exp['raises']}"))
        return problems
    got = evaluate.confusion_matrix(*args)
    if [list(r) for r in got] != exp["confusion"]:
        problems.append(("confusion matrix", f"confusion_matrix = {got}, expected {exp['confusion']}"))
    metrics = evaluate.per_topic_metrics(*args)
    for topic, want in exp["metrics"].items():
        have = metrics.get(topic, {}) if isinstance(metrics, dict) else {}
        for k, v in want.items():
            if not _close(have.get(k), v):
                problems.append(("metrics", f"{topic} {k} = {have.get(k)!r}, expected {v!r}"))
    return problems


def hidden_cases():
    return json.loads(zlib.decompress(base64.b64decode((HERE / "hidden.b64").read_text())))


def run_all(solution, evaluate, cases, posts=None):
    posts = posts or load_posts()
    results = []
    for case in cases:
        try:
            if case.get("kind") == "metrics":
                problems = run_metrics_case(evaluate, case)
            else:
                problems = run_agent_case(solution, case, posts)
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


def main(path, eval_path):
    solution = _load(path, "solution")
    evaluate = _load(eval_path, "evaluate")
    shown = run_all(solution, evaluate, json.loads((HERE / "examples.json").read_text()))
    hidden = run_all(solution, evaluate, hidden_cases())
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
    args = sys.argv[1:] + ["solution.py", "evaluate.py"][len(sys.argv[1:]):]
    sys.exit(main(args[0], args[1]))
