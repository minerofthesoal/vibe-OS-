"""
vibeOS Installer - Pages
Multi-step installation wizard with dark glassmorphism theme
"""
import os
import subprocess
import customtkinter as ctk
from core.installer_backend import InstallerBackend

# Color palette
BG = "#0d1117"
CARD = "#161b22"
CARD_HOVER = "#1c2333"
BORDER = "#30363d"
TEXT = "#e6edf3"
TEXT_DIM = "#8b949e"
ACCENT = "#89b4fa"
ACCENT_HOVER = "#a4c4fc"
RED = "#f38ba8"
GREEN = "#a6e3a1"
MAUVE = "#cba6f7"


class BasePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.controller = controller


class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Center content
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.45, anchor="center")

        # Logo / title
        ctk.CTkLabel(
            center, text="vibeOS",
            font=("Inter", 48, "bold"), text_color=ACCENT
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            center, text="Arch Linux × Hyprland Desktop",
            font=("Inter", 16), text_color=TEXT_DIM
        ).pack(pady=(0, 30))

        # Feature highlights
        features = [
            "  Hyprland Wayland compositor with macOS-style animations",
            "  Auto hardware detection & driver installation",
            "  Catppuccin Mocha theme with glassmorphism effects",
            "  Full UEFI + BIOS boot support",
            "  PipeWire audio, Bluetooth, Flatpak ready",
        ]
        for feat in features:
            ctk.CTkLabel(
                center, text=feat,
                font=("Inter", 13), text_color=TEXT_DIM,
                anchor="w"
            ).pack(fill="x", padx=40, pady=2)

        # Credits
        ctk.CTkLabel(
            center,
            text="by minerofthesoal",
            font=("Inter", 12), text_color=MAUVE
        ).pack(pady=(20, 0))

        # Get Started button
        ctk.CTkButton(
            self, text="Get Started →", font=("Inter", 16, "bold"),
            width=220, height=50, corner_radius=14,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="#11111b",
            command=lambda: controller.show_page("DiskSetupPage")
        ).place(relx=0.5, rely=0.88, anchor="center")


class DiskSetupPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Title
        ctk.CTkLabel(
            self, text="Disk Setup", font=("Inter", 28, "bold"), text_color=TEXT
        ).pack(pady=(40, 8))
        ctk.CTkLabel(
            self, text="Select the target disk for installation",
            font=("Inter", 14), text_color=TEXT_DIM
        ).pack(pady=(0, 30))

        # Card
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(padx=80, fill="x")

        # Disk selection
        ctk.CTkLabel(card, text="Target Disk", font=("Inter", 13, "bold"), text_color=TEXT).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(card, text="WARNING: Selected disk will be completely erased!", font=("Inter", 11), text_color=RED).pack(anchor="w", padx=24, pady=(0, 8))

        self.disk_var = ctk.StringVar()
        self.disk_dropdown = ctk.CTkComboBox(
            card, variable=self.disk_var,
            values=self._get_disk_list(),
            width=400, height=36, corner_radius=10,
            fg_color="#1c2333", border_color=BORDER,
            button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            dropdown_fg_color=CARD, dropdown_hover_color=CARD_HOVER,
            font=("JetBrains Mono", 12)
        )
        self.disk_dropdown.pack(padx=24, pady=(0, 16))

        # Swap toggle
        self.swap_var = ctk.BooleanVar(value=True)
        swap_frame = ctk.CTkFrame(card, fg_color="transparent")
        swap_frame.pack(fill="x", padx=24, pady=(8, 4))
        ctk.CTkSwitch(
            swap_frame, text="Create swap partition",
            variable=self.swap_var, font=("Inter", 13),
            progress_color=ACCENT, button_color=TEXT
        ).pack(side="left")

        ctk.CTkLabel(card, text="Swap Size:", font=("Inter", 12), text_color=TEXT_DIM).pack(anchor="w", padx=24, pady=(8, 4))
        self.swap_size_var = ctk.StringVar(value="4G")
        ctk.CTkComboBox(
            card, variable=self.swap_size_var,
            values=["2G", "4G", "8G", "16G"],
            width=120, height=32, corner_radius=8,
            fg_color="#1c2333", border_color=BORDER,
            font=("JetBrains Mono", 12)
        ).pack(anchor="w", padx=24, pady=(0, 20))

        # Refresh button
        ctk.CTkButton(
            card, text="↻ Refresh Disks", width=140, height=32,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color=CARD_HOVER, font=("Inter", 12),
            command=self._refresh_disks
        ).pack(padx=24, pady=(0, 20))

        # Navigation
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(side="bottom", fill="x", padx=80, pady=30)
        ctk.CTkButton(
            nav, text="← Back", width=120, height=40,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color=CARD_HOVER, font=("Inter", 13),
            command=lambda: controller.show_page("WelcomePage")
        ).pack(side="left")
        ctk.CTkButton(
            nav, text="Next →", width=120, height=40,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="#11111b", font=("Inter", 13, "bold"),
            command=self._save_and_next
        ).pack(side="right")

    def _get_disk_list(self):
        try:
            result = subprocess.run(
                ["lsblk", "-dpno", "NAME,SIZE,MODEL"],
                capture_output=True, text=True
            )
            disks = []
            for line in result.stdout.strip().split("\n"):
                if line and any(x in line for x in ["/dev/sd", "/dev/nvme", "/dev/vd", "/dev/mmcblk"]):
                    disks.append(line.strip())
            return disks if disks else ["/dev/sda  (not detected)"]
        except Exception:
            return ["/dev/sda", "/dev/nvme0n1", "/dev/vda"]

    def _refresh_disks(self):
        self.disk_dropdown.configure(values=self._get_disk_list())

    def _save_and_next(self):
        disk_str = self.disk_var.get().split()[0] if self.disk_var.get() else "/dev/sda"
        self.controller.install_data["disk"] = disk_str
        self.controller.install_data["use_swap"] = self.swap_var.get()
        self.controller.install_data["swap_size"] = self.swap_size_var.get()
        self.controller.show_page("UserSetupPage")


class UserSetupPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ctk.CTkLabel(
            self, text="User & System", font=("Inter", 28, "bold"), text_color=TEXT
        ).pack(pady=(40, 8))
        ctk.CTkLabel(
            self, text="Configure your user account and system settings",
            font=("Inter", 14), text_color=TEXT_DIM
        ).pack(pady=(0, 30))

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(padx=80, fill="x")

        fields = [
            ("Username", "user_entry", "user", False),
            ("Password", "pass_entry", "", True),
            ("Confirm Password", "pass2_entry", "", True),
            ("Hostname", "host_entry", "vibeos-pc", False),
        ]

        for label, attr, default, is_pass in fields:
            ctk.CTkLabel(card, text=label, font=("Inter", 13, "bold"), text_color=TEXT).pack(anchor="w", padx=24, pady=(12, 4))
            entry = ctk.CTkEntry(
                card, width=360, height=38, corner_radius=10,
                fg_color="#1c2333", border_color=BORDER,
                font=("Inter", 13),
                show="•" if is_pass else ""
            )
            if default:
                entry.insert(0, default)
            entry.pack(anchor="w", padx=24, pady=(0, 4))
            setattr(self, attr, entry)

        # Timezone
        ctk.CTkLabel(card, text="Timezone", font=("Inter", 13, "bold"), text_color=TEXT).pack(anchor="w", padx=24, pady=(12, 4))
        self.tz_var = ctk.StringVar(value="UTC")
        ctk.CTkComboBox(
            card, variable=self.tz_var,
            values=[
                "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
                "Europe/London", "Europe/Berlin", "Europe/Paris",
                "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata",
                "Australia/Sydney", "America/Sao_Paulo"
            ],
            width=360, height=36, corner_radius=10,
            fg_color="#1c2333", border_color=BORDER, font=("Inter", 12)
        ).pack(anchor="w", padx=24, pady=(0, 20))

        self.error_label = ctk.CTkLabel(self, text="", font=("Inter", 12), text_color=RED)
        self.error_label.pack(pady=(8, 0))

        # Navigation
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(side="bottom", fill="x", padx=80, pady=30)
        ctk.CTkButton(
            nav, text="← Back", width=120, height=40,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color=CARD_HOVER, font=("Inter", 13),
            command=lambda: controller.show_page("DiskSetupPage")
        ).pack(side="left")
        ctk.CTkButton(
            nav, text="Next →", width=120, height=40,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="#11111b", font=("Inter", 13, "bold"),
            command=self._validate_and_next
        ).pack(side="right")

    def _validate_and_next(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        password2 = self.pass2_entry.get()
        hostname = self.host_entry.get().strip()

        if not username:
            self.error_label.configure(text="Username cannot be empty")
            return
        if not username.isalnum() and "_" not in username:
            self.error_label.configure(text="Username must be alphanumeric")
            return
        if len(password) < 4:
            self.error_label.configure(text="Password must be at least 4 characters")
            return
        if password != password2:
            self.error_label.configure(text="Passwords do not match")
            return
        if not hostname:
            self.error_label.configure(text="Hostname cannot be empty")
            return

        self.error_label.configure(text="")
        self.controller.install_data["username"] = username
        self.controller.install_data["password"] = password
        self.controller.install_data["hostname"] = hostname
        self.controller.install_data["timezone"] = self.tz_var.get()
        self.controller.show_page("HardwarePage")


class HardwarePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ctk.CTkLabel(
            self, text="Hardware Detection", font=("Inter", 28, "bold"), text_color=TEXT
        ).pack(pady=(40, 8))
        ctk.CTkLabel(
            self, text="vibeOS will automatically detect and install the right drivers",
            font=("Inter", 14), text_color=TEXT_DIM
        ).pack(pady=(0, 30))

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(padx=80, fill="x")

        self.hw_text = ctk.CTkTextbox(
            card, width=600, height=180,
            font=("JetBrains Mono", 12),
            fg_color="#1c2333", text_color=GREEN,
            corner_radius=10, border_width=1, border_color=BORDER,
            state="disabled"
        )
        self.hw_text.pack(padx=24, pady=20)

        ctk.CTkButton(
            card, text="⟳ Run Detection", width=160, height=36,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="#11111b", font=("Inter", 13),
            command=self._run_detection
        ).pack(pady=(0, 20))

        # Navigation
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(side="bottom", fill="x", padx=80, pady=30)
        ctk.CTkButton(
            nav, text="← Back", width=120, height=40,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color=CARD_HOVER, font=("Inter", 13),
            command=lambda: controller.show_page("UserSetupPage")
        ).pack(side="left")
        ctk.CTkButton(
            nav, text="Next →", width=120, height=40,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="#11111b", font=("Inter", 13, "bold"),
            command=lambda: controller.show_page("SummaryPage")
        ).pack(side="right")

    def on_show(self):
        self._run_detection()

    def _run_detection(self):
        self.hw_text.configure(state="normal")
        self.hw_text.delete("1.0", "end")
        self.hw_text.insert("1.0", "Detecting hardware...\n")
        self.hw_text.configure(state="disabled")

        def _detect():
            backend = InstallerBackend()
            backend.run_command(
                f"bash {backend.script_dir}/01-hardware-detect.sh",
                on_complete=lambda rc: self.after(100, self._show_results)
            )

        self.after(200, _detect)

    def _show_results(self):
        self.hw_text.configure(state="normal")
        self.hw_text.delete("1.0", "end")

        info = ""
        try:
            if os.path.exists("/tmp/vibeos_hw_info.txt"):
                with open("/tmp/vibeos_hw_info.txt") as f:
                    info = f.read().strip()
            if os.path.exists("/tmp/vibeos_hw_pkgs.txt"):
                with open("/tmp/vibeos_hw_pkgs.txt") as f:
                    pkgs = f.read().strip()
                    info += f"\n\nPackages to install:\n{pkgs}"
        except Exception as e:
            info = f"Detection completed.\nDetails may not be available: {e}"

        if not info.strip():
            info = "Hardware detection completed.\nDrivers will be auto-selected during installation."

        self.hw_text.insert("1.0", info)
        self.hw_text.configure(state="disabled")


class SummaryPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ctk.CTkLabel(
            self, text="Installation Summary", font=("Inter", 28, "bold"), text_color=TEXT
        ).pack(pady=(40, 8))
        ctk.CTkLabel(
            self, text="Review your settings before installing",
            font=("Inter", 14), text_color=TEXT_DIM
        ).pack(pady=(0, 30))

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(padx=80, fill="x")

        self.summary_text = ctk.CTkTextbox(
            card, width=600, height=220,
            font=("JetBrains Mono", 13),
            fg_color="#1c2333", text_color=TEXT,
            corner_radius=10, border_width=1, border_color=BORDER,
            state="disabled"
        )
        self.summary_text.pack(padx=24, pady=20)

        warning = ctk.CTkLabel(
            self,
            text="⚠  This will ERASE the selected disk. This action cannot be undone!",
            font=("Inter", 13, "bold"), text_color=RED
        )
        warning.pack(pady=10)

        # Navigation
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(side="bottom", fill="x", padx=80, pady=30)
        ctk.CTkButton(
            nav, text="← Back", width=120, height=40,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color=CARD_HOVER, font=("Inter", 13),
            command=lambda: controller.show_page("HardwarePage")
        ).pack(side="left")
        ctk.CTkButton(
            nav, text="Install vibeOS", width=160, height=44,
            fg_color="#f38ba8", hover_color="#e06c88",
            text_color="#11111b", font=("Inter", 14, "bold"),
            command=lambda: controller.show_page("InstallingPage")
        ).pack(side="right")

    def on_show(self):
        data = self.controller.install_data
        swap_info = f"Yes ({data['swap_size']})" if data['use_swap'] else "No"
        summary = (
            f"┌──────────────────────────────────────┐\n"
            f"│  Installation Configuration           │\n"
            f"├──────────────────────────────────────┤\n"
            f"│  Disk:      {data['disk']:<24s}│\n"
            f"│  Swap:      {swap_info:<24s}│\n"
            f"│  Username:  {data['username']:<24s}│\n"
            f"│  Hostname:  {data['hostname']:<24s}│\n"
            f"│  Timezone:  {data['timezone']:<24s}│\n"
            f"├──────────────────────────────────────┤\n"
            f"│  Steps:                               │\n"
            f"│  1. Hardware auto-detection            │\n"
            f"│  2. Disk partitioning & formatting     │\n"
            f"│  3. Base system installation           │\n"
            f"│  4. System configuration               │\n"
            f"│  5. vibeOS DE deployment               │\n"
            f"│  6. Bootloader & finalization           │\n"
            f"└──────────────────────────────────────┘\n"
        )
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", summary)
        self.summary_text.configure(state="disabled")


class InstallingPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.title_label = ctk.CTkLabel(
            self, text="Installing vibeOS...", font=("Inter", 28, "bold"), text_color=TEXT
        )
        self.title_label.pack(pady=(30, 8))

        self.step_label = ctk.CTkLabel(
            self, text="Preparing...", font=("Inter", 14), text_color=ACCENT
        )
        self.step_label.pack(pady=(0, 12))

        self.progress = ctk.CTkProgressBar(
            self, width=700, height=10, corner_radius=5,
            progress_color=ACCENT, fg_color=BORDER
        )
        self.progress.pack(pady=(0, 16))
        self.progress.set(0)

        self.log_box = ctk.CTkTextbox(
            self, width=800, height=340,
            font=("JetBrains Mono", 11),
            fg_color="#0a0e14", text_color="#8b949e",
            corner_radius=12, border_width=1, border_color=BORDER
        )
        self.log_box.pack(padx=40, pady=(0, 10))

        self.scripts_queue = []
        self.current_index = 0
        self.backend = InstallerBackend(log_callback=self._log)

    def on_show(self):
        self.log_box.delete("1.0", "end")
        self.progress.set(0)

        data = self.controller.install_data
        sd = self.backend.script_dir

        swap_args = "yes " + data['swap_size'] if data['use_swap'] else "no"

        self.scripts_queue = [
            ("Detecting hardware...", f"bash {sd}/01-hardware-detect.sh"),
            ("Partitioning disk...", f"bash {sd}/02-partition-disk.sh {data['disk']} {swap_args}"),
            ("Installing base system (this takes a while)...", f"bash {sd}/03-base-install.sh"),
            ("Configuring system...",
             f"cp -r {sd} /mnt/opt/vibeos/scripts 2>/dev/null; "
             f"arch-chroot /mnt bash /opt/vibeos/scripts/04-chroot-configure.sh "
             f"{data['username']} {data['password']} {data['hostname']} {data['timezone']}"),
            ("Installing desktop environment...",
             f"arch-chroot /mnt bash /opt/vibeos/scripts/05-install-de.sh {data['username']}"),
            ("Finalizing installation...",
             f"arch-chroot /mnt bash /opt/vibeos/scripts/06-finalize.sh"),
        ]

        self.current_index = 0
        self._run_next()

    def _log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def _run_next(self):
        if self.current_index < len(self.scripts_queue):
            label, cmd = self.scripts_queue[self.current_index]
            self.step_label.configure(text=label)
            self._log(f"\n{'='*60}")
            self._log(f"Step {self.current_index + 1}/{len(self.scripts_queue)}: {label}")
            self._log(f"{'='*60}\n")

            self.backend.run_command(
                f"pkexec bash -c '{cmd}'",
                on_complete=lambda rc: self.after(100, lambda: self._on_complete(rc))
            )
        else:
            self.step_label.configure(text="Installation complete!")
            self.title_label.configure(text="Installation Complete!", text_color=GREEN)
            self.progress.set(1.0)
            self.controller.show_page("CompletePage")

    def _on_complete(self, return_code):
        if return_code == 0:
            self.current_index += 1
            self.progress.set(self.current_index / len(self.scripts_queue))
            self.after(500, self._run_next)
        else:
            self._log(f"\n[ERROR] Step failed with code {return_code}")
            self.step_label.configure(text="Installation failed!", text_color=RED)
            self.title_label.configure(text="Installation Failed", text_color=RED)


class CompletePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.4, anchor="center")

        ctk.CTkLabel(
            center, text="✓", font=("Inter", 72), text_color=GREEN
        ).pack(pady=(0, 16))

        ctk.CTkLabel(
            center, text="vibeOS Installed Successfully!",
            font=("Inter", 32, "bold"), text_color=TEXT
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            center, text="Remove the installation media and reboot to start using vibeOS.",
            font=("Inter", 15), text_color=TEXT_DIM
        ).pack(pady=(0, 40))

        ctk.CTkButton(
            center, text="Reboot Now", width=200, height=50,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="#11111b", font=("Inter", 16, "bold"),
            corner_radius=14,
            command=lambda: os.system("pkexec reboot")
        ).pack(pady=(0, 12))

        ctk.CTkButton(
            center, text="Continue Testing", width=200, height=40,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color=CARD_HOVER, font=("Inter", 13),
            command=lambda: controller.show_page("WelcomePage")
        ).pack()
