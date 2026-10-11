#!/usr/bin/env bash
# Concatenate rules, plan template, skills and subagents into KIT.md: one file to paste or attach.
set -euo pipefail
cd "$(dirname "$0")"
{
  echo "# Interview kit (combined; source: github.com/BrianMills2718/interview-kit)"
  for f in AGENTS.md PLAN.template.md skills/*/SKILL.md agents/*.md; do
    echo; echo "<!-- $f -->"; cat "$f"
  done
} > KIT.md
echo "wrote KIT.md ($(wc -l < KIT.md) lines)"
