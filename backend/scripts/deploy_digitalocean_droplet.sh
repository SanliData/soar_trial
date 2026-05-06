***REMOVED***!/bin/bash
***REMOVED*** DigitalOcean Droplet üzerinde canlı deploy
***REMOVED*** Kullanım: Droplet'te /opt/Finder_os dizininden:
***REMOVED***   ./backend/scripts/deploy_digitalocean_droplet.sh
***REMOVED*** veya: cd /opt/Finder_os && backend/scripts/deploy_digitalocean_droplet.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"

echo "=========================================="
echo "SOAR B2B - DigitalOcean Droplet Deploy"
echo "=========================================="
echo ""

echo "[1/3] Repo root: $REPO_ROOT"
cd "$REPO_ROOT"

echo "[2/3] Pulling latest from GitHub (main)..."
git fetch origin main
git pull origin main

echo "[3/3] Building and starting containers..."
cd "$BACKEND_DIR"
docker compose up -d --build

echo ""
echo "Deploy complete. Checking status..."
docker compose ps
echo ""
echo "Logs (last 20 lines):"
docker compose logs --tail=20
echo ""
echo "Health: curl http://localhost:${PORT:-8000}/healthz"
