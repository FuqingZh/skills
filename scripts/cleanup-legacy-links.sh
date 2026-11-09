#!/usr/bin/env bash
# Remove only links owned by the legacy calibration installer.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/cleanup-legacy-links.sh [OPTIONS]

Clean legacy calibration skill links. Does not remove AGENTS.md, shared
skills CLI installations, ordinary directories, or the source checkout.
Run from the original checkout; a link to another checkout is left untouched.

  --agent AGENTS...  codex (default), grok, pi, or all
  --dry-run          Preview without writes
  -h, --help         Show help

Homes: CODEX_HOME, CALIBRATION_GROK_HOME (installer only), PI_CODING_AGENT_DIR.
Unset or empty variables use ~/.codex, ~/.grok, and ~/.pi/agent respectively.
EOF
}

CALIBRATION_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
OPERATION=cleanup
# shellcheck source=scripts/agent-homes.sh
source "$CALIBRATION_ROOT/scripts/agent-homes.sh"

# This is historical ownership data, not an installation registry. Include
# former locations so dangling links remain cleanable after source retirement.
FIRST_PARTY=(calibration closeout retrospect writing-code-docs engineering-design
  global-defaults naming personal-strategy project-docs writing-docstrings)
THIRD_PARTY=(grilling teach brainstorming writing-great-skills writing-plans
  darwin-skill coding-protocol)

for AGENT in "${AGENTS[@]}"; do
  configure_target
  skills="$TARGET_HOME/skills"
  if [[ -L "$skills" || ( -e "$skills" && ! -d "$skills" ) ]]; then
    fail_usage "Legacy skills root must be a real directory: $skills"
  fi
done

clean_link() {
  local name="$1"; shift
  local target="$TARGET_HOME/skills/$name" source owned=false
  [[ -e "$target" || -L "$target" ]] || return 0
  if [[ -L "$target" ]]; then
    source="$(readlink -- "$target")"
    # Match the exact absolute targets emitted by the old installer. Do not
    # follow links or infer ownership from a matching directory/skill name.
    for relative in "$@"; do
      [[ "$source" != "$CALIBRATION_ROOT/$relative/$name" ]] || owned=true
    done
  fi
  if ! $owned; then
    echo "Left untouched (not an owned legacy link): $target"
  elif $DRY_RUN; then
    echo "[dry-run] unlink $target"
  else
    unlink -- "$target"
    echo "Removed legacy link: $target"
  fi
}

for AGENT in "${AGENTS[@]}"; do
  configure_target
  for name in "${FIRST_PARTY[@]}"; do clean_link "$name" skills; done
  for name in "${THIRD_PARTY[@]}"; do
    clean_link "$name" thirdparty/skills thirdparty/archive
  done
done
