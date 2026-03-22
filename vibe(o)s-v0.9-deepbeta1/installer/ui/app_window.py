import customtkinter as ctk
from ui.pages import WelcomePage, DiskSetupPage, HardwarePage, SummaryPage, InstallingPage

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("vibe(O)s Installer")
        self.geometry("900x600")
        self.resizable(False, False)

        # Shared Installation State
        self.install_data = {
            "disk": "/dev/sda",
            "surface_kernel": False,
            "username": "vibeos",
            "password": "password",
            "hostname": "vibeos-pc"
        }

        # Main Container for Pages
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize all pages
        self.pages = {}
        for PageClass in (WelcomePage, DiskSetupPage, HardwarePage, SummaryPage, InstallingPage):
            page_name = PageClass.__name__
            page = PageClass(parent=self.container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

        # Start at Welcome Page
        self.show_page("WelcomePage")

    def show_page(self, page_name):
        """Brings the requested page to the front."""
        page = self.pages[page_name]
        page.tkraise()
        
        # Trigger on_show hook if the page has one (useful for updating summaries)
        if hasattr(page, "on_show"):
            page.on_show()
