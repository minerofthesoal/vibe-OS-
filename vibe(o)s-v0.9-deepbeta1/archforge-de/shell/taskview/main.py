import gi
import os

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell

class ArchForgeTaskView(Gtk.Window):
    def __init__(self):
        super().__init__(title="archforge-taskview")
        
        # Set up Layer Shell for Wayland
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_namespace(self, "archforge-taskview")
        
        # Cover the entire screen
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        self.connect("key-press-event", self.on_key_press)
        
        # Main Container (Blurred Background)
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.main_box.get_style_context().add_class("taskview-container")
        self.add(self.main_box)
        
        # Title
        title = Gtk.Label(label="Task View")
        title.get_style_context().add_class("taskview-title")
        self.main_box.pack_start(title, False, False, 40)
        
        # Workspaces Grid
        self.grid = Gtk.Grid(column_spacing=30, row_spacing=30)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)
        self.main_box.pack_start(self.grid, True, True, 0)
        
        self.populate_workspaces()
        
    def populate_workspaces(self):
        # Mocking 4 workspaces with open windows
        workspaces = [
            {"id": 1, "name": "Workspace 1", "windows": [("firefox", "Browser"), ("utilities-terminal", "Terminal")]},
            {"id": 2, "name": "Workspace 2", "windows": [("system-file-manager", "Files")]},
            {"id": 3, "name": "Workspace 3", "windows": [("preferences-system", "Settings"), ("system-search", "AI")]},
            {"id": 4, "name": "Workspace 4", "windows": []},
        ]
        
        col = 0
        for ws in workspaces:
            ws_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            ws_box.get_style_context().add_class("workspace-card")
            
            # Workspace Label
            lbl = Gtk.Label(label=ws["name"])
            lbl.get_style_context().add_class("workspace-label")
            ws_box.pack_start(lbl, False, False, 10)
            
            # Windows Preview Area
            preview_box = Gtk.FlowBox()
            preview_box.set_selection_mode(Gtk.SelectionMode.NONE)
            preview_box.set_max_children_per_line(2)
            preview_box.get_style_context().add_class("preview-box")
            
            if not ws["windows"]:
                empty_lbl = Gtk.Label(label="Empty")
                empty_lbl.get_style_context().add_class("empty-label")
                preview_box.add(empty_lbl)
            else:
                for icon_name, win_title in ws["windows"]:
                    win_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                    win_card.get_style_context().add_class("window-card")
                    
                    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
                    icon.set_pixel_size(48)
                    win_lbl = Gtk.Label(label=win_title)
                    
                    win_card.pack_start(icon, True, True, 10)
                    win_card.pack_start(win_lbl, False, False, 5)
                    preview_box.add(win_card)
                    
            ws_box.pack_start(preview_box, True, True, 10)
            
            # Make workspace clickable
            event_box = Gtk.EventBox()
            event_box.add(ws_box)
            event_box.connect("button-press-event", self.switch_to_workspace, ws["id"])
            
            self.grid.attach(event_box, col, 0, 1, 1)
            col += 1

    def switch_to_workspace(self, widget, event, ws_id):
        # In a real compositor, we would send an IPC command to switch workspaces here
        print(f"Switching to Workspace {ws_id}")
        Gtk.main_quit()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        return False

def apply_css():
    css = b"""
    .taskview-container {
        background-color: rgba(10, 10, 10, 0.75); /* Dark translucent background */
    }
    .taskview-title {
        font-family: "Inter";
        font-size: 32px;
        font-weight: bold;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    .workspace-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        min-width: 300px;
        min-height: 250px;
        transition: all 0.2s ease;
    }
    .workspace-card:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: rgba(10, 132, 255, 0.8); /* macOS Blue highlight */
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .workspace-label {
        font-family: "Inter";
        font-size: 18px;
        font-weight: bold;
        color: white;
    }
    .preview-box {
        padding: 10px;
    }
    .window-card {
        background-color: rgba(0, 0, 0, 0.4);
        border-radius: 12px;
        padding: 10px;
        min-width: 100px;
        min-height: 100px;
    }
    .empty-label {
        color: rgba(255, 255, 255, 0.3);
        font-family: "Inter";
        font-size: 16px;
        margin-top: 50px;
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
    tv = ArchForgeTaskView()
    tv.show_all()
    Gtk.main()
