#!/usr/bin/env bash
set -euo pipefail

service_name="${SERVICE_NAME:-all-in-one}"
host="${RL_IDE_BACKEND_HOST:-0.0.0.0}"
gateway_port="${PORT:-${RL_IDE_GATEWAY_PORT:-8000}}"
worker_port="${RL_IDE_EXECUTION_WORKER_PORT:-8100}"
user_port="${RL_IDE_USER_EVALUATION_PORT:-8200}"

export RL_IDE_BACKEND_HOST="${host}"
export RL_IDE_GATEWAY_PORT="${gateway_port}"
export RL_IDE_EXECUTION_WORKER_PORT="${worker_port}"
export RL_IDE_USER_EVALUATION_PORT="${user_port}"

export RL_IDE_EXECUTION_MODE="${RL_IDE_EXECUTION_MODE:-remote}"
export RL_IDE_USER_SERVICE_MODE="${RL_IDE_USER_SERVICE_MODE:-remote}"
export RL_IDE_EXECUTION_WORKER_URL="${RL_IDE_EXECUTION_WORKER_URL:-http://127.0.0.1:${worker_port}}"
export RL_IDE_USER_SERVICE_URL="${RL_IDE_USER_SERVICE_URL:-http://127.0.0.1:${user_port}}"
export RL_IDE_WORKSPACE_USE_DOCKER="${RL_IDE_WORKSPACE_USE_DOCKER:-0}"
export RL_IDE_MANIM_PYTHON="${RL_IDE_MANIM_PYTHON:-python3}"

run_gateway() {
  exec uvicorn backend.api_gateway.base:create_app \
    --factory \
    --host "${host}" \
    --port "${gateway_port}"
}

run_worker() {
  exec uvicorn backend.execution_worker.base:create_app \
    --factory \
    --host "${host}" \
    --port "${worker_port}"
}

run_user_service() {
  exec uvicorn backend.user_evaluation_service.base:create_app \
    --factory \
    --host "${host}" \
    --port "${user_port}"
}

run_all_in_one() {
  local pids=()
  uvicorn backend.execution_worker.base:create_app --factory --host "${host}" --port "${worker_port}" &
  pids+=("$!")
  uvicorn backend.user_evaluation_service.base:create_app --factory --host "${host}" --port "${user_port}" &
  pids+=("$!")
  uvicorn backend.api_gateway.base:create_app --factory --host "${host}" --port "${gateway_port}" &
  pids+=("$!")

  cleanup() {
    for pid in "${pids[@]}"; do
      kill "${pid}" 2>/dev/null || true
    done
  }
  trap cleanup TERM INT EXIT

  wait -n "${pids[@]}"
  local exit_code=$?
  cleanup
  wait || true
  exit "${exit_code}"
}

case "${service_name}" in
  all-in-one)
    run_all_in_one
    ;;
  gateway)
    run_gateway
    ;;
  execution-worker)
    run_worker
    ;;
  user-evaluation)
    run_user_service
    ;;
  *)
    echo "Unsupported SERVICE_NAME '${service_name}'. Use one of: all-in-one, gateway, execution-worker, user-evaluation."
    exit 1
    ;;
esac
