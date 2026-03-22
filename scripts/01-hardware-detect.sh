#!/usr/bin/env bash
# ==============================================================================
# vibeOS - Hardware Detection & Auto-Driver Selection
# Detects CPU, GPU, Network, Bluetooth, and VM status
# Outputs: /tmp/vibeos_hw_pkgs.txt (package list for pacstrap)
#          /tmp/vibeos_hw_info.txt (human-readable hardware summary)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

log_step "Starting hardware auto-detection..."

HW_PKGS=""
HW_INFO=""

# ── 1. CPU Microcode ──────────────────────────────────────────
log_info "Detecting CPU..."
CPU_VENDOR=$(grep -m1 "vendor_id" /proc/cpuinfo | awk '{print $3}')
CPU_MODEL=$(grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //')

if [[ "$CPU_VENDOR" == "AuthenticAMD" ]]; then
    log_success "AMD CPU: $CPU_MODEL"
    HW_PKGS="$HW_PKGS amd-ucode"
    HW_INFO="${HW_INFO}CPU: $CPU_MODEL (AMD)\n"
elif [[ "$CPU_VENDOR" == "GenuineIntel" ]]; then
    log_success "Intel CPU: $CPU_MODEL"
    HW_PKGS="$HW_PKGS intel-ucode"
    HW_INFO="${HW_INFO}CPU: $CPU_MODEL (Intel)\n"
else
    log_warn "Unknown CPU vendor: $CPU_VENDOR"
    HW_INFO="${HW_INFO}CPU: $CPU_MODEL (Unknown)\n"
fi

# ── 2. GPU Detection ─────────────────────────────────────────
log_info "Detecting GPU..."
GPU_DETECTED=false

if command -v lspci &>/dev/null; then
    VGA_INFO=$(lspci -nn | grep -iE "vga|3d|display" || true)

    # NVIDIA GPU
    if echo "$VGA_INFO" | grep -iq "nvidia"; then
        GPU_NAME=$(echo "$VGA_INFO" | grep -i nvidia | head -1 | sed 's/.*: //')
        log_success "NVIDIA GPU: $GPU_NAME"
        HW_PKGS="$HW_PKGS nvidia nvidia-utils nvidia-settings egl-wayland lib32-nvidia-utils"
        HW_INFO="${HW_INFO}GPU: $GPU_NAME (NVIDIA proprietary)\n"
        GPU_DETECTED=true

        # Check for newer GPU that supports open kernel modules
        if echo "$VGA_INFO" | grep -iqE "\[10de:(2[0-9a-f]{3}|1[6-9][0-9a-f]{2})\]"; then
            log_info "Modern NVIDIA GPU detected - open kernel modules recommended"
        fi
    fi

    # AMD GPU
    if echo "$VGA_INFO" | grep -iqE "amd|radeon|ati"; then
        GPU_NAME=$(echo "$VGA_INFO" | grep -iE "amd|radeon|ati" | head -1 | sed 's/.*: //')
        log_success "AMD GPU: $GPU_NAME"
        HW_PKGS="$HW_PKGS mesa vulkan-radeon libva-mesa-driver mesa-vdpau lib32-mesa lib32-vulkan-radeon"
        HW_INFO="${HW_INFO}GPU: $GPU_NAME (AMD open-source)\n"
        GPU_DETECTED=true
    fi

    # Intel GPU
    if echo "$VGA_INFO" | grep -iq "intel"; then
        GPU_NAME=$(echo "$VGA_INFO" | grep -i intel | head -1 | sed 's/.*: //')
        log_success "Intel GPU: $GPU_NAME"
        HW_PKGS="$HW_PKGS mesa vulkan-intel intel-media-driver libva-intel-driver lib32-mesa lib32-vulkan-intel"
        HW_INFO="${HW_INFO}GPU: $GPU_NAME (Intel open-source)\n"
        GPU_DETECTED=true
    fi

    # Virtual Machine GPU
    if echo "$VGA_INFO" | grep -iqE "vmware|virtualbox|qxl|virtio|bochs|red hat"; then
        log_info "Virtual Machine GPU detected"
        HW_PKGS="$HW_PKGS mesa"
        HW_INFO="${HW_INFO}GPU: Virtual Machine\n"
        GPU_DETECTED=true
    fi
fi

if [[ "$GPU_DETECTED" == false ]]; then
    log_warn "No specific GPU detected, using generic Mesa drivers"
    HW_PKGS="$HW_PKGS mesa"
    HW_INFO="${HW_INFO}GPU: Generic (Mesa)\n"
fi

# ── 3. VM Detection ──────────────────────────────────────────
log_info "Checking for virtual machine..."
if is_virtual_machine; then
    VM_TYPE=$(systemd-detect-virt 2>/dev/null || echo "unknown")
    log_info "Running in VM: $VM_TYPE"
    HW_INFO="${HW_INFO}VM: $VM_TYPE\n"

    case "$VM_TYPE" in
        qemu|kvm)
            HW_PKGS="$HW_PKGS qemu-guest-agent spice-vdagent"
            ;;
        vmware)
            HW_PKGS="$HW_PKGS open-vm-tools"
            ;;
        oracle|virtualbox)
            HW_PKGS="$HW_PKGS virtualbox-guest-utils"
            ;;
    esac
