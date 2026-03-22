use smithay::reexports::wayland_server::Display;
use smithay::reexports::calloop::EventLoop;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;
use std::os::unix::io::AsRawFd;

mod window_manager;
mod animations;
mod state;
mod backend;
mod overclock;

use state::ArchForgeState;

fn main() {
    // Initialize logging
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber).expect("Setting default subscriber failed");

    info!("Starting ArchForge Compositor (Rust/Smithay Engine)...");

    // Initialize Calloop Event Loop (The core loop driving the compositor)
    let mut event_loop: EventLoop<ArchForgeState> = EventLoop::try_new().unwrap();
    
    // Initialize Wayland Display
    let mut display = Display::<ArchForgeState>::new().unwrap();
    let dh = display.handle();

    // Initialize our global state
    let mut state = ArchForgeState::new(&dh);

    // Setup the Wayland socket
    let listener = smithay::reexports::wayland_server::backend::sys::Socket::bind("wayland-1")
        .expect("Failed to bind Wayland socket");
    
    let mut display_loop = display.handle();
    event_loop.handle().insert_source(
        smithay::reexports::calloop::generic::Generic::new(
            listener.as_raw_fd(),
            smithay::reexports::calloop::Interest::READ,
            smithay::reexports::calloop::Mode::Level,
        ),
        move |_, _, state: &mut ArchForgeState| {
            if let Ok(Some(stream)) = listener.accept() {
                // Initialize client data when a new client connects
                let client_data = state::ClientState {
                    compositor_state: smithay::wayland::compositor::CompositorClientState::default(),
                };
                if let Err(e) = display_loop.insert_client(stream, std::sync::Arc::new(client_data)) {
                    tracing::warn!("Failed to insert client: {}", e);
                }
            }
            Ok(smithay::reexports::calloop::PostAction::Continue)
        },
    ).expect("Failed to insert Wayland socket source");

    info!("Listening on wayland-1");

    // Initialize Hardware Backends (DRM/KMS & Libinput)
    if let Err(e) = backend::init_backend(&mut event_loop, &dh, &mut state) {
        tracing::error!("Failed to initialize hardware backends: {}", e);
        return;
    }

    // Run the compositor event loop
    info!("Entering main event loop...");
    
    loop {
        event_loop.dispatch(Some(std::time::Duration::from_millis(16)), &mut state).unwrap();
        display.dispatch_clients(&mut state).unwrap();
        display.flush_clients().unwrap();
        
        // Tick our fluid spring animations
        state.window_manager.tick_animations(0.016);
        
        // Check DPMS state
        state.check_dpms();
    }
}
