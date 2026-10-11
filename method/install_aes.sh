#!/usr/bin/env bash
# Install the `aes` planning CLI at the revision this kit was tested with.
#   bash kit/method/install_aes.sh          install it as a uv tool (puts `aes` on PATH)
#   bash kit/method/install_aes.sh --spec   print the package spec only (for uvx or pip)
# The CLI lives in the same GitHub account as this kit; the account is read from the kit's
# git remote, so set AES_OWNER if the kit was copied rather than cloned.
set -euo pipefail
REV=e9ad250233c58dcaefbc8e91f3522644ab07fe66
KIT="$(cd "$(dirname "$0")/.." && pwd)"
OWNER="${AES_OWNER:-$(git -C "$KIT" remote get-url origin 2>/dev/null | sed -E 's#.*github\.com[:/]([^/]+)/.*#\1#')}"
[[ -n "$OWNER" && "$OWNER" != *[:/]* ]] || { echo "FAIL cannot read the GitHub account from the kit's git remote; set AES_OWNER" >&2; exit 2; }
SPEC="agentic-engineering-system @ git+https://github.com/$OWNER/agentic-engineering-system-canonical.git@$REV"
if [[ "${1:-}" == "--spec" ]]; then echo "$SPEC"; exit 0; fi
command -v uv >/dev/null || pip install -q uv
uv tool install --force "$SPEC"
aes --version