else
    HW_INFO="${HW_INFO}VM: No (bare metal)\n"
fi

# ── 4. Network / Wireless ────────────────────────────────────
log_info "Detecting network hardware..."
HW_PKGS="$HW_PKGS networkmanager"

if command -v lspci &>/dev/null; then
    if lspci | grep -iqE "network|wireless|wifi|802.11"; then
        log_success "Wireless adapter detected"
        HW_PKGS="$HW_PKGS iwd wireless_tools"
        HW_INFO="${HW_INFO}WiFi: Detected\n"
    else
        HW_INFO="${HW_INFO}WiFi: Not detected\n"
    fi
fi

# Broadcom WiFi (needs special drivers)
if command -v lspci &>/dev/null && lspci | grep -iq "broadcom.*wireless"; then
    log_info "Broadcom WiFi detected - adding b43 firmware"
    HW_PKGS="$HW_PKGS broadcom-wl-dkms"
fi

# ── 5. Bluetooth ─────────────────────────────────────────────
log_info "Detecting Bluetooth..."
if command -v lsusb &>/dev/null && lsusb | grep -iq "bluetooth"; then
    log_success "Bluetooth adapter detected (USB)"
    HW_PKGS="$HW_PKGS bluez bluez-utils"
    HW_INFO="${HW_INFO}Bluetooth: Detected\n"
elif command -v lspci &>/dev/null && lspci | grep -iq "bluetooth"; then
    log_success "Bluetooth adapter detected (PCI)"
    HW_PKGS="$HW_PKGS bluez bluez-utils"
    HW_INFO="${HW_INFO}Bluetooth: Detected\n"
else
    HW_PKGS="$HW_PKGS bluez bluez-utils"  # Include anyway, most systems have it
    HW_INFO="${HW_INFO}Bluetooth: Not detected (drivers included anyway)\n"
fi

# ── 6. Storage Controllers ───────────────────────────────────
log_info "Detecting storage controllers..."
if command -v lspci &>/dev/null && lspci | grep -iq "nvme"; then
    log_success "NVMe storage detected"
    HW_PKGS="$HW_PKGS nvme-cli"
fi

# ── 7. Touchpad / Input ──────────────────────────────────────
if [[ -d /proc/bus/input ]] && grep -riq "touchpad\|trackpad\|synaptics\|alps" /proc/bus/input/ 2>/dev/null; then
    log_success "Touchpad detected"
fi

# ── Output Results ────────────────────────────────────────────
# Clean up and deduplicate packages
HW_PKGS=$(echo "$HW_PKGS" | tr ' ' '\n' | sort -u | tr '\n' ' ' | xargs)

echo "$HW_PKGS" > /tmp/vibeos_hw_pkgs.txt
echo -e "$HW_INFO" > /tmp/vibeos_hw_info.txt

log_success "Hardware detection complete!"
log_info "Packages to install: $HW_PKGS"
echo ""
echo -e "$HW_INFO"
