#!/usr/bin/env bash
# ==============================================================================
# vibeOS - Chroot Configuration
# Run INSIDE chroot: arch-chroot /mnt bash /opt/vibeos/scripts/04-chroot-configure.sh
# Configures locale, timezone, users, bootloader, services
# ==============================================================================

set -euo pipefail

# Simple logging (utils.sh may not be available in chroot)
log_info()    { echo -e "\033[0;34m\033[1m[vibeOS]\033[0m $1"; }
log_success() { echo -e "\033[0;32m\033[1m[vibeOS]\033[0m $1"; }
log_warn()    { echo -e "\033[1;33m\033[1m[vibeOS]\033[0m $1"; }
log_error()   { echo -e "\033[0;31m\033[1m[vibeOS]\033[0m $1" >&2; }
log_step()    { echo -e "\033[0;35m\033[1m[STEP]\033[0m $1"; }

USERNAME="${1:-vibeos}"
PASSWORD="${2:-vibeos}"
HOSTNAME="${3:-vibeos-pc}"
TIMEZONE="${4:-UTC}"

log_step "Configuring system inside chroot..."

# ── 1. Timezone ───────────────────────────────────────────────
log_info "Setting timezone to $TIMEZONE..."
ln -sf "/usr/share/zoneinfo/$TIMEZONE" /etc/localtime
hwclock --systohc

# ── 2. Locale ─────────────────────────────────────────────────
log_info "Configuring locale..."
sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf
echo "KEYMAP=us" > /etc/vconsole.conf

# ── 3. Hostname ───────────────────────────────────────────────
log_info "Setting hostname to $HOSTNAME..."
echo "$HOSTNAME" > /etc/hostname
cat > /etc/hosts <<EOF
127.0.0.1   localhost
::1         localhost
127.0.1.1   $HOSTNAME.localdomain $HOSTNAME
EOF

# ── 4. User Creation ─────────────────────────────────────────
log_info "Creating user: $USERNAME..."
useradd -m -G wheel,video,audio,storage,optical,input,power,network -s /bin/bash "$USERNAME"
echo "$USERNAME:$PASSWORD" | chpasswd
echo "root:$PASSWORD" | chpasswd

# Enable sudo for wheel group
sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

# ── 5. Bootloader ────────────────────────────────────────────
log_info "Installing bootloader..."

if [[ -d /sys/firmware/efi ]]; then
    # UEFI - Install GRUB to EFI
    log_info "Installing GRUB for UEFI..."
    grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=vibeOS --recheck

    # NVIDIA kernel params if needed
    if pacman -Q nvidia &>/dev/null; then
        log_info "Adding NVIDIA kernel parameters..."
        sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="[^"]*/& nvidia-drm.modeset=1/' /etc/default/grub
    fi
else
    # BIOS - Install GRUB to MBR
    log_info "Installing GRUB for BIOS..."
    # Read the target disk from partition info
    if [[ -f /tmp/vibeos_partitions.txt ]]; then
        source /tmp/vibeos_partitions.txt
        grub-install --target=i386-pc "$TARGET_DISK" --recheck
    else
        log_warn "Cannot determine target disk for GRUB. Attempting /dev/sda..."
        grub-install --target=i386-pc /dev/sda --recheck
    fi
fi

# Configure GRUB
sed -i 's/GRUB_TIMEOUT=5/GRUB_TIMEOUT=3/' /etc/default/grub
sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="[^"]*/& quiet splash/' /etc/default/grub
# Remove duplicate quiet/splash
sed -i 's/quiet splash quiet splash/quiet splash/' /etc/default/grub
grub-mkconfig -o /boot/grub/grub.cfg

# ── 6. Enable Services ───────────────────────────────────────
log_info "Enabling system services..."
systemctl enable NetworkManager
systemctl enable bluetooth
systemctl enable sddm
systemctl enable fstrim.timer

# PipeWire is user-level, enabled by default via socket activation

# ── 7. NVIDIA DRM modesetting (if NVIDIA installed) ──────────
if pacman -Q nvidia &>/dev/null; then
    log_info "Configuring NVIDIA for Wayland..."
    # Add nvidia modules to initramfs
    sed -i 's/^MODULES=()/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)/' /etc/mkinitcpio.conf
    mkinitcpio -P

    # Create modprobe config
    mkdir -p /etc/modprobe.d
    echo "options nvidia_drm modeset=1 fbdev=1" > /etc/modprobe.d/nvidia.conf
fi

# ── 8. Pacman Configuration ──────────────────────────────────
log_info "Configuring pacman..."
sed -i 's/^#Color/Color/' /etc/pacman.conf
sed -i 's/^#ParallelDownloads/ParallelDownloads/' /etc/pacman.conf
sed -i '/^#\[multilib\]/,/^#Include/ s/^#//' /etc/pacman.conf

# ── 9. Flatpak ───────────────────────────────────────────────
log_info "Setting up Flatpak..."
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true

# ── 10. XDG User Directories ─────────────────────────────────
log_info "Creating XDG user directories..."
su - "$USERNAME" -c "xdg-user-dirs-update" 2>/dev/null || true

log_success "Chroot configuration complete!"
