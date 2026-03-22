# vibeOS

**A custom Arch Linux-based operating system with a Hyprland Wayland desktop, styled as a hybrid of macOS Ventura, Windows 11, KDE Plasma, and Hyprland.**

Bootable as a live ISO for both emulators (QEMU/VirtualBox) and bare-metal hardware with automatic driver detection and installation.

---

## Features

- **Hyprland compositor** with macOS Ventura-style fluid animations, blur, and rounded corners
- **Waybar panel** — macOS top bar + KDE/Win11 system tray hybrid with glassmorphism
- **Rofi launcher** — Spotlight-style centered search with dark translucent theme
- **SDDM login** — Custom macOS-inspired login screen with blur and accent colors
- **Catppuccin Mocha** color scheme throughout (GTK, Qt, terminal, notifications)
- **Auto hardware detection** — CPU, GPU (NVIDIA/AMD/Intel/VM), network, Bluetooth
- **Auto driver installation** — Proprietary NVIDIA, Mesa/RADV for AMD, Intel media drivers
- **UEFI + BIOS boot** — Works on modern and legacy systems
- **GUI installer** — Dark-themed multi-step installer with disk partitioning
- **PipeWire audio** — Full audio stack with PulseAudio/JACK compatibility
- **Flatpak ready** — Flathub configured out of the box
- **Hyprlock** — macOS-style lock screen with blur and clock
- **Hypridle** — Automatic screen dimming, locking, DPMS, and suspend
- **swaync** — Notification center with quick-settings toggles
- **Kitty terminal** — GPU-accelerated with Catppuccin theme

## Screenshots

*(Build the ISO and boot it to see the desktop!)*

## Architecture

```
vibeOS
├── build.sh                    # Main ISO builder (requires archiso)
├── Makefile                    # Build/test targets
├── iso-profile/                # archiso profile
│   ├── profiledef.sh           # archiso profile definition
│   ├── packages.x86_64         # Package list (200+ packages)
│   ├── pacman.conf             # Pacman config with multilib
│   ├── grub/grub.cfg           # GRUB boot menu
│   ├── efiboot/                # UEFI boot config
│   ├── syslinux/               # BIOS boot config
│   └── airootfs/               # Live filesystem overlay
│       ├── etc/
│       │   ├── skel/.config/   # Default user configs
│       │   │   ├── hypr/       # Hyprland, hyprlock, hypridle
│       │   │   ├── waybar/     # Panel config + CSS
│       │   │   ├── rofi/       # Launcher + power menu
│       │   │   ├── kitty/      # Terminal config
│       │   │   ├── swaync/     # Notification center
│       │   │   ├── gtk-3.0/    # GTK3 dark theme
│       │   │   ├── gtk-4.0/    # GTK4 dark theme
│       │   │   └── qt5ct/      # Qt5 theme (Kvantum)
│       │   ├── sddm.conf.d/   # Login manager config
│       │   └── profile.d/      # Live environment auto-start
│       └── usr/share/
│           ├── sddm/themes/vibeos/  # Custom SDDM QML theme
│           └── vibeos/wallpapers/   # Default wallpaper
├── installer/                  # GUI installer (Python/CustomTkinter)
│   ├── main.py                 # Entry point
│   ├── ui/
│   │   ├── app_window.py       # Window manager
│   │   └── pages.py            # 7-page installation wizard
│   └── core/
│       └── installer_backend.py # Script execution engine
└── scripts/                    # Installation scripts (Bash)
    ├── utils.sh                # Logging, helpers, partition detection
    ├── 01-hardware-detect.sh   # CPU/GPU/Network/BT/VM detection
    ├── 02-partition-disk.sh    # UEFI/BIOS partitioning
    ├── 03-base-install.sh      # pacstrap with 100+ packages
    ├── 04-chroot-configure.sh  # Locale, users, bootloader, services
    ├── 05-install-de.sh        # DE config deployment, wallpaper, SDDM
    └── 06-finalize.sh          # initramfs, GRUB, cleanup
```

## Building the ISO

### Requirements

- Arch Linux host system
- `archiso` package: `sudo pacman -S archiso`
- Root privileges
- ~15GB free disk space
- Internet connection

### Build

```bash
# Clone the repository
git clone https://github.com/minerofthesoal/vibe-OS-.git
cd vibe-OS-

# Build the ISO
sudo make iso

# Or with clean build
sudo make iso-clean
```

The ISO will be output to `build/out/vibeos-YYYY.MM.DD-x86_64.iso`.

### Testing in QEMU

```bash
# UEFI mode (recommended)
make test-qemu-uefi

# BIOS mode
make test-qemu-bios

# With a virtual disk (for testing the installer)
make test-qemu-disk
```

### Writing to USB

```bash
sudo dd if=build/out/vibeos-*.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

## Installation

1. Boot from the USB/ISO
2. The live Hyprland desktop will start automatically
3. The GUI installer launches on first boot
4. Follow the 7-step wizard:
   - Welcome
   - Disk selection & partitioning
   - User & system configuration
   - Hardware auto-detection
   - Installation summary
   - Installation (automated)
   - Reboot

## Default Keybindings

| Shortcut | Action |
|----------|--------|
| `Super + Return` | Open terminal (Kitty) |
| `Super + Space` | Application launcher (Rofi) |
| `Super + E` | File manager (Thunar) |
| `Super + B` | Browser (Firefox) |
| `Super + Q` | Close window |
| `Super + F` | Maximize window |
| `Super + T` | Toggle floating |
| `Super + 1-9` | Switch workspace |
| `Super + Shift + 1-9` | Move window to workspace |
| `Super + N` | Notification center |
| `Super + V` | Clipboard history |
| `Super + Shift + E` | Power menu (wlogout) |
| `Print` | Screenshot (full) |
| `Shift + Print` | Screenshot (area) |
| `Super + Mouse drag` | Move/resize windows |

## Theming

vibeOS uses **Catppuccin Mocha** as the base color scheme:

| Element | Color |
|---------|-------|
| Background | `#1e1e2e` |
| Surface | `#313244` |
| Text | `#cdd6f4` |
| Blue (accent) | `#89b4fa` |
| Mauve | `#cba6f7` |
| Green | `#a6e3a1` |
| Red | `#f38ba8` |

- **GTK**: Adwaita-dark + Papirus-Dark icons
- **Qt**: Kvantum dark + Papirus-Dark icons
- **Terminal**: Catppuccin Mocha with JetBrainsMono Nerd Font
- **Waybar**: Glassmorphism with blur and transparency
- **SDDM**: Custom QML theme with blur background

## License

MIT License — see [LICENSE](LICENSE)

## Credits

Created by [minerofthesoal](https://github.com/minerofthesoal)
