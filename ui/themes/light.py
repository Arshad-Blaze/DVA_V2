"""Light theme colors and CSS variables for DVA Platform UI."""

colors = {
    "bg_primary": "#ffffff",
    "bg_secondary": "#f5f5f5",
    "bg_sidebar": "#1e1e2e",
    "bg_header": "#1e1e2e",
    "bg_card": "#ffffff",
    "bg_hover": "#e8e8e8",
    "text_primary": "#1a1a2e",
    "text_secondary": "#6c757d",
    "text_on_dark": "#ffffff",
    "accent": "#4361ee",
    "accent_hover": "#3a56d4",
    "success": "#4caf50",
    "warning": "#ff9800",
    "error": "#f44336",
    "info": "#2196f3",
    "border": "#e0e0e0",
    "shadow": "0 2px 8px rgba(0,0,0,0.08)",
    "radius": "8px",
    "radius_sm": "4px",
}

css_vars = "\n".join(f"  --{k}: {v};" for k, v in colors.items())
