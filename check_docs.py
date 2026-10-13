"""Check the planning package check.sh requires: docs/PRD.md, docs/MODEL.md and docs/DECISIONS.md,
each filled in from kit/templates/ in the Unified Process order, and (with --final) bound to the code.

Usage: python3 check_docs.py PROJECT_DIR [--final]. Prints one PASS or FAIL line per check;
check.sh counts them. Standard library only, so it runs before the project has a venv.
"""

import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
PLACEHOLDER = re.compile(r"<(?!!--)[^<>\n]+>")  # <!-- guidance --> comments are not placeholders

PACKAGE = ("PRD", "MODEL", "DECISIONS")
PRD_SECTIONS = ["Goal", "Requirements", "Use cases", "Assumptions", "Risks"]
# PRD section -> the row id its table must have at least one of (`| R1 |`, `| UC1 |` ...)
PRD_ROWS = {"Requirements": "R", "Use cases": "UC", "Assumptions": "A", "Risks": "K"}
USE_CASE_KINDS = ("normal", "failure", "alternative")
# required MODEL.md section -> Mermaid kinds accepted (an empty tuple: a table, not a diagram)
MODEL_REQUIRED = {
    "Domain model": ("classDiagram", "erDiagram"),
    "State machine": ("stateDiagram-v2", "stateDiagram"),
    "Sequence": ("sequenceDiagram",),
    "Tests from the model": (),
}
MODEL_OPTIONAL = ["Context", "Agent loop", "Components"]
ADR_ROW = "ADR-1"
NO_STATES = "No states:"
FORBIDDEN = "Forbidden:"
DOMAIN_RULES = "Rules:"
TESTS_TABLE_HEADER = "| Claim | From | Test |"  # named in the memory sheet; rows are found by `test_` names


def sections(text: str) -> dict[str, str]:
    """Map each '## heading' to the text under it, up to the next '## '."""
    parts = re.split(r"^## +(.+)$", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}


def find_heading(secs: dict[str, str], prefix: str) -> str | None:
    """The first heading that starts with prefix (case-insensitive), else None."""
    for head in secs:
        if head.lower().startswith(prefix.lower()):
            return head
    return None


def find(secs: dict[str, str], prefix: str) -> str | None:
    """Body of the first section whose heading starts with prefix (case-insensitive), else None."""
    head = find_heading(secs, prefix)
    return None if head is None else secs[head]


def mermaid_blocks(body: str) -> list[str]:
    """The text of each ```mermaid block in body."""
    return re.findall(r"```mermaid\s*\n(.*?)```", body, flags=re.S)


def mermaid_kinds(body: str) -> list[str]:
    """First word of each ```mermaid block in body."""
    return [m.split()[0] for m in mermaid_blocks(body) if m.split()]


def has_answer(body: str) -> bool:
    """True if body has a filled '**Answer:**' line."""
    return bool(re.search(r"^\*\*Answer:\*\*\s*\S", body, re.M))


def list_after(body: str, label: str) -> list[str] | None:
    """Items of the '- ' or '1. ' list that follows the line starting with label; None if no such line."""
    lines = body.splitlines()
    name = label.rstrip(":")
    for i, line in enumerate(lines):
        s = line.strip().strip("*").strip()
        if s.startswith(label) or (s.startswith(name) and s.endswith(":")):  # 'Rules (in order):' counts too
            items: list[str] = []
            for nxt in lines[i + 1:]:
                m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.+?)\s*$", nxt)
                if m:
                    items.append(m.group(1))
                elif nxt.strip() or items:  # a blank line before the first item is fine; after, it ends the list
                    break
            return items
    return None


def arrow(text: str) -> str:
    """Spacing around every '-->' made uniform, so 'A-->B' and 'A  -->  B' match 'A --> B'."""
    return re.sub(r"\s*-->\s*", " --> ", text)


def transitions(state_block: str) -> list[str]:
    """Every 'A --> B' arrow in a stateDiagram block, labels after ':' dropped, [*] arrows included."""
    found = re.findall(r"^\s*(\[\*\]|[\w.]+)\s*-->\s*(\[\*\]|[\w.]+)", state_block, re.M)
    return list(dict.fromkeys(f"{a} --> {b}" for a, b in found))


def row_ids(body: str, prefix: str) -> list[str]:
    """Ids like UC1, R2 from table rows that start '| <prefix><n> |'."""
    return re.findall(rf"^\|\s*({prefix}\d+)\s*\|", body, re.M)


def table_cells(body: str, prefix: str) -> dict[str, list[str]]:
    """Row id -> its cells after the id, for table rows starting '| <prefix><n> |'."""
    rows: dict[str, list[str]] = {}
    for line in body.splitlines():
        m = re.match(rf"^\|\s*({prefix}\d+)\s*\|(.*)$", line)
        if m:
            rows[m.group(1)] = [c.strip() for c in m.group(2).rstrip().rstrip("|").split("|")]
    return rows


