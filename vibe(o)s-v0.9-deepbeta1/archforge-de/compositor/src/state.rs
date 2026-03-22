use smithay::reexports::wayland_server::DisplayHandle;
use smithay::utils::{Logical, Rectangle, Point};
use smithay::wayland::shell::xdg::{XdgShellState, XdgShellHandler, ToplevelSurface, PopupSurface, PositionerState};
use smithay::wayland::compositor::{CompositorState, CompositorHandler, CompositorClientState};
use smithay::wayland::seat::{SeatState, Seat, SeatHandler, PointerHandle, KeyboardHandle, TouchHandle};
use smithay::{delegate_xdg_shell, delegate_compositor, delegate_seat};
use smithay::reexports::wayland_server::protocol::wl_surface::WlSurface;
use smithay::reexports::wayland_server::protocol::wl_buffer::WlBuffer;
use smithay::reexports::wayland_protocols::xdg::shell::server::xdg_toplevel::XdgToplevel;
use smithay::reexports::wayland_server::Client;
use crate::window_manager::WindowManager;
use std::time::Instant;

pub struct ArchForgeState {
    pub window_manager: WindowManager,
    pub xdg_shell_state: XdgShellState,
    pub compositor_state: CompositorState,
    pub seat_state: SeatState<Self>,
    pub seat: Seat<Self>,
    pub pointer: PointerHandle<Self>,
    pub keyboard: KeyboardHandle<Self>,
    pub touch: TouchHandle<Self>,
    pub pointer_location: Point<f64, Logical>,
    pub last_input_time: Instant,
    pub display_active: bool,
}

impl ArchForgeState {
    pub fn new(display_handle: &DisplayHandle) -> Self {
        // Assume a 1080p screen for the initial bounds
        let initial_bounds = Rectangle::from_loc_and_size((0, 0), (1920, 1080));
        
        let mut seat_state = SeatState::new();
        let mut seat = seat_state.new_wl_seat(display_handle, "seat0");
        let pointer = seat.add_pointer();
        let keyboard = seat.add_keyboard(Default::default(), 200, 25).unwrap();
        let touch = seat.add_touch();
        
        Self {
            window_manager: WindowManager::new(initial_bounds),
            xdg_shell_state: XdgShellState::new::<Self>(display_handle),
            compositor_state: CompositorState::new::<Self>(display_handle),
            seat_state,
            seat,
            pointer,
            keyboard,
            touch,
            pointer_location: Point::from((0.0, 0.0)),
            last_input_time: Instant::now(),
            display_active: true,
        }
    }

    pub fn reset_idle_timer(&mut self) {
        self.last_input_time = Instant::now();
        if !self.display_active {
            self.display_active = true;
            tracing::info!("DPMS: Display waking up due to user input.");
            crate::backend::set_dpms_state(true);
        }
    }

    pub fn check_dpms(&mut self) {
        let idle_timeout = std::time::Duration::from_secs(300); // 5 minutes
        if self.display_active && self.last_input_time.elapsed() > idle_timeout {
            self.display_active = false;
            tracing::info!("DPMS: Display suspending due to inactivity.");
            crate::backend::set_dpms_state(false);
        }
    }

    pub fn surface_under(&self) -> Option<(WlSurface, Point<i32, Logical>)> {
        let pos = self.pointer_location;
        let pos_i32 = Point::from((pos.x as i32, pos.y as i32));

        for window in self.window_manager.windows.values() {
            if window.current_geometry.contains(pos_i32) {
                if let Some(toplevel) = &window.surface {
                    let surface = toplevel.wl_surface().clone();
                    let offset = Point::from((
                        pos_i32.x - window.current_geometry.loc.x,
                        pos_i32.y - window.current_geometry.loc.y,
                    ));
                    return Some((surface, offset));
                }
            }
        }
        None
    }
}

use smithay::reexports::wayland_server::backend::ClientData;
use smithay::reexports::wayland_server::backend::ClientId;

pub struct ClientState {
    pub compositor_state: CompositorClientState,
}

