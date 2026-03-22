"""
vibeOS Installer Backend
Handles subprocess execution with real-time output streaming
"""
import subprocess
import threading
import os
import json
import re


class InstallerBackend:
    """Manages installation script execution with real-time output."""

    def __init__(self, log_callback=None, progress_callback=None):
        self.log_callback = log_callback or print
        self.progress_callback = progress_callback
        self.current_process = None
        self.cancelled = False

        # Detect script path
        self.script_dir = self._find_scripts()

    def _find_scripts(self):
        """Find the installation scripts directory."""
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../scripts"),
            "/opt/vibeos/scripts",
            os.path.expanduser("~/vibe-OS-/scripts"),
        ]
        for path in candidates:
            real = os.path.realpath(path)
            if os.path.isdir(real) and os.path.isfile(os.path.join(real, "utils.sh")):
                return real
        return "/opt/vibeos/scripts"

    def log(self, text):
        """Send log message to callback."""
        if self.log_callback:
            self.log_callback(text)

    def run_command(self, cmd, on_complete=None):
        """Run a shell command asynchronously with real-time output."""
        def _run():
            try:
                self.log(f">>> {cmd}")
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                )
                self.current_process = process

                for line in process.stdout:
                    if self.cancelled:
                        process.terminate()
                        break
                    line = line.rstrip()
                    # Strip ANSI color codes for display
                    clean = re.sub(r'\033\[[0-9;]*m', '', line)
                    self.log(clean)

                process.wait()
                rc = process.returncode
                if on_complete:
                    on_complete(rc)

            except Exception as e:
                self.log(f"[ERROR] {str(e)}")
                if on_complete:
                    on_complete(1)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread

    def detect_disks(self):
        """Get available disks for installation."""
        disks = []
        try:
            result = subprocess.run(
                ["lsblk", "-dpno", "NAME,SIZE,MODEL,TYPE"],
                capture_output=True, text=True
            )
            for line in result.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 3 and parts[-1] == "disk":
                    name = parts[0]
                    size = parts[1]
                    model = " ".join(parts[2:-1]) if len(parts) > 3 else "Unknown"
                    disks.append({"name": name, "size": size, "model": model})
        except Exception:
            disks = [
                {"name": "/dev/sda", "size": "?", "model": "Unknown"},
                {"name": "/dev/vda", "size": "?", "model": "VirtIO"},
            ]
        return disks

    def detect_timezones(self):
        """Get common timezone list."""
        common = [
            "UTC",
            "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Berlin", "Europe/Paris",
            "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata",
            "Australia/Sydney",
            "America/Sao_Paulo", "America/Mexico_City",
        ]
        # Try to get full list
        try:
            result = subprocess.run(
                ["timedatectl", "list-timezones"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")
        except Exception:
            pass
        return common

    def get_hardware_info(self):
        """Read hardware detection results."""
        info = {}
        try:
            if os.path.exists("/tmp/vibeos_hw_info.txt"):
                with open("/tmp/vibeos_hw_info.txt") as f:
                    info["summary"] = f.read().strip()
            if os.path.exists("/tmp/vibeos_hw_pkgs.txt"):
                with open("/tmp/vibeos_hw_pkgs.txt") as f:
                    info["packages"] = f.read().strip()
        except Exception:
            info["summary"] = "Hardware detection not yet run"
            info["packages"] = ""
        return info

    def cancel(self):
        """Cancel current operation."""
        self.cancelled = True
        if self.current_process:
            self.current_process.terminate()