def leftover_placeholders(path: Path, template: Path) -> list[str]:
    """Template placeholders still present in the filled file (quoted task text in <> is fine)."""
    text = path.read_text(encoding="utf-8")
    return sorted({p for p in PLACEHOLDER.findall(template.read_text(encoding="utf-8")) if p in text})


def defined_names(project: Path) -> set[str]:
    """Every def, class and imported name in the project's own .py files (not the kit or the venv).

    Imported names count so a library call the code really makes, such as `interrupt()`, may be named."""
    names: set[str] = set()
    for py in project.rglob("*.py"):
        rel = py.relative_to(project).parts
        if rel[0] in {".venv", "venv", "kit"} or "site-packages" in rel:
            continue
        text = py.read_text(encoding="utf-8")
        names |= set(re.findall(r"^\s*(?:async\s+)?(?:def|class)\s+(\w+)", text, re.M))
        for group in re.findall(r"^\s*from\s+[\w.]+\s+import\s+(?:\(([^)]*)\)|([^\n]+))", text, re.M):
            group = "".join(group).split("#")[0]
            names |= {n.split()[-1] for n in group.replace("\n", " ").split(",") if n.strip()}
    return names


def check_prd(text: str) -> tuple[list[tuple[bool, str]], set[str]]:
    """PRD results, and the use case ids it defines (the sequence heading must name one)."""
    out: list[tuple[bool, str]] = []
    secs = sections(text)
    for s in PRD_SECTIONS:
        body = find(secs, s)
        ok = body is not None and body.strip() != ""
        out.append((ok, f"docs/PRD.md has '{s}'" if ok else f"docs/PRD.md lacks a filled '## {s}' section"))
    for s, prefix in PRD_ROWS.items():
        body = find(secs, s)
        if body is None:
            continue
        ok = bool(row_ids(body, prefix))
        out.append((ok, f"docs/PRD.md {s} has '| {prefix}1 |' rows" if ok
                    else f"docs/PRD.md {s} has no '| {prefix}1 |' row"))
    rows = table_cells(find(secs, "Use cases") or "", "UC")
    kinds = {uc: (cells[0].strip("`*").lower() if cells else "") for uc, cells in rows.items()}
    bad = sorted(uc for uc, k in kinds.items() if k not in USE_CASE_KINDS)
    if bad:
        out.append((False, f"docs/PRD.md use cases {', '.join(bad)} need Kind normal, failure or alternative"))
    if rows:
        ok = "normal" in kinds.values()
        out.append((ok, "docs/PRD.md has a normal use case" if ok else "docs/PRD.md has no use case of Kind 'normal'"))
        ok = bool({"failure", "alternative"} & set(kinds.values()))
        out.append((ok, "docs/PRD.md has a failure or alternative use case" if ok
                    else "docs/PRD.md has no use case of Kind 'failure' or 'alternative' (add what goes wrong)"))
    return out, set(rows)


