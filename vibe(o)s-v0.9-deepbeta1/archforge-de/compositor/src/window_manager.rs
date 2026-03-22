use smithay::utils::{Logical, Point, Rectangle, Size};
use smithay::wayland::shell::xdg::ToplevelSurface;
use std::collections::HashMap;

use crate::animations::{AnimationState, SpringAnimator};

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum LayoutMode {
    /// macOS-style free-floating windows
    Floating,
    /// ReviOS/Windows PowerToys style dynamic grid/stack tiling
    TilingMasterStack,
    TilingGrid,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SnapEdge {
    None,
    Left,
    Right,
    Top,
    Bottom,
    TopLeft,
    TopRight,
    BottomLeft,
    BottomRight,
    Maximize,
}

/// Represents a window in the ArchForge compositor
pub struct ArchWindow {
    pub id: u32,
    pub title: String,
    pub is_mapped: bool,
    pub surface: Option<ToplevelSurface>,
    
    // The actual physical geometry on screen
    pub current_geometry: Rectangle<i32, Logical>,
    // The target geometry (used for fluid spring animations)
    pub target_geometry: Rectangle<i32, Logical>,
    
    pub animator: SpringAnimator,
    pub is_focused: bool,
    pub is_floating_override: bool, // E.g., dialog boxes in a tiling layout
}

impl ArchWindow {
    pub fn new(id: u32, title: String, initial_rect: Rectangle<i32, Logical>) -> Self {
        Self {
            id,
            title,
            is_mapped: true,
            surface: None,
            current_geometry: initial_rect,
            target_geometry: initial_rect,
            animator: SpringAnimator::new(0.85, 0.15), // Exaggerated macOS-like bouncy spring
            is_focused: false,
            is_floating_override: false,
        }
    }

    /// Advances the window's animation state towards its target geometry
    pub fn update_animation(&mut self, dt: f64) {
        let (new_x, new_y) = self.animator.update_position(
            (self.current_geometry.loc.x as f64, self.current_geometry.loc.y as f64),
            (self.target_geometry.loc.x as f64, self.target_geometry.loc.y as f64),
            dt
        );
        let (new_w, new_h) = self.animator.update_size(
            (self.current_geometry.size.w as f64, self.current_geometry.size.h as f64),
            (self.target_geometry.size.w as f64, self.target_geometry.size.h as f64),
            dt
        );

        self.current_geometry.loc.x = new_x.round() as i32;
        self.current_geometry.loc.y = new_y.round() as i32;
        self.current_geometry.size.w = new_w.round() as i32;
        self.current_geometry.size.h = new_h.round() as i32;
    }
}

pub struct Workspace {
    pub id: u32,
    pub layout_mode: LayoutMode,
    pub windows: Vec<u32>, // IDs of windows in this workspace
    pub screen_bounds: Rectangle<i32, Logical>,
    pub gaps: i32,
}

impl Workspace {
    pub fn new(id: u32, bounds: Rectangle<i32, Logical>) -> Self {
        Self {
            id,
            layout_mode: LayoutMode::Floating, // Default to macOS style
            windows: Vec::new(),
            screen_bounds: bounds,
            gaps: 12, // ArchForge default aesthetic gap
        }
    }
}

pub struct WindowManager {
    pub windows: HashMap<u32, ArchWindow>,
    pub workspaces: HashMap<u32, Workspace>,
    pub active_workspace: u32,
    next_window_id: u32,
}

impl WindowManager {
    pub fn new(initial_bounds: Rectangle<i32, Logical>) -> Self {
        let mut workspaces = HashMap::new();
        workspaces.insert(1, Workspace::new(1, initial_bounds));

        Self {
            windows: HashMap::new(),
            workspaces,
            active_workspace: 1,
            next_window_id: 1,
        }
    }

    pub fn set_layout_mode(&mut self, mode: LayoutMode) {
        if let Some(ws) = self.workspaces.get_mut(&self.active_workspace) {
            ws.layout_mode = mode;
        }
        self.apply_layout();
    }

    pub fn add_window(&mut self, title: String, surface: Option<ToplevelSurface>) -> u32 {
        let id = self.next_window_id;
        self.next_window_id += 1;

        // Default spawn at center
        let bounds = self.workspaces.get(&self.active_workspace).unwrap().screen_bounds;
        let w = 800;
        let h = 600;
        let x = bounds.loc.x + (bounds.size.w - w) / 2;
        let y = bounds.loc.y + (bounds.size.h - h) / 2;

        let rect = Rectangle::from_loc_and_size((x, y), (w, h));
        let mut window = ArchWindow::new(id, title, rect);
        window.surface = surface;
        
        // Spawn animation: start small and scale up
        window.current_geometry.size = Size::from((w / 2, h / 2));
        window.current_geometry.loc = Point::from((x + w / 4, y + h / 4));

        self.windows.insert(id, window);
        
        if let Some(ws) = self.workspaces.get_mut(&self.active_workspace) {
            ws.windows.push(id);
        }

        self.apply_layout();
        id
    }

    pub fn remove_window(&mut self, id: u32) {
        self.windows.remove(&id);
        for ws in self.workspaces.values_mut() {
            ws.windows.retain(|&w| w != id);
        }
        self.apply_layout();
    }

    /// Handles floating window movement with macOS-like fluidity
    pub fn move_window_floating(&mut self, id: u32, dx: i32, dy: i32) {
        if let Some(window) = self.windows.get_mut(&id) {
            window.target_geometry.loc.x += dx;
            window.target_geometry.loc.y += dy;
            // Instantly update current to avoid lag during drag, spring handles release
            window.current_geometry.loc = window.target_geometry.loc; 
        }
    }

    /// Handles Aero-style edge snapping
    pub fn snap_window(&mut self, id: u32, edge: SnapEdge) {
        let bounds = self.workspaces.get(&self.active_workspace).unwrap().screen_bounds;
        let gaps = self.workspaces.get(&self.active_workspace).unwrap().gaps;
        
        if let Some(window) = self.windows.get_mut(&id) {
            let target = match edge {
                SnapEdge::Left => Rectangle::from_loc_and_size(
                    (bounds.loc.x + gaps, bounds.loc.y + gaps),
                    (bounds.size.w / 2 - gaps * 2, bounds.size.h - gaps * 2)
                ),
                SnapEdge::Right => Rectangle::from_loc_and_size(
                    (bounds.loc.x + bounds.size.w / 2 + gaps, bounds.loc.y + gaps),
                    (bounds.size.w / 2 - gaps * 2, bounds.size.h - gaps * 2)
                ),
                SnapEdge::Maximize => Rectangle::from_loc_and_size(
                    (bounds.loc.x + gaps, bounds.loc.y + gaps),
                    (bounds.size.w - gaps * 2, bounds.size.h - gaps * 2)
                ),
                _ => window.target_geometry, // Unhandled for brevity
            };
            
            // Set target, let the SpringAnimator smoothly transition the window
            window.target_geometry = target;
        }
    }

    /// Applies the current workspace's layout engine (Tiling or Floating)
    pub fn apply_layout(&mut self) {
        let ws = self.workspaces.get(&self.active_workspace).unwrap();
        let bounds = ws.screen_bounds;
        let gaps = ws.gaps;
        let window_ids = ws.windows.clone();

        match ws.layout_mode {
            LayoutMode::Floating => {
                // In floating mode, we do nothing automatically unless windows are off-screen
            },
            LayoutMode::TilingMasterStack => {
                let count = window_ids.len() as i32;
                if count == 0 { return; }

                if count == 1 {
                    // Single window takes full screen (minus gaps)
                    if let Some(win) = self.windows.get_mut(&window_ids[0]) {
                        if !win.is_floating_override {
                            win.target_geometry = Rectangle::from_loc_and_size(
                                (bounds.loc.x + gaps, bounds.loc.y + gaps),
                                (bounds.size.w - gaps * 2, bounds.size.h - gaps * 2)
                            );
                        }
                    }
                } else {
                    // Master window on left, stack on right
                    let master_w = bounds.size.w / 2;
                    if let Some(master) = self.windows.get_mut(&window_ids[0]) {
                        if !master.is_floating_override {
                            master.target_geometry = Rectangle::from_loc_and_size(
                                (bounds.loc.x + gaps, bounds.loc.y + gaps),
                                (master_w - gaps * 2, bounds.size.h - gaps * 2)
                            );
                        }
                    }

                    let stack_count = count - 1;
                    let stack_h = bounds.size.h / stack_count;
                    
                    for (i, &id) in window_ids.iter().skip(1).enumerate() {
                        if let Some(win) = self.windows.get_mut(&id) {
                            if !win.is_floating_override {
                                win.target_geometry = Rectangle::from_loc_and_size(
                                    (bounds.loc.x + master_w + gaps, bounds.loc.y + (i as i32 * stack_h) + gaps),
                                    (bounds.size.w - master_w - gaps * 2, stack_h - gaps * 2)
                                );
                            }
                        }
                    }
                }
            },
            LayoutMode::TilingGrid => {
                // Grid implementation omitted for brevity, but follows similar math
            }
        }
    }

    /// Called every frame by the compositor render loop
    pub fn tick_animations(&mut self, dt: f64) {
        for window in self.windows.values_mut() {
            window.update_animation(dt);
        }
    }
}
