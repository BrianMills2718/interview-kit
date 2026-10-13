"""Drift check for MEMORY_SHEET.md: every heading check.sh and check_docs.py require is named in a prompt.

A verbatim run of the script failed check.sh --final in rehearsal when a prompt left out a required
heading, so the required names are read from the checkers themselves rather than copied here.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET = (ROOT / "MEMORY_SHEET.md").read_text(encoding="utf-8")
CHECK_SH = (ROOT / "check.sh").read_text(encoding="utf-8")
CHECK_DOCS = (ROOT / "check_docs.py").read_text(encoding="utf-8")
# the Unified Process order the sheet follows (docs/plans/kit-v4-up-order.spec.md)
UP_ORDER = ["Rules", "Intent", "Questions", "Use cases and risks", "Domain model and states", "Off the shelf",
            "Prove it", "Shape", "Riskiest case and tests", "Plan", "Build one step", "Review", "README", "Finish"]


def _quoted_list(src: str, anchor: str) -> list[str]:
    """Return the double-quoted words on the line containing anchor (a bash `for sec in ...` list)."""
    line = next(l for l in src.splitlines() if anchor in l)
    return re.findall(r'"([^"]+)"', line)


def _constant(name: str):
    """The literal value assigned to a module-level name in check_docs.py, read without importing it."""
    for node in ast.parse(CHECK_DOCS).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"check_docs.py no longer defines {name}")


def _prompts() -> list[tuple[int, str, str]]:
    """(number, bold name, text up to the next prompt) for each numbered prompt in the sheet."""
    parts = re.split(r"^\*\*(\d+)\. ([^*]+)\*\*", SHEET, flags=re.M)
    return [(int(parts[i]), parts[i + 1].strip(), parts[i + 2]) for i in range(1, len(parts), 3)]


def _prompt(name: str) -> str:
    """Text of the prompt with this bold name."""
    return next(text for _, n, text in _prompts() if n == name)


def test_prompts_follow_the_up_order():
    prompts = _prompts()
    assert [n for n, _, _ in prompts] == list(range(1, 15))
    assert [name for _, name, _ in prompts] == UP_ORDER


def test_candidate_states_a_view_first_at_decision_points():
    for name in ("Intent", "Use cases and risks", "Shape"):
        text = _prompt(name)
        assert re.search(r"\b(My reading|I think|I want)\b[^>]*<", text), f"prompt '{name}' must have the candidate state a view"
        assert re.search(r"\b(Critique|Argue)\b", text), f"prompt '{name}' must ask the AI to argue with it"


def test_build_prompt_tests_every_arrow_and_never_bends_the_model():
    sequence = _prompt("Riskiest case and tests")
    assert "one row per arrow" in sequence and "one row per Forbidden line" in sequence
    build = _prompt("Build one step")
    assert "test what the diagrams forbid" in build
    assert "Never change a diagram or a test just to make the code pass" in build


def test_plan_headings_are_named():
    required = _quoted_list(CHECK_SH, 'for sec in "## Goal"') + ["## System model"]
    missing = [h for h in required if h not in SHEET]
    assert missing == [], f"MEMORY_SHEET.md prompts omit PLAN.md headings check.sh needs: {missing}"


def test_readme_sections_are_named():
    required = _quoted_list(CHECK_SH, 'for sec in "Run it"')
    assert "Run it" in required
    missing = [s for s in required if s.lower() not in SHEET.lower()]
    assert missing == [], f"MEMORY_SHEET.md prompts omit README sections check.sh needs: {missing}"
    assert '"## Run it"' in SHEET, "the README prompt must name the exact 'Run it' heading"


def test_prd_sections_and_rows_are_named():
    sections = _constant("PRD_SECTIONS")
    assert len(sections) >= 5
    missing = [s for s in sections if f"## {s}" not in SHEET]
    assert missing == [], f"MEMORY_SHEET.md prompts omit docs/PRD.md sections check_docs.py needs: {missing}"
    rows = [f"| {prefix}1 |" for prefix in _constant("PRD_ROWS").values()]
    missing = [r for r in rows if r not in SHEET]
    assert missing == [], f"MEMORY_SHEET.md prompts omit PRD row ids check_docs.py needs: {missing}"
    missing = [k for k in _constant("USE_CASE_KINDS") if k not in _prompt("Use cases and risks")]
    assert missing == [], f"the use case prompt omits Kind values: {missing}"


def test_model_sections_and_lists_are_named():
    missing = [s for s in _constant("MODEL_REQUIRED") if f"## {s}" not in SHEET]
    assert missing == [], f"MEMORY_SHEET.md prompts omit docs/MODEL.md sections check_docs.py needs: {missing}"
    for name in ("NO_STATES", "FORBIDDEN", "DOMAIN_RULES", "TESTS_TABLE_HEADER"):
        assert _constant(name) in SHEET, f"MEMORY_SHEET.md does not name {name} = {_constant(name)!r}"
    assert "**Answer:**" in SHEET


def test_adr_row_is_named():
    assert f"| {_constant('ADR_ROW')} |" in SHEET


def test_finish_prompt_ticks_done_when():
    assert "Tick each Done when item" in SHEET, "--final fails until PLAN.md's done-when items are ticked"
