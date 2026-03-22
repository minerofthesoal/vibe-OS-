#!/usr/bin/env python3
"""
vibeOS Installer
GUI-based system installer for vibeOS (Arch Linux + Hyprland)
"""
import sys
import os

# Ensure module imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from ui.app_window import AppWindow


def main():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = AppWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
