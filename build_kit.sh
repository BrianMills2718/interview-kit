#!/usr/bin/env bash
# Concatenate rules, plan template, skills, subagents and the method into KIT.md: one file to attach
# or, with no terminal or internet, to paste. No size cap: a cloned kit reads its files directly.
set -euo pipefail
cd "$(dirname "$0")"
{
  echo "# Interview kit (combined; source: the interview-kit repo)"
  for f in AGENTS.md PLAN.template.md skills/*/SKILL.md agents/*.md method/*.md; do
    echo; echo "<!-- $f -->"; cat "$f"
  done
} > KIT.md
echo "wrote KIT.md ($(wc -l < KIT.md) lines)"
