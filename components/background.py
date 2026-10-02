"""
Interactive Background & Theme Component for Educational Performance Dashboard.
Uses pure CSS animations injected via st.markdown — no DOM elements, no JS canvas —
so Streamlit's UI is never blocked or hidden.
"""

import json
from typing import Any, Dict, Optional
import streamlit as st
import streamlit.components.v1 as components


THEME_CONFIGS: Dict[str, Dict[str, Any]] = {
    "aurora": {
        "name": "Academic Aurora (Light)",
        "mode": "light",
        "bg_base": "#F2F4FF",
        "orb1_color": "rgba(99, 102, 241, 0.18)",
        "orb2_color": "rgba(168, 85, 247, 0.14)",
        "orb3_color": "rgba(6, 182, 212, 0.12)",
        "card_bg": "rgba(255,255,255,0.80)",
        "card_border": "rgba(226,232,240,0.85)",
        "card_shadow": "0 8px 32px rgba(79,70,229,0.08)",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "header_bg": "linear-gradient(135deg,#1E1B4B 0%,#312E81 50%,#4338CA 100%)",
        "header_text": "#FFFFFF",
        "header_sub": "#E0E7FF",
        "sidebar_bg": "rgba(242,244,255,0.85)",
        "sidebar_border": "rgba(226,232,240,0.7)",
        "tab_bg": "rgba(241,245,249,0.75)",
        "tab_selected_bg": "#FFFFFF",
        "tab_selected_color": "#4F46E5",
        "tab_color": "#475569",
        "particle_colors": ["#4F46E5","#3B82F6","#8B5CF6","#06B6D4","#10B981"],
        "line_color": "rgba(99,102,241,0.22)",
        "cursor_line_color": "rgba(79,70,229,0.48)",
        "glow_color": "rgba(99,102,241,0.28)",
    },
    "cosmic": {
        "name": "Cosmic Neural Network (Dark)",
        "mode": "dark",
        "bg_base": "#06091A",
        "orb1_color": "rgba(99,102,241,0.24)",
        "orb2_color": "rgba(168,85,247,0.18)",
        "orb3_color": "rgba(14,165,233,0.15)",
        "card_bg": "rgba(15,23,42,0.80)",
        "card_border": "rgba(255,255,255,0.09)",
        "card_shadow": "0 8px 32px rgba(0,0,0,0.55)",
        "text_primary": "#F1F5F9",
        "text_secondary": "#94A3B8",
        "header_bg": "linear-gradient(135deg,#0F172A 0%,#1E1B4B 50%,#312E81 100%)",
        "header_text": "#FFFFFF",
        "header_sub": "#C7D2FE",
        "sidebar_bg": "rgba(8,12,28,0.90)",
        "sidebar_border": "rgba(255,255,255,0.07)",
        "tab_bg": "rgba(15,23,42,0.65)",
        "tab_selected_bg": "rgba(51,65,85,0.90)",
        "tab_selected_color": "#38BDF8",
        "tab_color": "#94A3B8",
        "particle_colors": ["#818CF8","#38BDF8","#C084FC","#F472B6","#34D399"],
        "line_color": "rgba(129,140,248,0.26)",
        "cursor_line_color": "rgba(56,189,248,0.55)",
        "glow_color": "rgba(129,140,248,0.35)",
    },
    "matrix": {
        "name": "Cyber Emerald (Dark)",
        "mode": "dark",
        "bg_base": "#030D07",
        "orb1_color": "rgba(16,185,129,0.22)",
        "orb2_color": "rgba(6,182,212,0.16)",
        "orb3_color": "rgba(52,211,153,0.11)",
        "card_bg": "rgba(4,20,12,0.80)",
        "card_border": "rgba(16,185,129,0.20)",
        "card_shadow": "0 8px 32px rgba(0,0,0,0.60)",
        "text_primary": "#ECFDF5",
        "text_secondary": "#6EE7B7",
        "header_bg": "linear-gradient(135deg,#022C22 0%,#064E3B 50%,#065F46 100%)",
        "header_text": "#ECFDF5",
        "header_sub": "#A7F3D0",
        "sidebar_bg": "rgba(2,10,6,0.90)",
        "sidebar_border": "rgba(16,185,129,0.14)",
        "tab_bg": "rgba(4,20,12,0.70)",
        "tab_selected_bg": "rgba(6,45,28,0.90)",
        "tab_selected_color": "#34D399",
        "tab_color": "#6EE7B7",
        "particle_colors": ["#10B981","#06B6D4","#34D399","#A7F3D0","#2DD4BF"],
        "line_color": "rgba(16,185,129,0.26)",
        "cursor_line_color": "rgba(52,211,153,0.58)",
        "glow_color": "rgba(16,185,129,0.35)",
    },
    "sunset": {
        "name": "Sunset Horizon (Warm)",
        "mode": "light",
        "bg_base": "#FFF8F2",
        "orb1_color": "rgba(245,158,11,0.14)",
        "orb2_color": "rgba(239,68,68,0.10)",
        "orb3_color": "rgba(236,72,153,0.09)",
        "card_bg": "rgba(255,255,255,0.84)",
        "card_border": "rgba(254,215,170,0.80)",
        "card_shadow": "0 8px 32px rgba(245,158,11,0.08)",
        "text_primary": "#1C1917",
        "text_secondary": "#78716C",
        "header_bg": "linear-gradient(135deg,#7C2D12 0%,#9A3412 50%,#C2410C 100%)",
        "header_text": "#FFFFFF",
        "header_sub": "#FFEDD5",
        "sidebar_bg": "rgba(255,251,245,0.88)",
        "sidebar_border": "rgba(254,215,170,0.65)",
        "tab_bg": "rgba(254,243,199,0.65)",
        "tab_selected_bg": "#FFFFFF",
        "tab_selected_color": "#C2410C",
        "tab_color": "#78716C",
        "particle_colors": ["#F59E0B","#EF4444","#EC4899","#8B5CF6","#F97316"],
        "line_color": "rgba(245,158,11,0.22)",
        "cursor_line_color": "rgba(239,68,68,0.46)",
        "glow_color": "rgba(245,158,11,0.30)",
    },
}


