***REMOVED***!/bin/bash
***REMOVED*** SOAR B2B - Production Deployment Script
***REMOVED*** Purpose: Deploy application to /var/www/soarb2b on Ubuntu server

set -euo pipefail

***REMOVED*** Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

***REMOVED*** Configuration
APP_DIR="/var/www/soarb2b"
REPO_URL="https://github.com/SanliData/Finder_os.git"

***REMOVED*** Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (use sudo)"
    exit 1
fi

log_info "Starting SOAR B2B deployment..."
echo ""

***REMOVED*** Step 1: Clone or Update Repository
log_info "Step 1/4: Setting up application files..."

if [ -d "$APP_DIR" ] && [ -d "$APP_DIR/.git" ]; then
    log_info "Repository exists, updating..."
    cd "$APP_DIR"
    git pull origin main
else
    log_info "Cloning repository..."
    if [ -d "$APP_DIR" ]; then
        rm -rf "$APP_DIR"
    fi
    git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR/backend"
log_info "Repository ready"
echo ""

***REMOVED*** Step 2: Create .env File
log_info "Step 2/4: Setting up environment variables..."

if [ ! -f "$APP_DIR/backend/.env" ]; then
    log_warn ".env file not found. Creating from template..."
    cat > "$APP_DIR/backend/.env" << 'EOF'
ENV=production
PORT=8000
SOARB2B_API_KEYS=REPLACE_WITH_PRODUCTION_KEYS
FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
FINDEROS_CORS_ALLOW_ALL=false
FINDEROS_HOST=0.0.0.0
FINDEROS_PORT=8000
EOF
    log_warn "IMPORTANT: Edit .env file and add production API keys!"
    log_warn "  nano $APP_DIR/backend/.env"
else
    log_info ".env file exists"
fi
echo ""

***REMOVED*** Step 3: Set Permissions
log_info "Step 3/4: Setting up permissions..."

chown -R www-data:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"
chmod -R 775 "$APP_DIR/backend/data" 2>/dev/null || true

log_info "Permissions set"
echo ""

***REMOVED*** Step 4: Deploy with Docker Compose
log_info "Step 4/4: Deploying with Docker Compose..."

cd "$APP_DIR/backend"

***REMOVED*** Load environment variables from .env if it exists
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

***REMOVED*** Stop existing containers
docker-compose down 2>/dev/null || true

***REMOVED*** Build and start
docker-compose up -d --build

***REMOVED*** Wait for health check
log_info "Waiting for application to start..."
sleep 5

***REMOVED*** Check health
if curl -f http://localhost:8000/healthz > /dev/null 2>&1; then
    log_info "Application is healthy"
else
    log_warn "Health check failed. Check logs: docker-compose logs"
fi
echo ""

***REMOVED*** Summary
log_info "========================================="
log_info "Deployment Complete!"
log_info "========================================="
echo ""
log_info "Application directory: $APP_DIR"
log_info "Access application: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
log_info "Useful commands:"
echo "  View logs: cd $APP_DIR/backend && docker-compose logs -f"
echo "  Restart: cd $APP_DIR/backend && docker-compose restart"
echo "  Stop: cd $APP_DIR/backend && docker-compose down"
echo ""
