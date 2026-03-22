# ArchForge Desktop Environment - System Architecture

## 1. Vision & Philosophy
ArchForge is a bespoke Desktop Environment (DE) engineered from the ground up for Arch Linux. It rejects the bloat of traditional monolithic DEs (like GNOME or KDE) and the fragmentation of standalone window managers. 

**The Goal:** Combine the fluid, cohesive aesthetic of macOS with the debloated, bare-metal performance of Windows 10 ReviOS.

---

## 2. Core Component Breakdown

To build a true Desktop Environment, we must engineer five distinct pillars:

### I. ArchForge Compositor (The Engine)
The heart of the DE. It communicates directly with the Linux kernel (DRM/KMS) to draw pixels and `libinput` to handle hardware events.
* **Role:** Window management (floating and dynamic tiling), rendering, input routing, and Wayland protocol implementation.
* **Features:** Hardware-accelerated rendering, damage tracking, workspace management, and custom Wayland protocols for IPC.

### II. ArchForge Shell (The UI)
The user-facing graphical components that users interact with.
* **Role:** Renders the Dock, Top Panel, Control Center, App Launcher, and Task View.
* **Features:** Uses `gtk-layer-shell` (Wayland-specific) to anchor UI elements to screen edges without being treated as standard windows. Communicates with the compositor via custom Wayland protocols.

### III. ArchForge Session Manager (The Bootstrapper)
The initialization system that brings the DE to life.
* **Role:** Replaces `startx` or standard display manager scripts.
* **Features:** Bootstraps the Wayland compositor, launches essential background daemons (Polkit, Keyring, NetworkManager, Pipewire), manages environment variables (`WAYLAND_DISPLAY`, `XDG_CURRENT_DESKTOP`), and handles graceful logout/reboot/shutdown pipelines.

### IV. ArchForge Settings Daemon (The State Manager)
A headless background process that manages system state and user preferences.
* **Role:** Centralized configuration and live-reloading.
* **Features:** Listens for changes in configuration files or UI toggles (via the Control Center) and broadcasts state changes via IPC (D-Bus or custom Wayland protocols) to update themes, volume, brightness, and display scaling in real-time.

### V. ArchForge Installer (The Deployment Engine)
The gateway to the OS.
* **Role:** A GUI application that installs Arch Linux and compiles/deploys the ArchForge DE.
* **Features:** Automated hardware detection (NVIDIA, AMD, Intel, Surface kernels), disk partitioning, and compiling the DE from source (or pulling pre-compiled binaries).

---

## 3. Language Stack Recommendation

Building a compositor is systems programming at its most extreme. We have two viable paths:

### Option A: C/C++ with `wlroots` (The Industry Standard)
* **Pros:** `wlroots` is battle-tested. It powers Sway, Hyprland, and countless others. Massive ecosystem, extensive documentation, and direct C bindings to Wayland.
* **Cons:** C requires manual memory management. Compositors are highly concurrent and stateful; a single use-after-free or segmentation fault will crash the entire graphical session, taking all user applications down with it. Build systems (Meson/CMake) can be complex to integrate into an automated installer.

### Option B: Rust with `Smithay` (The Modern Vanguard) - **[HIGHLY RECOMMENDED]**
* **Pros:** Rust guarantees memory safety and thread safety. A compositor written in Rust is virtually immune to the segmentation faults that plague C-based compositors. `Smithay` is a fantastic, modular Rust framework for building Wayland compositors (used by System76's new COSMIC DE). Furthermore, Rust's `cargo` package manager makes compiling the entire DE from source during the OS installation trivial and reproducible.
* **Cons:** Steeper learning curve. `Smithay` is slightly less mature than `wlroots`, though it is rapidly becoming the gold standard for next-gen Linux DEs.

**My Recommendation:** 
We should use **Rust + Smithay** for the Compositor and Session Manager, and **Rust + GTK4 (gtk-rs)** for the Shell and Settings Daemon. This gives us a unified, memory-safe language stack, blazing-fast performance, and a trivial build process (`cargo build --release`) for the installer.

---

## 4. Source Code Directory Structure

We will restructure the repository to reflect a modular, enterprise-grade software project:

```text
archforge/
├── ARCHITECTURE.md
├── Cargo.toml                  # Unified Rust workspace configuration
├── compositor/                 # (Rust) The Smithay-based Wayland Compositor
│   ├── src/
│   │   ├── main.rs             # Entry point
│   │   ├── state.rs            # Global compositor state
│   │   ├── render.rs           # DRM/KMS rendering logic
│   │   ├── input.rs            # libinput handling
│   │   └── window_manager.rs   # Tiling/Floating logic
├── shell/                      # (Rust + GTK4) The UI Components
│   ├── panel/
│   ├── dock/
│   ├── control_center/
│   └── launcher/
├── session/                    # (Rust) Session Manager & Bootstrapper
├── settings-daemon/            # (Rust) IPC and State Management
├── protocols/                  # Custom Wayland XML protocols for Shell <-> Compositor IPC
├── installer/                  # (Python/PyQt6 or Rust) The OS Installer
└── scripts/                    # ISO generation and deployment scripts
```