def check_model(project: Path, model: str, use_cases: set[str] | None, final: bool) -> list[tuple[bool, str]]:
    """MODEL.md results: required diagrams, the tests table covering every state arrow, names bound to code."""
    out: list[tuple[bool, str]] = []
    secs = sections(model)
    checked: set[str] = set()
    for name, kinds in MODEL_REQUIRED.items():
        head = find_heading(secs, name)
        if head is None:
            out.append((False, f"docs/MODEL.md lacks '## {name}'"))
            continue
        checked.add(head)
        body = secs[head]
        if not kinds:
            continue
        got = mermaid_kinds(body)
        if name == "State machine" and not got and re.search(rf"^{NO_STATES}\s*\S", body, re.M):
            out.append((True, "docs/MODEL.md 'State machine': none, with a reason"))
            continue
        ok = any(k in kinds for k in got)
        out.append((ok, f"docs/MODEL.md '{name}' is a {got[0] if got else '?'}" if ok
                    else f"docs/MODEL.md '{name}' needs a ```mermaid {kinds[0]} block (found {got or 'none'})"))
        if not has_answer(body):
            out.append((False, f"docs/MODEL.md '{name}' lacks an '**Answer:**' line under its heading"))
        if name == "Domain model":
            ok = bool(list_after(body, DOMAIN_RULES))
            out.append((ok, "docs/MODEL.md domain model lists its rules" if ok
                        else f"docs/MODEL.md 'Domain model' lacks a '{DOMAIN_RULES}' list (the invariants)"))
        if name == "State machine":
            ok = bool(list_after(body, FORBIDDEN))
            out.append((ok, "docs/MODEL.md state machine lists its forbidden transitions" if ok
                        else f"docs/MODEL.md 'State machine' lacks a '{FORBIDDEN}' list (what must never happen)"))
        if name == "Sequence":
            named = re.findall(r"\bUC\d+\b", head)
            if not named:
                out.append((False, f"docs/MODEL.md sequence heading '{head}' names no use case (write '## Sequence: UC2 <name>')"))
            elif use_cases is not None:
                unknown = [u for u in named if u not in use_cases]
                out.append((not unknown, f"docs/MODEL.md sequence shows {named[0]} from docs/PRD.md" if not unknown
                            else f"docs/MODEL.md sequence heading names {', '.join(unknown)}, not a use case in docs/PRD.md"))
    for head, body in secs.items():
        if head in checked:
            continue
        optional = any(head.lower().startswith(o.lower()) for o in MODEL_OPTIONAL)
        if optional and not mermaid_kinds(body):
            out.append((False, f"docs/MODEL.md '{head}' needs a ```mermaid block, or delete the section"))
        elif (optional or mermaid_kinds(body)) and not has_answer(body):
            out.append((False, f"docs/MODEL.md '{head}' lacks an '**Answer:**' line under its heading"))
    tests_body = find(secs, "Tests from the model")
    if tests_body is not None:
        table = arrow(tests_body)
        rows = [l for l in tests_body.splitlines() if re.match(r"^\|(?!\s*-)", l) and "`test_" in l]
        out.append((bool(rows), f"docs/MODEL.md tests table has {len(rows)} rows" if rows
                    else "docs/MODEL.md 'Tests from the model' has no row naming a `test_` function"))
        state = find(secs, "State machine") or ""
        arrows = [a for block in mermaid_blocks(state) if block.split()[:1] in (["stateDiagram-v2"], ["stateDiagram"])
                  for a in transitions(block)]
        missing = [a for a in arrows if a not in table]
        out.append((not missing, f"docs/MODEL.md tests cover all {len(arrows)} state transitions" if not missing
                    else f"docs/MODEL.md 'Tests from the model' lacks state transitions: {'; '.join(missing)}"))
        forbidden = [arrow(f).rstrip(".") for f in list_after(state, FORBIDDEN) or []]
        missing = [f for f in forbidden if f not in table]
        out.append((not missing, f"docs/MODEL.md tests cover all {len(forbidden)} forbidden transitions" if not missing
                    else f"docs/MODEL.md 'Tests from the model' lacks forbidden lines: {'; '.join(missing)}"))
    if final:
        have = defined_names(project)
        funcs = set(re.findall(r"`(?:\w+\.)*(\w+)\(\)`", model))
        missing = sorted(f for f in funcs if f not in have)
        out.append((not missing, f"docs/MODEL.md names {len(funcs)} functions, all defined in the code" if not missing
                    else f"docs/MODEL.md names functions the code does not define: {', '.join(missing)}"))
        tests = set(re.findall(r"`(test_\w+)`", model))
        missing = sorted(t for t in tests if t not in have)
        out.append((not missing, f"docs/MODEL.md names {len(tests)} tests, all defined" if not missing
                    else f"docs/MODEL.md names tests no test file defines: {', '.join(missing)}"))
    return out


def check(project: Path, final: bool) -> list[tuple[bool, str]]:
    """All results as (passed, message)."""
    out: list[tuple[bool, str]] = []
    docs = project / "docs"
    files = {name: docs / f"{name}.md" for name in PACKAGE}
    for name, path in files.items():
        if not path.is_file():
            out.append((False, f"docs/{name}.md missing (copy kit/templates/{name}.md and fill it in)"))
            continue
        left = leftover_placeholders(path, KIT / "templates" / f"{name}.md")
        out.append((not left, f"docs/{name}.md has no template placeholders" if not left
                    else f"docs/{name}.md still has template placeholders: {' '.join(left[:5])}"))
    use_cases: set[str] | None = None  # None: no PRD to check the sequence's use case against
    if files["PRD"].is_file():
        results, use_cases = check_prd(files["PRD"].read_text(encoding="utf-8"))
        out += results
    if files["MODEL"].is_file():
        out += check_model(project, files["MODEL"].read_text(encoding="utf-8"), use_cases, final)
    if files["DECISIONS"].is_file():
        ok = bool(re.search(r"^\|\s*ADR-\d", files["DECISIONS"].read_text(encoding="utf-8"), re.M))
        out.append((ok, "docs/DECISIONS.md has ADR rows" if ok else f"docs/DECISIONS.md has no '| {ADR_ROW} |' row"))
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    final = "--final" in args
    paths = [a for a in args if a != "--final"]
    results = check(Path(paths[0] if paths else "."), final)
    for ok, msg in results:
        print(("PASS " if ok else "FAIL ") + msg)
    sys.exit(0 if all(ok for ok, _ in results) else 1)