def init_theme_state() -> None:
    """Ensures consistent theme session state across header toggle & sidebar selectbox."""
    if "bg_theme_key" not in st.session_state:
        st.session_state["bg_theme_key"] = "aurora"

    current_key = st.session_state["bg_theme_key"]
    if current_key not in THEME_CONFIGS:
        current_key = "aurora"
        st.session_state["bg_theme_key"] = "aurora"

    is_dark = (THEME_CONFIGS[current_key]["mode"] == "dark")
    if "header_dark_mode_toggle" not in st.session_state:
        st.session_state["header_dark_mode_toggle"] = is_dark

    theme_name = THEME_CONFIGS[current_key]["name"]
    if "bg_theme_selector" not in st.session_state:
        st.session_state["bg_theme_selector"] = theme_name


def on_sidebar_theme_change() -> None:
    """Callback when sidebar theme selectbox is changed."""
    sel_label = st.session_state.get("bg_theme_selector")
    for key, cfg in THEME_CONFIGS.items():
        if cfg["name"] == sel_label:
            st.session_state["bg_theme_key"] = key
            st.session_state["header_dark_mode_toggle"] = (cfg["mode"] == "dark")
            break


def on_header_toggle_change() -> None:
    """Callback when header dark mode toggle is clicked."""
    is_dark = st.session_state.get("header_dark_mode_toggle", False)
    new_theme = "cosmic" if is_dark else "aurora"
    st.session_state["bg_theme_key"] = new_theme
    st.session_state["bg_theme_selector"] = THEME_CONFIGS[new_theme]["name"]


def render_background_controls() -> Dict[str, Any]:
    """Renders background customization controls in the sidebar."""
    init_theme_state()
    theme_keys = list(THEME_CONFIGS.keys())
    theme_labels = [THEME_CONFIGS[k]["name"] for k in theme_keys]

    with st.sidebar.expander("✨ Background & Visual Ambience", expanded=False):
        st.selectbox(
            "Ambience Theme",
            options=theme_labels,
            key="bg_theme_selector",
            on_change=on_sidebar_theme_change,
        )
        selected_theme = st.session_state.get("bg_theme_key", "aurora")

        col_a, col_b = st.columns(2)
        with col_a:
            interactive_mode = st.selectbox(
                "Cursor Mode",
                options=["Constellation", "Magnetic Push", "Float Only"],
                index=0, key="bg_interactive_mode",
            )
        with col_b:
            particle_density = st.selectbox(
                "Density",
                options=["Gentle (45)", "Balanced (70)", "Dense (100)"],
                index=1, key="bg_density",
            )

        click_burst = st.checkbox("✨ Click Ripple", value=True, key="bg_click_burst")

    density_map = {"Gentle (45)": 45, "Balanced (70)": 70, "Dense (100)": 100}
    return {
        "theme": selected_theme,
        "interactive_mode": interactive_mode,
        "particle_count": density_map.get(particle_density, 70),
        "click_burst": click_burst,
    }


