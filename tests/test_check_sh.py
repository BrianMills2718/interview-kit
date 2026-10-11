"""check.sh must pass a well-formed project and fail each kind of broken one."""

import subprocess
from pathlib import Path

CHECK = Path(__file__).resolve().parents[1] / "check.sh"

PLAN = """# Plan
## Goal
Add two numbers.
## Done when
- [x] `pytest -v` -> test_add PASSED
## Steps
1. write add
"""
README = """# Adder
## Run it
## Approach
## Design decisions
## How I used the AI
## Limitations
"""
CODE = "def add(a, b):\n    return a + b\n"
TEST = "from add import add\n\ndef test_add():\n    assert add(2, 3) == 5\n"


def project(tmp_path, plan=PLAN, readme=README, code=CODE, test=TEST):
    for name, text in {"PLAN.md": plan, "README.md": readme, "add.py": code, "test_add.py": test}.items():
        if text is not None:
            (tmp_path / name).write_text(text)
    return tmp_path


def run(path, *args):
    r = subprocess.run(["bash", str(CHECK), *args, str(path)], capture_output=True, text=True)
    return r.returncode, r.stdout


def test_good_project_passes_final(tmp_path):
    code, out = run(project(tmp_path), "--final")
    assert code == 0, out
    assert "0 failed" in out


def test_missing_plan_fails(tmp_path):
    code, out = run(project(tmp_path, plan=None))
    assert code == 1 and "PLAN.md missing" in out


def test_template_placeholders_fail(tmp_path):
    code, out = run(project(tmp_path, plan=PLAN + "- <ambiguity> -> <reading>\n"))
    assert code == 1 and "placeholders" in out


def test_failing_test_fails(tmp_path):
    code, out = run(project(tmp_path, code="def add(a, b):\n    return a - b\n"))
    assert code == 1 and "tests failed" in out


def test_unticked_item_fails_only_in_final(tmp_path):
    p = project(tmp_path, plan=PLAN.replace("- [x]", "- [ ]"))
    assert run(p)[0] == 0
    code, out = run(p, "--final")
    assert code == 1 and "not ticked" in out


def test_readme_without_ai_section_fails_final(tmp_path):
    code, out = run(project(tmp_path, readme=README.replace("## How I used the AI\n", "")), "--final")
    assert code == 1 and "'AI'" in out
