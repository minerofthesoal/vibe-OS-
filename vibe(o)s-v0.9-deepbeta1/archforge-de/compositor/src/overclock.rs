use tracing::{info, warn};

#[derive(Debug, Clone)]
pub struct DisplayMode {
    pub width: u32,
    pub height: u32,
    pub refresh_rate: u32, // in mHz
}

/// Generates a custom overclocked mode using CVT-RB (Coordinated Video Timing - Reduced Blanking)
/// This reduces the blanking intervals, allowing a higher refresh rate within the same pixel clock limit.
pub fn generate_overclocked_mode(base_mode: &DisplayMode, target_refresh: u32) -> DisplayMode {
    info!("Auto-overclocking display from {}Hz to {}Hz", base_mode.refresh_rate / 1000, target_refresh / 1000);
    
    // In a real DRM backend, we would construct a drm::control::Mode here
    // using the CVT-RB formula to calculate hsync, vsync, and pixel clock.
    // For now, we return the requested mode structure.
    DisplayMode {
        width: base_mode.width,
        height: base_mode.height,
        refresh_rate: target_refresh,
    }
}

/// Applies a manual overclock to the display
pub fn apply_manual_overclock(width: u32, height: u32, refresh_rate: u32) -> DisplayMode {
    info!("Applying manual display overclock: {}x{} @ {}Hz", width, height, refresh_rate);
    DisplayMode {
        width,
        height,
        refresh_rate: refresh_rate * 1000, // Convert to mHz
    }
}
