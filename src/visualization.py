"""
Visualization Module for Educational Performance Analytics Dashboard.
Creates modern, interactive Plotly charts and visual components with a cohesive
educational design system, responsive layouts, hover tooltips, and rich aesthetics.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

# NumPy 2.0 backward compatibility shim
for _attr, _target in [
    ("round_", np.round),
    ("unicode_", np.str_),
    ("bytes_", bytes),
    ("string_", bytes),
    ("bool_", bool),
    ("int_", int),
    ("float_", float)
]:
    if not hasattr(np, _attr):
        setattr(np, _attr, _target)

import plotly.graph_objects as go


# Design System Color Palette
THEME_COLORS = {
    "primary": "#4F46E5",      # Indigo
    "secondary": "#06B6D4",    # Cyan
    "accent": "#8B5CF6",       # Violet
    "success": "#10B981",      # Emerald
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Rose / Red
    "info": "#3B82F6",         # Blue
    "dark": "#1E293B",         # Slate 800
    "light": "#F8FAFC",        # Slate 50
    "border": "#E2E8F0",       # Slate 200
    "text": "#0F172A"          # Slate 900
}

CATEGORY_COLOR_MAP = {
    "Excellent (16-20)": "#10B981",
    "Good (14-15)": "#3B82F6",
    "Satisfactory (12-13)": "#8B5CF6",
    "Needs Improvement (10-11)": "#F59E0B",
    "Fail / At-Risk (<10)": "#EF4444",
    "Excellent (80-100%)": "#10B981",
    "Good (70-79%)": "#3B82F6",
    "Satisfactory (60-69%)": "#8B5CF6",
    "Needs Improvement (50-59%)": "#F59E0B",
    "Fail / At-Risk (<50%)": "#EF4444",
    "Passed": "#10B981",
    "Failed": "#EF4444",
    "High (>90%)": "#10B981",
    "Moderate (75-90%)": "#F59E0B",
    "Low (<75%)": "#EF4444"
}

CHART_LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", size=12, color="#E2E8F0"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=30, t=50, b=40),
    hoverlabel=dict(bgcolor="#1E293B", font_size=12, font_family="Inter, sans-serif", font_color="#FFFFFF"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        font=dict(color="#E2E8F0"),
        bgcolor="rgba(15,23,42,0.6)",
        bordercolor="rgba(255,255,255,0.1)",
        borderwidth=1
    )
)


def apply_chart_styling(fig: go.Figure, title: str = "", height: int = 400) -> go.Figure:
    """Applies modern typography, gridlines, and layout polish to any Plotly figure."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=15, color="#E2E8F0"),
            x=0.01,
            y=0.98
        ),
        height=height,
        **CHART_LAYOUT_DEFAULTS
    )
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        tickfont=dict(color="#CBD5E1"),
        title_font=dict(color="#CBD5E1")
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        tickfont=dict(color="#CBD5E1"),
        title_font=dict(color="#CBD5E1")
    )
    return fig


