# deploy/ — DigitalOcean Production Quick Reference

## Files in this directory

| File | Purpose |
|---|---|
| `setup-droplet.sh` | Idempotent Ubuntu 22.04 droplet bootstrap |
| `prod.env.template` | Copy → `.env` on droplet, fill in real secrets |

Compose file lives at repo root: `docker-compose.prod.yml`.

## Pre-requisites

- DigitalOcean droplet running **Ubuntu 22.04** (2 vCPU / 4 GB RAM minimum)
- Domain A record pointing to the droplet's public IP
- GitHub repo secrets for CI/CD (`DO_HOST`, `DO_USER`, `DO_SSH_KEY`, `DO_DEPLOY_PATH`, `GHCR_TOKEN`)
- Firebase service-account JSON key from the Firebase Console

## Quick Start

### 1 — Bootstrap the droplet

```bash
scp deploy/setup-droplet.sh root@<droplet-ip>:~
ssh root@<droplet-ip> "bash setup-droplet.sh"
```

Installs Docker Engine, configures UFW (22/80/443), creates `/srv/rl-platform/` dirs, installs Certbot.

### 2 — Configure environment

```bash
# On the droplet
cp deploy/prod.env.template /srv/rl-platform/.env
nano /srv/rl-platform/.env                           # fill in every blank value
scp firebase-admin-key.json ubuntu@<droplet-ip>:/srv/rl-platform/secrets/
```

Generate secrets: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

### 3 — Start the stack

```bash
docker compose -f docker-compose.prod.yml --env-file /srv/rl-platform/.env pull
docker compose -f docker-compose.prod.yml --env-file /srv/rl-platform/.env up -d
docker compose -f docker-compose.prod.yml logs -f
```

Frontend (nginx + Flutter web) is on **port 80**. Browser-facing API/media routes proxy to the gateway on the internal Docker network. The gateway calls the dedicated `manim-service` container at `http://manim-service:8300` for trace/video rendering.

### 4 — CI/CD

The workflow at `.github/workflows/ci.yml` runs tests for pull requests. On pushes to `main`, it also:

1. Builds and pushes backend/frontend images to GHCR with both `${GITHUB_SHA}` and `latest` tags.
2. Uploads `docker-compose.prod.yml` to the Droplet.
3. Logs the Droplet into GHCR.
4. Runs `docker compose pull` and `docker compose up -d --no-build --remove-orphans` with the immutable SHA image tags.
5. Smoke-tests `http://127.0.0.1/health` on the Droplet.

Required GitHub Actions secrets:

| Secret | Purpose |
|---|---|
| `DO_HOST` | Droplet IP or hostname |
| `DO_USER` | SSH user, usually `ubuntu` |
| `DO_SSH_KEY` | Private deploy key authorized on the Droplet |
| `DO_DEPLOY_PATH` | Repo/compose directory on Droplet, e.g. `/home/ubuntu/rl-platform` |
| `GHCR_TOKEN` | PAT with permission to pull GHCR packages from the Droplet |
| `DO_PORT` | Optional SSH port, defaults to `22` |
| `DO_ENV_FILE` | Optional env path, defaults to `/srv/rl-platform/.env` |
| `GHCR_PULL_USER` | Optional GHCR username, defaults to the GitHub actor |
