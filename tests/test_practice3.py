"""The practice3 grader passes the reference, fails broken copies, hides expected values, and the data is reproducible."""

import csv
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
P3 = ROOT / "practice3"
_spec = importlib.util.spec_from_file_location("practice3_grade", P3 / "grade.py")
grade = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(grade)

REFERENCE = (P3 / "reference/solution.py").read_text(encoding="utf-8")
EVALUATE = (P3 / "reference/evaluate.py").read_text(encoding="utf-8")
EXAMPLES = json.loads((P3 / "examples.json").read_text(encoding="utf-8"))


def module_from(source, name):
    mod = types.ModuleType(name)
    mod.__file__ = str(P3 / "reference" / f"{name}.py")
    exec(compile(source, f"{name}.py", "exec"), mod.__dict__)
    return mod


def failed(results):
    return sorted(name for name, problems in results if problems)


def run(solution_src=REFERENCE, evaluate_src=EVALUATE, cases=None):
    cases = grade.hidden_cases() if cases is None else cases
    return grade.run_all(module_from(solution_src, "solution"), module_from(evaluate_src, "evaluate"), cases)


def test_hidden_file_matches_its_source():
    """hidden.b64 is rebuilt from reference/hidden_cases.json; a stale encoding would grade old cases."""
    source = json.loads((P3 / "reference/hidden_cases.json").read_text(encoding="utf-8"))
    assert grade.hidden_cases() == source
    assert not {c["name"] for c in source} & {c["name"] for c in EXAMPLES}


def test_reference_passes_every_case():
    assert failed(run(cases=EXAMPLES)) == []
    hidden = run()
    assert len(hidden) == 12
    assert failed(hidden) == []


@pytest.mark.parametrize("target, broken, expect_failed", [
    # z compared with > instead of "at or above"
    ("solution", ("if score >= z:", "if score > z:"), ["z-threshold-is-inclusive"]),
    # z not rounded before comparing: 2.993 lets in a day whose rounded z is 2.99
    ("solution", ("score = round((c - mean) / std, 2)", "score = (c - mean) / std"), ["z-threshold-is-inclusive"]),
    # window exclusive instead of inclusive
    ("solution", ("<= timedelta(minutes=window_minutes)", "< timedelta(minutes=window_minutes)"), ["window-boundary"]),
    # posts counted instead of distinct accounts
    ("solution", ('if len({p["account_id"] for p in window}) >= min_accounts:', "if len(window) >= min_accounts:"),
     ["same-account-counts-once"]),
    # flag recorded before the analyst answers (and so a "no" still records it)
    ("solution", ("answer = interrupt(", 'data["flagged"].append(group)\n        answer = interrupt('),
     ["flag-declined-records-nothing", "flag-input-checked-before-pause"]),
    # self-replies counted as links
    ("solution", (' and target["account_id"] != p["account_id"]', ""), ["hub-ties-by-account-id", "self-replies-not-counted"]),
    # an empty language string treated as a language
    ("solution", ("if lang and lang not in LANGUAGES:", "if lang not in LANGUAGES:"),
     ["count-empty-filter-means-all", "count-range-matches-nothing"]),
    # lenient schema: a coordination finding with no evidence is accepted instead of retried
    ("solution", ('if self.question_type == "coordination" and not self.evidence_post_ids:', "if False:"),
     ["coordination-finding-needs-evidence"]),
    # precision divides by zero for a topic never predicted
    ("evaluate", ('"precision": tp / predicted if predicted else 0.0', '"precision": tp / predicted'), ["precision-zero-division"]),
    # labels outside the topic list not rejected
    ("evaluate", ("        if label not in topics:\n            raise", "        if False:\n            raise"),
     ["prediction-outside-topics-raises"]),
])
def test_grader_fails_a_broken_solution(target, broken, expect_failed):
    old, new = broken
    source = REFERENCE if target == "solution" else EVALUATE
    assert old in source
    mutated = source.replace(old, new)
    results = run(solution_src=mutated) if target == "solution" else run(evaluate_src=mutated)
    assert failed(results) == expect_failed


def test_trivial_metrics_fail():
    """All-zero metrics (and an all-zero matrix) must fail the metric cases, shown and hidden."""
    trivial = EVALUATE + (
        "\ndef per_topic_metrics(gold, pred, topics):\n"
        "    _check(gold, pred, topics)\n"
        "    return {t: {'precision': 0.0, 'recall': 0.0, 'support': 0} for t in topics}\n"
        "\ndef confusion_matrix(gold, pred, topics):\n"
        "    _check(gold, pred, topics)\n"
        "    return [[0] * len(topics) for _ in topics]\n")
    assert failed(run(evaluate_src=trivial)) == ["precision-zero-division"]
    assert failed(run(evaluate_src=trivial, cases=EXAMPLES)) == ["classifier-metrics"]


