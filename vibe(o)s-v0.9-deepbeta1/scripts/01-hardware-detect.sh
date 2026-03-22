#!/usr/bin/env bash
# ==============================================================================
# ArchForge - Module 1: Hardware Detection
# Description: Scans CPU, GPU, and Network to determine required drivers.
# Outputs: /tmp/archforge_hw_pkgs.txt (List of packages for pacstrap)
# ==============================================================================

source "$(dirname "$0")/utils.sh"

log_info "Starting Hardware Auto-Detection..."

HW_PKGS=""

# 1. CPU Microcode Detection
log_info "Detecting CPU architecture..."
if grep -q "AuthenticAMD" /proc/cpuinfo; then
    log_success "AMD CPU detected. Adding amd-ucode."
    HW_PKGS="$HW_PKGS amd-ucode"
elif grep -q "GenuineIntel" /proc/cpuinfo; then
    log_success "Intel CPU detected. Adding intel-ucode."
    HW_PKGS="$HW_PKGS intel-ucode"
else
    log_warn "Unknown CPU vendor. Skipping microcode."
fi

# 2. GPU Detection
log_info "Detecting Graphics Hardware..."
if command -v lspci &> /dev/null; then
    VGA_INFO=$(lspci | grep -i vga || true)
    
    if echo "$VGA_INFO" | grep -iq "nvidia"; then
        log_success "NVIDIA GPU detected. Adding proprietary drivers."
        HW_PKGS="$HW_PKGS nvidia nvidia-utils egl-wayland"
    fi
    
    if echo "$VGA_INFO" | grep -iq "amd" || echo "$VGA_INFO" | grep -iq "radeon"; then
        log_success "AMD GPU detected. Adding open-source drivers."
        HW_PKGS="$HW_PKGS xf86-video-amdgpu vulkan-radeon mesa"
    fi
    
    if echo "$VGA_INFO" | grep -iq "intel"; then
        log_success "Intel GPU detected. Adding open-source drivers."
        HW_PKGS="$HW_PKGS xf86-video-intel vulkan-intel mesa"
    fi
    
    if echo "$VGA_INFO" | grep -iq "vmware" || echo "$VGA_INFO" | grep -iq "virtualbox" || echo "$VGA_INFO" | grep -iq "qxl"; then
        log_warn "Virtual Machine GPU detected. Adding guest utilities."
        HW_PKGS="$HW_PKGS xf86-video-vmware qemu-guest-agent virtualbox-guest-utils-nox"
    fi
else
    log_warn "'lspci' not found. Cannot accurately detect GPU."
fi

# 3. Network / Bluetooth Detection
log_info "Detecting Network Interfaces..."
HW_PKGS="$HW_PKGS networkmanager bluez bluez-utils"
if lspci | grep -iq "network" || lsusb | grep -iq "wireless"; then
    log_success "Wireless interface detected. Adding wpa_supplicant and wireless_tools."
    HW_PKGS="$HW_PKGS wpa_supplicant wireless_tools iwd"
fi

# Clean up formatting and save to file
HW_PKGS=$(echo "$HW_PKGS" | xargs) # Trim whitespace
echo "$HW_PKGS" > /tmp/archforge_hw_pkgs.txt

log_success "Hardware detection complete!"
log_info "Packages to be installed: $HW_PKGS"
