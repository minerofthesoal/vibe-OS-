#!/usr/bin/env bash
# ==============================================================================
# vibeOS - Desktop Environment Installation
# Run INSIDE chroot: Copies configs, themes, and vibeOS-specific files
# ==============================================================================

set -euo pipefail

log_info()    { echo -e "\033[0;34m\033[1m[vibeOS]\033[0m $1"; }
log_success() { echo -e "\033[0;32m\033[1m[vibeOS]\033[0m $1"; }
log_step()    { echo -e "\033[0;35m\033[1m[STEP]\033[0m $1"; }

USERNAME="${1:-vibeos}"
VIBEOS_SRC="${2:-/opt/vibeos}"

log_step "Installing vibeOS Desktop Environment..."

USER_HOME="/home/$USERNAME"

# ── 1. Copy configuration files ──────────────────────────────
log_info "Deploying vibeOS configuration files..."

# Ensure .config directories exist
CONFIG_DIRS=(
    hypr waybar rofi kitty swaync gtk-3.0 gtk-4.0 qt5ct
    Kvantum fastfetch
)
for dir in "${CONFIG_DIRS[@]}"; do
    mkdir -p "$USER_HOME/.config/$dir"
done

# Copy from /etc/skel (populated during ISO build or from source)
if [[ -d /etc/skel/.config ]]; then
    cp -rT /etc/skel/.config "$USER_HOME/.config/"
fi

if [[ -f /etc/skel/.gtkrc-2.0 ]]; then
    cp /etc/skel/.gtkrc-2.0 "$USER_HOME/.gtkrc-2.0"
fi

# ── 2. SDDM Theme ────────────────────────────────────────────
log_info "Configuring SDDM login theme..."
mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/vibeos.conf <<EOF
[Theme]
Current=vibeos

[General]
InputMethod=
Numlock=on

[Users]
MaximumUid=60513
MinimumUid=1000
EOF

# ── 3. Wallpaper ─────────────────────────────────────────────
log_info "Setting up wallpaper..."
mkdir -p /usr/share/vibeos/wallpapers

# Generate a default gradient wallpaper if none exists
if [[ ! -f /usr/share/vibeos/wallpapers/default.png ]]; then
    if command -v magick &>/dev/null; then
        magick -size 3840x2160 \
            gradient:'#0d1117'-'#1a1b2e' \
            -sigmoidal-contrast 5,50% \
            -fill 'rgba(137,180,250,0.08)' -draw "circle 2800,600 2800,1200" \
            -fill 'rgba(203,166,247,0.06)' -draw "circle 800,1800 800,2600" \
            -blur 0x30 \
            /usr/share/vibeos/wallpapers/default.png
    elif command -v convert &>/dev/null; then
        convert -size 3840x2160 \
            gradient:'#0d1117'-'#1a1b2e' \
            -blur 0x20 \
            /usr/share/vibeos/wallpapers/default.png
    else
        log_info "ImageMagick not available, creating minimal placeholder..."
        # Create a tiny PPM and let swww handle it
        python3 -c "
import struct, zlib
def create_png(w, h, r, g, b, path):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    raw = b''
    for y in range(h):
        raw += b'\x00' + bytes([r, g, b]) * w
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(raw)) +
            chunk(b'IEND', b''))
with open('$( echo /usr/share/vibeos/wallpapers/default.png )', 'wb') as f:
    f.write(create_png(64, 36, 13, 17, 23))
" 2>/dev/null || true
    fi
fi

# ── 4. Wayland session entry ─────────────────────────────────
log_info "Creating wayland session entry..."
mkdir -p /usr/share/wayland-sessions
cat > /usr/share/wayland-sessions/vibeos.desktop <<EOF
[Desktop Entry]
Name=vibeOS
Comment=vibeOS Desktop Environment (Hyprland)
Exec=Hyprland
Type=Application
DesktopNames=Hyprland
EOF

# ── 5. Application desktop entries ───────────────────────────
log_info "Creating application menu entries..."
mkdir -p /usr/share/applications

cat > /usr/share/applications/vibeos-installer.desktop <<EOF
[Desktop Entry]
Name=vibeOS Installer
Comment=Install vibeOS to your system
Exec=pkexec python3 /opt/vibeos/installer/main.py
Icon=system-software-install
Terminal=false
Type=Application
Categories=System;
StartupWMClass=vibeOS-installer
EOF

# ── 6. Fix permissions ───────────────────────────────────────
log_info "Setting file permissions..."
chown -R "$USERNAME:$USERNAME" "$USER_HOME"

# ── 7. Shell configuration ───────────────────────────────────
log_info "Configuring shell environment..."
cat >> "$USER_HOME/.bashrc" <<'EOF'

# vibeOS environment
export QT_QPA_PLATFORMTHEME=qt5ct
export QT_QPA_PLATFORM=wayland
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
export MOZ_ENABLE_WAYLAND=1
export GDK_BACKEND=wayland,x11
export XCURSOR_THEME=Bibata-Modern-Classic
export XCURSOR_SIZE=24
export EDITOR=nvim

# Fastfetch on new terminal
if command -v fastfetch &>/dev/null && [[ -z "$VIBEOS_GREETED" ]]; then
    fastfetch
    export VIBEOS_GREETED=1
fi

alias ls='ls --color=auto'
alias ll='ls -lah'
alias grep='grep --color=auto'
alias vim='nvim'
EOF

chown "$USERNAME:$USERNAME" "$USER_HOME/.bashrc"

log_success "vibeOS Desktop Environment installed!"
