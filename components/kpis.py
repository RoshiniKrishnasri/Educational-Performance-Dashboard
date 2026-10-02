"""
KPI and Metric Cards Component for Educational Performance Dashboard.
Renders responsive, beautifully styled metric summary cards with status indicators.
"""

from typing import Any, Dict
import pandas as pd
import streamlit as st


def render_kpi_card(
    label: str,
    value: str,
    subtitle: str = "",
    badge_text: str = "",
    badge_type: str = "primary",  # primary, success, warning, danger, info
    icon_svg: str = ""
) -> str:
    """Generates modern HTML/CSS for a glassmorphic KPI card with responsive theme styling."""
    badge_class_map = {
        "primary": "badge-primary",
        "success": "badge-success",
        "warning": "badge-warning",
        "danger": "badge-danger",
        "info": "badge-info"
    }
    b_class = badge_class_map.get(badge_type, "badge-primary")

    badge_html = f'<span class="kpi-badge {b_class}">{badge_text}</span>' if badge_text else ""
    sub_html = f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ""

    return f"""
    <div class="kpi-glass-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <span class="kpi-label">{label}</span>
            {badge_html}
        </div>
        <div>
            <div class="kpi-value">{value}</div>
            {sub_html}
        </div>
    </div>
    """


def render_overview_kpis(df: pd.DataFrame, desc_stats: Dict[str, Any]) -> None:
    """Renders the top KPI row for the Overview page."""
    if df.empty or not desc_stats:
        st.warning("No student records available for current filter selection.")
        return

    total_students = len(df)
    avg_score = desc_stats.get("mean", 0.0)
    is_20_scale = desc_stats.get("is_20_scale", True)
    
    pass_rate = desc_stats.get("pass_rate_pct", 0.0)
    fail_rate = desc_stats.get("fail_rate_pct", 0.0)
    passed_count = desc_stats.get("pass_count", 0)
    failed_count = desc_stats.get("fail_count", 0)

    at_risk_count = int(df["is_at_risk"].sum()) if "is_at_risk" in df.columns else 0
    at_risk_pct = round((at_risk_count / total_students) * 100, 1) if total_students > 0 else 0.0

    avg_attendance = round(df["attendance_rate"].mean(), 1) if "attendance_rate" in df.columns else 90.0

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(render_kpi_card(
            label="Total Students",
            value=f"{total_students:,}",
            subtitle="Active enrollment cohort",
            badge_text="Cohort",
            badge_type="primary"
        ), unsafe_allow_html=True)

    with c2:
        score_sub = f"{((avg_score/20)*100):.1f}% equivalent" if is_20_scale else "Overall cohort mean"
        st.markdown(render_kpi_card(
            label="Average Score",
            value=f"{avg_score:.2f}" + ("/20" if is_20_scale else "%"),
            subtitle=score_sub,
            badge_text="Scale 0-20" if is_20_scale else "Scale 0-100",
            badge_type="info"
        ), unsafe_allow_html=True)

    with c3:
        st.markdown(render_kpi_card(
            label="Pass Percentage",
            value=f"{pass_rate:.1f}%",
            subtitle=f"{passed_count} students meeting standard",
            badge_text="≥ 10.0 pts",
            badge_type="success" if pass_rate >= 75 else "warning"
        ), unsafe_allow_html=True)

    with c4:
        st.markdown(render_kpi_card(
            label="Failure Percentage",
            value=f"{fail_rate:.1f}%",
            subtitle=f"{failed_count} students under benchmark",
            badge_text="< 10.0 pts",
            badge_type="danger" if fail_rate > 25 else "warning"
        ), unsafe_allow_html=True)

    with c5:
        st.markdown(render_kpi_card(
            label="At-Risk Students",
            value=f"{at_risk_count}",
            subtitle=f"{at_risk_pct}% flagged for intervention",
            badge_text="Alert",
            badge_type="danger" if at_risk_pct > 30 else "warning"
        ), unsafe_allow_html=True)

    with c6:
        st.markdown(render_kpi_card(
            label="Avg. Attendance",
            value=f"{avg_attendance:.1f}%",
            subtitle="Estimated academic presence",
            badge_text="Attendance",
            badge_type="success" if avg_attendance >= 90 else "info"
        ), unsafe_allow_html=True)
