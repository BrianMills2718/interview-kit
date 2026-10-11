#!/usr/bin/env bash
# Enforce the kit's workflow on the project in the current directory (or $1).
#   bash kit/check.sh            plan exists and is concrete, code compiles, tests pass
#   bash kit/check.sh --final    also: every done-when item ticked, README has the required sections
#   bash kit/check.sh --install-hook   run this check before every git commit
# Prints each check's result and a summary line; exit 0 only if nothing failed.
set -uo pipefail
FINAL=0; DIR=.
for a in "$@"; do
  case "$a" in
    --final) FINAL=1 ;;
    --install-hook)
      mkdir -p .git/hooks
      printf '#!/usr/bin/env bash\nbash "%s" || { echo "pre-commit: check failed"; exit 1; }\n' "$(cd "$(dirname "$0")" && pwd)/check.sh" > .git/hooks/pre-commit
      chmod +x .git/hooks/pre-commit; echo "installed .git/hooks/pre-commit"; exit 0 ;;
    *) DIR="$a" ;;
  esac
done
KIT="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || { echo "FAIL cannot cd to $DIR"; exit 2; }
# the project's own environment if it has one, so tests see its packages without activating it
PY=python3; for v in .venv/bin/python venv/bin/python; do [[ -x $v ]] && { PY=$v; break; }; done
PASS=0; FAILN=0
ok()   { echo "PASS $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL $1"; FAILN=$((FAILN+1)); }

# 1. Plan: exists, has the sections, done-when items are concrete
if [[ ! -f PLAN.md ]]; then
  bad "PLAN.md missing (copy PLAN.template.md and fill it in before writing code)"
else
  for sec in "## Goal" "## Done when" "## Steps"; do
    grep -q "^$sec" PLAN.md && ok "PLAN.md has '$sec'" || bad "PLAN.md lacks '$sec'"
  done
  items=$(grep -cE '^\s*- \[( |x)\]' PLAN.md || true)
  [[ "$items" -gt 0 ]] && ok "PLAN.md has $items done-when items" || bad "PLAN.md has no '- [ ]' done-when items"
  # only the template's own placeholders count, so quoted requirement text like `<policy text>` is fine
  left=$(grep -oE '<[^<>]+>' "$KIT/PLAN.template.md" 2>/dev/null | sort -u | while read -r ph; do grep -qF "$ph" PLAN.md && echo "$ph"; done)
  [[ -n "$left" ]] && bad "PLAN.md still has template placeholders: $(echo $left)" || ok "PLAN.md has no template placeholders"
  if [[ $FINAL == 1 ]]; then
    open=$(grep -cE '^\s*- \[ \]' PLAN.md || true)
    [[ "$open" == 0 ]] && ok "all done-when items ticked" || bad "$open done-when item(s) not ticked (tick with evidence, or move to README Limitations)"
  fi
fi

# 2. Code compiles
if find . -name '*.py' -not -path './.venv/*' -not -path './kit/*' | grep -q .; then
  if out=$(find . -name '*.py' -not -path './.venv/*' -not -path './kit/*' -print0 | xargs -0 "$PY" -m py_compile 2>&1); then
    ok "all .py files compile"
  else
    bad "syntax error: $(echo "$out" | head -3)"
  fi
fi

# 3. Tests pass (counts shown, none skipped silently)
if find . -name 'test*.py' -not -path './.venv/*' -not -path './kit/*' | grep -q .; then
  out=$("$PY" -m pytest -v --ignore=kit 2>&1); code=$?
  summary=$(echo "$out" | tail -1)
  echo "     pytest: $summary (exit $code)"
  if [[ $code == 0 ]]; then ok "tests pass"; else bad "tests failed (exit $code)"; echo "$out" | grep -E 'FAILED|ERROR' | head -10; fi
  echo "$summary" | grep -q skipped && bad "tests skipped: say why in the README or unskip them"
elif [[ $FINAL == 1 ]]; then
  bad "no test files found (test_*.py)"
else
  echo "WAIT no test files yet (fine right after the plan; --final needs them)"
fi

# 4. Final: README explains the work
if [[ $FINAL == 1 ]]; then
  if [[ ! -f README.md ]]; then bad "README.md missing (see skills/explain-your-work)"; else
    for sec in "Run it" "Approach" "Design decisions" "AI" "Limitations"; do
      # "AI" must be the word, not the letters inside "Details"
      if [[ $sec == AI ]]; then pat='^#+ .*\bAI\b'; flags=-qE; else pat="^#+ .*$sec"; flags=-qiE; fi
      grep $flags "$pat" README.md && ok "README has a '$sec' section" || bad "README lacks a '$sec' section"
    done
  fi
fi

echo "== check: $PASS passed, $FAILN failed (final=$FINAL)"
[[ $FAILN == 0 ]]
