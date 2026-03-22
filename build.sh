#!/usr/bin/env bash
# ==============================================================================
# vibeOS - ISO Builder
# Builds a bootable vibeOS ISO using archiso
#
# Usage: sudo ./build.sh [--output /path/to/output]
#
# Requirements:
#   - Arch Linux host system
#   - archiso package installed (sudo pacman -S archiso)
#   - Root privileges
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$SCRIPT_DIR/iso-profile"
WORK_DIR="$SCRIPT_DIR/build/work"
OUT_DIR="$SCRIPT_DIR/build/out"

# Colors
BOLD='\033[1m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}${BOLD}[vibeOS Build]${NC} $1"; }
log_success() { echo -e "${GREEN}${BOLD}[vibeOS Build]${NC} $1"; }
log_error()   { echo -e "${RED}${BOLD}[vibeOS Build]${NC} $1" >&2; }
log_warn()    { echo -e "${YELLOW}${BOLD}[vibeOS Build]${NC} $1"; }

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --output|-o) OUT_DIR="$2"; shift ;;
        --clean|-c) CLEAN=true ;;
        --help|-h)
            echo "Usage: sudo $0 [--output /path] [--clean]"
            echo ""
            echo "Options:"
            echo "  --output, -o    Output directory for ISO (default: ./build/out)"
            echo "  --clean, -c     Clean build directory before building"
            echo "  --help, -h      Show this help"
            exit 0
            ;;
        *) log_error "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Check root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (sudo ./build.sh)"
    exit 1
fi

# Check archiso
if ! command -v mkarchiso &>/dev/null; then
    log_error "archiso is not installed. Run: sudo pacman -S archiso"
    exit 1
fi

echo ""
echo -e "${BLUE}${BOLD}"
echo "  ┌─────────────────────────────────────┐"
echo "  │        vibeOS ISO Builder            │"
echo "  │   Arch Linux × Hyprland Desktop     │"
echo "  └─────────────────────────────────────┘"
echo -e "${NC}"

# Clean if requested
if [[ "${CLEAN:-}" == "true" ]]; then
    log_info "Cleaning previous build..."
    rm -rf "$WORK_DIR"
fi

mkdir -p "$WORK_DIR" "$OUT_DIR"

# ── Prepare archiso profile ──────────────────────────────────
log_info "Preparing archiso profile..."

# Create a working copy of the profile
BUILD_PROFILE="$WORK_DIR/profile"
rm -rf "$BUILD_PROFILE"
mkdir -p "$BUILD_PROFILE"

