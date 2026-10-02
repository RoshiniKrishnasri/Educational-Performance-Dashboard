"""
Chart container components and layout wrappers for Educational Performance Dashboard.
"""

from typing import Optional
import plotly.graph_objects as go
import streamlit as st


def render_chart_card(
    fig: go.Figure,
    title: str = "",
    subtitle: str = "",
    badge: Optional[str] = None,
    use_container_width: bool = True
) -> None:
    """Renders a chart within a styled card container."""
    badge_html = f'<span style="background: #EEF2FF; color: #4F46E5; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 9999px; border: 1px solid #C7D2FE;">{badge}</span>' if badge else ""
    sub_html = f'<p style="font-size: 0.8rem; color: var(--app-text-sub, #64748B); margin: 2px 0 10px 0;">{subtitle}</p>' if subtitle else ""

    if title:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
            <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--app-text-main, #1E293B); margin: 0;">{title}</h3>
            {badge_html}
        </div>
        {sub_html}
        """, unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=use_container_width, config={
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"]
    })
