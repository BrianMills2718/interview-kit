"""check_docs.py passes a complete planning package and names each kind of gap."""

import shutil
import subprocess
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
DOCS = Path(__file__).resolve().parent / "fixtures/adder_docs"
CODE = "def add(a, b):\n    return a + b\n"
TEST = "def test_add():\n    pass\n"


def package(tmp_path):
    shutil.copytree(DOCS, tmp_path / "docs")
    (tmp_path / "add.py").write_text(CODE)
    (tmp_path / "test_add.py").write_text(TEST)
    return tmp_path


def edit(path, old, new):
    text = path.read_text()
    assert old in text, f"{old!r} not in {path.name}"
    path.write_text(text.replace(old, new))


def run(path, *args):
    r = subprocess.run(["python3", str(KIT / "check_docs.py"), str(path), *args], capture_output=True, text=True)
    return r.returncode, r.stdout


def test_complete_package_passes_final(tmp_path):
    code, out = run(package(tmp_path), "--final")
    assert code == 0, out
    assert "FAIL" not in out
    assert "diagram 5 'States': none, with a reason" in out


def test_templates_copied_unfilled_fail_on_placeholders(tmp_path):
    (tmp_path / "docs").mkdir()
    for name in ("DESIGN", "MODEL", "DECISIONS"):
        shutil.copy(KIT / "templates" / f"{name}.md", tmp_path / "docs" / f"{name}.md")
    code, out = run(tmp_path)
    assert code == 1
    for name in ("DESIGN", "MODEL", "DECISIONS"):
        assert f"FAIL docs/{name}.md still has template placeholders" in out, out


def test_missing_diagram_names_it(tmp_path):
    p = package(tmp_path)
    model = p / "docs/MODEL.md"
    text = model.read_text()
    start, end = text.index("## 3. Main sequence"), text.index("## 4. Rules")
    model.write_text(text[:start] + text[end:])
    code, out = run(p)
    assert code == 1 and "lacks diagram '## 3. Main sequence'" in out, out


def test_wrong_diagram_kind_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "sequenceDiagram", "flowchart LR")
    code, out = run(p)
    assert code == 1 and "diagram 3 'Main sequence' needs a ```mermaid sequenceDiagram block" in out, out


def test_states_needs_a_diagram_or_a_reason(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "No states: add is a pure function.", "TODO")
    code, out = run(p)
    assert code == 1 and "diagram 5 'States' needs" in out, out


def test_empty_model_table_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "| floats allowed? | a task line saying so |", "")
    edit(p / "docs/MODEL.md", "| Unknown | What would decide it |\n|---|---|\n", "")
    code, out = run(p)
    assert code == 1 and "lacks a filled '## Unknowns' table" in out, out


def test_design_without_requirement_rows_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/DESIGN.md", '| R1 | "Add two numbers." | integers only |', "")
    code, out = run(p)
    assert code == 1 and "Requirements has no '| R1 |' row" in out, out


def test_design_missing_section_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/DESIGN.md", "## Fixtures", "## Examples")
    code, out = run(p)
    assert code == 1 and "lacks a filled '## Fixtures' section" in out, out


def test_decisions_without_rows_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/DECISIONS.md", "| D1 |", "| x |")
    code, out = run(p)
    assert code == 1 and "no '| D1 |' row" in out, out


def test_final_fails_a_function_the_code_does_not_define(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "| adder | the sum | `add()` |", "| adder | the sum | `add()` and `subtract()` |")
    assert run(p)[0] == 0, "only --final binds names to code"
    code, out = run(p, "--final")
    assert code == 1 and "functions the code does not define: subtract" in out, out


def test_final_fails_a_test_name_no_test_defines(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "`test_add` |", "`test_add_floats` |")
    code, out = run(p, "--final")
    assert code == 1 and "tests no test file defines: test_add_floats" in out, out


def test_kit_and_venv_code_does_not_count(tmp_path):
    p = package(tmp_path)
    (p / "add.py").write_text("x = 1\n")
    for d in ("kit", ".venv/lib"):
        (p / d).mkdir(parents=True)
        (p / d / "add.py").write_text(CODE)
    code, out = run(p, "--final")
    assert code == 1 and "does not define: add" in out, out
