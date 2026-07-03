#!/bin/bash
# Antigravity2RPM & DEB Autobuild - Quick Installer
# Usage: curl -sSL https://raw.githubusercontent.com/RLuf/antigravity_autobuild_rpm_deb/main/install.sh | bash

set -e

echo "=== Antigravity Autobuild (RPM/DEB) Installer ==="
INSTALL_DIR="$HOME/antigravity_autobuild"

echo "1. Checking dependencies..."
if command -v dnf >/dev/null 2>&1; then
    echo "Fedora/RHEL detected. Installing dependencies..."
    sudo dnf install -y rpm-build rpmdevtools python3
elif command -v apt-get >/dev/null 2>&1; then
    echo "Debian/Ubuntu detected. Installing dependencies..."
    sudo apt-get update && sudo apt-get install -y dpkg-dev python3 python3-venv
else
    echo "Unsupported package manager. Please install rpm-build or dpkg-dev manually."
fi

echo "2. Setting up environment at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "3. Downloading files..."
curl -sSLO https://raw.githubusercontent.com/RLuf/antigravity_autobuild_rpm_deb/main/antigravity_rpm_builder.py
curl -sSLO https://raw.githubusercontent.com/RLuf/antigravity_autobuild_rpm_deb/main/requirements.txt
chmod +x antigravity_rpm_builder.py

echo "4. Setting up Python Virtual Environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo ""
echo "=== Installation Successful! ==="
echo "You can now run the builder script by doing:"
echo "cd $INSTALL_DIR && source .venv/bin/activate && ./antigravity_rpm_builder.py"