def plot_subject_performance(df: pd.DataFrame) -> go.Figure:
    """Subject-wise average performance bar chart with pass rates and error bars."""
    if df.empty or "subject" not in df.columns:
        fig = go.Figure()
        return apply_chart_styling(fig, "No Subject Data Available")

    agg = df.groupby("subject").agg(
        avg_g3=("G3", "mean"),
        std_g3=("G3", "std"),
        avg_g1=("G1", "mean"),
        avg_g2=("G2", "mean"),
        count=("G3", "count"),
        pass_rate=("is_passed", lambda x: round(x.mean() * 100, 1))
    ).reset_index()

    fig = go.Figure()
    
    colors = ["#4F46E5", "#06B6D4", "#8B5CF6", "#10B981"]
    fig.add_trace(go.Bar(
        x=agg["subject"],
        y=agg["avg_g3"].round(2),
        name="Final Score (G3)",
        marker=dict(
            color=[colors[i % len(colors)] for i in range(len(agg))],
            line=dict(color="#312E81", width=1.5)
        ),
        text=[f"<b>{v:.2f}</b><br>Pass: {p}%" for v, p in zip(agg["avg_g3"], agg["pass_rate"])],
        textposition="outside",
        error_y=dict(type="data", array=agg["std_g3"].fillna(0).round(2), visible=True, color="#94A3B8"),
        hovertemplate="<b>%{x}</b><br>Avg Final Score: %{y:.2f} / 20<br>Students: %{customdata[0]}<br>Pass Rate: %{customdata[1]}%<extra></extra>",
        customdata=np.stack((agg["count"], agg["pass_rate"]), axis=-1)
    ))

    # Benchmark reference line
    overall_mean = df["G3"].mean()
    fig.add_hline(
        y=overall_mean,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text=f"Cohort Mean ({overall_mean:.2f})",
        annotation_position="top right"
    )

    fig.update_yaxes(range=[0, 22], title_text="Score (Scale 0 - 20)")
    fig.update_xaxes(title_text="Course Subject")
    return apply_chart_styling(fig, "Subject-Wise Academic Performance & Pass Rates", height=380)