# Copy base releng profile
cp -r /usr/share/archiso/configs/releng/* "$BUILD_PROFILE/"

# Override with our custom profile
cp "$PROFILE_DIR/profiledef.sh" "$BUILD_PROFILE/"
cp "$PROFILE_DIR/pacman.conf" "$BUILD_PROFILE/"

# Merge package lists (keep releng base + add ours)
cat "$PROFILE_DIR/packages.x86_64" >> "$BUILD_PROFILE/packages.x86_64"
# Remove duplicates
sort -u "$BUILD_PROFILE/packages.x86_64" -o "$BUILD_PROFILE/packages.x86_64"

# ── Inject vibeOS files into airootfs ─────────────────────────
log_info "Injecting vibeOS files into live filesystem..."

AIROOTFS="$BUILD_PROFILE/airootfs"

# Copy our airootfs overlay
cp -rT "$PROFILE_DIR/airootfs" "$AIROOTFS/"

# Copy installer
mkdir -p "$AIROOTFS/opt/vibeos/installer"
cp -r "$SCRIPT_DIR/installer/"* "$AIROOTFS/opt/vibeos/installer/"

# Copy installation scripts
mkdir -p "$AIROOTFS/opt/vibeos/scripts"
cp -r "$SCRIPT_DIR/scripts/"* "$AIROOTFS/opt/vibeos/scripts/"
chmod +x "$AIROOTFS/opt/vibeos/scripts/"*.sh

# Create vibeos-installer launcher
mkdir -p "$AIROOTFS/usr/local/bin"
cat > "$AIROOTFS/usr/local/bin/vibeos-installer" <<'LAUNCHER'
#!/bin/bash
# vibeOS Installer launcher
cd /opt/vibeos/installer
exec python3 main.py "$@"
LAUNCHER
chmod +x "$AIROOTFS/usr/local/bin/vibeos-installer"

# Copy first-boot service
if [[ -f "$PROFILE_DIR/airootfs/etc/systemd/system/vibeos-firstboot.service" ]]; then
    mkdir -p "$AIROOTFS/etc/systemd/system"
    cp "$PROFILE_DIR/airootfs/etc/systemd/system/vibeos-firstboot.service" \
        "$AIROOTFS/etc/systemd/system/"
fi

if [[ -f "$PROFILE_DIR/airootfs/usr/local/bin/vibeos-firstboot" ]]; then
    cp "$PROFILE_DIR/airootfs/usr/local/bin/vibeos-firstboot" \
        "$AIROOTFS/usr/local/bin/"
    chmod +x "$AIROOTFS/usr/local/bin/vibeos-firstboot"
fi

# ── Live environment configuration ───────────────────────────
log_info "Configuring live environment..."

# Auto-login for live environment
mkdir -p "$AIROOTFS/etc/systemd/system/getty@tty1.service.d"
cat > "$AIROOTFS/etc/systemd/system/getty@tty1.service.d/autologin.conf" <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin root --noclear %I \$TERM
EOF

# Enable services in live environment
mkdir -p "$AIROOTFS/etc/systemd/system/multi-user.target.wants"
ln -sf /usr/lib/systemd/system/NetworkManager.service \
    "$AIROOTFS/etc/systemd/system/multi-user.target.wants/NetworkManager.service" 2>/dev/null || true

# Ensure pip packages for installer
mkdir -p "$AIROOTFS/etc/systemd/system/multi-user.target.wants"
cat > "$AIROOTFS/usr/local/bin/vibeos-setup-live" <<'SETUP'
#!/bin/bash
# One-time live environment setup
if [[ ! -f /tmp/.vibeos-live-setup-done ]]; then
    pip install --break-system-packages customtkinter 2>/dev/null || true
    touch /tmp/.vibeos-live-setup-done
fi
SETUP
chmod +x "$AIROOTFS/usr/local/bin/vibeos-setup-live"

# Add setup to profile
cat >> "$AIROOTFS/etc/profile.d/vibeos-live.sh" <<'EOF'

# Run one-time setup
vibeos-setup-live 2>/dev/null &
EOF

# ── Locale configuration ─────────────────────────────────────
echo "en_US.UTF-8 UTF-8" > "$AIROOTFS/etc/locale.gen"
echo "LANG=en_US.UTF-8" > "$AIROOTFS/etc/locale.conf"

# ── Shadow/passwd for live user ──────────────────────────────
# Root with no password for live environment
cat > "$AIROOTFS/etc/shadow" <<EOF
root::14871::::::
EOF

cat > "$AIROOTFS/etc/passwd" <<EOF
root:x:0:0:root:/root:/bin/bash
EOF

cat > "$AIROOTFS/etc/group" <<EOF
root:x:0:root
wheel:x:10:root
video:x:44:root
audio:x:92:root
input:x:97:root
EOF

# ── Build the ISO ─────────────────────────────────────────────
log_info "Building vibeOS ISO (this will take a while)..."
echo ""

mkarchiso -v -w "$WORK_DIR/archiso-work" -o "$OUT_DIR" "$BUILD_PROFILE"

echo ""
log_success "═══════════════════════════════════════════════"
log_success "  vibeOS ISO built successfully!"
log_success "  Output: $OUT_DIR/"
log_success ""
log_success "  To test in QEMU:"
log_success "  qemu-system-x86_64 -cdrom $OUT_DIR/vibeos-*.iso \\"
log_success "    -m 4G -enable-kvm -bios /usr/share/ovmf/OVMF.fd"
log_success ""
log_success "  To write to USB:"
log_success "  sudo dd if=$OUT_DIR/vibeos-*.iso of=/dev/sdX bs=4M status=progress"
log_success "═══════════════════════════════════════════════"
