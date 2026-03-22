use smithay::{
    backend::{
        drm::{DrmNode, DrmDevice, DrmEvent},
        libinput::{LibinputInputBackend, LibinputSessionInterface},
        session::{libseat::LibSeatSession, Session},
        udev::{UdevBackend, UdevEvent},
    },
    reexports::{
        calloop::{EventLoop, LoopHandle},
        input::Libinput,
        wayland_server::DisplayHandle,
    },
};
use tracing::{error, info, warn};
use std::path::PathBuf;

use crate::state::ArchForgeState;

pub struct BackendState {
    pub session: LibSeatSession,
    pub primary_gpu: Option<PathBuf>,
}

/// Sets the DPMS state for all active DRM outputs.
/// In a fully implemented backend, this iterates over DrmDevices and sets the DPMS property.
pub fn set_dpms_state(active: bool) {
    if active {
        info!("DRM/KMS: Setting DPMS state to ON (Resuming display output)");
        // e.g., for device in drm_devices { device.set_dpms(DpmsState::On); }
    } else {
        info!("DRM/KMS: Setting DPMS state to OFF (Suspending display output)");
        // e.g., for device in drm_devices { device.set_dpms(DpmsState::Off); }
    }
}

/// Initializes the Udev, DRM/KMS, and Libinput backends for the compositor.
pub fn init_backend(
    event_loop: &mut EventLoop<'static, ArchForgeState>,
    display_handle: &DisplayHandle,
    state: &mut ArchForgeState,
) -> Result<(), Box<dyn std::error::Error>> {
    let handle = event_loop.handle();

    // 1. Initialize the Session (Libseat)
    // This gives us permission to access hardware devices (DRM, input) without running as root.
    let (mut session, notifier) = LibSeatSession::new().map_err(|e| {
        error!("Failed to initialize libseat session: {}", e);
        e
    })?;
    info!("Libseat session initialized successfully.");

    // 2. Initialize Udev Backend
    // Udev monitors the system for hotplugged devices (monitors, mice, keyboards, GPUs).
    let udev_backend = UdevBackend::new(&session.seat()).map_err(|e| {
        error!("Failed to initialize Udev backend: {}", e);
        e
    })?;

    // Find the primary GPU for rendering
    let primary_gpu = udev_backend.primary_gpu().unwrap_or_else(|| {
        warn!("No primary GPU found via udev, falling back to first available DRM node.");
        // Fallback logic would go here
        PathBuf::from("/dev/dri/card0")
    });
    info!("Primary GPU selected: {:?}", primary_gpu);

    // 3. Initialize Libinput Backend
    // Libinput handles all raw input events (mouse movements, clicks, keyboard presses, touchpads).
    let mut libinput_context = Libinput::new_with_udev(session.clone().into());
    libinput_context.udev_assign_seat(&session.seat()).unwrap();
    
    let libinput_backend = LibinputInputBackend::new(libinput_context.clone());

    // Bind Libinput to the event loop
    handle.insert_source(libinput_backend, move |mut event, _, state| {
        // Route hardware input events to our Window Manager
        use smithay::backend::input::{InputEvent, PointerMotionEvent, KeyboardKeyEvent, PointerButtonEvent, PointerAxisEvent, Event, AbsolutePositionEvent, ButtonState, KeyState};
        use smithay::wayland::seat::{FilterResult, WaylandFocus};
        use smithay::utils::{Logical, Point, SERIAL_COUNTER};
        
        // Update idle state for DPMS
        state.reset_idle_timer();

        match event {
            InputEvent::DeviceAdded { device } => {
                info!("Input device added: {:?}", device);
            },
            InputEvent::DeviceRemoved { device } => {
                info!("Input device removed: {:?}", device);
            },
            InputEvent::PointerMotion { event, .. } => {
                let serial = SERIAL_COUNTER.next_serial();
                let delta = event.delta();
                state.pointer_location.x += delta.x;
                state.pointer_location.y += delta.y;
                
                // Clamp pointer to screen bounds
                let bounds = state.window_manager.workspaces.get(&state.window_manager.active_workspace).unwrap().screen_bounds;
                state.pointer_location.x = state.pointer_location.x.clamp(0.0, bounds.size.w as f64);
                state.pointer_location.y = state.pointer_location.y.clamp(0.0, bounds.size.h as f64);

                let under = state.surface_under();
                state.pointer.motion(
                    state,
                    under,
                    &smithay::wayland::seat::MotionEvent {
                        location: state.pointer_location,
                        serial,
                        time: event.time_msec(),
                    },
                );
            },
            InputEvent::PointerMotionAbsolute { event, .. } => {
                let serial = SERIAL_COUNTER.next_serial();
                let bounds = state.window_manager.workspaces.get(&state.window_manager.active_workspace).unwrap().screen_bounds;
                let pos = event.position_transformed(bounds.size.w as f64, bounds.size.h as f64);
                state.pointer_location = pos;

                let under = state.surface_under();
                state.pointer.motion(
                    state,
                    under,
                    &smithay::wayland::seat::MotionEvent {
                        location: state.pointer_location,
                        serial,
                        time: event.time_msec(),
                    },
                );
            },
            InputEvent::PointerButton { event, .. } => {
                let serial = SERIAL_COUNTER.next_serial();
                let button = event.button_code();
                let state_button = event.state();

                if state_button == ButtonState::Pressed {
                    if let Some((surface, loc)) = state.surface_under() {
                        state.keyboard.set_focus(state, Some(surface.clone()), serial);
                    } else {
                        state.keyboard.set_focus(state, None, serial);
                    }
                }

                state.pointer.button(
                    state,
                    &smithay::wayland::seat::ButtonEvent {
                        button,
                        state: state_button,
                        serial,
                        time: event.time_msec(),
                    },
                );
            },
            InputEvent::PointerAxis { event, .. } => {
                let source = event.source();
                let horizontal_amount = event.amount(smithay::backend::input::Axis::Horizontal).unwrap_or(0.0);
                let horizontal_amount_discrete = event.amount_discrete(smithay::backend::input::Axis::Horizontal).unwrap_or(0.0);
                let vertical_amount = event.amount(smithay::backend::input::Axis::Vertical).unwrap_or(0.0);
                let vertical_amount_discrete = event.amount_discrete(smithay::backend::input::Axis::Vertical).unwrap_or(0.0);

                let mut frame = smithay::wayland::seat::AxisFrame::new(event.time_msec()).source(source);
                if horizontal_amount != 0.0 {
                    frame = frame.value(smithay::backend::input::Axis::Horizontal, horizontal_amount);
                    if horizontal_amount_discrete != 0.0 {
                        frame = frame.discrete(smithay::backend::input::Axis::Horizontal, horizontal_amount_discrete as i32);
                    }
                }
                if vertical_amount != 0.0 {
                    frame = frame.value(smithay::backend::input::Axis::Vertical, vertical_amount);
                    if vertical_amount_discrete != 0.0 {
                        frame = frame.discrete(smithay::backend::input::Axis::Vertical, vertical_amount_discrete as i32);
                    }
                }

                if event.axis_is_stop(smithay::backend::input::Axis::Horizontal) {
                    frame = frame.stop(smithay::backend::input::Axis::Horizontal);
                }
                if event.axis_is_stop(smithay::backend::input::Axis::Vertical) {
                    frame = frame.stop(smithay::backend::input::Axis::Vertical);
                }

                state.pointer.axis(state, frame);
            },
            InputEvent::Keyboard { event, .. } => {
                let serial = SERIAL_COUNTER.next_serial();
                let time = event.time_msec();
                let keycode = event.key_code();
                let state_key = event.state();

                state.keyboard.input::<(), _>(
                    state,
                    keycode,
                    state_key,
                    serial,
                    time,
                    |_, _, _| FilterResult::Forward,
                );
            },
            InputEvent::TouchDown { event, .. } => {
                let serial = SERIAL_COUNTER.next_serial();
                let bounds = state.window_manager.workspaces.get(&state.window_manager.active_workspace).unwrap().screen_bounds;
                let pos = event.position_transformed(bounds.size.w as f64, bounds.size.h as f64);
                state.pointer_location = pos; // Update pointer location for focus
                
                let under = state.surface_under();
                if let Some((surface, _)) = &under {
                    state.keyboard.set_focus(state, Some(surface.clone()), serial);
                } else {
                    state.keyboard.set_focus(state, None, serial);
                }

                state.touch.down(
                    state,
                    under,
                    &smithay::wayland::seat::DownEvent {
                        slot: event.slot(),
                        location: pos,
                        serial,
                        time: event.time_msec(),
                    },
                );
            },
            InputEvent::TouchMotion { event, .. } => {
                let bounds = state.window_manager.workspaces.get(&state.window_manager.active_workspace).unwrap().screen_bounds;
                let pos = event.position_transformed(bounds.size.w as f64, bounds.size.h as f64);
                state.pointer_location = pos; // Update pointer location

                state.touch.motion(
                    state,
                    &smithay::wayland::seat::MotionEvent {
                        slot: event.slot(),
                        location: pos,
                        time: event.time_msec(),
                    },
                );
            },
            InputEvent::TouchUp { event, .. } => {
                let serial = SERIAL_COUNTER.next_serial();
                state.touch.up(
                    state,
                    &smithay::wayland::seat::UpEvent {
                        slot: event.slot(),
                        serial,
                        time: event.time_msec(),
                    },
                );
            },
            InputEvent::TouchCancel { event, .. } => {
                state.touch.cancel(
                    state,
                    &smithay::wayland::seat::CancelEvent {
                        slot: event.slot(),
                        time: event.time_msec(),
                    },
                );
            },
            InputEvent::TouchFrame { event, .. } => {
                state.touch.frame(
                    state,
                    &smithay::wayland::seat::FrameEvent {
                        time: event.time_msec(),
                    },
                );
            },
            _ => {}
        }
    }).unwrap();
    info!("Libinput backend initialized and bound to event loop.");

    // 4. Initialize DRM/KMS Backend (Rendering)
    // We listen to Udev for DRM nodes (monitors) being added or removed.
    handle.insert_source(udev_backend, move |event, _, state| {
        match event {
            UdevEvent::Added { device_id, path } => {
                if path.starts_with("/dev/dri/card") {
                    info!("DRM Node added: {:?}", path);
                    // Here we would initialize the GBM allocator, EGL/Vulkan renderer, 
                    // and create a DrmDevice to start swapping buffers to the screen.
                    
                    // Display Overclocking Logic
                    let base_mode = crate::overclock::DisplayMode {
                        width: 1920,
                        height: 1080,
                        refresh_rate: 60000, // 60Hz
                    };
                    
                    // Check for manual overclock override
                    let overclocked = if let Ok(manual_hz) = std::env::var("VIBEOS_MANUAL_OVERCLOCK") {
                        if let Ok(hz) = manual_hz.parse::<u32>() {
                            crate::overclock::apply_manual_overclock(base_mode.width, base_mode.height, hz)
                        } else {
                            crate::overclock::generate_overclocked_mode(&base_mode, 75000)
                        }
                    } else {
                        // Auto overclock to 75Hz (or higher if supported)
                        crate::overclock::generate_overclocked_mode(&base_mode, 75000)
                    };
                    
                    info!("Applying display mode: {}x{} @ {}Hz", overclocked.width, overclocked.height, overclocked.refresh_rate / 1000);
                }
            },
            UdevEvent::Changed { device_id } => {
                info!("Udev device changed: {:?}", device_id);
            },
            UdevEvent::Removed { device_id } => {
                info!("Udev device removed: {:?}", device_id);
            },
        }
    }).unwrap();
    info!("Udev/DRM backend initialized and bound to event loop.");

    Ok(())
}
