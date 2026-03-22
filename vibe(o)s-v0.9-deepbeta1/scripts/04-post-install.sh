#!/usr/bin/env bash
# ==============================================================================
# ArchForge - Module 1: Post Installation
# Description: Configures locale, timezone, users, bootloader, and services.
# Note: This script should be run INSIDE the chroot (/mnt).
# ==============================================================================

source "$(dirname "$0")/utils.sh"
require_root

USERNAME=${1:-"archforge"}
PASSWORD=${2:-"password"}
HOSTNAME=${3:-"archforge-pc"}

log_info "Starting Post-Installation Configuration..."

# 1. Timezone and Locale
log_info "Setting timezone and locale..."
ln -sf /usr/share/zoneinfo/UTC /etc/localtime
hwclock --systohc
sed -i 's/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf
echo "$HOSTNAME" > /etc/hostname

# 2. User Creation
log_info "Creating user: $USERNAME..."
useradd -m -G wheel,video,audio,storage,optical -s /bin/bash "$USERNAME"
echo "$USERNAME:$PASSWORD" | chpasswd
echo "root:$PASSWORD" | chpasswd

# Enable sudo for wheel group
sed -i 's/# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

# 3. Bootloader (systemd-boot)
log_info "Installing systemd-boot..."
bootctl install

cat <<EOF > /boot/efi/loader/loader.conf
default arch.conf
timeout 3
console-mode max
editor no
EOF

# Get root partition UUID
ROOT_UUID=$(blkid -s UUID -o value $(findmnt -n -o SOURCE /))

cat <<EOF > /boot/efi/loader/entries/arch.conf
title   ArchForge Linux
linux   /vmlinuz-linux
initrd  /initramfs-linux.img
options root=UUID=$ROOT_UUID rw quiet splash
EOF

# 4. Enable Services
log_info "Enabling essential system services..."
systemctl enable NetworkManager
systemctl enable bluetooth || log_warn "Bluetooth service not found. Skipping."

# 5. The "Support Everything" Goal (Flatpak, Portals, Audio, System Tools)
log_info "Installing widespread compatibility packages..."
pacman -S --noconfirm flatpak xdg-desktop-portal xdg-desktop-portal-wlr pipewire pipewire-pulse pipewire-alsa wireplumber pavucontrol brightnessctl grim slurp wl-clipboard python-pip

# 5.5 Auto-Detect and Install GPU Drivers
log_info "Detecting GPU architecture for driver installation..."
if lspci | grep -E -i "vga|3d" | grep -i "nvidia" > /dev/null; then
    log_info "NVIDIA GPU detected. Installing proprietary drivers..."
    pacman -S --noconfirm nvidia nvidia-utils egl-wayland
    # Enable DRM modesetting for Wayland
    sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="nvidia-drm.modeset=1 /' /etc/default/grub
    grub-mkconfig -o /boot/grub/grub.cfg
elif lspci | grep -E -i "vga|3d" | grep -i "amd" > /dev/null; then
    log_info "AMD GPU detected. Installing open-source RADV drivers..."
    pacman -S --noconfirm mesa vulkan-radeon xf86-video-amdgpu
elif lspci | grep -E -i "vga|3d" | grep -i "intel" > /dev/null; then
    log_info "Intel GPU detected. Installing open-source drivers..."
    pacman -S --noconfirm mesa vulkan-intel xf86-video-intel
else
    log_info "No specific GPU detected, falling back to Mesa..."
    pacman -S --noconfirm mesa
fi

# 6. Install Compositor Build Dependencies & Compile
log_info "Installing wlroots compositor build dependencies..."
pacman -S --noconfirm wlroots wayland wayland-protocols xorg-xwayland gcc make pkgconf
log_info "Compiling ArchForge Compositor..."
cd /opt/archforge/archforge-de/compositor
make
make install
cd /opt/archforge

# 7. Install Python AI & UI Dependencies globally
log_info "Installing Python dependencies for ArchForge AI and UI..."
pip install --break-system-packages huggingface_hub llama-cpp-python customtkinter pygobject

# 8. Setup Flathub for App Store
log_info "Adding Flathub repository..."
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

log_success "Post-installation complete! The system is ready for the ArchForge DE."