def inject_interactive_background(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Injects the complete CSS theme + animated background via st.markdown.
    Pure CSS only — no DOM node injections, no <script> tags.
    Streamlit UI is always fully visible on top.
    The particle canvas is rendered via components.html in a hidden 0-height iframe
    so it cannot block any Streamlit content.
    """
    if config is None:
        config = {
            "theme": st.session_state.get("bg_theme_key", "aurora"),
            "interactive_mode": st.session_state.get("bg_interactive_mode", "Constellation"),
            "particle_count": 70,
            "click_burst": True,
        }

    theme_key = config.get("theme", "aurora")
    if theme_key not in THEME_CONFIGS:
        theme_key = "aurora"
    t = THEME_CONFIGS[theme_key]
    is_dark = t["mode"] == "dark"

    dark_extra = ""
    if is_dark:
        dark_extra = f"""
        /* ── Dark mode text & widget overrides ── */
        header[data-testid="stHeader"], div[data-testid="stHeader"] {{
            background: transparent !important;
            color: {t['text_primary']} !important;
        }}
        .stApp p, .stApp span, .stApp div, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
            color: {t['text_primary']};
        }}
        div[data-testid="stExpander"] {{
            background: {t['card_bg']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 12px !important;
        }}
        div[data-testid="stExpander"] summary span {{
            color: {t['text_primary']} !important;
        }}
        .insight-card {{
            background: {t['card_bg']} !important;
            border-left: 4px solid {t['particle_colors'][0]} !important;
            color: {t['text_primary']} !important;
        }}
        div[data-testid="metric-container"] {{
            background: {t['card_bg']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 12px;
            padding: 12px !important;
        }}

        /* ── Selectboxes & Multiselect Tags in Dark Mode ── */
        div[data-baseweb="select"] > div {{
            background: rgba(15, 23, 42, 0.85) !important;
            color: {t['text_primary']} !important;
            border-color: rgba(255, 255, 255, 0.15) !important;
        }}
        div[data-baseweb="select"] span {{
            color: {t['text_primary']} !important;
        }}
        span[data-baseweb="tag"] {{
            background: rgba(99, 102, 241, 0.35) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(99, 102, 241, 0.5) !important;
        }}
        div[data-testid="stTextInput"] input {{
            background: rgba(15, 23, 42, 0.8) !important;
            color: {t['text_primary']} !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
        }}
        div[data-testid="stTextInput"] input::placeholder {{
            color: rgba(255, 255, 255, 0.5) !important;
        }}
        .stButton > button {{
            background: rgba(30, 41, 59, 0.9) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }}

        /* ── Download Buttons Dark Mode ── */
        .stDownloadButton > button {{
            background: rgba(20, 30, 55, 0.85) !important;
            color: {t['text_primary']} !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-radius: 8px !important;
        }}
        .stDownloadButton > button:hover {{
            background: rgba(40, 55, 90, 0.95) !important;
            border-color: rgba(99, 102, 241, 0.5) !important;
            color: #FFFFFF !important;
        }}
        .stDownloadButton > button span, .stDownloadButton > button p {{
            color: {t['text_primary']} !important;
        }}

        /* ── Textarea Dark Mode ── */
        div[data-testid="stTextArea"] textarea {{
            background: rgba(15, 23, 42, 0.8) !important;
            color: {t['text_primary']} !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-radius: 10px !important;
        }}
        div[data-testid="stTextArea"] textarea::placeholder {{
            color: rgba(255, 255, 255, 0.4) !important;
        }}

        /* ── Expander Dark Mode Overrides ── */
        div[data-testid="stExpander"], details {{
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
        }}
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpanderSummary"],
        details summary,
        div[data-baseweb="accordion"] header {{
            background: rgba(26, 38, 64, 0.95) !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        div[data-testid="stExpander"] summary:hover,
        div[data-testid="stExpanderSummary"]:hover,
        details summary:hover,
        div[data-baseweb="accordion"] header:hover {{
            background: rgba(40, 56, 90, 0.95) !important;
            color: #FFFFFF !important;
        }}
        div[data-testid="stExpander"] summary p,
        div[data-testid="stExpander"] summary span,
        div[data-testid="stExpanderSummary"] p,
        div[data-testid="stExpanderSummary"] span,
        details summary p,
        details summary span,
        div[data-baseweb="accordion"] header p,
        div[data-baseweb="accordion"] header span,
        details summary div {{
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }}
        div[data-testid="stExpander"] summary svg,
        div[data-testid="stExpanderSummary"] svg,
        details summary svg {{
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }}

        /* ── KPI Badges and Subtitles in Dark Mode ── */
        .kpi-label {{
            font-size: 0.82rem; font-weight: 600;
            color: {t['text_secondary']} !important;
            text-transform: uppercase; letter-spacing: 0.05em;
        }}
        .kpi-value {{
            font-size: 1.75rem; font-weight: 700;
            color: {t['text_primary']} !important;
            letter-spacing: -0.02em; line-height: 1.1;
        }}
        .kpi-subtitle {{
            font-size: 0.78rem;
            color: {t['text_secondary']} !important;
            margin-top: 4px; opacity: 0.9;
        }}
        .kpi-badge {{
            padding: 3px 10px; border-radius: 9999px;
            font-size: 0.72rem; font-weight: 600;
        }}
        .kpi-badge.badge-primary {{ background: rgba(99, 102, 241, 0.25) !important; color: #A5B4FC !important; border: 1px solid rgba(99, 102, 241, 0.4) !important; }}
        .kpi-badge.badge-success {{ background: rgba(16, 185, 129, 0.25) !important; color: #6EE7B7 !important; border: 1px solid rgba(16, 185, 129, 0.4) !important; }}
        .kpi-badge.badge-warning {{ background: rgba(245, 158, 11, 0.25) !important; color: #FDE047 !important; border: 1px solid rgba(245, 158, 11, 0.4) !important; }}
        .kpi-badge.badge-danger  {{ background: rgba(239, 68, 68, 0.25) !important; color: #FCA5A5 !important; border: 1px solid rgba(239, 68, 68, 0.4) !important; }}
        .kpi-badge.badge-info    {{ background: rgba(14, 165, 233, 0.25) !important; color: #7DD3FC !important; border: 1px solid rgba(14, 165, 233, 0.4) !important; }}

        /* Header status pills dark mode */
        .status-pill.pill-blue   {{ background: rgba(99, 102, 241, 0.25) !important; color: #C7D2FE !important; border: 1px solid rgba(99, 102, 241, 0.4) !important; }}
        .status-pill.pill-green  {{ background: rgba(16, 185, 129, 0.25) !important; color: #A7F3D0 !important; border: 1px solid rgba(16, 185, 129, 0.4) !important; }}
        .status-pill.pill-yellow {{ background: rgba(245, 158, 11, 0.25) !important; color: #FDE68A !important; border: 1px solid rgba(245, 158, 11, 0.4) !important; }}
        .status-pill.pill-red    {{ background: rgba(239, 68, 68, 0.25) !important; color: #FECACA !important; border: 1px solid rgba(239, 68, 68, 0.4) !important; }}

        /* ── Sidebar Brand & Stats in Dark Mode ── */
        .sidebar-brand {{
            padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px;
        }}
        .sidebar-brand-title {{
            font-size: 1.25rem !important; font-weight: 700 !important;
            color: {t['text_primary']} !important;
            margin: 0 !important; display: flex; align-items: center; gap: 8px;
        }}
        .sidebar-brand-sub {{
            font-size: 0.8rem !important; color: {t['text_secondary']} !important; margin: 4px 0 0 0 !important;
        }}
        .sidebar-stats-box {{
            background: rgba(15, 23, 42, 0.7) !important;
            border-radius: 8px; padding: 10px 12px; margin-top: 15px;
            font-size: 0.8rem; color: {t['text_primary']} !important;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .sidebar-stats-box b {{
            color: {t['text_primary']} !important;
        }}
        .sidebar-contact-box {{
            background: rgba(15, 23, 42, 0.7) !important;
            border-radius: 8px; padding: 12px; margin-top: 12px;
            font-size: 0.8rem; color: {t['text_primary']} !important;
            border: 1px solid rgba(99, 102, 241, 0.25);
        }}
        .contact-title {{
            font-weight: 700; font-size: 0.83rem; color: {t['text_primary']}; margin-bottom: 8px;
            display: flex; align-items: center; gap: 6px;
        }}
        .contact-links {{
            display: flex; flex-direction: column; gap: 6px;
        }}
        .contact-link {{
            text-decoration: none !important; color: {t['text_primary']} !important;
            display: flex; align-items: center; gap: 8px; font-size: 0.78rem; font-weight: 500;
            padding: 5px 8px; border-radius: 6px; transition: all 0.2s ease;
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
            word-break: break-all;
        }}
        .contact-link:hover {{
            background: rgba(99, 102, 241, 0.25) !important;
            border-color: rgba(99, 102, 241, 0.5) !important;
            color: #A5B4FC !important;
            transform: translateX(2px);
        }}

        /* ── Sidebar labels & subheaders Dark Mode ── */
        section[data-testid="stSidebar"] label {{
            color: {t['text_primary']} !important;
        }}
        section[data-testid="stSidebar"] .stSubheader, section[data-testid="stSidebar"] h3 {{
            color: {t['text_primary']} !important;
        }}
        """
    else:
        dark_extra = f"""
        /* ── Light mode KPI badges & text ── */
        header[data-testid="stHeader"], div[data-testid="stHeader"] {{
            background: transparent !important;
        }}
        div[data-testid="stTextInput"] input {{
            background: rgba(255, 255, 255, 0.8) !important;
            color: #0F172A !important;
            border: 1px solid rgba(15, 23, 42, 0.2) !important;
        }}
        div[data-testid="stTextInput"] input::placeholder {{
            color: rgba(15, 23, 42, 0.5) !important;
        }}
        .stButton > button {{
            background: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid rgba(15, 23, 42, 0.2) !important;
        }}
        .kpi-label {{
            font-size: 0.82rem; font-weight: 600;
            color: #475569 !important;
            text-transform: uppercase; letter-spacing: 0.05em;
        }}
        .kpi-value {{
            font-size: 1.75rem; font-weight: 700;
            color: #0F172A !important;
            letter-spacing: -0.02em; line-height: 1.1;
        }}
        .kpi-subtitle {{
            font-size: 0.78rem; color: #64748B !important; margin-top: 4px;
        }}
        .kpi-badge {{
            padding: 3px 10px; border-radius: 9999px;
            font-size: 0.72rem; font-weight: 600;
        }}
        .kpi-badge.badge-primary {{ background: #EEF2FF !important; color: #4F46E5 !important; border: 1px solid #C7D2FE !important; }}
        .kpi-badge.badge-success {{ background: #ECFDF5 !important; color: #059669 !important; border: 1px solid #A7F3D0 !important; }}
        .kpi-badge.badge-warning {{ background: #FFFBEB !important; color: #D97706 !important; border: 1px solid #FDE68A !important; }}
        .kpi-badge.badge-danger  {{ background: #FEF2F2 !important; color: #DC2626 !important; border: 1px solid #FECACA !important; }}
        .kpi-badge.badge-info    {{ background: #F0F9FF !important; color: #0284C7 !important; border: 1px solid #BAE6FD !important; }}

        /* ── Sidebar Brand & Stats in Light Mode ── */
        .sidebar-brand {{
            padding: 10px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 15px;
        }}
        .sidebar-brand-title {{
            font-size: 1.25rem !important; font-weight: 700 !important;
            color: #1E293B !important;
            margin: 0 !important; display: flex; align-items: center; gap: 8px;
        }}
        .sidebar-brand-sub {{
            font-size: 0.8rem !important; color: #64748B !important; margin: 4px 0 0 0 !important;
        }}
        .sidebar-stats-box {{
            background: #F1F5F9 !important;
            border-radius: 8px; padding: 10px 12px; margin-top: 15px;
            font-size: 0.8rem; color: #334155 !important;
        }}
        .sidebar-stats-box b {{
            color: #1E293B !important;
        }}
        .sidebar-contact-box {{
            background: #F8FAFC !important;
            border-radius: 8px; padding: 12px; margin-top: 12px;
            font-size: 0.8rem; color: #1E293B !important;
            border: 1px solid #E2E8F0;
        }}
        .contact-title {{
            font-weight: 700; font-size: 0.83rem; color: #0F172A; margin-bottom: 8px;
            display: flex; align-items: center; gap: 6px;
        }}
        .contact-links {{
            display: flex; flex-direction: column; gap: 6px;
        }}
        .contact-link {{
            text-decoration: none !important; color: #334155 !important;
            display: flex; align-items: center; gap: 8px; font-size: 0.78rem; font-weight: 500;
            padding: 5px 8px; border-radius: 6px; transition: all 0.2s ease;
            background: #FFFFFF; border: 1px solid #E2E8F0;
            word-break: break-all;
        }}
        .contact-link:hover {{
            background: #EEF2FF !important;
            border-color: #6366F1 !important;
            color: #4F46E5 !important;
            transform: translateX(2px);
        }}
        """

    css = f"""
<style>
/* ══════════════════════════════════════════
   FONTS
═══════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

/* ══════════════════════════════════════════
   ANIMATED BACKGROUND  (on stApp itself)
   Three slow-drifting radial blobs via
   multiple background-images. No extra DOM.
═══════════════════════════════════════════ */
.stApp {{
    background-color: {t['bg_base']} !important;
    background-image:
        radial-gradient(ellipse 55% 40% at 15% 20%, {t['orb1_color']}, transparent),
        radial-gradient(ellipse 50% 42% at 85% 80%, {t['orb2_color']}, transparent),
        radial-gradient(ellipse 42% 38% at 50% 52%, {t['orb3_color']}, transparent) !important;
    background-attachment: fixed !important;
    animation: bgShift 18s ease-in-out infinite alternate !important;
}}

@keyframes bgShift {{
    0%   {{ background-position: 0% 0%,   100% 100%, 50% 50%; }}
    33%  {{ background-position: 10% 15%, 88% 82%,  42% 60%; }}
    66%  {{ background-position: 5% 8%,   92% 88%,  55% 44%; }}
    100% {{ background-position: 12% 18%, 85% 78%,  48% 55%; }}
}}

/* ══════════════════════════════════════════
   DASHBOARD HEADER
═══════════════════════════════════════════ */
.dashboard-header {{
    background: {t['header_bg']} !important;
    padding: 24px 28px;
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 10px 28px -5px rgba(0,0,0,0.28), 0 0 0 1px rgba(255,255,255,0.12);
    position: relative;
    overflow: hidden;
}}
.dashboard-header::after {{
    content: '';
    position: absolute;
    top: -55%; right: -12%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.11) 0%, transparent 70%);
    border-radius: 50%;
    animation: hdrGlow 9s ease-in-out infinite alternate;
    pointer-events: none;
}}
@keyframes hdrGlow {{
    0%   {{ transform: scale(0.85) translate(0, 0); opacity: 0.7; }}
    100% {{ transform: scale(1.25) translate(-18px, 14px); opacity: 1; }}
}}
.dashboard-header h1 {{
    font-size: 1.85rem; font-weight: 800; margin: 0 0 5px 0;
    color: {t['header_text']} !important; letter-spacing: -0.025em;
}}
.dashboard-header p {{
    font-size: 0.92rem; color: {t['header_sub']} !important; margin: 0; opacity: 0.94;
}}

/* ══════════════════════════════════════════
   STATUS PILLS
═══════════════════════════════════════════ */
.status-pill {{
    display: inline-flex; align-items: center;
    padding: 4px 12px; border-radius: 9999px;
    font-size: 0.78rem; font-weight: 600; margin-right: 6px;
}}
.pill-green  {{ background:#ECFDF5; color:#059669; border:1px solid #A7F3D0; }}
.pill-blue   {{ background:#EEF2FF; color:#4F46E5; border:1px solid #C7D2FE; }}
.pill-yellow {{ background:#FFFBEB; color:#D97706; border:1px solid #FDE68A; }}
.pill-red    {{ background:#FEF2F2; color:#DC2626; border:1px solid #FECACA; }}

/* ══════════════════════════════════════════
   GLASSMORPHIC KPI CARDS
═══════════════════════════════════════════ */
.kpi-glass-card {{
    background: {t['card_bg']} !important;
    border: 1px solid {t['card_border']} !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
    box-shadow: {t['card_shadow']} !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    display: flex; flex-direction: column;
    justify-content: space-between; height: 100%;
    transition: transform 0.25s cubic-bezier(.16,1,.3,1), box-shadow 0.25s ease;
}}
.kpi-glass-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 18px 36px rgba(79,70,229,0.14) !important;
}}

/* ══════════════════════════════════════════
   EDU CONTENT CARDS
═══════════════════════════════════════════ */
.edu-card {{
    background: {t['card_bg']} !important;
    border: 1px solid {t['card_border']} !important;
    border-radius: 16px !important;
    padding: 20px !important;
    margin-bottom: 20px !important;
    box-shadow: {t['card_shadow']} !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}}
.edu-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 14px 34px rgba(79,70,229,0.12) !important;
}}

/* ══════════════════════════════════════════
   INSIGHT CARD
═══════════════════════════════════════════ */
.insight-card {{
    border-left: 4px solid #4F46E5;
    background: {t['card_bg']};
    border-top: 1px solid {t['card_border']};
    border-right: 1px solid {t['card_border']};
    border-bottom: 1px solid {t['card_border']};
    padding: 14px 18px;
    border-radius: 0 12px 12px 0;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}}

/* ══════════════════════════════════════════
   PLOTLY CHART CONTAINER
═══════════════════════════════════════════ */
div[data-testid="stPlotlyChart"] > div {{
    background: {t['card_bg']} !important;
    border: 1px solid {t['card_border']} !important;
    border-radius: 16px !important;
    padding: 10px !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    box-shadow: {t['card_shadow']} !important;
}}

/* ══════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: {t['sidebar_bg']} !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    border-right: 1px solid {t['sidebar_border']} !important;
}}
{"section[data-testid='stSidebar'] * { color: " + t['text_primary'] + " !important; }" if is_dark else ""}

/* ══════════════════════════════════════════
   NAVIGATION TABS
═══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background: {t['tab_bg']};
    backdrop-filter: blur(8px);
    padding: 6px; border-radius: 12px;
    border: 1px solid {t['card_border']};
}}
.stTabs [data-baseweb="tab"] {{
    height: 42px; border-radius: 8px;
    padding: 0 16px; font-weight: 600;
    font-size: 0.87rem; color: {t['tab_color']};
    transition: all 0.18s ease;
}}
.stTabs [aria-selected="true"] {{
    background-color: {t['tab_selected_bg']} !important;
    color: {t['tab_selected_color']} !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}}

/* ══════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════ */
.stButton > button {{
    border-radius: 8px; font-weight: 600;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}}
.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}}

/* ══════════════════════════════════════════
   FOOTER
═══════════════════════════════════════════ */
.dashboard-footer {{
    background: {t['card_bg']} !important;
    border: 1px solid {t['card_border']} !important;
    border-radius: 16px !important;
    padding: 24px 28px !important;
    margin-top: 40px !important;
    margin-bottom: 20px !important;
    box-shadow: {t['card_shadow']} !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
}}
.footer-badge {{
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.76rem;
    font-weight: 600;
    background: rgba(99, 102, 241, 0.08);
    color: {t['text_primary']};
    border: 1px solid {t['card_border']};
}}

{dark_extra}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)

    # ── Interactive particle canvas via components.html ──
    # Rendered in a 0-height hidden iframe — CANNOT block Streamlit UI.
    js_data = json.dumps({
        "particleColors": t["particle_colors"],
        "lineColor": t["line_color"],
        "cursorLineColor": t["cursor_line_color"],
        "glowColor": t["glow_color"],
        "particleCount": config.get("particle_count", 70),
        "interactiveMode": config.get("interactive_mode", "Constellation"),
        "clickBurst": config.get("click_burst", True),
        "themeKey": theme_key,
    })

    # The canvas targets window.parent (the main Streamlit frame).
    # We carefully use z-index:-1 so it never blocks clicks or visibility.
    canvas_html = f"""<!DOCTYPE html>
<html><head><style>
  body {{ margin:0; overflow:hidden; background:transparent; }}
  canvas {{
    position:fixed; top:0; left:0;
    width:100vw; height:100vh;
    pointer-events:none;
    z-index:0;
    opacity:0.85;
  }}
</style></head><body>
<canvas id="c"></canvas>
<script>
(function(){{
  var cfg={js_data};
  var win=window.parent||window;
  var doc=win.document;
  // Find or create canvas in PARENT document
  var canvas=doc.getElementById('edu-sys-canvas');
  if(!canvas){{
    canvas=doc.createElement('canvas');
    canvas.id='edu-sys-canvas';
    Object.assign(canvas.style,{{
      position:'fixed',top:'0',left:'0',
      width:'100vw',height:'100vh',
      zIndex:'0',pointerEvents:'none',
      opacity:'0.82'
    }});
    // Insert as the very first child of body so it's behind everything
    doc.body.insertBefore(canvas,doc.body.firstChild);
  }}
  var ctx=canvas.getContext('2d');
  function resize(){{
    var dpr=win.devicePixelRatio||1;
    canvas.width=win.innerWidth*dpr;
    canvas.height=win.innerHeight*dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }}
  win.addEventListener('resize',resize); resize();

  var mouse={{x:null,y:null,r:140}};
  doc.addEventListener('mousemove',function(e){{mouse.x=e.clientX;mouse.y=e.clientY;}});
  doc.addEventListener('mouseleave',function(){{mouse.x=null;mouse.y=null;}});

  var particles=[];
  for(var i=0;i<cfg.particleCount;i++){{
    particles.push({{
      x:Math.random()*win.innerWidth,
      y:Math.random()*win.innerHeight,
      vx:(Math.random()-0.5)*0.7,
      vy:(Math.random()-0.5)*0.7,
      r:Math.random()*2+1,
      color:cfg.particleColors[Math.floor(Math.random()*cfg.particleColors.length)],
      phase:Math.random()*Math.PI*2,
      speed:0.018+Math.random()*0.022
    }});
  }}

  var ripples=[];
  doc.addEventListener('click',function(e){{
    if(!cfg.clickBurst)return;
    ripples.push({{x:e.clientX,y:e.clientY,r:4,maxR:100,a:0.6,color:cfg.particleColors[0]}});
    for(var k=0;k<6;k++){{
      var ang=Math.random()*Math.PI*2,spd=Math.random()*2+0.8;
      ripples.push({{spark:true,x:e.clientX,y:e.clientY,
        vx:Math.cos(ang)*spd,vy:Math.sin(ang)*spd,
        r:Math.random()*1.6+0.7,a:0.88,
        color:cfg.particleColors[Math.floor(Math.random()*cfg.particleColors.length)]}});
    }}
  }});

  function frame(){{
    var w=win.innerWidth,h=win.innerHeight;
    ctx.clearRect(0,0,w,h);
    // Ripples
    for(var ri=ripples.length-1;ri>=0;ri--){{
      var rp=ripples[ri];
      if(rp.spark){{rp.x+=rp.vx;rp.y+=rp.vy;rp.a-=0.026;
        ctx.beginPath();ctx.arc(rp.x,rp.y,rp.r,0,Math.PI*2);
        ctx.fillStyle=rp.color;ctx.globalAlpha=Math.max(0,rp.a);ctx.fill();
      }}else{{rp.r+=2.4;rp.a-=0.019;
        ctx.beginPath();ctx.arc(rp.x,rp.y,rp.r,0,Math.PI*2);
        ctx.strokeStyle=rp.color;ctx.lineWidth=1.5;
        ctx.globalAlpha=Math.max(0,rp.a);ctx.stroke();
      }}
      if(rp.a<=0||rp.r>=(rp.maxR||999))ripples.splice(ri,1);
    }}
    ctx.globalAlpha=1;
    // Particles
    for(var i=0;i<particles.length;i++){{
      var p=particles[i];
      p.x+=p.vx;p.y+=p.vy;
      if(p.x<-8)p.x=w+8;else if(p.x>w+8)p.x=-8;
      if(p.y<-8)p.y=h+8;else if(p.y>h+8)p.y=-8;
      if(mouse.x!==null){{
        var dx=mouse.x-p.x,dy=mouse.y-p.y,dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<mouse.r){{
          if(cfg.interactiveMode==='Magnetic Push'){{
            var f=(mouse.r-dist)/mouse.r;
            p.x-=(dx/dist)*f*3;p.y-=(dy/dist)*f*3;
          }}else if(cfg.interactiveMode==='Constellation'){{
            ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(mouse.x,mouse.y);
            ctx.strokeStyle=cfg.cursorLineColor;ctx.lineWidth=1;
            ctx.globalAlpha=(1-dist/mouse.r)*0.6;ctx.stroke();ctx.globalAlpha=1;
            p.x+=(dx/dist)*0.2;p.y+=(dy/dist)*0.2;
          }}
        }}
      }}
      for(var j=i+1;j<particles.length;j++){{
        var p2=particles[j],dx2=p.x-p2.x,dy2=p.y-p2.y,d2=Math.sqrt(dx2*dx2+dy2*dy2);
        if(d2<108){{
          ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(p2.x,p2.y);
          ctx.strokeStyle=cfg.lineColor;ctx.lineWidth=0.75;
          ctx.globalAlpha=(1-d2/108)*0.42;ctx.stroke();ctx.globalAlpha=1;
        }}
      }}
      p.phase+=p.speed;
      var dr=p.r+Math.sin(p.phase)*0.4;
      ctx.beginPath();ctx.arc(p.x,p.y,Math.max(0.5,dr),0,Math.PI*2);
      ctx.fillStyle=p.color;ctx.globalAlpha=0.72;ctx.fill();
      ctx.beginPath();ctx.arc(p.x,p.y,dr*2.1,0,Math.PI*2);
      ctx.fillStyle=cfg.glowColor;ctx.globalAlpha=0.2;ctx.fill();
      ctx.globalAlpha=1;
    }}
    requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);
}})();
</script></body></html>"""

    components.html(canvas_html, height=0, width=0)
