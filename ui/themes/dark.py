"""Dark theme colors and CSS variables for DVA Platform UI."""

colors = {
    "bg_primary": "#1a1a2e",
    "bg_secondary": "#16213e",
    "bg_sidebar": "#0f0f23",
    "bg_header": "#0f0f23",
    "bg_card": "#1e1e3a",
    "bg_hover": "#2a2a4a",
    "text_primary": "#e0e0e0",
    "text_secondary": "#a0a0b0",
    "text_on_dark": "#ffffff",
    "accent": "#4361ee",
    "accent_hover": "#5a7aff",
    "success": "#4caf50",
    "warning": "#ff9800",
    "error": "#f44336",
    "info": "#2196f3",
    "border": "#2a2a4a",
    "shadow": "0 2px 8px rgba(0,0,0,0.3)",
    "radius": "8px",
    "radius_sm": "4px",
}

css_vars = "\n".join(f"  --{k}: {v};" for k, v in colors.items())
