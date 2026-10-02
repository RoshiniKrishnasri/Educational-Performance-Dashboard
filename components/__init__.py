"""Dashboard UI Components Package"""

from components.background import inject_interactive_background, render_background_controls
from components.charts import render_chart_card
from components.filters import render_sidebar_filters
from components.kpis import render_kpi_card, render_overview_kpis
from components.layout import render_header, render_footer
from components.pages import render_home_page, render_about_page

__all__ = [
    "inject_interactive_background",
    "render_background_controls",
    "render_chart_card",
    "render_sidebar_filters",
    "render_kpi_card",
    "render_overview_kpis",
    "render_header",
    "render_footer",
    "render_home_page",
    "render_about_page",
]
