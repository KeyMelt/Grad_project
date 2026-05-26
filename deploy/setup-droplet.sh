#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# setup-droplet.sh — Idempotent bootstrap for an Ubuntu 22.04 DigitalOcean
# Droplet running the RL Platform Docker Compose stack.
#
# Usage:
#   sudo ./setup-droplet.sh [--user USERNAME]
#
# Defaults to ubuntu as the deploy user. Safe to re-run multiple times.
# ---------------------------------------------------------------------------

# ── Root check ──────────────────────────────────────────────────────────────
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "ERROR: This script must be run as root (sudo ./setup-droplet.sh)" >&2
  exit 1
fi

# ── Argument parsing ─────────────────────────────────────────────────────────
DEPLOY_USER="${SUDO_USER:-ubuntu}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)
      DEPLOY_USER="${2:?--user requires a username argument}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      echo "Usage: sudo $0 [--user USERNAME]" >&2
      exit 1
      ;;
  esac
done

echo "==> Deploy user: ${DEPLOY_USER}"

# ── 1. System packages ───────────────────────────────────────────────────────
echo "==> [1/8] Updating apt and installing prerequisites..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  ufw \
  git

# ── 2. Docker Engine (official apt repo, not snap) ───────────────────────────
echo "==> [2/8] Installing Docker Engine from official apt repository..."

DOCKER_KEYRING=/etc/apt/keyrings/docker.gpg
if [[ ! -f "${DOCKER_KEYRING}" ]]; then
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o "${DOCKER_KEYRING}"
  chmod a+r "${DOCKER_KEYRING}"
  echo "    Docker GPG key added."
else
  echo "    Docker GPG key already present, skipping."
fi

DOCKER_LIST=/etc/apt/sources.list.d/docker.list
if [[ ! -f "${DOCKER_LIST}" ]]; then
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=${DOCKER_KEYRING}] \
https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" \
    > "${DOCKER_LIST}"
  echo "    Docker apt repository added."
else
  echo "    Docker apt repository already present, skipping."
fi

apt-get update -q
apt-get install -y -q \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

# ── 3. Start and enable Docker ───────────────────────────────────────────────
echo "==> [3/8] Enabling and starting Docker service..."
systemctl enable --now docker
echo "    Docker is running: $(docker version --format '{{.Server.Version}}' 2>/dev/null || echo 'check manually')"

# ── 4. Add deploy user to docker group ──────────────────────────────────────
echo "==> [4/8] Adding '${DEPLOY_USER}' to the docker group..."
if id "${DEPLOY_USER}" &>/dev/null; then
  usermod -aG docker "${DEPLOY_USER}"
  echo "    Done. '${DEPLOY_USER}' must log out and back in for this to take effect."
else
  echo "    WARNING: User '${DEPLOY_USER}' does not exist — skipping docker group add."
fi

# ── 5. Create data directories ───────────────────────────────────────────────
echo "==> [5/8] Creating /srv/rl-platform data directories..."
mkdir -p \
  /srv/rl-platform/data \
  /srv/rl-platform/animations \
  /srv/rl-platform/concept-videos \
  /srv/rl-platform/letsencrypt \
  /srv/rl-platform/secrets
echo "    Directories created."

# ── 6. Set ownership ─────────────────────────────────────────────────────────
echo "==> [6/8] Setting ownership of /srv/rl-platform to ${DEPLOY_USER}:${DEPLOY_USER}..."
if id "${DEPLOY_USER}" &>/dev/null; then
  chown -R "${DEPLOY_USER}:${DEPLOY_USER}" /srv/rl-platform
else
  echo "    WARNING: User '${DEPLOY_USER}' does not exist — ownership not changed."
fi

# ── 7. Configure UFW firewall ────────────────────────────────────────────────
echo "==> [7/8] Configuring UFW firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   comment 'SSH'
ufw allow 80/tcp   comment 'HTTP'
ufw allow 443/tcp  comment 'HTTPS'
ufw --force enable
echo "    UFW status:"
ufw status verbose

# ── 8. Install Certbot ───────────────────────────────────────────────────────
echo "==> [8/8] Installing Certbot (Let's Encrypt)..."
apt-get install -y -q certbot
echo "    Certbot version: $(certbot --version 2>&1)"

# ── Done ─────────────────────────────────────────────────────────────────────
cat <<EOF

============================================================
  Droplet setup complete!
============================================================

Next steps:

  1. Upload your Firebase service-account JSON key:
       scp firebase-admin-key.json ${DEPLOY_USER}@<droplet-ip>:/srv/rl-platform/secrets/

  2. Copy the environment template and fill in real values:
       cp deploy/prod.env.template .env
       nano .env   # Set all required secrets

  3. (Optional) Issue a TLS certificate with Certbot before starting:
       certbot certonly --standalone -d your-domain.com

  4. Pull images and start the stack:
       docker compose -f docker-compose.prod.yml --env-file .env pull
       docker compose -f docker-compose.prod.yml --env-file .env up -d

  5. Tail logs to confirm healthy startup:
       docker compose -f docker-compose.prod.yml logs -f

NOTE: '${DEPLOY_USER}' must re-login for the docker group change to take effect.
============================================================
EOF