def plot_performance_distribution(df: pd.DataFrame) -> go.Figure:
    """Performance category distribution donut chart."""
    if df.empty or "performance_category" not in df.columns:
        return apply_chart_styling(go.Figure(), "No Performance Category Data")

    counts = df["performance_category"].value_counts().reset_index()
    counts.columns = ["category", "count"]

    # Order standard categories
    cat_order = [
        "Excellent (16-20)", "Good (14-15)", "Satisfactory (12-13)",
        "Needs Improvement (10-11)", "Fail / At-Risk (<10)",
        "Excellent (80-100%)", "Good (70-79%)", "Satisfactory (60-69%)",
        "Needs Improvement (50-59%)", "Fail / At-Risk (<50%)"
    ]
    counts["order"] = counts["category"].map(lambda x: cat_order.index(x) if x in cat_order else 99)
    counts = counts.sort_values(by="order")

    colors = [CATEGORY_COLOR_MAP.get(cat, "#64748B") for cat in counts["category"]]

    fig = go.Figure(data=[go.Pie(
        labels=counts["category"],
        values=counts["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Count: %{value} students<br>Proportion: %{percent}<extra></extra>",
        insidetextorientation="radial"
    )])

    fig.update_layout(
        annotations=[dict(text=f"<b>{len(df)}</b><br>Students", x=0.5, y=0.5, font_size=16, showarrow=False)],
        showlegend=True
    )
    return apply_chart_styling(fig, "Performance Category Distribution", height=380)


def plot_grade_progression(df: pd.DataFrame) -> go.Figure:
    """Comparison of Grade Progression (Period 1 G1 vs Period 2 G2 vs Final G3)."""
    if df.empty:
        return apply_chart_styling(go.Figure(), "No Grade Data")

    grade_cols = [c for c in ["G1", "G2", "G3"] if c in df.columns]
    if not grade_cols:
        return apply_chart_styling(go.Figure(), "Grade Columns Missing")

    fig = go.Figure()
    palette = {"G1": "#6366F1", "G2": "#0EA5E9", "G3": "#10B981"}
    labels = {"G1": "Period 1 (G1)", "G2": "Period 2 (G2)", "G3": "Final Exam (G3)"}

    for col in grade_cols:
        fig.add_trace(go.Box(
            y=df[col],
            name=labels.get(col, col),
            marker_color=palette.get(col, "#4F46E5"),
            boxmean=True,
            boxpoints="outliers",
            jitter=0.2
        ))

    fig.update_yaxes(title_text="Grade Score (0 - 20)", range=[-0.5, 21])
    return apply_chart_styling(fig, "Academic Progression Across Periods (G1 → G2 → G3)", height=380)


def plot_score_histogram(df: pd.DataFrame, score_col: str = "G3") -> go.Figure:
    """Score distribution histogram with mean indicator and performance bands."""
    if df.empty or score_col not in df.columns:
        return apply_chart_styling(go.Figure(), "No Score Distribution Data")

    fig = go.Figure()

    if "performance_category" in df.columns:
        for cat, sub_df in df.groupby("performance_category"):
            fig.add_trace(go.Histogram(
                x=sub_df[score_col],
                name=cat,
                marker_color=CATEGORY_COLOR_MAP.get(cat, "#64748B"),
                opacity=0.75,
                xbins=dict(start=-0.5, end=20.5, size=1.0)
            ))
        fig.update_layout(barmode="stack")
    else:
        fig.add_trace(go.Histogram(
            x=df[score_col],
            marker_color="#4F46E5",
            opacity=0.8,
            xbins=dict(start=-0.5, end=20.5, size=1.0)
        ))

    mean_val = df[score_col].mean()
    median_val = df[score_col].median()

    fig.add_vline(x=mean_val, line_dash="dash", line_color="#1E293B", line_width=2,
                  annotation_text=f"Mean ({mean_val:.2f})", annotation_position="top left")
    fig.add_vline(x=median_val, line_dash="dot", line_color="#10B981", line_width=2,
                  annotation_text=f"Median ({median_val:.2f})", annotation_position="top right")

    fig.update_xaxes(title_text=f"{score_col} Score (Scale 0 - 20)", range=[-0.5, 20.5])
    fig.update_yaxes(title_text="Number of Students")
    return apply_chart_styling(fig, f"Score Distribution & Frequency ({score_col})", height=380)


def plot_group_comparison(
    df: pd.DataFrame,
    group_col: str,
    target_col: str = "G3",
    chart_type: str = "box"
) -> go.Figure:
    """Multi-variable cohort comparison chart (box, violin, or grouped bar)."""
    if df.empty or group_col not in df.columns or target_col not in df.columns:
        return apply_chart_styling(go.Figure(), f"Cannot compare {group_col}")

    clean_group_name = group_col.replace("_", " ").title()
    fig = go.Figure()

    palette = ["#4F46E5", "#06B6D4", "#8B5CF6", "#10B981", "#F59E0B", "#EC4899", "#3B82F6", "#64748B"]

    if chart_type == "violin":
        for i, (g_name, g_df) in enumerate(df.groupby(group_col)):
            fig.add_trace(go.Violin(
                y=g_df[target_col],
                name=str(g_name),
                box_visible=True,
                meanline_visible=True,
                line_color=palette[i % len(palette)]
            ))
    elif chart_type == "bar":
        agg = df.groupby(group_col)[target_col].agg(["mean", "std", "count"]).reset_index()
        fig.add_trace(go.Bar(
            x=agg[group_col],
            y=agg["mean"].round(2),
            error_y=dict(type="data", array=agg["std"].fillna(0).round(2)),
            marker_color=[palette[i % len(palette)] for i in range(len(agg))],
            text=[f"<b>{m:.2f}</b><br>n={c}" for m, c in zip(agg["mean"], agg["count"])],
            textposition="outside"
        ))
    else:  # box plot
        for i, (g_name, g_df) in enumerate(df.groupby(group_col)):
            fig.add_trace(go.Box(
                y=g_df[target_col],
                name=str(g_name),
                boxmean=True,
                marker_color=palette[i % len(palette)]
            ))

    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text=clean_group_name)
    fig.update_yaxes(title_text=f"{target_col} Score")
    return apply_chart_styling(fig, f"Comparative Performance Analysis by {clean_group_name}", height=400)


