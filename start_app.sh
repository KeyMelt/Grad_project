#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${RL_IDE_PYTHON_BIN:-python3}"
FLUTTER_BIN="${RL_IDE_FLUTTER_BIN:-flutter}"
FRONTEND_DEVICE="macos"
GATEWAY_PORT="${RL_IDE_GATEWAY_PORT:-8000}"
DOCKER_APP_BIN="/Applications/Docker.app/Contents/Resources/bin"
COMPOSE_PROJECT_NAME="${RL_IDE_COMPOSE_PROJECT_NAME:-rl_ide}"
START_BACKEND_ONLY=0
REBUILD_BACKEND="${RL_IDE_REBUILD_BACKEND:-1}"
BACKEND_SERVICES=(gateway execution-service user-evaluation-service)

info() {
  printf '[start_app] %s\n' "$*"
}

fail() {
  printf '[start_app] ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<EOF
Usage: ./start_app.sh [device] [options]

Examples:
  ./start_app.sh
  ./start_app.sh chrome
  ./start_app.sh --backend-only

Options:
  --backend-only   Start and verify Docker backend services, then exit.
  --no-build       Do not rebuild backend images before starting services.
  -h, --help       Show this help message.
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --backend-only)
        START_BACKEND_ONLY=1
        ;;
      --no-build)
        REBUILD_BACKEND=0
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      -*)
        fail "Unknown option: $1"
        ;;
      *)
        FRONTEND_DEVICE="$1"
        ;;
    esac
    shift
  done
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

ensure_python() {
  command -v "${PYTHON_BIN}" >/dev/null 2>&1 || fail "Python binary not found: ${PYTHON_BIN}"
}

ensure_flutter() {
  require_command "${FLUTTER_BIN}"
}

ensure_docker_cli() {
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

compose() {
  (
    cd "${ROOT_DIR}" &&
      COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME}" \
      PROJECT_ROOT="${ROOT_DIR}" \
      docker compose "$@"
  )
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

  show_backend_status
  show_backend_logs
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
  return 0
}

start_gateway() {
  return 0
}

ensure_compose() {
  docker compose version >/dev/null 2>&1 || fail "Docker Compose is not available."
}

show_backend_status() {
  info "Docker Compose service status:"
  compose ps "${BACKEND_SERVICES[@]}" || true
}

show_backend_logs() {
  info "Recent backend container logs:"
  compose logs --tail=120 "${BACKEND_SERVICES[@]}" || true
}

wait_for_compose_services() {
  local attempts="${1:-60}"
  local service
  local status

  for ((i = 1; i <= attempts; i++)); do
    local ready=1
    for service in "${BACKEND_SERVICES[@]}"; do
      status="$(compose ps --format json "${service}" 2>/dev/null | python3 -c '
import json
import sys

raw = sys.stdin.read().strip()
if not raw:
    print("missing")
    raise SystemExit

try:
    parsed = json.loads(raw)
    records = parsed if isinstance(parsed, list) else [parsed]
except json.JSONDecodeError:
    records = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parsed_line = json.loads(line)
        if isinstance(parsed_line, list):
            records.extend(parsed_line)
        else:
            records.append(parsed_line)

if not records:
    print("missing")
    raise SystemExit

record = records[0]
health = record.get("Health") or ""
state = record.get("State") or record.get("Status") or ""
print(health or state)
')"
      if [[ "${status}" != "healthy" && "${status}" != "running" ]]; then
        ready=0
        break
      fi
    done

    if [[ "${ready}" -eq 1 ]]; then
      info "Docker backend services are running."
      show_backend_status
      return
    fi
    sleep 2
  done

  show_backend_status
  show_backend_logs
  fail "Docker backend services did not become healthy in time."
}

start_backend_stack() {
  local up_args=(up -d --remove-orphans)
  if [[ "${REBUILD_BACKEND}" == "1" || "${REBUILD_BACKEND}" == "true" || "${REBUILD_BACKEND}" == "yes" ]]; then
    up_args+=(--build)
  fi
  up_args+=("${BACKEND_SERVICES[@]}")

  info "Starting Docker backend services: ${BACKEND_SERVICES[*]}"
  compose "${up_args[@]}"

  wait_for_compose_services 90
  wait_for_http "http://127.0.0.1:${GATEWAY_PORT}/" "Backend gateway" 90
}

verify_workspace_health() {
  local payload
  payload="$(curl -fsS "http://127.0.0.1:${GATEWAY_PORT}/workspace/health")" || fail "Could not fetch workspace health."
  if ! printf '%s' "${payload}" | grep -q '"ready":true'; then
    show_backend_status
    show_backend_logs
    fail "Workspace runtime is not ready. Response: ${payload}"
  fi
  info "Workspace runtime health check passed."
}

launch_frontend() {
  info "Launching Flutter app on device '${FRONTEND_DEVICE}'..."
  cd "${ROOT_DIR}/frontend"
  exec "${FLUTTER_BIN}" run -d "${FRONTEND_DEVICE}"
}

main() {
  parse_args "$@"
  ensure_python
  if [[ "${START_BACKEND_ONLY}" -eq 0 ]]; then
    ensure_flutter
  fi
  ensure_docker_cli
  ensure_compose
  wait_for_docker
  start_backend_stack
  verify_workspace_health
  info "Backend logs: COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME} PROJECT_ROOT=${ROOT_DIR} docker compose logs -f ${BACKEND_SERVICES[*]}"
  if [[ "${START_BACKEND_ONLY}" -eq 1 ]]; then
    info "Backend-only mode complete."
    exit 0
  fi
  launch_frontend
}

main "$@"
