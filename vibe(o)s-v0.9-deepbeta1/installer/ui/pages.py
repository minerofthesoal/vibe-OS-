import os
import customtkinter as ctk
from core.process_runner import ProcessRunner

class BasePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#1e1e1e", corner_radius=15)
        self.controller = controller

class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        title = ctk.CTkLabel(self, text="Welcome to vibe(O)s", font=("Inter", 32, "bold"))
        title.pack(pady=(40, 10))
        
        desc = ctk.CTkLabel(self, text="This installer will guide you through setting up your custom\nWayland Desktop Environment.", font=("Inter", 16), text_color="gray")
        desc.pack(pady=5)
        
        credits = ctk.CTkLabel(self, text="Made by Gemini 3.1 Pro (so far)\nPrompted by ray0ffire/minerofthesoal", font=("Inter", 14, "bold"), text_color="#a371f7")
        credits.pack(pady=(10, 20))
        
        btn_next = ctk.CTkButton(self, text="Get Started", font=("Inter", 16), width=200, height=45, command=lambda: controller.show_page("DiskSetupPage"))
        btn_next.pack(side="bottom", pady=40)

class DiskSetupPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        title = ctk.CTkLabel(self, text="System Setup", font=("Inter", 28, "bold"))
        title.pack(pady=(40, 30))
        
        # Disk Selection
        ctk.CTkLabel(self, text="Target Disk (WARNING: Will be wiped):", font=("Inter", 14)).pack(anchor="w", padx=100)
        self.disk_var = ctk.StringVar(value="/dev/sda")
        self.disk_dropdown = ctk.CTkComboBox(self, variable=self.disk_var, values=["/dev/sda", "/dev/nvme0n1", "/dev/vda"], width=300)
        self.disk_dropdown.pack(pady=(5, 20))
        
        # User Details
        ctk.CTkLabel(self, text="Username:", font=("Inter", 14)).pack(anchor="w", padx=100)
        self.user_entry = ctk.CTkEntry(self, width=300)
        self.user_entry.insert(0, "vibeos")
        self.user_entry.pack(pady=(5, 10))
        
        ctk.CTkLabel(self, text="Password:", font=("Inter", 14)).pack(anchor="w", padx=100)
        self.pass_entry = ctk.CTkEntry(self, width=300, show="*")
        self.pass_entry.insert(0, "password")
        self.pass_entry.pack(pady=(5, 10))
        
        ctk.CTkLabel(self, text="Hostname:", font=("Inter", 14)).pack(anchor="w", padx=100)
        self.host_entry = ctk.CTkEntry(self, width=300)
        self.host_entry.insert(0, "vibeos-pc")
        self.host_entry.pack(pady=(5, 20))
        
        # Navigation
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(side="bottom", fill="x", pady=40, padx=100)
        ctk.CTkButton(nav_frame, text="Back", width=120, fg_color="gray", hover_color="#555", command=lambda: controller.show_page("WelcomePage")).pack(side="left")
        ctk.CTkButton(nav_frame, text="Next", width=120, command=self.save_and_next).pack(side="right")

    def save_and_next(self):
        self.controller.install_data["disk"] = self.disk_var.get()
        self.controller.install_data["username"] = self.user_entry.get()
        self.controller.install_data["password"] = self.pass_entry.get()
        self.controller.install_data["hostname"] = self.host_entry.get()
        self.controller.show_page("HardwarePage")

class HardwarePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        title = ctk.CTkLabel(self, text="Hardware & Drivers", font=("Inter", 28, "bold"))
        title.pack(pady=(40, 30))
        
        info = ctk.CTkLabel(self, text="ArchForge will automatically detect your CPU, GPU, and Network\ninterfaces to install the correct drivers.", font=("Inter", 14), text_color="gray")
        info.pack(pady=10)
        
        # Surface Kernel Toggle
        self.surface_var = ctk.BooleanVar(value=False)
        self.surface_switch = ctk.CTkSwitch(self, text="Install linux-surface Kernel (For Microsoft Surface Devices)", variable=self.surface_var, font=("Inter", 14))
        self.surface_switch.pack(pady=40)
        
        # Navigation
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(side="bottom", fill="x", pady=40, padx=100)
        ctk.CTkButton(nav_frame, text="Back", width=120, fg_color="gray", hover_color="#555", command=lambda: controller.show_page("DiskSetupPage")).pack(side="left")
        ctk.CTkButton(nav_frame, text="Next", width=120, command=self.save_and_next).pack(side="right")

    def save_and_next(self):
        self.controller.install_data["surface_kernel"] = self.surface_var.get()
        self.controller.show_page("SummaryPage")

class SummaryPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        title = ctk.CTkLabel(self, text="Ready to Install", font=("Inter", 28, "bold"))
        title.pack(pady=(40, 20))
        
        self.summary_text = ctk.CTkTextbox(self, width=500, height=200, font=("Inter", 14), state="disabled", fg_color="#2a2a2a")
        self.summary_text.pack(pady=20)
        
        warning = ctk.CTkLabel(self, text="WARNING: The selected disk will be completely wiped.", font=("Inter", 14, "bold"), text_color="#ff4444")
        warning.pack(pady=10)
        
        # Navigation
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(side="bottom", fill="x", pady=40, padx=100)
        ctk.CTkButton(nav_frame, text="Back", width=120, fg_color="gray", hover_color="#555", command=lambda: controller.show_page("HardwarePage")).pack(side="left")
        ctk.CTkButton(nav_frame, text="INSTALL", width=120, fg_color="#ff4444", hover_color="#cc0000", command=lambda: controller.show_page("InstallingPage")).pack(side="right")

    def on_show(self):
        data = self.controller.install_data
        summary = (
            f"Target Disk: {data['disk']}\n"
            f"Username: {data['username']}\n"
            f"Hostname: {data['hostname']}\n"
            f"Surface Kernel: {'Yes' if data['surface_kernel'] else 'No'}\n\n"
            f"Automated Steps:\n"
            f"1. Hardware Auto-Detection\n"
            f"2. Disk Partitioning & Formatting\n"
            f"3. Base System Pacstrap\n"
            f"4. vibe(O)s DE Configuration"
        )
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", summary)
        self.summary_text.configure(state="disabled")

class InstallingPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        self.title = ctk.CTkLabel(self, text="Installing vibe(O)s...", font=("Inter", 28, "bold"))
        self.title.pack(pady=(40, 20))
        
        self.progress = ctk.CTkProgressBar(self, width=600, mode="determinate")
        self.progress.pack(pady=10)
        self.progress.set(0)
        
        self.log_box = ctk.CTkTextbox(self, width=700, height=300, font=("JetBrains Mono", 12), fg_color="#111111", text_color="#00ff00")
        self.log_box.pack(pady=20)
        
        self.btn_finish = ctk.CTkButton(self, text="Reboot System", width=200, height=45, state="disabled", command=self.reboot)
        self.btn_finish.pack(side="bottom", pady=20)
        
        self.scripts_queue = []
        self.current_script_index = 0

    def on_show(self):
        self.log_box.delete("1.0", "end")
        self.progress.set(0)
        self.btn_finish.configure(state="disabled")
        
        data = self.controller.install_data
        
        # Determine script path (handles running from source or from compiled binary in /opt/archforge)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts"))
        if not os.path.exists(base_path):
            base_path = "/opt/archforge/scripts" # Fallback for Live ISO
            
        # Queue the bash scripts
        # Note: pkexec is used to elevate privileges for the bash scripts
        self.scripts_queue = [
            f"pkexec bash {base_path}/01-hardware-detect.sh",
            f"pkexec bash {base_path}/02-base-install.sh {data['disk']}"
        ]
        
        if data["surface_kernel"]:
            self.scripts_queue.append(f"pkexec arch-chroot /mnt bash {base_path}/03-surface-kernel.sh")
            
        self.scripts_queue.append(f"pkexec arch-chroot /mnt bash {base_path}/04-post-install.sh {data['username']} {data['password']} {data['hostname']}")
        
        self.current_script_index = 0
        self.run_next_script()

    def log_output(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def run_next_script(self):
        if self.current_script_index < len(self.scripts_queue):
            cmd = self.scripts_queue[self.current_script_index]
            self.log_output(f"\n>>> RUNNING: {cmd}\n")
            
            runner = ProcessRunner(self.log_output, self.on_script_complete)
            runner.run(cmd)
        else:
            self.log_output("\n[SUCCESS] Installation Complete! You may now reboot.")
            self.progress.set(1.0)
            self.title.configure(text="Installation Complete!")
            self.btn_finish.configure(state="normal")

    def on_script_complete(self, return_code):
        if return_code == 0:
            self.current_script_index += 1
            progress_val = self.current_script_index / len(self.scripts_queue)
            self.progress.set(progress_val)
            # Run next script on the main thread
            self.after(500, self.run_next_script)
        else:
            self.log_output(f"\n[ERROR] Script failed with return code {return_code}. Halting installation.")
            self.title.configure(text="Installation Failed", text_color="#ff4444")

    def reboot(self):
        os.system("pkexec reboot")
