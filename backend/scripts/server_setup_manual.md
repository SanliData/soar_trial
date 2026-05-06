***REMOVED*** SOAR B2B - Manual Server Setup Guide
***REMOVED*** Ubuntu 22.04 LTS Production Server

***REMOVED******REMOVED*** Prerequisites

- Ubuntu 22.04 LTS server
- Root or sudo access
- SSH access to the server

***REMOVED******REMOVED*** Step-by-Step Manual Setup

***REMOVED******REMOVED******REMOVED*** 1. Connect to Server

```bash
ssh root@YOUR_SERVER_IP
***REMOVED*** or
ssh user@YOUR_SERVER_IP
```

***REMOVED******REMOVED******REMOVED*** 2. System Update

```bash
apt-get update
apt-get upgrade -y
apt-get install -y curl wget git nano htop ufw fail2ban
```

***REMOVED******REMOVED******REMOVED*** 3. Firewall Configuration (UFW)

```bash
***REMOVED*** Enable UFW
ufw --force enable

***REMOVED*** Set defaults
ufw default deny incoming
ufw default allow outgoing

***REMOVED*** Allow SSH (CRITICAL - do this first!)
ufw allow 22/tcp comment 'SSH'

***REMOVED*** Allow HTTP and HTTPS
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

***REMOVED*** Check status
ufw status verbose
```

**WARNING:** Make sure SSH access works before proceeding!

***REMOVED******REMOVED******REMOVED*** 4. Docker Installation

```bash
***REMOVED*** Remove old Docker versions
apt-get remove -y docker docker-engine docker.io containerd runc

***REMOVED*** Install prerequisites
apt-get install -y ca-certificates gnupg lsb-release

***REMOVED*** Add Docker's GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

***REMOVED*** Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

***REMOVED*** Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

***REMOVED*** Start Docker
systemctl start docker
systemctl enable docker

***REMOVED*** Add user to docker group (replace 'youruser' with actual username)
usermod -aG docker youruser

***REMOVED*** Verify installation
docker --version
docker compose version
```

***REMOVED******REMOVED******REMOVED*** 5. Create Application Directory

```bash
***REMOVED*** Create directory
mkdir -p /var/www/soarb2b
chown -R www-data:www-data /var/www/soarb2b
chmod 755 /var/www/soarb2b

***REMOVED*** Create subdirectories
mkdir -p /var/www/soarb2b/data
mkdir -p /var/www/soarb2b/logs
chown -R www-data:www-data /var/www/soarb2b/data
chown -R www-data:www-data /var/www/soarb2b/logs
```

***REMOVED******REMOVED******REMOVED*** 6. Fail2ban Configuration

```bash
***REMOVED*** Enable fail2ban
systemctl enable fail2ban
systemctl start fail2ban

***REMOVED*** Create custom jail config
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400
findtime = 600
EOF

***REMOVED*** Restart fail2ban
systemctl restart fail2ban

***REMOVED*** Check status
fail2ban-client status
```

***REMOVED******REMOVED******REMOVED*** 7. Automatic Security Updates

```bash
***REMOVED*** Install unattended-upgrades
apt-get install -y unattended-upgrades apt-listchanges

***REMOVED*** Configure
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

***REMOVED*** Enable
systemctl enable unattended-upgrades
systemctl start unattended-upgrades
```

***REMOVED******REMOVED******REMOVED*** 8. Reboot and Verify

```bash
***REMOVED*** Reboot server
reboot

***REMOVED*** After reboot, reconnect and verify:
***REMOVED*** - SSH access works
***REMOVED*** - Docker is running: systemctl status docker
***REMOVED*** - Firewall is active: ufw status
***REMOVED*** - Fail2ban is active: systemctl status fail2ban
```

***REMOVED******REMOVED*** Next Steps

1. Clone repository to `/var/www/soarb2b`
2. Set up `.env` file with production values
3. Configure Nginx reverse proxy
4. Set up SSL certificate (Let's Encrypt)
5. Deploy application with Docker Compose

See `DEPLOY_TO_SOARB2B_COM.md` for deployment instructions.
