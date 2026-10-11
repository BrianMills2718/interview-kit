#!/usr/bin/env bash
# Concatenate the rules and skills into KIT.md, one file to paste when there is no internet.
set -euo pipefail
cd "$(dirname "$0")"
{
  echo "# Interview kit (combined; source: github.com/BrianMills2718/interview-kit)"
  for f in AGENTS.md skills/*.md; do
    echo; echo "<!-- $f -->"; cat "$f"
  done
} > KIT.md
echo "wrote KIT.md ($(wc -l < KIT.md) lines)"
