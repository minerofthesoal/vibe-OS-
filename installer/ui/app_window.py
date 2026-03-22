"""
vibeOS Installer - Main Application Window
"""
import customtkinter as ctk
from ui.pages import (
    WelcomePage, DiskSetupPage, UserSetupPage,
    HardwarePage, SummaryPage, InstallingPage, CompletePage
)


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("vibeOS Installer")
        self.geometry("950x650")
        self.minsize(900, 600)
        self.configure(fg_color="#0d1117")

        # Set WM class for Hyprland window rules
        try:
            self.wm_attributes("-class", "vibeOS-installer")
        except Exception:
            pass

        # Shared installation state
        self.install_data = {
            "disk": "",
            "username": "user",
            "password": "",
            "hostname": "vibeos-pc",
            "timezone": "UTC",
            "use_swap": True,
            "swap_size": "4G",
            "surface_kernel": False,
        }

        # Page container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=0, pady=0)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize pages
        self.pages = {}
        for PageClass in (
            WelcomePage, DiskSetupPage, UserSetupPage,
            HardwarePage, SummaryPage, InstallingPage, CompletePage
        ):
            page = PageClass(parent=self.container, controller=self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("WelcomePage")

    def show_page(self, page_name):
        """Bring requested page to front."""
        page = self.pages[page_name]
        page.tkraise()
        if hasattr(page, "on_show"):
            page.on_show()
