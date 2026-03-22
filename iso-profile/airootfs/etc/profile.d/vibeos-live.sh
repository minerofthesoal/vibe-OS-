#!/bin/bash
# vibeOS Live Environment - Auto-start installer on TTY1

if [[ "$(tty)" == "/dev/tty1" ]] && [[ -z "$DISPLAY" ]] && [[ -z "$WAYLAND_DISPLAY" ]]; then
    # Check if we're in live environment
    if [[ -f /opt/vibeos/installer/main.py ]]; then
        echo ""
        echo "  ┌─────────────────────────────────────────┐"
        echo "  │     Welcome to vibeOS Live Environment   │"
        echo "  │                                          │"
        echo "  │  Starting Hyprland desktop...            │"
        echo "  │  The installer will launch automatically │"
        echo "  └─────────────────────────────────────────┘"
        echo ""
        sleep 2
        exec Hyprland
    fi
fi
