"""The practice grader passes the reference solution and fails broken copies of it (so it can fail)."""

import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "practice"))
import grade  # noqa: E402

REFERENCE = (ROOT / "practice/reference/solution.py").read_text()


def module_from(source):
    mod = types.ModuleType("solution")
    exec(compile(source, "solution.py", "exec"), mod.__dict__)
    return mod


def failed(results):
    return sorted(name for name, problems in results if problems)


def test_reference_passes_every_case():
    results = grade.run_all(module_from(REFERENCE))
    assert len(results) == 8
    assert failed(results) == []


@pytest.mark.parametrize("broken, expect_failed", [
    # no approval step: large refunds go through without pausing
    (("APPROVAL_OVER = 50", "APPROVAL_OVER = 500"), ["large-refund-approved", "large-refund-declined"]),
    # lenient schema: an invalid category is accepted instead of retried
    (('category: Literal["refund", "shipping", "damaged", "other"]', "category: str"), ["unknown-order-and-invalid-reply"]),
    # no idempotency: the same order is refunded twice
    (('if order_id in shop["refunds"]:', "if False:"), ["refund-twice"]),
])
def test_grader_fails_a_broken_solution(broken, expect_failed):
    old, new = broken
    assert old in REFERENCE
    assert failed(grade.run_all(module_from(REFERENCE.replace(old, new)))) == expect_failed


def test_problem_removal_command_deletes_the_reference(tmp_path):
    """The command PROBLEM.md gives removes kit/practice/reference and nothing else, without rm -rf."""
    import re
    import shutil
    import subprocess

    problem = (ROOT / "practice/PROBLEM.md").read_text()
    assert "rm -rf" not in problem, "a host safety hook may block rm -rf; use the Python command"
    commands = [c for c in re.findall(r"`([^`]+)`", problem) if "shutil.rmtree" in c]
    assert len(commands) == 1, commands
    shutil.copytree(ROOT / "practice", tmp_path / "kit/practice", ignore=shutil.ignore_patterns("__pycache__"))
    subprocess.run(commands[0], shell=True, cwd=tmp_path, check=True)
    assert not (tmp_path / "kit/practice/reference").exists()
    assert (tmp_path / "kit/practice/grade.py").exists()


def test_filled_template_passes_check(tmp_path):
    """Filling every placeholder in PLAN.template.md gives a plan check.sh accepts, Shape section included."""
    import re
    import subprocess

    template = (ROOT / "PLAN.template.md").read_text()
    assert "## Shape" in template
    (tmp_path / "PLAN.md").write_text(re.sub(r"<[^<>]+>", "filled", template))
    (tmp_path / "test_x.py").write_text("def test_x():\n    assert 1 + 1 == 2\n")
    r = subprocess.run(["bash", str(ROOT / "check.sh"), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
