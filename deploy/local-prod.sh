#!/bin/sh
set -eu

ROOT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
SUPPORT_DIR="${HOME}/Desktop/grad_support_files/grad_project"
GENERATED_RENDERS_DIR="${SUPPORT_DIR}/generated_renders"
ENV_FILE="${RL_IDE_LOCAL_PROD_ENV_FILE:-${SUPPORT_DIR}/local-prod.env}"
STATE_DIR_DEFAULT="${SUPPORT_DIR}/local_prod"
CERTS_DIR_DEFAULT="${STATE_DIR_DEFAULT}/letsencrypt-empty"
FIREBASE_DEFAULT="${HOME}/Desktop/grad_support_files/keys/rlplat-firebase-adminsdk-fbsvc-a681c11b6c.json"
GENERATED_CONCEPT_MEDIA_DIR="${GENERATED_RENDERS_DIR}/backend/media/concept_videos"
REPO_CONCEPT_MEDIA_DIR="${ROOT_DIR}/backend/media/concept_videos"
REPO_TRACE_MEDIA_DIR="${ROOT_DIR}/backend/media/traces"
REPO_VISUALIZATION_DIR="${ROOT_DIR}/backend/visualization/animations"

generate_secret() {
  python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
}

ensure_env_file() {
  mkdir -p "${SUPPORT_DIR}" "${STATE_DIR_DEFAULT}/data" "${STATE_DIR_DEFAULT}/animations" "${STATE_DIR_DEFAULT}/concept-videos" "${CERTS_DIR_DEFAULT}"
  if [ -f "${ENV_FILE}" ]; then
    return
  fi

  firebase_file=""
  if [ -f "${FIREBASE_DEFAULT}" ]; then
    firebase_file="${FIREBASE_DEFAULT}"
  fi

  cat > "${ENV_FILE}" <<EOF
RL_IDE_IMAGE=rl-platform:cloud
RL_IDE_FRONTEND_IMAGE=rl-platform-frontend:local

RL_IDE_LOCAL_STATE_DIR=${STATE_DIR_DEFAULT}
RL_IDE_LOCAL_CERTS_DIR=${CERTS_DIR_DEFAULT}

RL_IDE_HTTP_BIND=127.0.0.1:18080
RL_IDE_HTTPS_BIND=127.0.0.1:18443
RL_IDE_GATEWAY_BIND=127.0.0.1:18000
RL_IDE_TLS_DOMAIN=localhost
RL_IDE_ALLOWED_ORIGINS=http://127.0.0.1:18080,http://localhost:18080,https://127.0.0.1:18443,https://localhost:18443

RL_IDE_INTERNAL_TOKEN=$(generate_secret)
RL_IDE_AUTH_TOKEN_SECRET=$(generate_secret)
RL_IDE_SHELL_TOKEN_SECRET=$(generate_secret)

RL_IDE_FIREBASE_CREDENTIALS_FILE=${firebase_file}
RL_IDE_FIREBASE_APP_NAME=rl-ide-backend
RL_IDE_BOOTSTRAP_ADMIN_FIREBASE_UID=
RL_IDE_BOOTSTRAP_ADMIN_DISPLAY_NAME=Platform Admin

RL_IDE_OPEN_PROVISIONING=1
RL_IDE_ALLOW_LEGACY_PASSWORD_SIGN_IN=1
RL_IDE_ALLOW_LOCAL_PASSWORD_AUTH=1
RL_IDE_MEDIA_STORAGE_BACKEND=local
RL_IDE_ALLOW_LOCAL_MEDIA_FALLBACK=1

RL_IDE_WORKSPACE_USE_DOCKER=1
RL_IDE_WORKSPACE_IMAGE=python:3.11-slim
RL_IDE_MANIM_RENDER_QUALITY=l
RL_IDE_GEMINI_ENABLED=0
RL_IDE_STUDY_BUDDY_AI_ENABLED=1
EOF

  echo "Created ${ENV_FILE}" >&2
}

ensure_state_dirs() {
  mkdir -p \
    "${GENERATED_CONCEPT_MEDIA_DIR}" \
    "${STATE_DIR_DEFAULT}/data" \
    "${STATE_DIR_DEFAULT}/animations" \
    "${STATE_DIR_DEFAULT}/animations/traces" \
    "${STATE_DIR_DEFAULT}/concept-videos" \
    "${CERTS_DIR_DEFAULT}"
}

copy_if_present() {
  src="$1"
  dest="$2"
  if [ -f "${src}" ]; then
    cp -f "${src}" "${dest}"
  fi
}

