#!/usr/bin/env bash
# ==============================================================================
# vibeOS - Shared Utilities
# Provides logging, error handling, and common functions
# ==============================================================================

set -euo pipefail

# ANSI Colors
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}${BOLD}[vibeOS]${NC} $1"; }
log_success() { echo -e "${GREEN}${BOLD}[vibeOS]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}${BOLD}[vibeOS]${NC} $1"; }
log_error()   { echo -e "${RED}${BOLD}[vibeOS]${NC} $1" >&2; }
log_step()    { echo -e "${MAGENTA}${BOLD}[STEP]${NC} $1"; }

die() {
    log_error "$1"
    exit 1
}

# Error trap with line info
trap 'log_error "Script failed at line $LINENO: $BASH_COMMAND"' ERR

require_root() {
    if [[ $EUID -ne 0 ]]; then
        die "This script must be run as root (use sudo or pkexec)."
    fi
}

# Detect partition naming scheme (NVMe uses p1, p2; SATA uses 1, 2)
get_partition() {
    local disk="$1"
    local num="$2"
    if [[ "$disk" == *"nvme"* ]] || [[ "$disk" == *"loop"* ]] || [[ "$disk" == *"mmcblk"* ]]; then
        echo "${disk}p${num}"
    else
        echo "${disk}${num}"
    fi
}

# Check if running in a VM
is_virtual_machine() {
    if systemd-detect-virt -q 2>/dev/null; then
        return 0
    fi
    if grep -qE "hypervisor|VMware|VirtualBox|KVM|QEMU|Xen" /proc/cpuinfo 2>/dev/null; then
        return 0
    fi
    return 1
}

# Check UEFI or BIOS
is_uefi() {
    [[ -d /sys/firmware/efi ]]
}

# Get available disks (for installer)
list_disks() {
    lsblk -dpno NAME,SIZE,MODEL | grep -E "^/dev/(sd|nvme|vd|mmcblk)" | sort
}

# Progress indicator
progress() {
    local current="$1"
    local total="$2"
    local label="${3:-}"
    local pct=$((current * 100 / total))
    local filled=$((pct / 2))
    local empty=$((50 - filled))
    printf "\r${CYAN}[%-${filled}s%-${empty}s]${NC} %3d%% %s" \
        "$(printf '#%.0s' $(seq 1 $filled 2>/dev/null) 2>/dev/null)" \
        "" "$pct" "$label"
    if [[ $current -eq $total ]]; then echo; fi
}
