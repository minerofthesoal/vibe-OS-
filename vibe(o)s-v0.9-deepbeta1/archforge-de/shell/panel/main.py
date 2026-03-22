import gi
import os
import time
import subprocess

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GLib

class VibePanel(Gtk.Window):
    def __init__(self):
        super().__init__(title="vibe-panel")
        
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_namespace(self, "vibe-panel")
        
        # Anchor to top, full width
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_exclusive_zone(self, 32)
        
        self.set_size_request(-1, 32)
        
        # Main Layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_box.get_style_context().add_class("panel-container")
        self.add(self.main_box)
        
        # Left: Logo (Clickable for About) & Workspaces
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        logo_btn = Gtk.Button()
        logo_btn.get_style_context().add_class("panel-btn")
        logo_icon = Gtk.Image.new_from_icon_name("start-here-archlinux", Gtk.IconSize.MENU)
        logo_btn.add(logo_icon)
        logo_btn.connect("clicked", lambda w: subprocess.Popen("python3 /opt/archforge/archforge-de/shell/about/main.py", shell=True))
        left_box.pack_start(logo_btn, False, False, 5)
        
        # Task View / Workspace Button
        workspace_btn = Gtk.Button(label="Workspaces")
        workspace_btn.get_style_context().add_class("panel-btn")
        workspace_btn.get_style_context().add_class("panel-text")
        workspace_btn.connect("clicked", lambda w: subprocess.Popen("python3 /opt/archforge/archforge-de/shell/taskview/main.py", shell=True))
        left_box.pack_start(workspace_btn, False, False, 0)
        
        # Center: Clock
        center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.clock_lbl = Gtk.Label()
        self.clock_lbl.get_style_context().add_class("panel-clock")
        center_box.pack_start(self.clock_lbl, True, True, 0)
        
        # Right: SysTray & Control Center Toggle
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.tray_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.tray_box.get_style_context().add_class("tray-box")
        
        for icon_name in ["network-wireless-symbolic", "bluetooth-active-symbolic", "audio-volume-high-symbolic", "battery-good-symbolic"]:
            img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            self.tray_box.pack_start(img, False, False, 0)
            
        right_box.pack_start(self.tray_box, False, False, 5)
        
        cc_btn = Gtk.Button()
        cc_btn.get_style_context().add_class("panel-btn")
        cc_icon = Gtk.Image.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.MENU)
        cc_btn.add(cc_icon)
        cc_btn.connect("clicked", lambda w: subprocess.Popen("python3 /opt/archforge/archforge-de/shell/control-center/main.py", shell=True))
        
        right_box.pack_end(cc_btn, False, False, 10)
        
        self.main_box.pack_start(left_box, False, False, 0)
        self.main_box.set_center_widget(center_box)
        self.main_box.pack_end(right_box, False, False, 0)
        
        self.update_clock()
        GLib.timeout_add_seconds(1, self.update_clock)

    def update_clock(self):
        current_time = time.strftime("%a %b %d  %H:%M")
        self.clock_lbl.set_text(current_time)
        return True

def apply_css():
    css = b"""
    .panel-container {
        background-color: rgba(20, 20, 20, 0.85);
        color: white;
        font-family: "Inter";
        font-size: 13px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .panel-text {
        font-weight: 500;
    }
    .panel-clock {
        font-weight: 600;
    }
    .panel-btn {
        background: transparent;
        border: none;
        padding: 4px 10px;
        border-radius: 6px;
        color: white;
        transition: all 0.2s ease;
    }
    .panel-btn:hover {
        background: rgba(255, 255, 255, 0.15);
    }
    .tray-box {
        padding: 0 10px;
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
    panel = VibePanel()
    panel.show_all()
    Gtk.main()
