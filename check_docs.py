"""Check the planning package check.sh requires: docs/DESIGN.md, docs/MODEL.md (six diagrams) and
docs/DECISIONS.md, each filled in from kit/templates/, and (with --final) bound to the real code.

Usage: python3 check_docs.py PROJECT_DIR [--final]. Prints one PASS or FAIL line per check;
check.sh counts them. Standard library only, so it runs before the project has a venv.
"""

import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
PLACEHOLDER = re.compile(r"<[^<>\n]+>")

DESIGN_SECTIONS = ["Outcome", "Requirements", "Failure modes", "Domain rules", "Fixtures", "Slices"]
# diagram number -> (name used in messages, Mermaid kinds accepted)
DIAGRAMS = {
    1: ("Context", ("flowchart", "graph")),
    2: ("Building blocks", ("flowchart", "graph")),
    3: ("Main sequence", ("sequenceDiagram",)),
    4: ("Rules", ("flowchart", "graph")),
    5: ("States", ("stateDiagram-v2", "stateDiagram")),
    6: ("Data", ("classDiagram", "erDiagram")),
}
MODEL_TABLES = ["Runtime", "Contracts", "Quality", "Unknowns"]


def sections(text: str) -> dict[str, str]:
    """Map each '## heading' to the text under it, up to the next '## '."""
    parts = re.split(r"^## +(.+)$", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}


def find(secs: dict[str, str], prefix: str) -> str | None:
    """Body of the first section whose heading starts with prefix (case-insensitive), else None."""
    for head, body in secs.items():
        if head.lower().startswith(prefix.lower()):
            return body
    return None


def mermaid_kinds(body: str) -> list[str]:
    """First word of each ```mermaid block in body."""
    return [m.split()[0] for m in re.findall(r"```mermaid\s*\n(.*?)```", body, flags=re.S) if m.split()]


def leftover_placeholders(path: Path, template: Path) -> list[str]:
    """Template placeholders still present in the filled file (quoted task text in <> is fine)."""
    text = path.read_text(encoding="utf-8")
    return sorted({p for p in PLACEHOLDER.findall(template.read_text(encoding="utf-8")) if p in text})


def defined_names(project: Path) -> set[str]:
    """Every def and class name in the project's own .py files (not the kit or the venv)."""
    names: set[str] = set()
    for py in project.rglob("*.py"):
        rel = py.relative_to(project).parts
        if rel[0] in {".venv", "venv", "kit"} or "site-packages" in rel:
            continue
        names |= set(re.findall(r"^\s*(?:async\s+)?(?:def|class)\s+(\w+)", py.read_text(encoding="utf-8"), re.M))
    return names


def check(project: Path, final: bool) -> list[tuple[bool, str]]:
    """All results as (passed, message)."""
    out: list[tuple[bool, str]] = []
    docs = project / "docs"
    files = {name: docs / f"{name}.md" for name in ("DESIGN", "MODEL", "DECISIONS")}
    for name, path in files.items():
        if not path.is_file():
            out.append((False, f"docs/{name}.md missing (copy kit/templates/{name}.md and fill it in)"))
            continue
        left = leftover_placeholders(path, KIT / "templates" / f"{name}.md")
        out.append((not left, f"docs/{name}.md has no template placeholders" if not left
                    else f"docs/{name}.md still has template placeholders: {' '.join(left[:5])}"))
    if files["DESIGN"].is_file():
        secs = sections(files["DESIGN"].read_text(encoding="utf-8"))
        for s in DESIGN_SECTIONS:
            body = find(secs, s)
            ok = body is not None and body.strip() != ""
            out.append((ok, f"docs/DESIGN.md has '{s}'" if ok else f"docs/DESIGN.md lacks a filled '## {s}' section"))
        req = find(secs, "Requirements") or ""
        ok = bool(re.search(r"^\|\s*R\d", req, re.M))
        out.append((ok, "docs/DESIGN.md quotes requirements R1.." if ok else "docs/DESIGN.md Requirements has no '| R1 |' row"))
    if files["MODEL"].is_file():
        model = files["MODEL"].read_text(encoding="utf-8")
        secs = sections(model)
        for n, (name, kinds) in DIAGRAMS.items():
            body = find(secs, f"{n}.")
            if body is None:
                out.append((False, f"docs/MODEL.md lacks diagram '## {n}. {name}'"))
                continue
            got = mermaid_kinds(body)
            if n == 5 and not got and re.search(r"^No states:\s*\S", body, re.M):
                out.append((True, "docs/MODEL.md diagram 5 'States': none, with a reason"))
                continue
            ok = any(k in kinds for k in got)
            out.append((ok, f"docs/MODEL.md diagram {n} '{name}' is a {got[0] if got else '?'}" if ok
                        else f"docs/MODEL.md diagram {n} '{name}' needs a ```mermaid {kinds[0]} block (found {got or 'none'})"))
        for t in MODEL_TABLES:
            body = find(secs, t)
            ok = body is not None and bool(re.search(r"^\|(?!\s*-)", body, re.M))
            out.append((ok, f"docs/MODEL.md has a '{t}' table" if ok else f"docs/MODEL.md lacks a filled '## {t}' table"))
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
    if files["DECISIONS"].is_file():
        ok = bool(re.search(r"^\|\s*D\d", files["DECISIONS"].read_text(encoding="utf-8"), re.M))
        out.append((ok, "docs/DECISIONS.md has decision rows" if ok else "docs/DECISIONS.md has no '| D1 |' row"))
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    final = "--final" in args
    paths = [a for a in args if a != "--final"]
    results = check(Path(paths[0] if paths else "."), final)
    for ok, msg in results:
        print(("PASS " if ok else "FAIL ") + msg)
    sys.exit(0 if all(ok for ok, _ in results) else 1)
