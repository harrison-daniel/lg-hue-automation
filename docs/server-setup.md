# Ubuntu Server Setup & Hardening Guide

This documents every step taken to secure and configure the Ubuntu Server
(MacBook Air running Ubuntu 24.04 LTS) for this project.

---

## Step 0.1 — SSH Key Authentication

### What this does
Switches SSH login from password-based to key-based authentication.
Password login is vulnerable to brute-force attacks. SSH keys use
cryptographic key pairs — your private key stays on your laptop,
the public key goes on the server. Only someone with the private key
can connect.

### On your main laptop (Windows/Git Bash):

```bash
# Check if you already have an SSH key
ls ~/.ssh/id_ed25519.pub
```

If that file doesn't exist, generate a new key:

```bash
# Generate an Ed25519 SSH key pair
# Ed25519 is the modern standard — faster and more secure than RSA
ssh-keygen -t ed25519 -C "your-email@example.com"

# When prompted:
#   - Save location: press Enter (default ~/.ssh/id_ed25519)
#   - Passphrase: enter a strong passphrase (protects key if laptop is stolen)
```

Copy the public key to the server:

```bash
# This adds your public key to the server's authorized_keys file
# Replace 'hd' with your username and the IP with your server's static IP
ssh-copy-id hd@<server-ip>
```

### On the server (SSH in first):

```bash
# Test that key-based login works BEFORE disabling password auth
# Open a NEW terminal and try connecting — it should not ask for a password
# (it may ask for your key passphrase — that's different and expected)

# Only after confirming key login works, disable password auth:
sudo nano /etc/ssh/sshd_config
```

Find and change these lines:

```
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
```

Then restart the SSH service:

```bash
# Apply the changes
sudo systemctl restart ssh

# Verify sshd is running
sudo systemctl status ssh
```

**Test immediately:** Open a new terminal, try `ssh hd@<server-ip>`.
It should connect without asking for a password. If it fails,
your current session is still open — fix the config before disconnecting.

---

## Step 0.2 — UFW Firewall

### What this does
UFW (Uncomplicated Firewall) is Ubuntu's built-in firewall tool.
It wraps iptables (the Linux kernel firewall) with a simpler interface.
Even though your UniFi network blocks inter-VLAN traffic, the server
itself should explicitly only accept traffic on ports it needs.
This is "defense in depth" — multiple layers of security.

### On the server:

```bash
# Check current status (likely inactive)
sudo ufw status

# Set default policies:
# - Deny all incoming traffic (nothing gets in unless we allow it)
# - Allow all outgoing traffic (server can reach the internet, TV, Hue Bridge)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (port 22) — CRITICAL: do this BEFORE enabling UFW
# or you'll lock yourself out
sudo ufw allow ssh

# Allow HTTP (port 80) — for the Nginx reverse proxy (your dashboard)
sudo ufw allow 80/tcp

# Allow Home Assistant (port 8123) — so you can still access HA GUI directly
# during development. You can remove this rule later once Nginx proxies it.
sudo ufw allow 8123/tcp

# Enable the firewall
sudo ufw enable

# Verify rules
sudo ufw status verbose
```

Expected output:

```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
8123/tcp                   ALLOW       Anywhere
```

### What each port is for:
- **22 (SSH):** Remote terminal access from your laptop
- **80 (HTTP):** Your Nginx reverse proxy (serves the dashboard)
- **8123 (HA):** Home Assistant web GUI (temporary, for development)

### What's NOT open:
- 443 (HTTPS) — not needed for a LAN-only app
- 3000 (Next.js dev) — only accessible via Nginx
- 8000 (FastAPI) — only accessible via Nginx
- 3001 (LG TV WebSocket) — outbound from server, not inbound

---

## Step 0.3 — Unattended Security Updates

### What this does
Automatically installs security patches. Your server runs 24/7.
If a critical vulnerability is disclosed in an Ubuntu package,
you want the fix applied within hours, not whenever you remember
to run `apt update`.

### On the server:

```bash
# Install the unattended-upgrades package (may already be installed)
sudo apt install -y unattended-upgrades

# Enable automatic security updates
sudo dpkg-reconfigure -plow unattended-upgrades
# Select "Yes" when prompted

# Verify it's configured
cat /etc/apt/apt.conf.d/20auto-upgrades
```

Expected contents:

```
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
```

This means: check for updates daily, install security updates daily.

---

## Step 0.4 — Lid Close Behavior

### What this does
By default, Ubuntu suspends (sleeps) when you close the laptop lid.
Since this is a headless server with no battery, you want it to
keep running with the lid closed.

### On the server:

```bash
# Edit the login manager config
sudo nano /etc/systemd/logind.conf
```

Find and uncomment (remove the #) these lines:

```
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
```

Apply the changes:

```bash
# Restart the login manager (this won't disconnect your SSH session)
sudo systemctl restart systemd-logind
```

Now you can close the MacBook lid and it stays running.

---

## Step 0.5 — Screen Off & Temperature Monitoring

### Screen Off

The MacBook display draws power and generates heat for no reason
on a headless server. Turn it off.

```bash
# Turn off the console display immediately
sudo sh -c 'echo 1 > /sys/class/backlight/*/bl_power' 2>/dev/null

# If the above doesn't work (depends on hardware), try:
sudo setterm --blank 1 --powerdown 2
# This blanks the screen after 1 minute, powers off display after 2

# To make it permanent across reboots, add to /etc/rc.local or a systemd service:
sudo tee /etc/systemd/system/screen-off.service << 'EOF'
[Unit]
Description=Turn off laptop screen
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/setterm --blank 1 --powerdown 2
StandardOutput=tty
TTYPath=/dev/tty1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable screen-off.service
sudo systemctl start screen-off.service
```

### Temperature Monitoring

```bash
# Install lm-sensors (hardware monitoring)
sudo apt install -y lm-sensors

# Detect available sensors on your hardware
sudo sensors-detect
# Press Enter/Yes for each prompt — it probes for sensor chips

# Read current temperatures
sensors
```

You should see output like:

```
coretemp-isa-0000
Adapter: ISA adapter
Package id 0:  +52.0°C  (high = +105.0°C, crit = +105.0°C)
Core 0:        +49.0°C  (high = +105.0°C, crit = +105.0°C)
Core 1:        +52.0°C  (high = +105.0°C, crit = +105.0°C)
```

For ongoing monitoring, a simple check you can run anytime:

```bash
# Quick temp check via SSH
sensors | grep -E "Package|Core"
```

**Safe ranges for the MacBook Air:**
- Normal idle: 40-55°C
- Under load (Docker builds): 60-80°C
- Warning: above 90°C
- Critical (auto-shutdown): 105°C

---

## Step 0.6 — Convenient SSH Alias & Shutdown

### On your main laptop (Windows/Git Bash):

Edit your SSH config to make connecting easier:

```bash
# Create or edit SSH config
nano ~/.ssh/config
```

Add:

```
Host ha-server
    HostName <server-static-ip>
    User hd
    IdentityFile ~/.ssh/id_ed25519
```

Now you can connect with just:

```bash
ssh ha-server
```

And shut down the server remotely:

```bash
ssh ha-server 'sudo shutdown now'
```

---

## Summary of What's Secured

| Layer | Protection |
|-------|-----------|
| Network (UniFi) | VLAN segmentation, IoT isolated from Main |
| Firewall (UFW) | Only ports 22, 80, 8123 open |
| SSH | Key-only auth, no root login, no passwords |
| Updates | Automatic security patches |
| Physical | Lid close ignored, screen off, temp monitoring |
