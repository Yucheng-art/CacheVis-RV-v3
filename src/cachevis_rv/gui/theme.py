"""Styles scoped to the V3 platform shell, sidebar, and Home page."""

COLORS = {
    "background": "#0b1220",
    "sidebar": "#101a2d",
    "card": "#152238",
    "card_hover": "#1b2c48",
    "border": "#2a3d5f",
    "text": "#eef4ff",
    "muted": "#9fb0c8",
    "accent": "#4f8cff",
    "accent_hover": "#70a3ff",
    "available": "#45d483",
    "coming_soon": "#f1b957",
    "selected": "#203b66",
}

SIDEBAR_WIDTH = 248

PLATFORM_STYLESHEET = f"""
#PlatformShell {{
    background: {COLORS["background"]};
}}
#NavigationSidebar {{
    background: {COLORS["sidebar"]};
    border-right: 1px solid {COLORS["border"]};
}}
#NavigationSidebar QLabel {{
    color: {COLORS["text"]};
}}
#NavigationSidebar QLabel[role="section"] {{
    color: {COLORS["muted"]};
    font-size: 11px;
    font-weight: 700;
    padding: 14px 12px 5px 12px;
}}
#NavigationSidebar QPushButton {{
    color: {COLORS["muted"]};
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
}}
#NavigationSidebar QPushButton:hover {{
    color: {COLORS["text"]};
    background: {COLORS["card_hover"]};
}}
#NavigationSidebar QPushButton:checked {{
    color: {COLORS["text"]};
    background: {COLORS["selected"]};
    border-color: {COLORS["accent"]};
}}
#HomePage, #HomePageContent {{
    background: {COLORS["background"]};
}}
#HomePage QLabel {{
    color: {COLORS["text"]};
}}
#HomePage QLabel[role="muted"] {{
    color: {COLORS["muted"]};
}}
#LabCard {{
    background: {COLORS["card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
}}
#LabCard:hover {{
    background: {COLORS["card_hover"]};
    border-color: {COLORS["accent"]};
}}
#LabCard QLabel[status="Available"] {{
    color: {COLORS["available"]};
    font-weight: 700;
}}
#LabCard QLabel[status="Coming Soon"] {{
    color: {COLORS["coming_soon"]};
    font-weight: 700;
}}
#LabCard QPushButton {{
    color: white;
    background: {COLORS["accent"]};
    border: none;
    border-radius: 7px;
    padding: 8px 14px;
    font-weight: 700;
}}
#LabCard QPushButton:hover {{
    background: {COLORS["accent_hover"]};
}}
#LabCard QPushButton:disabled {{
    color: {COLORS["muted"]};
    background: #25334a;
}}
"""

__all__ = ["COLORS", "PLATFORM_STYLESHEET", "SIDEBAR_WIDTH"]
