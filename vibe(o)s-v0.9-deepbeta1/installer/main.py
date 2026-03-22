import sys
import os
import customtkinter as ctk

# Ensure the installer directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.app_window import AppWindow

def main():
    # Set the macOS/ReviOS dark mode aesthetic
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = AppWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
