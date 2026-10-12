"""Drift check for MEMORY_SHEET.md: every heading check.sh and check_docs.py require is named in a prompt.

A verbatim run of the script failed check.sh --final in rehearsal when a prompt left out a required
heading, so the required names are read from the checkers themselves rather than copied here.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET = (ROOT / "MEMORY_SHEET.md").read_text(encoding="utf-8")
CHECK_SH = (ROOT / "check.sh").read_text(encoding="utf-8")
CHECK_DOCS = (ROOT / "check_docs.py").read_text(encoding="utf-8")


def _quoted_list(src: str, anchor: str) -> list[str]:
    """Return the double-quoted words on the line containing anchor (a bash `for sec in ...` list)."""
    line = next(l for l in src.splitlines() if anchor in l)
    return re.findall(r'"([^"]+)"', line)


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


def test_design_sections_are_named():
    required = re.search(r"DESIGN_SECTIONS = \[([^\]]+)\]", CHECK_DOCS).group(1)
    names = re.findall(r'"([^"]+)"', required)
    assert len(names) >= 5
    missing = [n for n in names if n not in SHEET]
    assert missing == [], f"MEMORY_SHEET.md prompts omit DESIGN.md sections check_docs.py needs: {missing}"


def test_finish_prompt_ticks_done_when():
    assert "Tick each Done when item" in SHEET, "--final fails until PLAN.md's done-when items are ticked"
