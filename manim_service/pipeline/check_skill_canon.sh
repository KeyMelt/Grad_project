#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# check_skill_canon.sh — guard against pipeline skill drift.
#
# Canonical skill definitions live under ~/.codex/skills/. Claude Code reads
# them via symlinks under ~/.claude/skills/. This script verifies every
# Claude-side entry is a symlink resolving to the canonical Codex copy.
#
# Usage:
#   ./check_skill_canon.sh            # verify only; exit 1 on any drift
#   ./check_skill_canon.sh --repair   # recreate missing/forked symlinks
#
# See SKILL_OWNERSHIP.md for the ownership model.
# ---------------------------------------------------------------------------

CODEX_SKILLS="${HOME}/.codex/skills"
CLAUDE_SKILLS="${HOME}/.claude/skills"

PIPELINE_SKILLS=(
  producer
  rl-expert
  script-writer
  visual-director
  technical-validator
  voice-bgm
  qa-agent
  series-continuity
  transcript-writer
  rl-course-architect
  manim-rl-animation-style-lock
)

REPAIR=0
if [[ "${1:-}" == "--repair" ]]; then
  REPAIR=1
fi

mkdir -p "${CLAUDE_SKILLS}"

drift=0
repaired=0

for skill in "${PIPELINE_SKILLS[@]}"; do
  canon="${CODEX_SKILLS}/${skill}"
  link="${CLAUDE_SKILLS}/${skill}"

  if [[ ! -e "${canon}" ]]; then
    echo "MISSING CANONICAL: ${canon} (skill '${skill}' has no source of truth)" >&2
    drift=1
    continue
  fi

  # Resolve the symlink target (strip trailing slash for comparison)
  current_target=""
  if [[ -L "${link}" ]]; then
    current_target="$(readlink "${link}")"
    current_target="${current_target%/}"
  fi

  if [[ "${current_target}" == "${canon}" ]]; then
    echo "OK       ${skill}"
    continue
  fi

  # Drift: either not a symlink, missing, or points elsewhere
  if [[ -L "${link}" ]]; then
    echo "DRIFT    ${skill}: symlink points to '${current_target}' (expected '${canon}')" >&2
  elif [[ -e "${link}" ]]; then
    echo "DRIFT    ${skill}: FORKED real copy at ${link} (expected symlink to ${canon})" >&2
  else
    echo "DRIFT    ${skill}: missing at ${link}" >&2
  fi
  drift=1

  if [[ "${REPAIR}" -eq 1 ]]; then
    rm -rf "${link}"
    ln -s "${canon}" "${link}"
    echo "REPAIRED ${skill} -> ${canon}"
    repaired=1
  fi
done

if [[ "${REPAIR}" -eq 1 && "${repaired}" -eq 1 ]]; then
  echo ""
  echo "Repairs applied. Re-run without --repair to confirm a clean state."
  exit 0
fi

if [[ "${drift}" -eq 1 ]]; then
  echo "" >&2
  echo "Skill drift detected. Run: $0 --repair" >&2
  exit 1
fi

echo ""
echo "All ${#PIPELINE_SKILLS[@]} pipeline skills are canonical (no drift)."
