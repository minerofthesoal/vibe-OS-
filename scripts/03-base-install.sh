#!/usr/bin/env bash
# ==============================================================================
# vibeOS - Base System Installation
# Installs base Arch Linux system with hardware-specific packages
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
require_root

log_step "Installing base system..."

# Verify /mnt is mounted
if ! mountpoint -q /mnt; then
    die "/mnt is not mounted. Run 02-partition-disk.sh first."
fi

# Read hardware packages
HW_PKGS=""
if [[ -f /tmp/vibeos_hw_pkgs.txt ]]; then
    HW_PKGS=$(cat /tmp/vibeos_hw_pkgs.txt)
    log_info "Hardware packages: $HW_PKGS"
fi

# ── Base packages ─────────────────────────────────────────────
BASE_PKGS=(
    # Core system
    base base-devel linux linux-firmware linux-headers
    # Boot
    grub efibootmgr os-prober
    # Filesystem
    btrfs-progs dosfstools e2fsprogs ntfs-3g gptfdisk parted
    # Essential tools
    sudo neovim nano git curl wget rsync
    # Networking
    networkmanager dhcpcd openssh
    # System
    man-db man-pages texinfo
    # Compression
    zip unzip p7zip
)

# ── Desktop Environment packages ─────────────────────────────
DE_PKGS=(
    # Wayland / Hyprland
    hyprland xdg-desktop-portal-hyprland xdg-desktop-portal-gtk
    xdg-desktop-portal xorg-xwayland qt5-wayland qt6-wayland
    # Shell components
    waybar rofi-wayland swaync swww hyprlock hypridle wlogout
    cliphist wl-clipboard
    # Display Manager
    sddm qt5-graphicaleffects qt5-quickcontrols2 qt5-svg
    # Audio
    pipewire pipewire-alsa pipewire-pulse pipewire-jack wireplumber
    pavucontrol playerctl
    # Bluetooth
    bluez bluez-utils blueman
    # GTK/Qt theming
    nwg-look qt5ct kvantum kvantum-qt5
    papirus-icon-theme
    # Fonts
    ttf-jetbrains-mono-nerd ttf-font-awesome
    noto-fonts noto-fonts-emoji noto-fonts-cjk inter-font
    # File Manager
    thunar thunar-archive-plugin thunar-volman tumbler
    ffmpegthumbnailer gvfs gvfs-mtp file-roller
    # Terminal
    kitty
    # Browser
    firefox
    # Screenshot & brightness
    grim slurp swappy brightnessctl
    # System utilities
    polkit-kde-agent gnome-keyring fastfetch htop btop
    xdg-utils xdg-user-dirs
    # Network GUI
    network-manager-applet
    # Python for vibeOS apps
    python python-pip python-gobject python-psutil tk
    # GPU base
    mesa vulkan-icd-loader
    # Flatpak
    flatpak
    # Misc
    imagemagick jq pacman-contrib reflector
)

# ── Run pacstrap ──────────────────────────────────────────────
log_info "Running pacstrap (this will take a while)..."

# Update mirror list first for faster downloads
if command -v reflector &>/dev/null; then
    log_info "Optimizing mirror list..."
    reflector --latest 10 --protocol https --sort rate --save /etc/pacman.d/mirrorlist 2>/dev/null || true
fi

# Enable parallel downloads in pacman
sed -i 's/^#ParallelDownloads/ParallelDownloads/' /etc/pacman.conf 2>/dev/null || true

pacstrap -K /mnt "${BASE_PKGS[@]}" "${DE_PKGS[@]}" $HW_PKGS

# ── Generate fstab ────────────────────────────────────────────
log_info "Generating fstab..."
genfstab -U /mnt >> /mnt/etc/fstab

# Verify fstab
log_info "Generated fstab:"
cat /mnt/etc/fstab

log_success "Base system installation complete!"
