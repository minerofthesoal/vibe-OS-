#!/usr/bin/env bash
# ==============================================================================
# ArchForge - Module 1: Surface Kernel Injection
# Description: Adds linux-surface repo and installs the custom kernel.
# Note: This script should be run INSIDE the chroot (/mnt).
# ==============================================================================

source "$(dirname "$0")/utils.sh"
require_root

log_info "Injecting linux-surface repository..."

# 1. Import Keys
log_info "Importing linux-surface GPG keys..."
pacman-key --recv-keys 56C464BAAC421453
pacman-key --finger 56C464BAAC421453
pacman-key --lsign-key 56C464BAAC421453

# 2. Add Repository to pacman.conf
if ! grep -q "\[linux-surface\]" /etc/pacman.conf; then
    log_info "Adding [linux-surface] to /etc/pacman.conf..."
    cat <<EOF >> /etc/pacman.conf

[linux-surface]
Server = https://pkg.surfacelinux.com/arch/
EOF
else
    log_warn "[linux-surface] repository already exists."
fi

# 3. Update and Install
log_info "Syncing repositories and installing Surface kernel..."
pacman -Sy --noconfirm
pacman -S --noconfirm linux-surface linux-surface-headers iptsd

# 4. Enable Touchscreen Daemon
log_info "Enabling iptsd (Touchscreen Daemon)..."
systemctl enable iptsd.service

log_success "Surface kernel and utilities successfully installed!"
