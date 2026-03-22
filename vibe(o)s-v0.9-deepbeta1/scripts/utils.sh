#!/usr/bin/env bash
# ==============================================================================
# ArchForge - Shared Utilities
# Description: Provides colorful logging, error handling, and shared functions.
# ==============================================================================

# Strict mode
set -euo pipefail

# ANSI Colors
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging Functions
log_info() {
    echo -e "${BLUE}${BOLD}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}${BOLD}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}${BOLD}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}${BOLD}[ERROR]${NC} $1" >&2
}

die() {
    log_error "$1"
    exit 1
}

# Error trap
trap_err() {
    local line=$1
    local msg=$2
    log_error "Script failed at line $line: $msg"
}
trap 'trap_err ${LINENO} "$BASH_COMMAND"' ERR

# Check if running as root
require_root() {
    if [[ $EUID -ne 0 ]]; then
        die "This script must be run as root."
    fi
}
