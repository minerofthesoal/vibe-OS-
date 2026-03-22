#!/usr/bin/env bash
# ==============================================================================
# ArchForge - Module 1: Base Installation
# Description: Formats disk, mounts, pacstraps base system, and generates fstab.
# ==============================================================================

source "$(dirname "$0")/utils.sh"
require_root

TARGET_DISK=${1:-""}

if [[ -z "$TARGET_DISK" ]]; then
    die "Usage: $0 <target_disk> (e.g., $0 /dev/nvme0n1)"
fi

log_info "Starting Base Installation on $TARGET_DISK..."

# 1. Disk Formatting (UEFI/GPT Layout)
log_info "Wiping and partitioning $TARGET_DISK..."
sgdisk -Z "$TARGET_DISK"
sgdisk -n 1:0:+512M -t 1:ef00 -c 1:"EFI" "$TARGET_DISK"
sgdisk -n 2:0:0     -t 2:8300 -c 2:"ROOT" "$TARGET_DISK"

# Determine partition names (handle NVMe vs SATA naming)
if [[ "$TARGET_DISK" == *"nvme"* ]] || [[ "$TARGET_DISK" == *"loop"* ]]; then
    PART_EFI="${TARGET_DISK}p1"
    PART_ROOT="${TARGET_DISK}p2"
else
    PART_EFI="${TARGET_DISK}1"
    PART_ROOT="${TARGET_DISK}2"
fi

log_info "Formatting partitions..."
mkfs.fat -F32 "$PART_EFI"
mkfs.ext4 -F "$PART_ROOT"

# 2. Mounting
log_info "Mounting partitions to /mnt..."
mount "$PART_ROOT" /mnt
mkdir -p /mnt/boot/efi
mount "$PART_EFI" /mnt/boot/efi

# 3. Pacstrap
log_info "Reading hardware packages..."
HW_PKGS=""
if [[ -f /tmp/archforge_hw_pkgs.txt ]]; then
    HW_PKGS=$(cat /tmp/archforge_hw_pkgs.txt)
fi

BASE_PKGS="base base-devel linux linux-firmware neovim git sudo"

log_info "Running pacstrap..."
pacstrap /mnt $BASE_PKGS $HW_PKGS

# 4. Generate fstab
log_info "Generating fstab..."
genfstab -U /mnt >> /mnt/etc/fstab

log_success "Base installation complete! Ready for chroot configuration."
