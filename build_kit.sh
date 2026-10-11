#!/usr/bin/env bash
# Concatenate rules, plan template, skills and subagents into KIT.md: one file to paste or attach.
set -euo pipefail
cd "$(dirname "$0")"
# Skills kept out of KIT.md (it must stay pasteable, at most 600 lines); they ship in the clone.
STANDALONE="debug production-hardening raw-api-agent"
{
  echo "# Interview kit (combined; source: the interview-kit repo)"
  for f in AGENTS.md PLAN.template.md skills/*/SKILL.md agents/*.md; do
    case " $STANDALONE " in *" $(basename "$(dirname "$f")") "*) continue ;; esac
    echo; echo "<!-- $f -->"; cat "$f"
  done
  echo; echo "<!-- not bundled, to keep this file pasteable; in the cloned kit: -->"
  for s in $STANDALONE; do echo "- skills/$s/SKILL.md"; done
} > KIT.md
echo "wrote KIT.md ($(wc -l < KIT.md) lines)"
