import customtkinter as ctk
import subprocess
import threading

class AppStore(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ArchForge App Store")
        self.geometry("1000x700")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="App Store", font=("Inter", 24, "bold")).pack(pady=20, padx=20)
        
        self.btn_discover = ctk.CTkButton(self.sidebar, text="Discover", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.switch_tab("discover"))
        self.btn_discover.pack(fill="x", pady=5, padx=10)
        
        self.btn_sources = ctk.CTkButton(self.sidebar, text="Sources", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.switch_tab("sources"))
        self.btn_sources.pack(fill="x", pady=5, padx=10)
        
        # Main Content Area
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.build_discover_tab()
        self.build_sources_tab()
        
        self.switch_tab("discover")

    def build_discover_tab(self):
        self.discover_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        
        # Search Bar
        search_box = ctk.CTkFrame(self.discover_frame, fg_color="transparent")
        search_box.pack(fill="x", pady=(0, 20))
        
        self.search_entry = ctk.CTkEntry(search_box, placeholder_text="Search KDE Apps (Pacman) or Flathub...", font=("Inter", 14), height=40)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", self.perform_search)
        
        ctk.CTkButton(search_box, text="Search", width=100, height=40, command=self.perform_search).pack(side="right")
        
        # Results Area
        self.results_scroll = ctk.CTkScrollableFrame(self.discover_frame, fg_color="transparent")
        self.results_scroll.pack(fill="both", expand=True)

    def build_sources_tab(self):
        self.sources_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        ctk.CTkLabel(self.sources_frame, text="Software Sources", font=("Inter", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(self.sources_frame, text="Flatpak Remotes:", font=("Inter", 16, "bold")).pack(anchor="w", pady=(10, 5))
        self.remotes_box = ctk.CTkTextbox(self.sources_frame, height=100)
        self.remotes_box.pack(fill="x", pady=(0, 20))
        
        ctk.CTkButton(self.sources_frame, text="Add Flathub Repository", command=self.add_flathub).pack(anchor="w")
        
        self.refresh_sources()

    def switch_tab(self, tab_name):
        self.discover_frame.pack_forget()
        self.sources_frame.pack_forget()
        
        if tab_name == "discover":
            self.discover_frame.pack(fill="both", expand=True)
        elif tab_name == "sources":
            self.sources_frame.pack(fill="both", expand=True)
            self.refresh_sources()

    def perform_search(self, event=None):
        query = self.search_entry.get().strip()
        if not query: return
        
        # Clear old results
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self.results_scroll, text="Searching...", font=("Inter", 14)).pack(pady=20)
        threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()

    def _search_thread(self, query):
        results = []
        
        # Search Pacman (Native KDE/Arch apps)
        try:
            pacman_out = subprocess.getoutput(f"pacman -Ss {query}").split('\n')
            for i in range(0, len(pacman_out)-1, 2):
                if pacman_out[i].strip():
                    name = pacman_out[i].split('/')[1].split(' ')[0]
                    desc = pacman_out[i+1].strip()
                    results.append({"name": name, "desc": desc, "source": "Pacman", "cmd": f"pkexec pacman -S --noconfirm {name}"})
        except: pass
        
        # Search Flatpak
        try:
            flatpak_out = subprocess.getoutput(f"flatpak search {query}").split('\n')[1:] # Skip header
            for line in flatpak_out:
                parts = line.split('\t')
                if len(parts) >= 3:
                    results.append({"name": parts[0].strip(), "desc": parts[1].strip(), "source": "Flathub", "cmd": f"flatpak install -y flathub {parts[2].strip()}"})
        except: pass
        
        self.after(0, self.display_results, results)

    def display_results(self, results):
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
            
        if not results:
            ctk.CTkLabel(self.results_scroll, text="No results found.", font=("Inter", 14)).pack(pady=20)
            return
            
        for app in results:
            card = ctk.CTkFrame(self.results_scroll, fg_color="#2a2a2a", corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)
            
            info_box = ctk.CTkFrame(card, fg_color="transparent")
            info_box.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            
            ctk.CTkLabel(info_box, text=app["name"], font=("Inter", 16, "bold")).pack(anchor="w")
            ctk.CTkLabel(info_box, text=app["desc"], font=("Inter", 12), text_color="gray", wraplength=600, justify="left").pack(anchor="w", pady=(5,0))
            
            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.pack(side="right", padx=15, pady=15)
            
            ctk.CTkLabel(btn_box, text=app["source"], font=("Inter", 10), text_color="#0a84ff").pack(pady=(0, 5))
            ctk.CTkButton(btn_box, text="Install", width=80, command=lambda c=app["cmd"]: self.install_app(c)).pack()

    def install_app(self, cmd):
        # In a real app, this would show a progress bar. For now, we spawn a terminal to show the install process.
        subprocess.Popen(f"kitty -e bash -c '{cmd}; echo Press Enter to close...; read'", shell=True)

    def refresh_sources(self):
        self.remotes_box.delete("1.0", "end")
        try:
            remotes = subprocess.getoutput("flatpak remotes")
            self.remotes_box.insert("end", remotes if remotes else "No Flatpak remotes configured.")
        except:
            self.remotes_box.insert("end", "Flatpak is not installed or accessible.")

    def add_flathub(self):
        subprocess.run("flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo", shell=True)
        self.refresh_sources()

if __name__ == "__main__":
    app = AppStore()
    app.mainloop()
