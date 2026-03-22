#!/usr/bin/env bash
# ==============================================================================
# vibeOS - Disk Partitioning
# Supports UEFI (GPT) and BIOS (MBR) systems
# Creates: EFI partition (512M), Root partition (remaining space)
# Optional: Swap partition
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
require_root

TARGET_DISK="${1:-}"
USE_SWAP="${2:-no}"
SWAP_SIZE="${3:-4G}"

if [[ -z "$TARGET_DISK" ]]; then
    die "Usage: $0 <target_disk> [use_swap: yes/no] [swap_size: 4G]"
fi

if [[ ! -b "$TARGET_DISK" ]]; then
    die "Device $TARGET_DISK does not exist or is not a block device"
fi

log_step "Partitioning $TARGET_DISK..."

# Unmount any existing partitions on the disk
log_info "Unmounting any existing partitions..."
umount -R /mnt 2>/dev/null || true
swapoff -a 2>/dev/null || true
for part in $(lsblk -pno NAME "$TARGET_DISK" | tail -n +2); do
    umount "$part" 2>/dev/null || true
done

if is_uefi; then
    # ── UEFI/GPT Partitioning ──
    log_info "UEFI system detected - creating GPT partition table..."

    sgdisk -Z "$TARGET_DISK"        # Zap existing partition table
    sgdisk -o "$TARGET_DISK"        # Create new GPT

    if [[ "$USE_SWAP" == "yes" ]]; then
        sgdisk -n 1:0:+512M  -t 1:ef00 -c 1:"EFI"  "$TARGET_DISK"
        sgdisk -n 2:0:+${SWAP_SIZE} -t 2:8200 -c 2:"SWAP" "$TARGET_DISK"
        sgdisk -n 3:0:0      -t 3:8300 -c 3:"ROOT" "$TARGET_DISK"

        PART_EFI=$(get_partition "$TARGET_DISK" 1)
        PART_SWAP=$(get_partition "$TARGET_DISK" 2)
        PART_ROOT=$(get_partition "$TARGET_DISK" 3)
    else
        sgdisk -n 1:0:+512M  -t 1:ef00 -c 1:"EFI"  "$TARGET_DISK"
        sgdisk -n 2:0:0      -t 2:8300 -c 2:"ROOT" "$TARGET_DISK"

        PART_EFI=$(get_partition "$TARGET_DISK" 1)
        PART_ROOT=$(get_partition "$TARGET_DISK" 2)
    fi

    # Wait for kernel to re-read partition table
    partprobe "$TARGET_DISK" 2>/dev/null || true
    sleep 2

    # Format partitions
    log_info "Formatting EFI partition ($PART_EFI)..."
    mkfs.fat -F32 "$PART_EFI"

    if [[ "$USE_SWAP" == "yes" ]]; then
        log_info "Creating swap ($PART_SWAP)..."
        mkswap "$PART_SWAP"
        swapon "$PART_SWAP"
    fi

    log_info "Formatting root partition ($PART_ROOT) as ext4..."
    mkfs.ext4 -F -L "vibeOS" "$PART_ROOT"

    # Mount
    log_info "Mounting partitions..."
    mount "$PART_ROOT" /mnt
    mkdir -p /mnt/boot/efi
    mount "$PART_EFI" /mnt/boot/efi

else
    # ── BIOS/MBR Partitioning ──
    log_info "BIOS system detected - creating MBR partition table..."

    # Create MBR partition table with fdisk
    if [[ "$USE_SWAP" == "yes" ]]; then
        # Calculate swap size in MB
        SWAP_MB=$(echo "$SWAP_SIZE" | sed 's/G/*1024/;s/M//' | bc 2>/dev/null || echo "4096")

        (
            echo o      # Create new DOS table
            echo n      # New partition (swap)
            echo p      # Primary
            echo 1      # Partition 1
            echo        # Default start
            echo "+${SWAP_MB}M"
            echo t      # Change type
            echo 82     # Linux swap
            echo n      # New partition (root)
            echo p      # Primary
            echo 2      # Partition 2
            echo        # Default start
            echo        # Default end (rest of disk)
            echo a      # Make bootable
            echo 2      # Partition 2
            echo w      # Write
        ) | fdisk "$TARGET_DISK"

        PART_SWAP=$(get_partition "$TARGET_DISK" 1)
        PART_ROOT=$(get_partition "$TARGET_DISK" 2)

        sleep 2

        mkswap "$PART_SWAP"
        swapon "$PART_SWAP"
    else
        (
            echo o      # Create new DOS table
            echo n      # New partition
            echo p      # Primary
            echo 1      # Partition 1
            echo        # Default start
            echo        # Default end
            echo a      # Make bootable
            echo 1
            echo w      # Write
        ) | fdisk "$TARGET_DISK"

        PART_ROOT=$(get_partition "$TARGET_DISK" 1)
        sleep 2
    fi

    log_info "Formatting root partition ($PART_ROOT) as ext4..."
    mkfs.ext4 -F -L "vibeOS" "$PART_ROOT"

    mount "$PART_ROOT" /mnt
fi

# Save partition info for later scripts
cat > /tmp/vibeos_partitions.txt <<EOF
TARGET_DISK=$TARGET_DISK
PART_ROOT=$PART_ROOT
PART_EFI=${PART_EFI:-}
PART_SWAP=${PART_SWAP:-}
BOOT_MODE=$(is_uefi && echo "uefi" || echo "bios")
EOF

log_success "Disk partitioning complete!"
log_info "Root: $PART_ROOT -> /mnt"
[[ -n "${PART_EFI:-}" ]] && log_info "EFI: $PART_EFI -> /mnt/boot/efi"
[[ -n "${PART_SWAP:-}" ]] && log_info "Swap: $PART_SWAP"
