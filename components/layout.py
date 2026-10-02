"""
Header and Footer Layout Components for Educational Performance Dashboard.
Provides interactive header with Dark/Light mode toggle and glassmorphic footer.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_header(filtered_df: pd.DataFrame, metadata: Dict[str, Any]) -> None:
    """
    Renders the interactive dashboard header with:
    - Title & Subtitle
    - Data source & student count pills
    - Quick Student Search Input (with 🔍 icon)
    - Interactive Dark/Light mode theme toggle switch
    """
    from components.background import init_theme_state, on_header_toggle_change

    init_theme_state()

    col_title, col_search, col_toggle = st.columns([3.6, 1.8, 1.0], vertical_alignment="center")

    source_label = metadata.get("source_label", "UCI Student Performance")
    student_count = len(filtered_df)

    with col_title:
        st.markdown(f"""
        <div class="dashboard-header" style="margin-bottom: 0px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h1>🎓 EduAnalytics Pro</h1>
                    <p style="font-weight: 500; font-size: 0.95rem;">
                        Educational Performance Analytics • Learning Diagnostics • ML Intelligence
                    </p>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span class="status-pill pill-blue">📊 Dataset: {source_label}</span>
                    <span class="status-pill pill-green">✓ Validated ({student_count:,} Students)</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_search:
        s_col, x_col = st.columns([5, 1], vertical_alignment="center")
        with s_col:
            st.text_input(
                "Search Student",
                key="header_student_search",
                placeholder="🔍 Search student, school, category…",
                label_visibility="collapsed",
                help="Type student ID, school name, or category to filter records"
            )
        with x_col:
            if st.session_state.get("header_student_search", "").strip():
                if st.button("✕", key="clear_search_btn", help="Clear search",
                             use_container_width=True):
                    st.session_state["header_student_search"] = ""
                    st.rerun()

    with col_toggle:
        st.toggle(
            "🌙 Dark Mode",
            key="header_dark_mode_toggle",
            on_change=on_header_toggle_change,
            help="Toggle between Dark (Cosmic) and Light (Aurora) visual themes"
        )

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


def render_footer() -> None:
    """
    Renders a glassmorphic footer at the bottom of the dashboard.
    """
    st.markdown("""
    <div class="dashboard-footer">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.3rem;">🎓</span>
                <strong style="font-size: 1rem; font-weight: 700; letter-spacing: -0.01em;">EduAnalytics Pro</strong>
                <span style="opacity: 0.45; font-size: 1rem;">|</span>
                <span style="font-size: 0.82rem; opacity: 0.85;">Developed by <strong style="color: inherit;">Roshini Krishna Sri</strong></span>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
                <a href="mailto:roshinikrishnasri@gmail.com" target="_blank" class="footer-badge footer-contact-badge" style="text-decoration: none;">
                    ✉️ roshinikrishnasri@gmail.com
                </a>
                <a href="https://github.com/roshinikrishnasri" target="_blank" class="footer-badge footer-contact-badge" style="text-decoration: none;">
                    💻 GitHub
                </a>
                <a href="https://www.linkedin.com/in/roshinikrishnasri" target="_blank" class="footer-badge footer-contact-badge" style="text-decoration: none;">
                    🔗 LinkedIn
                </a>
                <span class="footer-badge">🐍 Python 3.9</span>
                <span class="footer-badge">🚀 Streamlit 1.50</span>
                <span class="footer-badge">📊 Plotly</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
