#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${RL_IDE_PYTHON_BIN:-/Users/ultramarine/.venvs/manim/bin/python}"
FLUTTER_BIN="${RL_IDE_FLUTTER_BIN:-flutter}"
FRONTEND_DEVICE="${1:-macos}"
WORKER_PORT="${RL_IDE_WORKER_PORT:-8100}"
GATEWAY_PORT="${RL_IDE_GATEWAY_PORT:-8000}"
WORKER_URL="${RL_IDE_EXECUTION_WORKER_URL:-http://127.0.0.1:${WORKER_PORT}}"
LOG_DIR="${ROOT_DIR}/output/runtime_logs"
DOCKER_APP_BIN="/Applications/Docker.app/Contents/Resources/bin"

mkdir -p "${LOG_DIR}"

info() {
  printf '[start_app] %s\n' "$*"
}

fail() {
  printf '[start_app] ERROR: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

ensure_python() {
  [[ -x "${PYTHON_BIN}" ]] || fail "Python binary not found: ${PYTHON_BIN}"
}

ensure_flutter() {
  require_command "${FLUTTER_BIN}"
}

ensure_docker_cli() {
  if command -v docker >/dev/null 2>&1; then
    return
  fi

  if [[ -x "${DOCKER_APP_BIN}/docker" ]]; then
    export PATH="${DOCKER_APP_BIN}:${PATH}"
  fi

  command -v docker >/dev/null 2>&1 || fail "Docker CLI not found. Install Docker Desktop first."

  if [[ -x "${DOCKER_APP_BIN}/docker-credential-desktop" ]]; then
    ln -sf "${DOCKER_APP_BIN}/docker" /opt/homebrew/bin/docker 2>/dev/null || true
    ln -sf "${DOCKER_APP_BIN}/docker-credential-desktop" /opt/homebrew/bin/docker-credential-desktop 2>/dev/null || true
    ln -sf "${DOCKER_APP_BIN}/docker-credential-osxkeychain" /opt/homebrew/bin/docker-credential-osxkeychain 2>/dev/null || true
  fi
}

wait_for_http() {
  local url="$1"
  local label="$2"
  local attempts="${3:-30}"

  for ((i = 1; i <= attempts; i++)); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      info "${label} is ready."
      return 0
    fi
    sleep 1
  done

  fail "${label} did not become ready at ${url}"
}

wait_for_docker() {
  if docker info >/dev/null 2>&1; then
    info "Docker daemon is ready."
    return
  fi

  info "Starting Docker Desktop..."
  open -a Docker >/dev/null 2>&1 || fail "Could not launch Docker Desktop."

  for ((i = 1; i <= 60; i++)); do
    if docker info >/dev/null 2>&1; then
      info "Docker daemon is ready."
      return
    fi
    sleep 2
  done

  fail "Docker Desktop did not become ready in time."
}

start_worker() {
  if lsof -nP -iTCP:"${WORKER_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
    info "Execution worker already listening on ${WORKER_PORT}."
    return
  fi

  info "Starting execution worker..."
  (
    cd "${ROOT_DIR}" &&
      exec "${PYTHON_BIN}" -m backend.execution_worker.main
  ) >"${LOG_DIR}/worker.log" 2>&1 &

  wait_for_http "http://127.0.0.1:${WORKER_PORT}/" "Execution worker"
}

start_gateway() {
  if lsof -nP -iTCP:"${GATEWAY_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
    info "Gateway already listening on ${GATEWAY_PORT}."
    return
  fi

  info "Starting backend gateway..."
  (
    cd "${ROOT_DIR}" &&
      export RL_IDE_EXECUTION_MODE=remote &&
      export RL_IDE_EXECUTION_WORKER_URL="${WORKER_URL}" &&
      exec "${PYTHON_BIN}" -m backend.main
  ) >"${LOG_DIR}/gateway.log" 2>&1 &

  wait_for_http "http://127.0.0.1:${GATEWAY_PORT}/" "Backend gateway"
}

verify_workspace_health() {
  local payload
  payload="$(curl -fsS "http://127.0.0.1:${GATEWAY_PORT}/workspace/health")" || fail "Could not fetch workspace health."
  printf '%s' "${payload}" | grep -q '"ready":true' || fail "Workspace runtime is not ready. Response: ${payload}"
  info "Workspace runtime health check passed."
}

launch_frontend() {
  info "Launching Flutter app on device '${FRONTEND_DEVICE}'..."
  cd "${ROOT_DIR}/frontend"
  exec "${FLUTTER_BIN}" run -d "${FRONTEND_DEVICE}"
}

main() {
  ensure_python
  ensure_flutter
  ensure_docker_cli
  wait_for_docker
  start_worker
  start_gateway
  verify_workspace_health
  info "Logs:"
  info "  worker  -> ${LOG_DIR}/worker.log"
  info "  gateway -> ${LOG_DIR}/gateway.log"
  launch_frontend
}

main "$@"
