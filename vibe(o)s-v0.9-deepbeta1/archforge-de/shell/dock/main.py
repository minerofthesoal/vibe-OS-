import gi
import os
import subprocess

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell

class ArchForgeDock(Gtk.Window):
    def __init__(self):
        super().__init__(title="archforge-dock")
        
        # Set up Layer Shell for Wayland
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_namespace(self, "archforge-dock") # Used by compositor for blur rules
        
        # Anchor to the bottom center (macOS / Win11 style)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, False)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 15)
        
        # Main Container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.main_box.get_style_context().add_class("dock-container")
        self.add(self.main_box)
        
        # Define Pinned Apps
        self.pinned_apps = [
            {"name": "Firefox", "icon": "firefox", "cmd": "firefox"},
            {"name": "Files", "icon": "system-file-manager", "cmd": "thunar"},
            {"name": "Terminal", "icon": "utilities-terminal", "cmd": "kitty"},
            {"name": "AI Assistant", "icon": "system-search", "cmd": "python3 /opt/archforge/archforge-de/ai/app.py"},
            {"name": "Settings", "icon": "preferences-system", "cmd": "python3 /opt/archforge/archforge-de/shell/control-center/main.py"}
        ]
        
        # Mock running apps state (In a real wlroots compositor, we listen to wlr-foreign-toplevel-management)
        self.running_apps = ["Firefox", "Terminal"]
        
        self.populate_dock()
        
    def populate_dock(self):
        for app in self.pinned_apps:
            app_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            app_box.get_style_context().add_class("app-box")
            
            # Application Icon Button
            btn = Gtk.Button()
            btn.get_style_context().add_class("dock-icon-btn")
            icon = Gtk.Image.new_from_icon_name(app["icon"], Gtk.IconSize.DIALOG)
            icon.set_pixel_size(48)
            btn.add(icon)
            
            # Launch command on click
            btn.connect("clicked", self.launch_app, app["cmd"])
            app_box.pack_start(btn, False, False, 0)
            
            # Running Indicator (The little dot below the icon, macOS/Win11 style)
            indicator = Gtk.Box()
            indicator.set_size_request(4, 4)
            indicator.set_halign(Gtk.Align.CENTER)
            if app["name"] in self.running_apps:
                indicator.get_style_context().add_class("running-indicator-active")
            else:
                indicator.get_style_context().add_class("running-indicator-inactive")
                
            app_box.pack_start(indicator, False, False, 0)
            self.main_box.pack_start(app_box, False, False, 0)

    def launch_app(self, widget, cmd):
        subprocess.Popen(cmd, shell=True)

def apply_css():
    css = b"""
    .dock-container {
        /* Subtle blur transparency matching the compositor */
        background-color: rgba(20, 20, 20, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 8px 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .app-box {
        margin: 0 4px;
    }
    .dock-icon-btn {
        background: transparent;
        border: none;
        border-radius: 12px;
        padding: 8px;
        transition: all 0.2s ease-in-out;
    }
    .dock-icon-btn:hover {
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    .running-indicator-active {
        background-color: #ffffff;
        border-radius: 50%;
        margin-top: 2px;
        box-shadow: 0 0 4px rgba(255, 255, 255, 0.8);
    }
    .running-indicator-inactive {
        background-color: transparent;
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
    dock = ArchForgeDock()
    dock.show_all()
    Gtk.main()