def plot_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Annotated correlation heatmap for numerical academic and behavioral factors."""
    if corr_df.empty:
        return apply_chart_styling(go.Figure(), "No Correlation Data Available")

    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns,
        y=corr_df.index,
        colorscale="Tealrose",
        zmin=-1,
        zmax=1,
        colorbar=dict(title="Pearson r", thickness=15, len=0.8),
        text=corr_df.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))

    fig.update_layout(height=520, margin=dict(l=60, r=40, t=50, b=60))
    return apply_chart_styling(fig, "Factor Correlation Matrix (Grades, Study Time, Absences, Family)", height=520)


def plot_student_radar(student: pd.Series, cohort_df: pd.DataFrame) -> go.Figure:
    """Radar chart comparing an individual student's multidimensional scores to cohort benchmarks."""
    categories = ["Final (G3)", "Period 1 (G1)", "Period 2 (G2)", "Study Time", "Attendance %", "Parent Edu"]
    
    # Scale all metrics to 0-100% for fair radar comparison
    def get_scaled(series_or_row):
        g3 = (series_or_row.get("G3", 10) / 20.0 * 100)
        g1 = (series_or_row.get("G1", 10) / 20.0 * 100)
        g2 = (series_or_row.get("G2", 10) / 20.0 * 100)
        st = (series_or_row.get("studytime", 2) / 4.0 * 100)
        att = series_or_row.get("attendance_rate", 85)
        pedu = ((series_or_row.get("Medu", 2) + series_or_row.get("Fedu", 2)) / 8.0 * 100)
        return [g3, g1, g2, st, att, pedu]

    student_vals = get_scaled(student)
    cohort_means = {
        "G3": cohort_df["G3"].mean() if "G3" in cohort_df.columns else 10,
        "G1": cohort_df["G1"].mean() if "G1" in cohort_df.columns else 10,
        "G2": cohort_df["G2"].mean() if "G2" in cohort_df.columns else 10,
        "studytime": cohort_df["studytime"].mean() if "studytime" in cohort_df.columns else 2,
        "attendance_rate": cohort_df["attendance_rate"].mean() if "attendance_rate" in cohort_df.columns else 85,
        "Medu": cohort_df["Medu"].mean() if "Medu" in cohort_df.columns else 2.5,
        "Fedu": cohort_df["Fedu"].mean() if "Fedu" in cohort_df.columns else 2.5
    }
    cohort_vals = get_scaled(cohort_means)

    fig = go.Figure()

    # Cohort Benchmark trace
    fig.add_trace(go.Scatterpolar(
        r=cohort_vals + [cohort_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(148, 163, 184, 0.2)",
        line=dict(color="#94A3B8", dash="dash"),
        name="Cohort Average Benchmark"
    ))

    # Student trace
    fig.add_trace(go.Scatterpolar(
        r=student_vals + [student_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(79, 70, 229, 0.35)",
        line=dict(color="#4F46E5", width=2.5),
        name=f"Student ({student.get('student_id', 'Selected')})"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%"),
        ),
        showlegend=True,
        height=400
    )
    return apply_chart_styling(fig, "Multidimensional Student Radar vs. Cohort Benchmark", height=400)


def plot_student_grade_timeline(student: pd.Series, cohort_df: pd.DataFrame) -> go.Figure:
    """Historical timeline trajectory for a single student (G1 -> G2 -> G3)."""
    periods = ["Period 1 (G1)", "Period 2 (G2)", "Final Exam (G3)"]
    student_scores = [student.get("G1", 0), student.get("G2", 0), student.get("G3", 0)]
    cohort_scores = [
        cohort_df["G1"].mean() if "G1" in cohort_df.columns else 0,
        cohort_df["G2"].mean() if "G2" in cohort_df.columns else 0,
        cohort_df["G3"].mean() if "G3" in cohort_df.columns else 0
    ]

    fig = go.Figure()

    # Cohort Trend Line
    fig.add_trace(go.Scatter(
        x=periods,
        y=cohort_scores,
        mode="lines+markers",
        name="Cohort Average",
        line=dict(color="#94A3B8", width=2, dash="dash"),
        marker=dict(size=8)
    ))

    # Student Trend Line
    trend_color = "#10B981" if student_scores[-1] >= student_scores[0] else "#EF4444"
    fig.add_trace(go.Scatter(
        x=periods,
        y=student_scores,
        mode="lines+markers+text",
        name=f"Student {student.get('student_id', '')}",
        text=[f"<b>{s:.1f}</b>" for s in student_scores],
        textposition="top center",
        line=dict(color=trend_color, width=3.5),
        marker=dict(size=12, color=trend_color, symbol="circle")
    ))

    fig.add_hline(y=10, line_dash="dot", line_color="#F59E0B", annotation_text="Pass Line (10.0)")
    fig.update_yaxes(range=[0, 21], title_text="Score (0 - 20)")
    return apply_chart_styling(fig, "Term Grade Progression & Trajectory", height=350)


def plot_learning_gap_bars(gap_df: pd.DataFrame) -> go.Figure:
    """Divergent horizontal bar chart showing performance gaps from benchmark."""
    if gap_df.empty or "Gap from Benchmark" not in gap_df.columns:
        return apply_chart_styling(go.Figure(), "No Gap Data")

    colors = ["#10B981" if x >= 0 else "#EF4444" for x in gap_df["Gap from Benchmark"]]

    fig = go.Figure(go.Bar(
        x=gap_df["Gap from Benchmark"],
        y=gap_df["Subject"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="#1E293B", width=1)),
        text=[f"{'+' if g >= 0 else ''}{g:.2f} pts" for g in gap_df["Gap from Benchmark"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Gap from Benchmark: %{x:+.2f} pts<extra></extra>"
    ))

    fig.add_vline(x=0, line_width=1.5, line_color="#334155")
    fig.update_xaxes(title_text="Gap from Cohort Benchmark (Points)")
    return apply_chart_styling(fig, "Subject Disparity Gap from Cohort Benchmark", height=320)


def plot_confusion_matrix(cm: np.ndarray, classes: List[str]) -> go.Figure:
    """Interactive confusion matrix heatmap."""
    row_sums = cm.sum(axis=1)[:, np.newaxis]
    row_sums[row_sums == 0] = 1
    cm_norm = cm.astype("float") / row_sums
    cm_norm = np.nan_to_num(cm_norm)

    text_labels = [
        [f"<b>{count}</b><br>({pct:.1%})" for count, pct in zip(row_counts, row_pcts)]
        for row_counts, row_pcts in zip(cm, cm_norm)
    ]

    fig = go.Figure(data=go.Heatmap(
        z=cm_norm,
        x=[f"Pred: {c}" for c in classes],
        y=[f"True: {c}" for c in classes],
        colorscale="Blues",
        text=text_labels,
        texttemplate="%{text}",
        colorbar=dict(title="Normalized Rate", thickness=15),
        hoverongaps=False
    ))

    fig.update_layout(height=420, margin=dict(l=60, r=40, t=50, b=40))
    return apply_chart_styling(fig, "Model Confusion Matrix (Predictions vs. Ground Truth)", height=420)


def plot_feature_importance(fi_list: List[Dict[str, Any]]) -> go.Figure:
    """Top feature importance horizontal bar chart."""
    if not fi_list:
        return apply_chart_styling(go.Figure(), "No Feature Importance Available")

    df_fi = pd.DataFrame(fi_list).sort_values(by="importance", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_fi["importance"],
        y=df_fi["feature"],
        orientation="h",
        marker=dict(
            color=df_fi["importance"],
            colorscale="Viridis",
            line=dict(color="#1E293B", width=1)
        ),
        text=[f"{v:.3f}" for v in df_fi["importance"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Importance Weight: %{x:.4f}<extra></extra>"
    ))

    fig.update_xaxes(title_text="Relative Feature Importance Weight")
    return apply_chart_styling(fig, "Top Predictive Academic & Behavioral Features", height=450)
