#!/usr/bin/env bash
set -euo pipefail

# Home Dashboard CRT installer for Raspberry Pi
# Usage (from your Pi):
#   wget -qO- https://raw.githubusercontent.com/<YOUR-USER>/Home_Dashboard_CRT/main/install_pi.sh | sudo bash
# Edit REPO_URL below if you want the script to clone a different repository.

REPO_URL="${REPO_URL:-https://github.com/USERNAME/Home_Dashboard_CRT.git}"
BRANCH="${BRANCH:-main}"
INSTALL_DIR="${INSTALL_DIR:-/opt/home_dashboard_crt}"
RUN_USER="${SUDO_USER:-pi}"
VENV_DIR="$INSTALL_DIR/venv"

if [ "$(id -u)" -ne 0 ]; then
  echo "This installer requires sudo. Re-running with sudo..."
  exec sudo bash "$0" "$@"
fi

echo "Installing Home Dashboard CRT to $INSTALL_DIR"

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This installer expects a Debian-based distro with apt. Aborting."
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git python3 python3-venv python3-pip chromium-browser x11-xserver-utils unclutter xdotool || true

if [ -d "$INSTALL_DIR" ]; then
  echo "Directory $INSTALL_DIR already exists."
  read -p "Do you want to update it (git pull) [Y/n]? " ans || true
  ans="${ans:-Y}"
  if [[ "$ans" =~ ^[Yy]$ ]]; then
    cd "$INSTALL_DIR"
    if [ -d .git ]; then
      git fetch --all || true
      git reset --hard "origin/$BRANCH" || true
      git pull --rebase origin "$BRANCH" || true
    else
      echo "No git repo found in $INSTALL_DIR — removing and re-cloning."
      rm -rf "$INSTALL_DIR"
      git clone --depth 1 -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    fi
  else
    echo "Leaving existing directory. Exiting."
    exit 0
  fi
else
  git clone --depth 1 -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

# Create Python venv and install requirements
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
  "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
else
  "$VENV_DIR/bin/pip" install flask requests feedparser ics python-dateutil
fi

# Set ownership
chown -R "$RUN_USER":"$RUN_USER" "$INSTALL_DIR"

# Create config.json from example if missing
if [ ! -f "$INSTALL_DIR/config.json" ]; then
  cp "$INSTALL_DIR/config.example.json" "$INSTALL_DIR/config.json"
  chown "$RUN_USER":"$RUN_USER" "$INSTALL_DIR/config.json"
  chmod 600 "$INSTALL_DIR/config.json"
  echo "Created $INSTALL_DIR/config.json — please edit it with your Home Assistant token and settings."
fi

# Install systemd service templates if present
if [ -d "$INSTALL_DIR/systemd" ]; then
  for f in "$INSTALL_DIR"/systemd/*.service; do
    [ -e "$f" ] || continue
    dest="/etc/systemd/system/$(basename "$f")"
    echo "Installing $dest"
    sed -e "s|@INSTALL_DIR@|$INSTALL_DIR|g" -e "s|@RUN_USER@|$RUN_USER|g" "$f" > "$dest"
    chmod 644 "$dest"
  done
  systemctl daemon-reload
  systemctl enable --now home_dashboard.service || true
  systemctl enable --now home_dashboard_kiosk.service || true
fi

cat <<EOF

Installation complete.

Next steps:
- Edit the configuration: sudo -u $RUN_USER nano $INSTALL_DIR/config.json
- If you prefer to run manually: start the python server (inside venv):
    $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/server.py
- To manage services:
    sudo systemctl restart home_dashboard.service
    sudo systemctl restart home_dashboard_kiosk.service

Notes:
- If you use autologin into the Pi desktop, the kiosk service should be able to start Chromium on display :0.
- If Chromium fails to start, try running the kiosk command manually as the user to debug.

EOF
