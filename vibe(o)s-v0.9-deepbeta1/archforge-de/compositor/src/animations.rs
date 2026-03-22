//! ArchForge Fluid Animations System
//! Implements macOS-style spring physics for window movements, resizing, and snapping.

pub struct AnimationState {
    pub velocity_x: f64,
    pub velocity_y: f64,
    pub velocity_w: f64,
    pub velocity_h: f64,
}

pub struct SpringAnimator {
    pub stiffness: f64,
    pub damping: f64,
    pub state: AnimationState,
}

impl SpringAnimator {
    pub fn new(stiffness: f64, damping: f64) -> Self {
        Self {
            stiffness,
            damping,
            state: AnimationState {
                velocity_x: 0.0,
                velocity_y: 0.0,
                velocity_w: 0.0,
                velocity_h: 0.0,
            },
        }
    }

    /// Applies Hooke's Law (F = -kx - cv) to calculate the next position
    pub fn update_position(&mut self, current: (f64, f64), target: (f64, f64), dt: f64) -> (f64, f64) {
        let dx = current.0 - target.0;
        let dy = current.1 - target.1;

        let force_x = -self.stiffness * dx - self.damping * self.state.velocity_x;
        let force_y = -self.stiffness * dy - self.damping * self.state.velocity_y;

        self.state.velocity_x += force_x * dt;
        self.state.velocity_y += force_y * dt;

        let new_x = current.0 + self.state.velocity_x * dt;
        let new_y = current.1 + self.state.velocity_y * dt;

        // Snap to target if very close to prevent micro-jitter
        if dx.abs() < 0.5 && self.state.velocity_x.abs() < 0.5 {
            self.state.velocity_x = 0.0;
            return (target.0, new_y);
        }

        (new_x, new_y)
    }

    pub fn update_size(&mut self, current: (f64, f64), target: (f64, f64), dt: f64) -> (f64, f64) {
        let dw = current.0 - target.0;
        let dh = current.1 - target.1;

        let force_w = -self.stiffness * dw - self.damping * self.state.velocity_w;
        let force_h = -self.stiffness * dh - self.damping * self.state.velocity_h;

        self.state.velocity_w += force_w * dt;
        self.state.velocity_h += force_h * dt;

        let new_w = current.0 + self.state.velocity_w * dt;
        let new_h = current.1 + self.state.velocity_h * dt;

        (new_w, new_h)
    }
}
