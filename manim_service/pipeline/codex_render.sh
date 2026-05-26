#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# codex_render.sh — hand a heavy execution stage to Codex (GPT-5.5).
#
# The Claude Code orchestrator (producer / produce-video.md) calls this after
# it has written a brief to disk. Codex reads the brief, does the work
# (scene code-gen + render, or narration synth + mux), and writes a structured
# result to the --result file. Claude reads that result and resumes the gates.
#
# Codex runs non-interactively with danger-full-access (already its configured
# default), so it executes manim / kokoro / ffmpeg without approval prompts.
#
# Usage:
#   codex_render.sh --lesson-id <id> --stage <scene_render|narrate_mux> \
#                   --brief <path> [--result <path>] [--model <model>]
#
# Exit code is Codex's exit code. The orchestrator should also inspect the
# result file and pipeline_state.json before trusting success.
# ---------------------------------------------------------------------------

PROJECT_ROOT="/Users/ultramarine/Desktop/grad_project"
# Prefer the Homebrew CLI; fall back to the app-bundle binary.
if [[ -z "${CODEX_BIN:-}" ]]; then
  if [[ -x "/opt/homebrew/bin/codex" ]]; then
    CODEX_BIN="/opt/homebrew/bin/codex"
  else
    CODEX_BIN="/Applications/Codex.app/Contents/Resources/codex"
  fi
fi

LESSON_ID=""
STAGE=""
BRIEF=""
RESULT=""
MODEL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lesson-id) LESSON_ID="${2:?}"; shift 2 ;;
    --stage)     STAGE="${2:?}";     shift 2 ;;
    --brief)     BRIEF="${2:?}";     shift 2 ;;
    --result)    RESULT="${2:?}";    shift 2 ;;
    --model)     MODEL="${2:?}";     shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -n "${LESSON_ID}" ]] || { echo "ERROR: --lesson-id required" >&2; exit 2; }
[[ -n "${STAGE}" ]]     || { echo "ERROR: --stage required" >&2; exit 2; }
[[ -n "${BRIEF}" ]]     || { echo "ERROR: --brief required" >&2; exit 2; }

case "${STAGE}" in
  full_pipeline|scene_render|narrate_mux) ;;
  *) echo "ERROR: --stage must be full_pipeline, scene_render, or narrate_mux" >&2; exit 2 ;;
esac

if [[ ! -x "${CODEX_BIN}" ]]; then
  echo "ERROR: Codex CLI not found at ${CODEX_BIN}" >&2
  echo "Set CODEX_BIN env var to the codex binary path." >&2
  exit 127
fi

# Resolve brief to an absolute path so Codex finds it regardless of --cd.
if [[ "${BRIEF}" != /* ]]; then
  BRIEF="${PROJECT_ROOT}/${BRIEF}"
fi
[[ -f "${BRIEF}" ]] || { echo "ERROR: brief not found: ${BRIEF}" >&2; exit 2; }

# Default result path next to the brief if not supplied.
if [[ -z "${RESULT}" ]]; then
  RESULT="${PROJECT_ROOT}/manim_service/concept_videos/${LESSON_ID}_codex_result.md"
fi
if [[ "${RESULT}" != /* ]]; then
  RESULT="${PROJECT_ROOT}/${RESULT}"
fi

STATE_HELPER="manim_service.pipeline.pipeline_state"
PY="/Users/ultramarine/.venvs/manim/bin/python"

# Mark the handoff as running so a crashed run is distinguishable from success.
"${PY}" -m "${STATE_HELPER}" set-handoff "${LESSON_ID}" \
  --stage "${STAGE}" --status codex_running \
  --brief "${BRIEF}" --result "${RESULT}" >/dev/null 2>&1 || true
"${PY}" -m "${STATE_HELPER}" set-owner "${LESSON_ID}" codex >/dev/null 2>&1 || true

# The prompt is intentionally short — the full instructions are in the brief on
# disk. This keeps the invocation reproducible and the brief auditable.
if [[ "${STAGE}" == "full_pipeline" ]]; then
  PROMPT="Execute the RL concept-video full_pipeline stage for lesson_id '${LESSON_ID}'.
Read your complete instructions from this brief file first: ${BRIEF}
This stage covers: Script Writer plan.md, Visual Director choreo.md, Gate 1 RL Expert review,
Gate 2 Technical Validator (including live Gymnasium checks), and Manim scene_render.
Use all relevant skills listed in the brief. Do the work end-to-end without asking for confirmation.
Your FINAL message must be exactly the structured result block specified in the brief's 'Result format' section — nothing else."
else
  PROMPT="Execute the RL concept-video ${STAGE} stage for lesson_id '${LESSON_ID}'.
Read your complete instructions from this brief file first: ${BRIEF}
Use the manim-rl-animation-style-lock skill (canonical: ~/.codex/skills/manim-rl-animation-style-lock/SKILL.md).
Do the work end-to-end without asking for confirmation.
Your FINAL message must be exactly the structured result block specified in the brief's 'Result format' section — nothing else."
fi

MODEL_ARGS=()
[[ -n "${MODEL}" ]] && MODEL_ARGS=(--model "${MODEL}")

set +e
"${CODEX_BIN}" exec \
  --cd "${PROJECT_ROOT}" \
  --sandbox danger-full-access \
  --output-last-message "${RESULT}" \
  ${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"} \
  "${PROMPT}"
codex_rc=$?
set -e

if [[ ${codex_rc} -eq 0 ]]; then
  "${PY}" -m "${STATE_HELPER}" set-handoff "${LESSON_ID}" \
    --stage "${STAGE}" --status codex_done --result "${RESULT}" >/dev/null 2>&1 || true
  echo ""
  echo "Codex ${STAGE} stage finished. Result written to:"
  echo "  ${RESULT}"
else
  "${PY}" -m "${STATE_HELPER}" set-handoff "${LESSON_ID}" \
    --stage "${STAGE}" --status codex_failed --result "${RESULT}" >/dev/null 2>&1 || true
  echo "Codex ${STAGE} stage FAILED (exit ${codex_rc}). Inspect ${RESULT}" >&2
fi

# Return ownership to the orchestrator regardless of outcome.
"${PY}" -m "${STATE_HELPER}" set-owner "${LESSON_ID}" claude >/dev/null 2>&1 || true

exit ${codex_rc}
