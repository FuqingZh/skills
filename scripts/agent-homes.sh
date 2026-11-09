#!/usr/bin/env bash
# Shared target parsing and safety checks for install and legacy cleanup.
# Sourced after the caller defines usage() and OPERATION (install or cleanup).

DRY_RUN=false
FORCE=false
AGENTS=()

fail_usage() { echo "$1" >&2; usage >&2; exit 2; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      shift
      [[ $# -gt 0 && "$1" != -* ]] || fail_usage '--agent requires a value'
      while [[ $# -gt 0 && "$1" != -* ]]; do
        case "$1" in
          codex|grok|pi) AGENTS+=("$1") ;;
          all) AGENTS+=(codex grok pi) ;;
          *) fail_usage "Unknown agent: $1" ;;
        esac
        shift
      done
      continue ;;
    --dry-run) DRY_RUN=true ;;
    --force)
      [[ "$OPERATION" == install ]] || fail_usage '--force is not supported for link cleanup'
      FORCE=true ;;
    --skills-only|--instructions-only|--profile)
      fail_usage "$1 is retired. Use skills add for skills; install.sh only manages global instructions." ;;
    --codex-home|--grok-home|--pi-home)
      fail_usage "$1 is retired. Set CODEX_HOME, CALIBRATION_GROK_HOME, or PI_CODING_AGENT_DIR instead." ;;
    --no-backup) fail_usage '--no-backup is retired. Changed existing files are always backed up.' ;;
    --help|-h) usage; exit 0 ;;
    *) fail_usage "Unknown option: $1" ;;
  esac
  shift
done
[[ ${#AGENTS[@]} -gt 0 ]] || AGENTS=(codex)

configure_target() {
  case "$AGENT" in
    codex) TARGET_HOME="${CODEX_HOME:-${HOME:+$HOME/.codex}}" ;;
    grok) TARGET_HOME="${CALIBRATION_GROK_HOME:-${HOME:+$HOME/.grok}}" ;;
    pi) TARGET_HOME="${PI_CODING_AGENT_DIR:-${HOME:+$HOME/.pi/agent}}" ;;
  esac
  [[ "$TARGET_HOME" == /* ]] || fail_usage "Cannot derive absolute $AGENT home; set its home environment variable"
  TARGET_HOME="$(realpath -m -- "$TARGET_HOME")"
  [[ "$TARGET_HOME" != / ]] || fail_usage "Refusing / as $AGENT home"
  case "$TARGET_HOME/" in "$CALIBRATION_ROOT/"*) fail_usage 'Agent home must not be inside the checkout' ;; esac
  case "$CALIBRATION_ROOT/" in "$TARGET_HOME/"*) fail_usage 'Agent home must not contain the checkout' ;; esac
  [[ ! -e "$TARGET_HOME" || -d "$TARGET_HOME" ]] || fail_usage "Agent home is not a directory: $TARGET_HOME"
  AGENTS_TARGET="$TARGET_HOME/AGENTS.md"
}

# Preflight every selected destination before the first write; duplicates are
# rejected too, so a caller never updates or cleans one destination twice.
SELECTED_HOMES=()
for AGENT in "${AGENTS[@]}"; do
  configure_target
  for selected_home in "${SELECTED_HOMES[@]}"; do
    case "$TARGET_HOME/" in "$selected_home/"*) fail_usage 'Selected agent homes must not overlap' ;; esac
    case "$selected_home/" in "$TARGET_HOME/"*) fail_usage 'Selected agent homes must not overlap' ;; esac
  done
  SELECTED_HOMES+=("$TARGET_HOME")
done