def test_hidden_failures_print_no_expected_values(tmp_path, capsys):
    """Break several rules at once; the report must name cases and check kinds, never an expected string."""
    broken = REFERENCE
    for old, new in [("if score >= z:", "if score > z:"),
                     ('if len({p["account_id"] for p in window}) >= min_accounts:', "if len(window) >= min_accounts:"),
                     (' and target["account_id"] != p["account_id"]', ""),
                     ("if lang and lang not in LANGUAGES:", "if lang not in LANGUAGES:")]:
        broken = broken.replace(old, new)
    (tmp_path / "solution.py").write_text(broken, encoding="utf-8")
    (tmp_path / "evaluate.py").write_text(
        EVALUATE.replace('"precision": tp / predicted if predicted else 0.0', '"precision": tp / predicted'), encoding="utf-8")
    assert grade.main(tmp_path / "solution.py", tmp_path / "evaluate.py") == 1
    out = capsys.readouterr().out
    secrets = set()
    for case in grade.hidden_cases():
        e = case["expect"]
        secrets |= set(e.get("tool_output_contains", [])) | {str(v) for v in e.get("finding", {}).values()}
        for m in e.get("metrics", {}).values():
            secrets |= {str(v) for v in m.values()}
    names = " ".join(c["name"] for c in grade.hidden_cases())  # case names are printed on purpose
    leaked = [s for s in secrets if len(s) > 6 and s in out and s not in names]
    assert leaked == []
    assert "FAIL hidden: z-threshold-is-inclusive" in out and "failed check: tool output text" in out
    assert "FAIL hidden: precision-zero-division" in out and "failed check: crashed" in out


def test_data_is_reproducible(tmp_path):
    """make_data.py regenerates the committed CSVs byte for byte."""
    r = subprocess.run([sys.executable, str(P3 / "make_data.py"), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    for name in ("posts.csv", "labels.csv"):
        assert (tmp_path / name).read_bytes() == (P3 / name).read_bytes(), name


def test_planted_signals_are_where_the_cases_expect():
    """Membership, not counts: the spike days, the coordinated accounts and posts, the empty day, the gold topics."""
    rows = list(csv.DictReader(open(P3 / "posts.csv", encoding="utf-8")))
    per_day = {}
    for r in rows:
        per_day[r["date"][:10]] = per_day.get(r["date"][:10], 0) + 1
    top_two = sorted(per_day, key=per_day.get, reverse=True)[:2]
    assert sorted(top_two) == ["2026-03-12", "2026-03-21"]
    assert "2026-03-25" not in per_day
    norm = lambda t: " ".join(t.lower().split())
    group = [r for r in rows if r["date"].startswith("2026-03-08 14:0")
             and norm(r["text"]).startswith("мост на северной улице")]
    assert [r["post_id"] for r in group] == ["P0091", "P0092", "P0093", "P0094", "P0095", "P0096"]
    assert sorted({r["account_id"] for r in group}) == ["A34", "A35", "A36", "A37", "A38"]
    assert {r["language"] for r in rows} == {"en", "es", "ru"}
    labels = list(csv.DictReader(open(P3 / "labels.csv", encoding="utf-8")))
    assert len(labels) == 60 and {r["topic"] for r in labels} == {"transport", "weather", "sports", "prices"}
    ids = {r["post_id"] for r in rows}
    assert all(r["post_id"] in ids for r in labels)
    assert not {r["post_id"] for r in labels} & {r["post_id"] for r in group}


def test_reference_evaluation_runs_offline():
    """evaluate.py prints a report with the stand-in model and no API key."""
    r = subprocess.run([sys.executable, str(P3 / "reference/evaluate.py")], capture_output=True, text=True,
                       env={k: v for k, v in __import__("os").environ.items() if k != "EVAL_MODEL"})
    assert r.returncode == 0, r.stderr
    assert "confusion (rows gold, columns predicted)" in r.stdout and "wrong" in r.stdout


def test_problem_removal_command_deletes_the_reference(tmp_path):
    problem = (P3 / "PROBLEM.md").read_text(encoding="utf-8")
    assert "rm -rf" not in problem
    commands = [c for c in re.findall(r"`([^`]+)`", problem) if "shutil.rmtree" in c]
    assert len(commands) == 1, commands
    for d in ("practice", "practice2", "practice3"):
        shutil.copytree(ROOT / d, tmp_path / "kit" / d, ignore=shutil.ignore_patterns("__pycache__"))
    subprocess.run(commands[0], shell=True, cwd=tmp_path, check=True)
    for d in ("practice", "practice2", "practice3"):
        assert not (tmp_path / "kit" / d / "reference").exists(), d
    # the grader still runs without the reference folder (it needs only hidden.b64 and practice/grade.py)
    (tmp_path / "solution.py").write_text(REFERENCE, encoding="utf-8")
    (tmp_path / "evaluate.py").write_text(EVALUATE, encoding="utf-8")
    r = subprocess.run([sys.executable, "kit/practice3/grade.py"], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "== grade: 15 passed, 0 failed of 15 cases (12 hidden)" in r.stdout


@pytest.mark.parametrize("page", ["practice/PROBLEM.md", "practice2/PROBLEM.md"])
def test_earlier_problems_also_remove_this_reference(page):
    """A practice-1 or practice-2 run must not leave practice3's answer readable."""
    assert "'kit/practice3/reference'" in (ROOT / page).read_text(encoding="utf-8")
