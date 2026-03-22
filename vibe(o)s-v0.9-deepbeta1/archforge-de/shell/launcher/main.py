import gi
import os
import subprocess
import configparser

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, Pango

class ArchForgeLauncher(Gtk.Window):
    def __init__(self):
        super().__init__(title="archforge-launcher")
        
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_namespace(self, "archforge-launcher")
        
        # Center on screen (Spotlight style)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, False)
        
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        self.connect("focus-out-event", lambda w, e: Gtk.main_quit())
        self.connect("key-press-event", self.on_key_press)
        
        self.apps = self.load_desktop_entries()
        
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.get_style_context().add_class("launcher-container")
        self.add(self.main_box)
        
        # Search Entry
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        search_box.get_style_context().add_class("search-box")
        
        search_icon = Gtk.Image.new_from_icon_name("system-search-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Search for apps, files, or settings...")
        self.entry.get_style_context().add_class("search-entry")
        self.entry.set_hexpand(True)
        self.entry.connect("changed", self.on_search_changed)
        self.entry.connect("activate", self.on_search_enter)
        
        search_box.pack_start(search_icon, False, False, 10)
        search_box.pack_start(self.entry, True, True, 10)
        self.main_box.pack_start(search_box, False, False, 0)
        
        # Results List
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled.set_min_content_height(350)
        
        self.listbox = Gtk.ListBox()
        self.listbox.get_style_context().add_class("results-list")
        self.listbox.connect("row-activated", self.on_row_activated)
        self.scrolled.add(self.listbox)
        self.main_box.pack_start(self.scrolled, True, True, 0)
        
        self.populate_results("")

    def load_desktop_entries(self):
        apps = []
        app_dirs = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
        for d in app_dirs:
            if not os.path.exists(d): continue
            for f in os.listdir(d):
                if f.endswith(".desktop"):
                    try:
                        config = configparser.ConfigParser(interpolation=None)
                        config.read(os.path.join(d, f))
                        if "Desktop Entry" in config:
                            entry = config["Desktop Entry"]
                            if entry.get("NoDisplay", "false").lower() == "true": continue
                            apps.append({
                                "name": entry.get("Name", f),
                                "exec": entry.get("Exec", "").split(" %")[0],
                                "icon": entry.get("Icon", "application-x-executable")
                            })
                    except: pass
        return sorted(apps, key=lambda x: x["name"])

    def populate_results(self, query):
        for child in self.listbox.get_children():
            self.listbox.remove(child)
            
        query = query.lower()
        count = 0
        for app in self.apps:
            if query in app["name"].lower() or query in app["exec"].lower():
                row = Gtk.ListBoxRow()
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
                box.get_style_context().add_class("result-row")
                
                icon = Gtk.Image.new_from_icon_name(app["icon"], Gtk.IconSize.DND)
                icon.set_pixel_size(32)
                lbl = Gtk.Label(label=app["name"])
                lbl.set_halign(Gtk.Align.START)
                
                box.pack_start(icon, False, False, 10)
                box.pack_start(lbl, True, True, 0)
                row.add(box)
                row.app_cmd = app["exec"]
                self.listbox.add(row)
                count += 1
                if count > 8: break # Limit results for performance/UI
                
        self.listbox.show_all()
        if count > 0:
            self.listbox.select_row(self.listbox.get_row_at_index(0))

    def on_search_changed(self, entry):
        self.populate_results(entry.get_text())

    def on_search_enter(self, entry):
        selected = self.listbox.get_selected_row()
        if selected:
            self.launch_app(selected.app_cmd)

    def on_row_activated(self, listbox, row):
        self.launch_app(row.app_cmd)

    def launch_app(self, cmd):
        subprocess.Popen(cmd, shell=True)
        Gtk.main_quit()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        elif event.keyval == Gdk.KEY_Down:
            # Move selection down
            pass # GtkListBox handles basic arrow keys if focused, but we might need to pass focus
        return False

def apply_css():
    css = b"""
    .launcher-container {
        background-color: rgba(30, 30, 30, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        min-width: 600px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .search-box {
        padding: 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .search-entry {
        background: transparent;
        border: none;
        box-shadow: none;
        color: white;
        font-size: 20px;
        font-family: "Inter";
    }
    .search-entry:focus {
        border: none;
        box-shadow: none;
    }
    .results-list {
        background: transparent;
        padding: 10px;
    }
    .result-row {
        padding: 8px;
        border-radius: 8px;
    }
    row:selected .result-row {
        background-color: rgba(10, 132, 255, 0.8);
        color: white;
    }
    """
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), 
        provider, 
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

if __name__ == "__main__":
    apply_css()
    win = ArchForgeLauncher()
    win.show_all()
    Gtk.main()
