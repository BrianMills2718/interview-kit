"""The hidden-case grader passes the reference, fails broken copies, and never prints a hidden expected value."""

import base64
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import types
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("practice2_grade", ROOT / "practice2/grade.py")
grade = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(grade)

REFERENCE = (ROOT / "practice2/reference/solution.py").read_text()
EXAMPLES = json.loads((ROOT / "practice2/examples.json").read_text())


def module_from(source):
    mod = types.ModuleType("solution")
    exec(compile(source, "solution.py", "exec"), mod.__dict__)
    return mod


def failed(results):
    return sorted(name for name, problems in results if problems)


def test_hidden_file_matches_its_source():
    """hidden.b64 is rebuilt from reference/hidden_cases.json; a stale encoding would grade old cases."""
    source = json.loads((ROOT / "practice2/reference/hidden_cases.json").read_text())
    assert grade.hidden_cases() == source
    assert not {c["name"] for c in source} & {c["name"] for c in EXAMPLES}


def test_reference_passes_every_case():
    assert failed(grade.run_all(module_from(REFERENCE), EXAMPLES)) == []
    hidden = grade.run_all(module_from(REFERENCE), grade.hidden_cases())
    assert len(hidden) == 10
    assert failed(hidden) == []


@pytest.mark.parametrize("broken, expect_failed", [
    # internal addresses not refused: the db host's address goes to a reviewer instead
    (("if addr in INTERNAL:", "if False:"), ["internal-ip-refused"]),
    # no idempotency: the second block of the same address blocks it twice
    (('if ip in soc["blocked"]:', "if False:"), ["second-block-is-a-no-op"]),
    # off-by-one limit: the fourth search is already refused
    (('if searches["n"] > SEARCH_LIMIT:', 'if searches["n"] >= SEARCH_LIMIT:'), ["search-limit-enforced"]),
    # host names compared as given
    (("h = hosts.get(name.lower())", "h = hosts.get(name)"), ["host-names-ignore-case"]),
    # lenient schema: a high verdict with no evidence is accepted instead of retried
    (('if self.severity in ("high", "critical") and not self.evidence:', "if False:"), ["high-without-evidence-is-retried"]),
    # oldest first instead of newest first
    (('key=lambda l: l["ts"], reverse=True', 'key=lambda l: l["ts"]'), ["host-names-ignore-case"]),
])
def test_grader_fails_a_broken_solution(broken, expect_failed):
    old, new = broken
    assert old in REFERENCE
    assert failed(grade.run_all(module_from(REFERENCE.replace(old, new)), grade.hidden_cases())) == expect_failed


def test_hidden_failures_print_no_expected_values(tmp_path, capsys):
    """Break every rule at once; the report must name cases and check kinds, never an expected string."""
    broken = REFERENCE
    for old, new in [("if addr in INTERNAL:", "if False:"), ('if ip in soc["blocked"]:', "if False:"),
                     ("h = hosts.get(name.lower())", "h = hosts.get(name)"),
                     ('if self.severity in ("high", "critical") and not self.evidence:', "if False:"),
                     ('severity: Literal["low", "medium", "high", "critical"]', "severity: str")]:
        broken = broken.replace(old, new)
    path = tmp_path / "solution.py"
    path.write_text(broken)
    assert grade.main(path) == 1
    out = capsys.readouterr().out
    secrets = set()
    for case in grade.hidden_cases():
        e = case["expect"]
        secrets |= set(e["tool_output_contains"]) | {str(v) for v in e.get("verdict", {}).values()}
        secrets |= {str(e["blocked"])}
    leaked = [s for s in secrets if len(s) > 6 and s in out]
    assert leaked == []
    assert "FAIL hidden: internal-ip-refused" in out and "failed check: approval pause, tool output text" in out


def test_problem_removal_command_deletes_the_reference(tmp_path):
    problem = (ROOT / "practice2/PROBLEM.md").read_text()
    assert "rm -rf" not in problem
    commands = [c for c in re.findall(r"`([^`]+)`", problem) if "shutil.rmtree" in c]
    assert len(commands) == 1, commands
    shutil.copytree(ROOT / "practice", tmp_path / "kit/practice", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "practice2", tmp_path / "kit/practice2", ignore=shutil.ignore_patterns("__pycache__"))
    subprocess.run(commands[0], shell=True, cwd=tmp_path, check=True)
    assert not (tmp_path / "kit/practice2/reference").exists()
    assert not (tmp_path / "kit/practice/reference").exists()  # the first answer shows this one's patterns
    assert (tmp_path / "kit/practice/grade.py").exists()
    # the grader still runs without the reference folder (it needs only hidden.b64 and practice/grade.py)
    (tmp_path / "solution.py").write_text(REFERENCE)
    r = subprocess.run([sys.executable, "kit/practice2/grade.py", "solution.py"], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "== grade: 13 passed, 0 failed of 13 cases (10 hidden)" in r.stdout
