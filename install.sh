#!/usr/bin/env bash
# Install FuqingZh/skills global instructions. Skills use the upstream CLI.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./install.sh [OPTIONS]

Install or refresh the FuqingZh/skills block in global instruction files.
Does not install, update, or remove skills.

  --agent AGENTS...  codex (default), grok, pi, agy, or all
  --dry-run          Preview without writes
  --force            Back up and replace an unmarked Codex regular file
  -h, --help         Show help

Homes: CODEX_HOME, CALIBRATION_GROK_HOME (installer only), PI_CODING_AGENT_DIR.
Unset or empty variables use ~/.codex, ~/.grok, and ~/.pi/agent respectively.
Antigravity CLI (agy) uses ~/.gemini/AGENTS.md.
Changed existing files are always backed up; unchanged files are left alone.
EOF
}

CALIBRATION_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
OPERATION=install
# shellcheck source=scripts/agent-homes.sh
source "$CALIBRATION_ROOT/scripts/agent-homes.sh"
TEMPLATE="$CALIBRATION_ROOT/templates/AGENTS.md.template"
[[ -f "$TEMPLATE" ]] || fail_usage "Missing template: $TEMPLATE"
BEGIN_MARKER='<!-- FuqingZh/skills:begin -->'
END_MARKER='<!-- FuqingZh/skills:end -->'
LEGACY_BEGIN='<!-- calibration:begin -->'
LEGACY_END='<!-- calibration:end -->'

render_template() {
  local body input=/dev/null final_newline=true
  body="$(<"$TEMPLATE")"
  [[ ! -f "$AGENTS_TARGET" ]] || input="$AGENTS_TARGET"
  [[ ! -s "$input" || -z "$(tail -c 1 -- "$input")" ]] || final_newline=false
  CALIBRATION_BODY="$body" awk -v agent="$AGENT" -v force="$FORCE" -v final_newline="$final_newline" \
    -v begin="$BEGIN_MARKER" -v end="$END_MARKER" \
    -v legacy_begin="$LEGACY_BEGIN" -v legacy_end="$LEGACY_END" '
    function malformed() { invalid=1; exit 2 }
    BEGIN { body=ENVIRON["CALIBRATION_BODY"]; inside=0; count=0; prefix="" }
    $0 == begin || $0 == legacy_begin {
      if (inside || count) malformed()
      expected_end=($0 == legacy_begin ? legacy_end : end)
      inside=1; count++; printf "%s", prefix
      print begin; print body; next
    }
    $0 == end || $0 == legacy_end {
      if (!inside || $0 != expected_end) malformed()
      inside=0; print end; next
    }
    index($0, "<!-- calibration:") || index($0, "<!-- FuqingZh/skills:") { malformed() }
    !inside {
      if (count) suffix=suffix $0 "\n"
      else prefix=prefix $0 "\n"
    }
    END {
      if (invalid || inside) exit 2
      if (count) {
        if (final_newline == "false" && length(suffix)) suffix=substr(suffix, 1, length(suffix)-1)
        printf "%s", suffix
      }
      if (!count) {
        if (agent == "codex" && FILENAME != "/dev/null" && force != "true") exit 3
        if (agent != "codex") printf "%s", prefix
        print begin "\n" body "\n" end
      }
    }
  ' "$input"
}

preflight() {
  if [[ -L "$AGENTS_TARGET" || ( -e "$AGENTS_TARGET" && ! -f "$AGENTS_TARGET" ) ]]; then
    fail_usage "Instruction target must be a regular file, never a symlink or directory: $AGENTS_TARGET"
  fi
  local status=0
  render_template >/dev/null || status=$?
  case "$status" in
    0) ;;
    3) fail_usage "Unmarked Codex AGENTS.md: preview --force to back up and replace $AGENTS_TARGET" ;;
    *) fail_usage "Malformed managed block: $AGENTS_TARGET" ;;
  esac
}

for AGENT in "${AGENTS[@]}"; do
  configure_target
  preflight
done

for AGENT in "${AGENTS[@]}"; do
  configure_target
  if [[ -f "$AGENTS_TARGET" ]] && cmp -s "$AGENTS_TARGET" <(render_template); then
    echo "${AGENTS_TARGET##*/} already current: $AGENTS_TARGET"
    continue
  fi
  if $DRY_RUN; then
    [[ ! -f "$AGENTS_TARGET" ]] || echo "[dry-run] back up $AGENTS_TARGET"
    if [[ -f "$AGENTS_TARGET" ]] && grep -qFx "$LEGACY_BEGIN" "$AGENTS_TARGET"; then
      echo "[dry-run] migrate calibration markers to FuqingZh/skills: $AGENTS_TARGET"
    else
      echo "[dry-run] write FuqingZh/skills block to $AGENTS_TARGET"
    fi
    continue
  fi
  mkdir -p -- "$TARGET_HOME"
  preflight
  if [[ -f "$AGENTS_TARGET" ]]; then
    backup="$(mktemp "$AGENTS_TARGET.bak.XXXXXX")"
    cp -p -- "$AGENTS_TARGET" "$backup"
    cmp -s -- "$AGENTS_TARGET" "$backup" || { echo "Backup verification failed: $backup" >&2; exit 1; }
    echo "Backup: $backup"
    if [[ "$AGENT" == codex ]] && ! grep -qFx -e "$BEGIN_MARKER" -e "$LEGACY_BEGIN" "$AGENTS_TARGET"; then
      echo 'Personal instructions remain in the backup; restore them outside the new block as needed.'
    fi
  fi
  tmp="$(mktemp "$TARGET_HOME/.calibration-AGENTS.XXXXXX")"
  trap 'rm -f -- "$tmp"' EXIT
  render_template >"$tmp"
  if [[ -f "$AGENTS_TARGET" ]]; then chmod --reference="$AGENTS_TARGET" "$tmp"; fi
  mv -T -- "$tmp" "$AGENTS_TARGET"
  trap - EXIT
  echo "Installed FuqingZh/skills block: $AGENTS_TARGET"
done
