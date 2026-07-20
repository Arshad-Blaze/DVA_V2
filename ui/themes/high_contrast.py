colors = {
    "bg_primary": "#000000",
    "bg_secondary": "#1a1a1a",
    "bg_sidebar": "#000000",
    "bg_header": "#000000",
    "bg_card": "#1a1a1a",
    "bg_hover": "#333333",
    "text_primary": "#ffffff",
    "text_secondary": "#cccccc",
    "text_on_dark": "#ffffff",
    "accent": "#ffff00",
    "accent_hover": "#ffcc00",
    "success": "#00ff00",
    "warning": "#ff8800",
    "error": "#ff4444",
    "info": "#44aaff",
    "border": "#ffffff",
    "shadow": "0 2px 8px rgba(255,255,255,0.15)",
    "radius": "8px",
    "radius_sm": "4px",
}

css_vars = "\n".join(f"  --{k}: {v};" for k, v in colors.items())
