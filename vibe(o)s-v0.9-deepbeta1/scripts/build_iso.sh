#!/usr/bin/env bash
# ==============================================================================
# ArchForge - ISO Builder Script
# Description: Compiles the ArchForge DE and Installer into a bootable .iso
# Supports: Arch Linux (--os arch) and Ubuntu 25 (--os ubuntu)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/utils.sh"

OS_TARGET="arch"
BUILD_DIR="$PROJECT_ROOT/build/iso-work"
OUT_DIR="$PROJECT_ROOT/build/iso-out"

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --os) OS_TARGET="$2"; shift ;;
        *) die "Unknown parameter passed: $1" ;;
    esac
    shift
done

log_info "Starting ISO Compilation for OS: ${OS_TARGET^^}"

require_root

mkdir -p "$BUILD_DIR" "$OUT_DIR"

build_arch_iso() {
    log_info "Preparing Arch Linux archiso environment..."
    
    if ! command -v mkarchiso &> /dev/null; then
        die "mkarchiso is required. Run: sudo pacman -S archiso"
    fi

    local PROFILE_DIR="$BUILD_DIR/archiso-profile"
    rm -rf "$PROFILE_DIR"
    cp -r /usr/share/archiso/configs/releng/ "$PROFILE_DIR"

    log_info "Injecting ArchForge Installer into the Live Environment..."
    local AIROOTFS="$PROFILE_DIR/airootfs"
    mkdir -p "$AIROOTFS/opt/archforge"
    
    # Copy project files into the ISO root filesystem
    cp -r "$PROJECT_ROOT/"* "$AIROOTFS/opt/archforge/" 2>/dev/null || true

    # Add required packages to the ISO
    log_info "Adding dependencies to packages.x86_64..."
    cat <<EOF >> "$PROFILE_DIR/packages.x86_64"
python
python-pip
tk
git
wayland
xorg-xwayland
hyprland
rofi-wayland
kitty
EOF

    # Create an autostart script for the Live ISO to launch the GUI installer
    mkdir -p "$AIROOTFS/etc/profile.d/"
    cat <<'EOF' > "$AIROOTFS/etc/profile.d/archforge-autorun.sh"
#!/bin/bash
if [[ "$(tty)" == "/dev/tty1" ]]; then
    echo "Welcome to ArchForge Live!"
    echo "Starting the GUI Installer..."
    cd /opt/archforge
    # Launch the compiled binary if it exists, otherwise run python script
    if [ -f "dist/archforge-installer/archforge-installer" ]; then
        exec Hyprland -c /opt/archforge/configs/archforge/live-installer.conf
    fi
fi
EOF
    chmod +x "$AIROOTFS/etc/profile.d/archforge-autorun.sh"

    log_info "Building the Arch Linux ISO (This will take a while)..."
    mkarchiso -v -w "$BUILD_DIR/work" -o "$OUT_DIR" "$PROFILE_DIR"
    
    log_success "Arch Linux ISO successfully built in $OUT_DIR!"
}

build_ubuntu_iso() {
    log_info "Preparing Ubuntu 25 (Plucky Puffin) live-build environment..."
    
    if ! command -v lb &> /dev/null; then
        die "live-build is required. Run: sudo apt install live-build"
    fi

    local LB_DIR="$BUILD_DIR/ubuntu-live"
    rm -rf "$LB_DIR"
    mkdir -p "$LB_DIR"
    cd "$LB_DIR"

    log_info "Configuring live-build for Ubuntu 25..."
    lb config \
        --distribution plucky \
        --architecture amd64 \
        --archive-areas "main restricted universe multiverse" \
        --iso-application "ArchForge Ubuntu Edition" \
        --iso-publisher "ArchForge" \
        --iso-volume "ARCHFORGE_UBUNTU"

    log_info "Injecting ArchForge Installer..."
    mkdir -p config/includes.chroot/opt/archforge
    cp -r "$PROJECT_ROOT/"* config/includes.chroot/opt/archforge/ 2>/dev/null || true

    log_info "Adding dependencies..."
    mkdir -p config/package-lists
    echo "python3 python3-pip python3-tk git wayland-protocols hyprland rofi kitty" > config/package-lists/archforge.list.chroot

    log_info "Building the Ubuntu 25 ISO (This will take a while)..."
    lb build

    cp live-image-amd64.hybrid.iso "$OUT_DIR/archforge-ubuntu25.iso"
    log_success "Ubuntu 25 ISO successfully built in $OUT_DIR!"
}

if [[ "$OS_TARGET" == "arch" ]]; then
    build_arch_iso
elif [[ "$OS_TARGET" == "ubuntu" ]]; then
    build_ubuntu_iso
else
    die "Unsupported OS target: $OS_TARGET. Use 'arch' or 'ubuntu'."
fi
