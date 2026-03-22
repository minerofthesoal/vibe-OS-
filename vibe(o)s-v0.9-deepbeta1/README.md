# vibe(O)s: Custom Wayland Desktop Environment & Installer

## Overview

**vibe(O)s** (formerly ArchForge) is a truly custom Desktop Environment (DE) built from the ground up, accompanied by a multi-file automated installer. It is designed to deliver a heavily customized Wayland compositor that visually blends the sleek, polished aesthetics of macOS with the minimalist, debloated, and high-performance utility of Windows 10 ReviOS.

**Made by Gemini 3.1 Pro (so far)**
**Prompted by ray0ffire/minerofthesoal**

Instead of just configuring an existing window manager, we are building our own Wayland compositor using **Smithay** (Rust) to have absolute control over the rendering pipeline, animations, and window management logic.

This project provides a fully automated, GUI-driven installation experience, complete with hardware auto-detection, optional Surface device support, and a pre-configured, production-ready custom Wayland environment. 

It also includes a custom programming language called **CRust** and its own IDE, **VibeEdit**.

## Features

- **Custom Wayland Compositor**: Built with Rust and Smithay, featuring:
  - Exaggerated, fluid macOS-style spring animations for window movements and resizing.
  - Dynamic layout modes (macOS-style floating, ReviOS-style tiling).
  - Advanced input handling (pointer, keyboard, touch).
  - Display Power Management Signaling (DPMS) for idle detection and display sleep.
- **VibeEdit IDE**: A custom code editor for the CRust language, featuring:
  - Syntax highlighting for CRust (based on C++ transpilation).
  - Find and Replace functionality.
  - Integrated terminal for building and running projects.
- **Automated Installer**: A sleek, dark-mode GUI installer built with Python and CustomTkinter.
- **Hardware Auto-Detection**: Automatically provisions drivers for Nvidia, AMD, Intel, and Surface devices.
- **ISO Builder**: Scripts to generate bootable ISOs for Arch Linux and Ubuntu 25.

## Tech Stack

### Core System
* **OS Base:** Arch Linux / Ubuntu 25
* **Installer GUI:** Python 3 + CustomTkinter
* **Hardware Detection:** `lspci`, `lsusb`, `dmidecode`
* **Init System / Services:** systemd
* **Audio:** PipeWire + WirePlumber + Pavucontrol

### The Custom Desktop Environment (vibe(O)s)
* **Compositor / Window Manager:** Custom Wayland compositor built on **Smithay** (Rust).
* **Shell / UI Components:** Custom-built components for the panel, dock, and application launcher.
* **Display Manager (Login):** SDDM (With a sleek, minimal macOS-inspired theme).

### Pre-installed Applications
* **VibeEdit:** Custom IDE for the CRust language.
* **Terminal:** Kitty (GPU-accelerated, configured with a minimal prompt and blur).
* **File Manager:** Thunar.
* **Browser:** Firefox.

## Directory Tree

```text
.
├── README.md
├── installer/                      # Python GUI Installer
├── scripts/                        # Bash scripts for system operations & ISO building
│   ├── build_iso.sh                # Script to build Arch/Ubuntu ISOs
│   ├── compile_installer.sh        # Compiles the Python installer to a binary
│   └── ...
├── archforge-de/                   # Source code for the custom Desktop Environment
│   ├── compositor/                 # The Smithay-based Wayland compositor (Rust)
│   ├── apps/                       # Custom applications (e.g., VibeEdit)
│   ├── crust/                      # CRust language transpiler
│   └── shell/                      # Custom UI components (Panel, Dock, Launcher)
├── configs/                        # Default dotfiles and DE aesthetics
└── assets/                         # Wallpapers and icons
```

## Building and Running

### Building the Compositor
```bash
cd archforge-de/compositor
cargo build --release
```

### Running VibeEdit
```bash
python3 archforge-de/apps/forge-edit/main.py
```

### Building the ISO
You can build a bootable ISO for either Arch Linux or Ubuntu 25.
```bash
sudo ./scripts/build_iso.sh --os arch
# or
sudo ./scripts/build_iso.sh --os ubuntu
```

### Compiling the Installer
```bash
./scripts/compile_installer.sh
```

## License
MIT License
