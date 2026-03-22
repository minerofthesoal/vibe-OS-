import gi
import os
import subprocess

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell

class ArchForgeControlCenter(Gtk.Window):
    def __init__(self):
        super().__init__(title="archforge-control-center")
        
        # Set up Layer Shell for Wayland
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_namespace(self, "archforge-control-center")
        
        # Anchor to the top right (macOS style)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 15)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 15)
        
        # Close on focus loss (click outside)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        self.connect("focus-out-event", self.on_focus_out)
        
        # Main Container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.main_box.get_style_context().add_class("cc-container")
        self.add(self.main_box)
        
        self.build_ui()
        
    def build_ui(self):
        # Top Grid: Wi-Fi and Bluetooth Toggles
        grid = Gtk.Grid(column_spacing=15, row_spacing=15)
        grid.set_halign(Gtk.Align.CENTER)
        
        # Get actual system states
        wifi_active = "enabled" in subprocess.getoutput("nmcli radio wifi")
        bt_active = "yes" in subprocess.getoutput("bluetoothctl show | grep Powered")
        
        self.wifi_btn, self.wifi_box = self.create_toggle_button("network-wireless", "Wi-Fi", wifi_active, self.toggle_wifi)
        self.bt_btn, self.bt_box = self.create_toggle_button("bluetooth", "Bluetooth", bt_active, self.toggle_bt)
        
        grid.attach(self.wifi_btn, 0, 0, 1, 1)
        grid.attach(self.bt_btn, 1, 0, 1, 1)
        self.main_box.pack_start(grid, False, False, 0)
        
        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_box.pack_start(sep, False, False, 0)
        
        # Get actual volume and brightness
        try:
            vol_str = subprocess.getoutput("wpctl get-volume @DEFAULT_AUDIO_SINK@").split()[1]
            vol_val = int(float(vol_str) * 100)
        except:
            vol_val = 50
            
        try:
            bright_str = subprocess.getoutput("brightnessctl -m").split(',')[3].replace('%','')
            bright_val = int(bright_str)
        except:
            bright_val = 100

        # Sliders: Brightness and Volume
        self.main_box.pack_start(self.create_slider("display-brightness", bright_val, self.set_brightness), False, False, 0)
        self.main_box.pack_start(self.create_slider("audio-volume-high", vol_val, self.set_volume), False, False, 0)

    def create_toggle_button(self, icon_name, label_text, is_active, callback):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.get_style_context().add_class("cc-toggle-box")
        if is_active:
            box.get_style_context().add_class("cc-toggle-active")
            
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DND)
        label = Gtk.Label(label=label_text)
        label.get_style_context().add_class("cc-label")
        
        box.pack_start(icon, False, False, 10)
        box.pack_start(label, False, False, 10)
        
        # Make it clickable
        event_box = Gtk.EventBox()
        event_box.add(box)
        event_box.connect("button-press-event", callback, box)
        return event_box, box

    def create_slider(self, icon_name, default_val, callback):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.get_style_context().add_class("cc-slider-box")
        
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        scale.set_value(default_val)
        scale.set_draw_value(False)
        scale.set_hexpand(True)
        scale.connect("value-changed", callback)
        
        box.pack_start(icon, False, False, 10)
        box.pack_start(scale, True, True, 10)
        return box

    # --- System Integrations ---
    def toggle_wifi(self, widget, event, box):
        current = "enabled" in subprocess.getoutput("nmcli radio wifi")
        new_state = "off" if current else "on"
        subprocess.run(f"nmcli radio wifi {new_state}", shell=True)
        
        if current:
            box.get_style_context().remove_class("cc-toggle-active")
        else:
            box.get_style_context().add_class("cc-toggle-active")

    def toggle_bt(self, widget, event, box):
        current = "yes" in subprocess.getoutput("bluetoothctl show | grep Powered")
        new_state = "off" if current else "on"
        subprocess.run(f"bluetoothctl power {new_state}", shell=True)
        
        if current:
            box.get_style_context().remove_class("cc-toggle-active")
        else:
            box.get_style_context().add_class("cc-toggle-active")

    def set_brightness(self, scale):
        val = int(scale.get_value())
        subprocess.run(f"brightnessctl s {val}%", shell=True)

    def set_volume(self, scale):
        val = scale.get_value()
        subprocess.run(f"wpctl set-volume @DEFAULT_AUDIO_SINK@ {val/100:.2f}", shell=True)

    def on_focus_out(self, widget, event):
        Gtk.main_quit()

def apply_css():
    css = b"""
    .cc-container {
        background-color: rgba(20, 20, 20, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 20px;
        min-width: 300px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .cc-toggle-box {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 15px;
        min-width: 130px;
        transition: all 0.2s ease;
    }
    .cc-toggle-box:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    .cc-toggle-active {
        background-color: rgba(10, 132, 255, 0.8); /* macOS Blue */
        color: white;
    }
    .cc-label {
        font-family: "Inter";
        font-weight: bold;
    }
    .cc-slider-box {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 10px 15px;
    }
    scale trough {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        min-height: 8px;
    }
    scale highlight {
        background-color: rgba(10, 132, 255, 0.8);
        border-radius: 10px;
    }
    scale slider {
        background-color: #ffffff;
        min-width: 16px;
        min-height: 16px;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
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
    cc = ArchForgeControlCenter()
    cc.show_all()
    Gtk.main()
