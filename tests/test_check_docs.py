"""check_docs.py passes a complete planning package and names each kind of gap."""

import shutil
import subprocess
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
DOCS = Path(__file__).resolve().parent / "fixtures/adder_docs"
CODE = "def add(a, b):\n    return a + b\n"
TEST = "def test_add():\n    pass\n"
STATES = """**Answer:** a request waits for approval before it is paid.
```mermaid
stateDiagram-v2
  [*] --> Requested
  Requested --> Paused: over the limit
  Paused --> Paid: approved
  Paid --> [*]
```

Forbidden:
- Requested --> Paid
"""
STATE_ROWS = """| [*] --> Requested | state machine | `test_add` |
| Requested --> Paused | state machine | `test_add` |
| Paused --> Paid | state machine | `test_add` |
| Paid --> [*] | state machine | `test_add` |
| Requested --> Paid | forbidden | `test_add` |
"""


def package(tmp_path):
    shutil.copytree(DOCS, tmp_path / "docs")
    (tmp_path / "add.py").write_text(CODE)
    (tmp_path / "test_add.py").write_text(TEST)
    return tmp_path


def with_states(tmp_path):
    """The fixture package with a state machine, its forbidden line and one test row per arrow."""
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "No states: add is a pure function.\n", STATES)
    model = p / "docs/MODEL.md"
    model.write_text(model.read_text() + STATE_ROWS)
    return p


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
    assert "'State machine': none, with a reason" in out


def test_package_with_state_machine_passes_final(tmp_path):
    code, out = run(with_states(tmp_path), "--final")
    assert code == 0, out
    assert "tests cover all 4 state transitions" in out
    assert "tests cover all 1 forbidden transitions" in out


def test_templates_copied_unfilled_fail_on_placeholders(tmp_path):
    (tmp_path / "docs").mkdir()
    for name in ("PRD", "MODEL", "DECISIONS"):
        shutil.copy(KIT / "templates" / f"{name}.md", tmp_path / "docs" / f"{name}.md")
    code, out = run(tmp_path)
    assert code == 1
    for name in ("PRD", "MODEL", "DECISIONS"):
        assert f"FAIL docs/{name}.md still has template placeholders" in out, out


def test_missing_prd_section_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/PRD.md", "## Risks", "## Worries")
    code, out = run(p)
    assert code == 1 and "docs/PRD.md lacks a filled '## Risks' section" in out, out


def test_prd_without_requirement_rows_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/PRD.md", '| R1 | "Add two numbers." | integers only |', "")
    code, out = run(p)
    assert code == 1 and "Requirements has no '| R1 |' row" in out, out


def test_no_failure_use_case_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/PRD.md", "| UC2 | failure |", "| UC2 | normal |")
    code, out = run(p)
    assert code == 1 and "no use case of Kind 'failure' or 'alternative'" in out, out


def test_alternative_counts_as_the_non_normal_use_case(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/PRD.md", "| UC2 | failure |", "| UC2 | alternative |")
    code, out = run(p)
    assert code == 0, out


def test_unknown_use_case_kind_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/PRD.md", "| UC2 | failure |", "| UC2 | error |")
    code, out = run(p)
    assert code == 1 and "use cases UC2 need Kind normal, failure or alternative" in out, out


def test_missing_state_machine_without_no_states_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "No states: add is a pure function.", "TODO")
    code, out = run(p)
    assert code == 1 and "'State machine' needs a ```mermaid stateDiagram-v2 block" in out, out


def test_state_machine_without_forbidden_list_fails(tmp_path):
    p = with_states(tmp_path)
    edit(p / "docs/MODEL.md", "Forbidden:\n- Requested --> Paid\n", "")
    code, out = run(p)
    assert code == 1 and "'State machine' lacks a 'Forbidden:' list" in out, out


def test_transition_absent_from_tests_table_fails(tmp_path):
    p = with_states(tmp_path)
    edit(p / "docs/MODEL.md", "| Paused --> Paid | state machine | `test_add` |\n", "")
    code, out = run(p)
    assert code == 1 and "lacks state transitions: Paused --> Paid" in out, out


def test_start_arrow_absent_from_tests_table_fails(tmp_path):
    p = with_states(tmp_path)
    edit(p / "docs/MODEL.md", "| [*] --> Requested | state machine | `test_add` |\n", "")
    code, out = run(p)
    assert code == 1 and "lacks state transitions: [*] --> Requested" in out, out


def test_forbidden_line_absent_from_tests_table_fails(tmp_path):
    p = with_states(tmp_path)
    edit(p / "docs/MODEL.md", "| Requested --> Paid | forbidden | `test_add` |\n", "")
    code, out = run(p)
    assert code == 1 and "lacks forbidden lines: Requested --> Paid" in out, out


def test_sequence_heading_naming_unknown_use_case_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "## Sequence: UC1", "## Sequence: UC7")
    code, out = run(p)
    assert code == 1 and "sequence heading names UC7, not a use case in docs/PRD.md" in out, out


def test_sequence_heading_without_use_case_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "## Sequence: UC1 add two numbers", "## Sequence: main path")
    code, out = run(p)
    assert code == 1 and "names no use case" in out, out


def test_diagram_without_an_answer_line_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "**Answer:** one call, one return.\n", "")
    code, out = run(p)
    assert code == 1
    assert "'Sequence' lacks an '**Answer:**' line" in out, out


def test_optional_diagram_needs_an_answer_line(tmp_path):
    p = package(tmp_path)
    model = p / "docs/MODEL.md"
    model.write_text(model.read_text() + "\n## Context: who is outside?\n```mermaid\nflowchart LR\n  Caller --> Adder\n```\n")
    code, out = run(p)
    assert code == 1 and "'Context: who is outside?' lacks an '**Answer:**' line" in out, out


def test_domain_model_without_rules_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "Rules:\n- the result equals a + b\n", "")
    code, out = run(p)
    assert code == 1 and "'Domain model' lacks a 'Rules:' list" in out, out


def test_missing_tests_table_fails(tmp_path):
    p = package(tmp_path)
    model = p / "docs/MODEL.md"
    text = model.read_text()
    model.write_text(text[:text.index("## Tests from the model")])
    code, out = run(p)
    assert code == 1 and "docs/MODEL.md lacks '## Tests from the model'" in out, out


def test_decisions_without_adr_rows_fails(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/DECISIONS.md", "| ADR-1 |", "| D1 |")
    code, out = run(p)
    assert code == 1 and "no '| ADR-1 |' row" in out, out


def test_final_fails_a_function_the_code_does_not_define(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "via `add()`", "via `add()` and `subtract()`")
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


def test_final_accepts_an_imported_library_function(tmp_path):
    p = package(tmp_path)
    (p / "add.py").write_text("from langgraph.types import interrupt, Command as Cmd\n" + CODE)
    edit(p / "docs/MODEL.md", "via `add()`", "via `add()` after `interrupt()` and `Cmd()`")
    code, out = run(p, "--final")
    assert code == 0, out


def test_template_guidance_comment_left_in_is_fine(tmp_path):
    p = package(tmp_path)
    edit(p / "docs/MODEL.md", "| Claim | From | Test |", "<!-- One row per state-machine arrow. -->\n\n| Claim | From | Test |")
    code, out = run(p)
    assert code == 0, out
