#!/usr/bin/env bash
# ==============================================================================
# vibeOS - Finalization
# Final cleanup and system optimization
# Run INSIDE chroot as last step
# ==============================================================================

set -euo pipefail

log_info()    { echo -e "\033[0;34m\033[1m[vibeOS]\033[0m $1"; }
log_success() { echo -e "\033[0;32m\033[1m[vibeOS]\033[0m $1"; }
log_step()    { echo -e "\033[0;35m\033[1m[STEP]\033[0m $1"; }

log_step "Finalizing vibeOS installation..."

# ── 1. Regenerate initramfs ───────────────────────────────────
log_info "Regenerating initramfs..."
mkinitcpio -P

# ── 2. Update GRUB config ────────────────────────────────────
log_info "Updating GRUB configuration..."
grub-mkconfig -o /boot/grub/grub.cfg

# ── 3. Set os-release ────────────────────────────────────────
log_info "Setting vibeOS identity..."
cat > /etc/vibeos-release <<EOF
NAME="vibeOS"
VERSION="1.0"
ID=vibeos
ID_LIKE=arch
PRETTY_NAME="vibeOS 1.0"
HOME_URL="https://github.com/minerofthesoal/vibe-OS-"
EOF

# ── 4. Create vibeOS system info script ──────────────────────
cat > /usr/local/bin/vibeos-info <<'EOF'
#!/bin/bash
echo ""
echo "  ┌─────────────────────────────────┐"
echo "  │         vibeOS v1.0             │"
echo "  │   Arch Linux × Hyprland DE     │"
echo "  │                                 │"
echo "  │   WM:    Hyprland              │"
echo "  │   Bar:   Waybar                │"
echo "  │   Shell: Rofi + swaync         │"
echo "  │   Login: SDDM                  │"
echo "  │   Audio: PipeWire              │"
echo "  │   Theme: Catppuccin Mocha      │"
echo "  └─────────────────────────────────┘"
echo ""
EOF
chmod +x /usr/local/bin/vibeos-info

# ── 5. Optimize pacman database ──────────────────────────────
log_info "Optimizing package database..."
pacman-db-upgrade 2>/dev/null || true

# ── 6. Clean package cache ───────────────────────────────────
log_info "Cleaning package cache..."
pacman -Scc --noconfirm 2>/dev/null || true

# ── 7. Enable periodic TRIM for SSDs ─────────────────────────
systemctl enable fstrim.timer 2>/dev/null || true

# ── 8. Set default target ────────────────────────────────────
systemctl set-default graphical.target

log_success "═══════════════════════════════════════"
log_success "  vibeOS installation complete!"
log_success "  You may now reboot into your new OS."
log_success "═══════════════════════════════════════"