impl ClientData for ClientState {
    fn initialized(&self, _client_id: ClientId) {}
    fn disconnected(&self, _client_id: ClientId, _reason: smithay::reexports::wayland_server::backend::DisconnectReason) {}
}

impl CompositorHandler for ArchForgeState {
    fn compositor_state(&mut self) -> &mut CompositorState {
        &mut self.compositor_state
    }

    fn client_compositor_state<'a>(&self, client: &'a Client) -> &'a CompositorClientState {
        &client.get_data::<ClientState>().unwrap().compositor_state
    }

    fn commit(&mut self, _surface: &WlSurface) {
        // Handle surface commit
    }
}

delegate_compositor!(ArchForgeState);

impl SeatHandler for ArchForgeState {
    type KeyboardFocus = WlSurface;
    type PointerFocus = WlSurface;
    type TouchFocus = WlSurface;

    fn seat_state(&mut self) -> &mut SeatState<Self> {
        &mut self.seat_state
    }

    fn focus_changed(&mut self, _seat: &Seat<Self>, focused: Option<&WlSurface>) {
        let mut focused_id = None;

        for (id, window) in self.window_manager.windows.iter_mut() {
            let is_match = match (&window.surface, focused) {
                (Some(toplevel), Some(focused_surface)) => {
                    toplevel.wl_surface() == focused_surface
                },
                _ => false,
            };

            if is_match {
                if !window.is_focused {
                    window.is_focused = true;
                    focused_id = Some(*id);
                    if let Some(toplevel) = &window.surface {
                        toplevel.with_pending_state(|state| {
                            state.states.set(smithay::reexports::wayland_protocols::xdg::shell::server::xdg_toplevel::State::Activated);
                        });
                        toplevel.send_configure();
                    }
                } else {
                    focused_id = Some(*id);
                }
            } else if window.is_focused {
                window.is_focused = false;
                if let Some(toplevel) = &window.surface {
                    toplevel.with_pending_state(|state| {
                        state.states.unset(smithay::reexports::wayland_protocols::xdg::shell::server::xdg_toplevel::State::Activated);
                    });
                    toplevel.send_configure();
                }
            }
        }

        if let Some(id) = focused_id {
            tracing::info!("Focus changed to window ID: {}", id);
        } else if focused.is_none() {
            tracing::info!("Focus cleared from all windows");
        }
    }
    fn cursor_image(&mut self, _seat: &Seat<Self>, _image: smithay::wayland::seat::CursorImageStatus) {
        // Handle cursor image changes
    }
}

delegate_seat!(ArchForgeState);

impl XdgShellHandler for ArchForgeState {
    fn xdg_shell_state(&mut self) -> &mut XdgShellState {
        &mut self.xdg_shell_state
    }

    fn new_toplevel(&mut self, surface: ToplevelSurface) {
        // When a new XDG surface is created, add it to the WindowManager
        // with an initial floating geometry, and its animation will be initiated.
        let title = surface.title().unwrap_or_else(|| "vibe(O)s Window".to_string());
        let id = self.window_manager.add_window(title, Some(surface.clone()));
        
        // We can store the surface in the ArchWindow if we modify WindowManager,
        // but for now, we just notify the window manager to track it.
        tracing::info!("New XDG Toplevel created: ID {}", id);
        
        // Send initial configure event to the client
        surface.with_pending_state(|state| {
            state.states.set(smithay::reexports::wayland_protocols::xdg::shell::server::xdg_toplevel::State::Activated);
        });
        surface.send_configure();
    }

    fn new_popup(&mut self, _surface: PopupSurface, _positioner: PositionerState) {
        // Handle popups (menus, tooltips)
    }

    fn grab(&mut self, _surface: PopupSurface, _seat: smithay::reexports::wayland_protocols::xdg::shell::server::xdg_popup::XdgPopup, _serial: smithay::utils::Serial) {
        // Handle popup grabs
    }
}

delegate_xdg_shell!(ArchForgeState);