seed_media() {
  ensure_state_dirs

  for concept_source_dir in "${GENERATED_CONCEPT_MEDIA_DIR}" "${REPO_CONCEPT_MEDIA_DIR}"; do
    if [ -d "${concept_source_dir}" ]; then
      find "${concept_source_dir}" -maxdepth 1 -type f \( -name '*.mp4' -o -name '*.vtt' \) | while IFS= read -r file; do
        base="$(basename "${file}")"
        case "${base}" in
          *.prefix_bak)
            continue
            ;;
        esac
        copy_if_present "${file}" "${STATE_DIR_DEFAULT}/concept-videos/${base}"
      done
    fi
  done

  # Alias narrated lesson videos back to the canonical filenames the app expects.
  find "${STATE_DIR_DEFAULT}/concept-videos" -maxdepth 1 -type f -name '*_concept_narrated.mp4' | while IFS= read -r file; do
    canonical="$(basename "${file}" | sed 's/_concept_narrated\.mp4$/_concept.mp4/')"
    if [ ! -f "${STATE_DIR_DEFAULT}/concept-videos/${canonical}" ]; then
      cp -f "${file}" "${STATE_DIR_DEFAULT}/concept-videos/${canonical}"
    fi
  done
  find "${STATE_DIR_DEFAULT}/concept-videos" -maxdepth 1 -type f -name '*_concept_narrated_720p.mp4' | while IFS= read -r file; do
    canonical="$(basename "${file}" | sed 's/_concept_narrated_720p\.mp4$/_concept.mp4/')"
    if [ ! -f "${STATE_DIR_DEFAULT}/concept-videos/${canonical}" ]; then
      cp -f "${file}" "${STATE_DIR_DEFAULT}/concept-videos/${canonical}"
    fi
  done

  if [ -d "${REPO_TRACE_MEDIA_DIR}" ]; then
    find "${REPO_TRACE_MEDIA_DIR}" -maxdepth 1 -type f -name '*.mp4' | while IFS= read -r file; do
      copy_if_present "${file}" "${STATE_DIR_DEFAULT}/animations/traces/$(basename "${file}")"
    done
  fi

  if [ -d "${REPO_VISUALIZATION_DIR}" ]; then
    find "${REPO_VISUALIZATION_DIR}" -maxdepth 1 -type f \( -name '*.mp4' -o -name '*.png' -o -name '*.json' \) | while IFS= read -r file; do
      copy_if_present "${file}" "${STATE_DIR_DEFAULT}/animations/$(basename "${file}")"
    done
  fi

  echo "Seeded local prod media into ${STATE_DIR_DEFAULT}" >&2
}

doctor() {
  ensure_state_dirs
  docker info >/dev/null
  echo "docker: ready"
  echo "env: ${ENV_FILE}"
  echo "state: ${STATE_DIR_DEFAULT}"
  if [ -f "${ENV_FILE}" ]; then
    echo "env-file: present"
  else
    echo "env-file: missing"
  fi
  concept_count="$(find "${STATE_DIR_DEFAULT}/concept-videos" -maxdepth 1 -type f \( -name '*.mp4' -o -name '*.vtt' \) | wc -l | tr -d ' ')"
  trace_count="$(find "${STATE_DIR_DEFAULT}/animations/traces" -maxdepth 1 -type f -name '*.mp4' | wc -l | tr -d ' ')"
  echo "seeded-concept-files: ${concept_count}"
  echo "seeded-trace-videos: ${trace_count}"
}

compose() {
  docker compose \
    --env-file "${ENV_FILE}" \
    -f "${ROOT_DIR}/docker-compose.prod.yml" \
    -f "${ROOT_DIR}/docker-compose.local-prod.yml" \
    "$@"
}

command="${1:-up}"
shift || true

ensure_env_file

case "${command}" in
  up)
    compose up -d --build "$@"
    ;;
  build)
    compose build "$@"
    ;;
  down)
    compose down "$@"
    ;;
  ps)
    compose ps "$@"
    ;;
  logs)
    compose logs -f "$@"
    ;;
  config)
    compose config "$@"
    ;;
  doctor)
    doctor "$@"
    ;;
  seed-media)
    seed_media "$@"
    ;;
  restart)
    compose restart "$@"
    ;;
  *)
    echo "Usage: $0 {up|build|down|ps|logs|config|doctor|seed-media|restart} [compose args...]" >&2
    exit 1
    ;;
esac
