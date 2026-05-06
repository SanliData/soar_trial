***REMOVED***!/bin/bash
***REMOVED*** SOAR B2B - Production Server Setup Script
***REMOVED*** Ubuntu 22.04 LTS
***REMOVED*** Purpose: Secure server setup for B2B SaaS deployment

set -euo pipefail

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' ***REMOVED*** No Color

***REMOVED*** Logging function
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

***REMOVED*** Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (use sudo)"
    exit 1
fi

log_info "Starting SOAR B2B production server setup..."
echo ""

***REMOVED*** Step 1: System Update
log_info "Step 1/5: Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
    curl \
    wget \
    git \
    nano \
    htop \
    ufw \
    fail2ban \
    unattended-upgrades \
    apt-listchanges
log_info "System packages updated"
echo ""

***REMOVED*** Step 2: UFW Firewall Configuration
log_info "Step 2/5: Configuring UFW firewall..."

***REMOVED*** Enable UFW if not already enabled
ufw --force enable

***REMOVED*** Default policies
ufw default deny incoming
ufw default allow outgoing

***REMOVED*** Allow SSH (important - do this first!)
log_warn "Allowing SSH on port 22. Make sure you have SSH access before continuing!"
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

***REMOVED*** Show status
ufw status verbose
log_info "Firewall configured: SSH (22), HTTP (80), HTTPS (443)"
echo ""

***REMOVED*** Step 3: Docker Installation
log_info "Step 3/5: Installing Docker and Docker Compose..."

***REMOVED*** Remove old versions if any
apt-get remove -y -qq docker docker-engine docker.io containerd runc 2>/dev/null || true

***REMOVED*** Install prerequisites
apt-get install -y -qq \
    ca-certificates \
    gnupg \
    lsb-release

***REMOVED*** Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

***REMOVED*** Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

***REMOVED*** Install Docker Engine
apt-get update -qq
apt-get install -y -qq \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

***REMOVED*** Start and enable Docker
systemctl start docker
systemctl enable docker

***REMOVED*** Add current user to docker group (if not root)
if [ -n "${SUDO_USER:-}" ]; then
    usermod -aG docker "$SUDO_USER"
    log_info "Added $SUDO_USER to docker group"
fi

***REMOVED*** Verify Docker installation
docker_version=$(docker --version)
docker_compose_version=$(docker compose version)
log_info "Docker installed: $docker_version"
log_info "Docker Compose installed: $docker_compose_version"
echo ""

***REMOVED*** Step 4: Application Directory Setup
log_info "Step 4/5: Creating application directory..."

APP_DIR="/var/www/soarb2b"

***REMOVED*** Create directory
mkdir -p "$APP_DIR"
chown -R www-data:www-data "$APP_DIR"
chmod 755 "$APP_DIR"

***REMOVED*** Create subdirectories
mkdir -p "$APP_DIR/data"
mkdir -p "$APP_DIR/logs"
chown -R www-data:www-data "$APP_DIR/data"
chown -R www-data:www-data "$APP_DIR/logs"
chmod 755 "$APP_DIR/data"
chmod 755 "$APP_DIR/logs"

log_info "Application directory created: $APP_DIR"
log_info "Owner: www-data:www-data"
echo ""

***REMOVED*** Step 5: Fail2ban Configuration
log_info "Step 5/5: Configuring fail2ban..."

***REMOVED*** Enable fail2ban
systemctl enable fail2ban
systemctl start fail2ban

***REMOVED*** Create custom jail for SSH
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = root@localhost
sendername = Fail2Ban
action = %(action_)s

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400
findtime = 600

[sshd-ddos]
enabled = true
port = 22
filter = sshd-ddos
logpath = /var/log/auth.log
maxretry = 10
findtime = 600
EOF

***REMOVED*** Restart fail2ban
systemctl restart fail2ban

***REMOVED*** Verify fail2ban status
fail2ban_status=$(systemctl is-active fail2ban)
if [ "$fail2ban_status" = "active" ]; then
    log_info "Fail2ban is active"
    fail2ban-client status
else
    log_warn "Fail2ban may not be running properly"
fi
echo ""

***REMOVED*** Additional Security: Automatic Security Updates
log_info "Configuring automatic security updates..."
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

systemctl enable unattended-upgrades
systemctl start unattended-upgrades
log_info "Automatic security updates configured"
echo ""

***REMOVED*** Summary
log_info "========================================="
log_info "Server Setup Complete!"
log_info "========================================="
echo ""
log_info "Summary:"
echo "  ✓ System updated"
echo "  ✓ Firewall configured (SSH, HTTP, HTTPS)"
echo "  ✓ Docker installed"
echo "  ✓ Application directory: $APP_DIR"
echo "  ✓ Fail2ban configured"
echo "  ✓ Automatic security updates enabled"
echo ""
log_warn "Important Next Steps:"
echo "  1. Reboot the server: sudo reboot"
echo "  2. Verify SSH access still works after reboot"
echo "  3. Clone SOAR B2B repository to $APP_DIR"
echo "  4. Set up environment variables (.env file)"
echo "  5. Configure Nginx reverse proxy"
echo "  6. Set up SSL certificate (Let's Encrypt)"
echo ""
log_info "For deployment instructions, see: DEPLOY_TO_SOARB2B_COM.md"
echo ""
