"""check.sh must pass a well-formed project and fail each kind of broken one."""

import re
import shutil
import subprocess
from pathlib import Path

CHECK = Path(__file__).resolve().parents[1] / "check.sh"
DOCS = Path(__file__).resolve().parent / "fixtures/adder_docs"

PLAN = """# Plan
## Goal
Add two numbers.
## Done when
- [x] `pytest -v` -> test_add PASSED
## Steps
1. write add
## System model
See docs/MODEL.md.
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


def project(tmp_path, plan=PLAN, readme=README, code=CODE, test=TEST, docs=True):
    if docs:
        shutil.copytree(DOCS, tmp_path / "docs")
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


def test_quoted_requirement_with_angle_brackets_is_not_a_placeholder(tmp_path):
    code, out = run(project(tmp_path, plan=PLAN + "## Assumptions\n- tool returns `P-2: <policy text>` lines\n"))
    assert code == 0, out


def test_unfilled_template_line_is_a_placeholder(tmp_path):
    code, out = run(project(tmp_path, plan=PLAN + "## Goal\n<2-3 sentences in my words, plus the exact requirement lines quoted from the prompt>\n"))
    assert code == 1 and "placeholders" in out


def test_no_tests_yet_waits_before_final_and_fails_final(tmp_path):
    p = project(tmp_path, test=None)
    code, out = run(p)
    assert code == 0 and "WAIT no test files yet" in out, out
    code, out = run(p, "--final")
    assert code == 1 and "no test files found" in out


def test_ai_section_needs_the_word_not_the_letters(tmp_path):
    readme = README.replace("## How I used the AI\n", "## Details\n")
    code, out = run(project(tmp_path, readme=readme), "--final")
    assert code == 1 and "'AI'" in out


def test_uses_the_project_venv_python(tmp_path):
    p = project(tmp_path)
    (p / ".venv/bin").mkdir(parents=True)
    marker = p / "venv_used"
    (p / ".venv/bin/python").write_text(f'#!/usr/bin/env bash\ntouch "{marker}"\nexec python3 "$@"\n')
    (p / ".venv/bin/python").chmod(0o755)
    code, out = run(p)
    assert code == 0, out
    assert marker.exists()


def test_plan_without_system_model_fails(tmp_path):
    code, out = run(project(tmp_path, plan=PLAN.split("## System model")[0]))
    assert code == 1 and "PLAN.md lacks '## System model'" in out


def test_empty_system_model_section_fails(tmp_path):
    code, out = run(project(tmp_path, plan=PLAN.split("## System model")[0] + "## System model\n\n## Risks\n- none\n"))
    assert code == 1 and "System model section is empty" in out


def test_system_model_pointing_at_docs_passes(tmp_path):
    code, out = run(project(tmp_path))
    assert code == 0 and "PASS PLAN.md has a System model" in out


def test_missing_planning_package_fails(tmp_path):
    code, out = run(project(tmp_path, docs=False))
    assert code == 1
    for name in ("DESIGN", "MODEL", "DECISIONS"):
        assert f"FAIL docs/{name}.md missing" in out, out


def test_package_results_are_counted(tmp_path):
    code, out = run(project(tmp_path), "--final")
    assert "PASS docs/MODEL.md diagram 3 'Main sequence' is a sequenceDiagram" in out, out
    assert "PASS docs/MODEL.md names 1 functions, all defined in the code" in out, out


def test_planner_notes_name_every_section_check_sh_requires():
    """The planner role and plan skill tell the planner to write each heading check.sh demands."""
    required = set(re.findall(r"grep -q '\^(## [^']+)' PLAN\.md", CHECK.read_text()))
    assert "## System model" in required, f"check.sh no longer requires a System model: {required}"
    for note in ["agents/planner.md", "skills/plan/SKILL.md", "PLAN.template.md"]:
        text = (CHECK.parent / note).read_text()
        missing = [h for h in required if h not in text]
        assert not missing, f"{note} does not name {missing}"


def test_ticked_item_with_placeholder_result_fails_final(tmp_path):
    """A done-when item ticked before its check ran still shows the expected-result placeholder."""
    p = project(tmp_path, plan=PLAN.replace("-> test_add PASSED", "-> N passed, 0 failed"))
    assert run(p)[0] == 0
    code, out = run(p, "--final")
    assert code == 1 and "placeholder result" in out, out
