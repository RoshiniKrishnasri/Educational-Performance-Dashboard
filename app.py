"""
Educational Performance Analytics Dashboard.
A comprehensive, interactive Streamlit web application for student performance analysis,
learning-gap identification, multi-attribute comparisons, machine learning insights,
and dynamic reporting.
"""

import io
import json
import os
from datetime import datetime
import numpy as np

# NumPy 2.0 compatibility shim
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

import pandas as pd
import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="EduAnalytics Pro | Student Performance Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import internal modules
from src.analytics import (
    compute_correlations,
    compute_descriptive_stats,
    compute_group_aggregates,
    compute_learning_gap_analysis
)
from src.data_loader import analyze_data_quality, load_builtin_dataset
from src.db import delete_dataset_from_db, init_db, list_saved_datasets, save_dataset_to_db, save_snapshot
from src.insights import (
    generate_learning_gap_insights,
    generate_overview_insights,
    generate_student_recommendations
)
from src.ml_model import (
    predict_single_student,
    train_performance_classifier
)
from src.visualization import (
    plot_confusion_matrix,
    plot_correlation_heatmap,
    plot_feature_importance,
    plot_grade_progression,
    plot_group_comparison,
    plot_learning_gap_bars,
    plot_performance_distribution,
    plot_score_histogram,
    plot_student_grade_timeline,
    plot_student_radar,
    plot_subject_performance
)
from components.background import inject_interactive_background, render_background_controls
from components.charts import render_chart_card
from components.filters import render_sidebar_filters
from components.kpis import render_overview_kpis
from components.layout import render_header, render_footer
from components.pages import render_home_page, render_about_page


def main():
    # Initialize SQLite database
    init_db()

    # Dynamic Interactive Canvas Background & Ambience Theme
    bg_config = render_background_controls()
    inject_interactive_background(bg_config)

    # Load baseline default dataframe
    default_df = load_builtin_dataset("combined")

    # Render Sidebar Filters
    filtered_df, filter_state, metadata = render_sidebar_filters(default_df)

    # Apply Header Quick Search Filter if query entered
    search_query = st.session_state.get("header_student_search", "").strip().lower()
    if search_query:
        search_mask = pd.Series(False, index=filtered_df.index)
        for col in ["student_id", "school_name", "performance_category", "subject"]:
            if col in filtered_df.columns:
                search_mask = search_mask | filtered_df[col].astype(str).str.lower().str.contains(search_query, na=False)
        filtered_df = filtered_df[search_mask]

    if filtered_df.empty:
        search_active = bool(st.session_state.get("header_student_search", "").strip())
        if search_active:
            st.warning(f"🔍 No results for **\"{st.session_state['header_student_search']}\"**. Clear the search to restore all records.")
            if st.button("✕ Clear Search", key="empty_clear_search"):
                st.session_state["header_student_search"] = ""
                st.rerun()
        else:
            st.error("No student records match the active filters. Please adjust or reset your sidebar filters.")
            if st.button("Reset Filters"):
                for key in list(st.session_state.keys()):
                    if key.startswith("filter_"):
                        del st.session_state[key]
                st.rerun()
        return

    # Calculate Data Quality Metrics
    raw_df = metadata.get("raw_df", filtered_df)
    data_quality = analyze_data_quality(raw_df, filtered_df)

    # Compute Core Descriptive Stats & Analytics
    desc_stats = compute_descriptive_stats(filtered_df, target_col="G3")

    source_label = metadata.get("source_label", "UCI Student Performance")

    # Dashboard Main Header with Dark/Light Toggle
    render_header(filtered_df, metadata)

    # Navigation Tabs (8 Pages)
    tabs = st.tabs([
        "🏠 Home",
        "📌 Overview",
        "📈 Performance Analysis",
        "👤 Student Dossier",
        "🎯 Learning Gap Analysis",
        "🤖 ML Insights",
        "📑 Reports & Export",
        "ℹ️ About"
    ])

    # =========================================================================
    # HOME PAGE
    # =========================================================================
    with tabs[0]:
        render_home_page(filtered_df, desc_stats, metadata)

    # =========================================================================
    # PAGE 1 — OVERVIEW
    # =========================================================================
    with tabs[1]:
        st.subheader("Executive Academic Overview")
        render_overview_kpis(filtered_df, desc_stats)

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # Overview Visuals Row 1
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            fig_subj = plot_subject_performance(filtered_df)
            render_chart_card(fig_subj)
        with col_c2:
            fig_dist = plot_performance_distribution(filtered_df)
            render_chart_card(fig_dist)

        # Overview Visuals Row 2
        col_c3, col_c4 = st.columns([1, 1])
        with col_c3:
            fig_prog = plot_grade_progression(filtered_df)
            render_chart_card(fig_prog)
        with col_c4:
            fig_hist = plot_score_histogram(filtered_df, score_col="G3")
            render_chart_card(fig_hist)

        # Dynamic Insights & Data Quality Summary
        st.markdown("<hr style='margin: 20px 0; border-color: rgba(226,232,240,0.3); opacity: 0.5;'>", unsafe_allow_html=True)
        col_ins, col_dq = st.columns([1.2, 0.8])

        with col_ins:
            st.markdown("### 💡 Dynamic Analytical Insights")
            insights = generate_overview_insights(filtered_df, desc_stats)
            for ins in insights:
                border_color = (
                    "#10B981" if ins["type"] == "success"
                    else "#EF4444" if ins["type"] == "danger"
                    else "#F59E0B" if ins["type"] == "warning"
                    else "#4F46E5"
                )
                st.markdown(f"""
                <div class="insight-card" style="border-left-color: {border_color};">
                    <strong class="insight-title">{ins['title']}</strong>
                    <div class="insight-body">{ins['text']}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_dq:
            st.markdown("### 🛡️ Data Quality Summary")
            with st.container():
                st.markdown(f"""
                <div class="edu-card" style="padding: 18px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span class="dq-label">Total Records Ingested:</span>
                        <strong class="dq-val">{data_quality['total_rows']:,}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span class="dq-label">Cleaned Active Records:</span>
                        <strong style="color: #059669;">{data_quality['cleaned_rows']:,}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span class="dq-label">Duplicate Records Detected:</span>
                        <strong style="color: {'#DC2626' if data_quality['duplicate_rows'] > 0 else '#059669'};">{data_quality['duplicate_rows']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span class="dq-label">Missing Cells Imputed:</span>
                        <strong style="color: {'#D97706' if data_quality['total_missing_cells'] > 0 else '#059669'};">{data_quality['total_missing_cells']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span class="dq-label">Invalid Values Coerced:</span>
                        <strong style="color: {'#DC2626' if data_quality['invalid_values_count'] > 0 else '#059669'};">{data_quality['invalid_values_count']}</strong>
                    </div>
                    <hr class="dq-hr">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="dq-title">Data Quality Index:</span>
                        <span class="status-pill {'pill-green' if data_quality['quality_score_pct'] >= 95 else 'pill-yellow'}">
                            {data_quality['quality_score_pct']}% Clean
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # =========================================================================
    # PAGE 2 — PERFORMANCE ANALYSIS
    # =========================================================================
    with tabs[2]:
        st.subheader("Multidimensional Comparative Performance Analysis")
        st.caption("Investigate academic disparities across demographic, behavioral, and family factors.")

        # Interactive controls for comparisons
        c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([1, 1, 1])

        compare_options = {
            "Subject": "subject",
            "Gender": "gender",
            "Study Time": "studytime_label",
            "Attendance Category": "attendance_category",
            "Performance Category": "performance_category",
            "School": "school_name",
            "Address (Urban / Rural)": "address_type",
            "Mother's Education": "medu_label",
            "Father's Education": "fedu_label",
            "Internet Access": "internet",
            "Higher Education Aspiration": "higher",
            "Extra Educational Support": "schoolsup",
            "Family Size": "famsize_label"
        }
        # Filter available options
        avail_options = {k: v for k, v in compare_options.items() if v in filtered_df.columns}

        with c_ctrl1:
            selected_group_label = st.selectbox("Primary Comparison Factor", options=list(avail_options.keys()), index=1)
            group_col = avail_options[selected_group_label]

        with c_ctrl2:
            metric_options = {"Final Exam Score (G3)": "G3", "Period 1 Score (G1)": "G1", "Period 2 Score (G2)": "G2", "Average Score": "average_score", "Absences": "absences", "Attendance Rate (%)": "attendance_rate"}
            avail_metrics = {k: v for k, v in metric_options.items() if v in filtered_df.columns}
            selected_metric_label = st.selectbox("Target Academic Metric", options=list(avail_metrics.keys()), index=0)
            target_metric_col = avail_metrics[selected_metric_label]

        with c_ctrl3:
            chart_type_choice = st.selectbox("Chart Style", options=["Box Plot (Distribution & Outliers)", "Violin Plot (Density & Spread)", "Aggregated Bar Chart (Means & Errors)"], index=0)
            chart_mode = "violin" if "Violin" in chart_type_choice else "bar" if "Bar" in chart_type_choice else "box"

        # Render Comparative Chart
        fig_comp = plot_group_comparison(filtered_df, group_col=group_col, target_col=target_metric_col, chart_type=chart_mode)
        render_chart_card(fig_comp)

        # Cohort Aggregate Summary Table
        st.markdown("#### 📋 Cohort Performance Aggregates")
        agg_table = compute_group_aggregates(filtered_df, group_col=group_col)
        st.dataframe(agg_table, use_container_width=True)

        st.markdown("<hr style='margin: 24px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)

        # Correlation Analysis Section
        st.subheader("Correlation Analysis & Top Academic Drivers")
        st.caption("Identify multi-variable relationships between grades, attendance, study habits, and lifestyle factors.")

        col_corr1, col_corr2 = st.columns([1.2, 0.8])

        corr_matrix, top_corrs = compute_correlations(filtered_df)

        with col_corr1:
            fig_corr = plot_correlation_heatmap(corr_matrix)
            render_chart_card(fig_corr)

        with col_corr2:
            st.markdown("#### 🎯 Top Correlates with Final Score (G3)")
            if top_corrs:
                corr_df_display = pd.DataFrame(top_corrs)
                style_func = lambda v: "color: #059669; font-weight: 600;" if v == "Positive" else "color: #DC2626; font-weight: 600;" if v == "Negative" else ""
                styler = corr_df_display.style.map(style_func, subset=["direction"]) if hasattr(corr_df_display.style, "map") else corr_df_display.style.applymap(style_func, subset=["direction"])
                st.dataframe(
                    styler,
                    use_container_width=True,
                    height=450
                )
            else:
                st.info("Insufficient numeric features to compute correlations.")

    # =========================================================================
    # PAGE 3 — STUDENT ANALYSIS
    # =========================================================================
    with tabs[3]:
        st.subheader("Individual Student Profile & Diagnostic Dossier")
        st.caption("Inspect individual student scorecards, longitudinal progress trajectories, and customized recommendations.")

        if "student_id" not in filtered_df.columns:
            st.warning("Student ID column not available.")
        else:
            student_list = filtered_df["student_id"].tolist()
            col_sel1, col_sel2 = st.columns([1, 2])
            with col_sel1:
                selected_student_id = st.selectbox("Select Student ID", options=student_list, index=0)
            
            # Retrieve single student record
            student_row = filtered_df[filtered_df["student_id"] == selected_student_id].iloc[0]

            # Student Snapshot Dossier Header
            risk_badge = (
                "pill-red" if student_row.get("risk_level") == "Critical Risk"
                else "pill-yellow" if student_row.get("risk_level") == "Moderate Risk"
                else "pill-green"
            )

            st.markdown(f"""
            <div class="edu-card" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <h2 style="font-size: 1.4rem; font-weight: 700; margin: 0;">
                            👤 Student Dossier: {selected_student_id}
                        </h2>
                        <div style="font-size: 0.85rem; margin-top: 4px; opacity: 0.75;">
                            <b>School:</b> {student_row.get('school_name', 'N/A')} | 
                            <b>Subject:</b> {student_row.get('subject', 'General')} | 
                            <b>Gender:</b> {student_row.get('gender', 'N/A')} | 
                            <b>Age:</b> {student_row.get('age', 'N/A')} yrs
                        </div>
                    </div>
                    <div>
                        <span class="status-pill {risk_badge}">Status: {student_row.get('risk_level', 'On Track')}</span>
                        <span class="status-pill pill-blue">{student_row.get('performance_category', 'Category')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Score & Metric Cards Row
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            with m1:
                st.metric("Final Score (G3)", f"{student_row.get('G3', 0)} / 20", delta=f"{student_row.get('grade_change', 0):+.1f} vs G1")
            with m2:
                st.metric("Period 1 (G1)", f"{student_row.get('G1', 0)} / 20")
            with m3:
                st.metric("Period 2 (G2)", f"{student_row.get('G2', 0)} / 20")
            with m4:
                st.metric("Study Time", f"{student_row.get('studytime_label', 'N/A')}")
            with m5:
                st.metric("Attendance Rate", f"{student_row.get('attendance_rate', 0)}%", delta=f"{int(student_row.get('absences', 0))} absences", delta_color="inverse")
            with m6:
                st.metric("Past Failures", f"{int(student_row.get('failures', 0))}")

            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

            # Student Visuals
            col_s_vis1, col_s_vis2 = st.columns([1, 1])
            with col_s_vis1:
                fig_radar = plot_student_radar(student_row, filtered_df)
                render_chart_card(fig_radar)
            with col_s_vis2:
                fig_timeline = plot_student_grade_timeline(student_row, filtered_df)
                render_chart_card(fig_timeline)

            # Student Recommendations & Peer Comparison
            col_rec, col_peer = st.columns([1.1, 0.9])
            with col_rec:
                st.markdown("### 📝 Pedagogical Recommendations for Educator")
                recs = generate_student_recommendations(student_row, filtered_df)
                for r in recs:
                    acc_color = '#DC2626' if r['priority']=='High' else '#2563EB' if r['priority']=='Positive' else '#F59E0B'
                    st.markdown(f"""
                    <div class="insight-card" style="border-left-color: {acc_color} !important; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-weight: 700; font-size: 0.88rem;">{r['badge']}</span>
                            <span style="font-size: 0.75rem; opacity: 0.7;">Priority: {r['priority']}</span>
                        </div>
                        <div style="font-size: 0.84rem; opacity: 0.88;">{r['text']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_peer:
                st.markdown("### 📊 Peer Benchmark Comparison")
                school_cohort = filtered_df[filtered_df["school_name"] == student_row.get("school_name")] if "school_name" in filtered_df.columns else filtered_df
                
                peer_data = {
                    "Metric": ["Final Score (G3)", "Period 1 (G1)", "Period 2 (G2)", "Attendance Rate", "Absences", "Study Time (hrs/wk)"],
                    "Student Value": [
                        f"{student_row.get('G3', 0):.1f}",
                        f"{student_row.get('G1', 0):.1f}",
                        f"{student_row.get('G2', 0):.1f}",
                        f"{student_row.get('attendance_rate', 0):.1f}%",
                        f"{student_row.get('absences', 0):.0f}",
                        f"{student_row.get('studytime', 0):.1f}"
                    ],
                    "School Avg": [
                        f"{school_cohort['G3'].mean():.1f}" if "G3" in school_cohort else "-",
                        f"{school_cohort['G1'].mean():.1f}" if "G1" in school_cohort else "-",
                        f"{school_cohort['G2'].mean():.1f}" if "G2" in school_cohort else "-",
                        f"{school_cohort['attendance_rate'].mean():.1f}%" if "attendance_rate" in school_cohort else "-",
                        f"{school_cohort['absences'].mean():.1f}" if "absences" in school_cohort else "-",
                        f"{school_cohort['studytime'].mean():.1f}" if "studytime" in school_cohort else "-"
                    ],
                    "Overall Cohort": [
                        f"{filtered_df['G3'].mean():.1f}" if "G3" in filtered_df else "-",
                        f"{filtered_df['G1'].mean():.1f}" if "G1" in filtered_df else "-",
                        f"{filtered_df['G2'].mean():.1f}" if "G2" in filtered_df else "-",
                        f"{filtered_df['attendance_rate'].mean():.1f}%" if "attendance_rate" in filtered_df else "-",
                        f"{filtered_df['absences'].mean():.1f}" if "absences" in filtered_df else "-",
                        f"{filtered_df['studytime'].mean():.1f}" if "studytime" in filtered_df else "-"
                    ]
                }
                st.dataframe(pd.DataFrame(peer_data), use_container_width=True)

    # =========================================================================
    # PAGE 4 — LEARNING GAP ANALYSIS
    # =========================================================================
    with tabs[4]:
        st.subheader("Learning Gap & Academic Equity Diagnostic")
        st.caption("Identify subjects and student cohorts with comparatively lower performance and equity gaps.")

        # Interactive Threshold Controller
        col_t1, col_t2, col_t3 = st.columns([1.5, 1, 1])
        with col_t1:
            threshold_val = st.slider(
                "Competency / Passing Score Threshold",
                min_value=5.0,
                max_value=18.0,
                value=10.0,
                step=0.5,
                help="Adjust competency threshold to analyze learning gaps and underperforming cohorts."
            )

        gap_analysis = compute_learning_gap_analysis(filtered_df, threshold=threshold_val)

        with col_t2:
            st.metric("Cohort Benchmark Mean", f"{gap_analysis['benchmark_mean']:.2f} / 20")
        with col_t3:
            st.metric("Students Below Threshold", f"{gap_analysis['students_below_threshold']}", delta=f"{gap_analysis['pct_below_threshold']}% of cohort", delta_color="inverse")

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Learning Gap Charts
        col_gap1, col_gap2 = st.columns([1, 1])
        with col_gap1:
            fig_gap_bar = plot_learning_gap_bars(gap_analysis["subject_gaps"])
            render_chart_card(fig_gap_bar)
        with col_gap2:
            st.markdown("#### 🎯 Subject Equity & Threshold Breakdown")
            st.dataframe(gap_analysis["subject_gaps"], use_container_width=True)

        st.markdown("<hr style='margin: 20px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)

        # Lowest Performing Cohorts & Dynamic Observations
        col_obs1, col_obs2 = st.columns([1.1, 0.9])
        with col_obs1:
            st.markdown("### 🔍 Underperforming Cohort Diagnostics")
            lowest_groups = gap_analysis.get("lowest_performing_groups", [])
            if lowest_groups:
                st.dataframe(pd.DataFrame(lowest_groups), use_container_width=True)
            else:
                st.success("No demographic groups show critical underperformance gaps below -0.4 points.")

        with col_obs2:
            st.markdown("### 💡 Dynamic Analytical Observations")
            gap_insights = generate_learning_gap_insights(gap_analysis)
            for gi in gap_insights:
                border_c = "#EF4444" if gi["type"] == "danger" else "#F59E0B" if gi["type"] == "warning" else "#10B981" if gi["type"] == "success" else "#4F46E5"
                st.markdown(f"""
                <div class="insight-card" style="border-left-color: {border_c};">
                    <strong style="font-size: 0.95rem;">{gi['title']}</strong>
                    <div style="font-size: 0.86rem; margin-top: 4px; opacity: 0.85;">{gi['text']}</div>
                </div>
                """, unsafe_allow_html=True)

    # =========================================================================
    # PAGE 5 — ML INSIGHTS
    # =========================================================================
    with tabs[5]:
        st.subheader("Machine Learning Performance Classification & What-If Simulator")
        st.caption("Predict student performance categories and explore feature importance using Scikit-learn pipelines.")

        # Disclaimer Callout
        st.info("ℹ️ **Educational Notice:** Predictions and classifications are statistical estimates derived from historical data patterns. They are designed as early decision-support tools for educators rather than definitive determinants.")

        # ML Model Configuration Controls
        with st.expander("⚙️ Machine Learning Pipeline Configuration", expanded=True):
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                selected_model_name = st.selectbox("Classification Algorithm", options=["Random Forest", "Decision Tree", "Logistic Regression"], index=0)
            with col_m2:
                target_classification = st.selectbox("Target Classification", options=["Performance Category (5 Classes)", "Pass / Fail Status (Binary)"], index=0)
                target_key = "category" if "Category" in target_classification else "pass_fail"
            with col_m3:
                include_period_grades = st.checkbox("Include Early Period Grades (G1 & G2)", value=True, help="Uncheck to predict final outcome based purely on behavioral, demographic, and attendance factors.")
            with col_m4:
                test_split_val = st.slider("Test Split Proportion", min_value=0.15, max_value=0.40, value=0.25, step=0.05)

        # Train Model Pipeline
        with st.spinner("Training classification pipeline..."):
            ml_results = train_performance_classifier(
                df=filtered_df,
                model_name=selected_model_name,
                target_type=target_key,
                test_size=test_split_val,
                include_earlier_grades=include_period_grades
            )

        if "error" in ml_results:
            st.error(f"❌ {ml_results['error']}")
        else:
            # Display Evaluation Metrics Row
            met1, met2, met3, met4, met5 = st.columns(5)
            with met1:
                st.metric("Test Accuracy", f"{ml_results['accuracy']*100:.2f}%")
            with met2:
                st.metric("Precision (Weighted)", f"{ml_results['precision']*100:.2f}%")
            with met3:
                st.metric("Recall (Weighted)", f"{ml_results['recall']*100:.2f}%")
            with met4:
                st.metric("F1-Score (Weighted)", f"{ml_results['f1_score']*100:.2f}%")
            with met5:
                st.metric("Train / Test Samples", f"{ml_results['train_samples']} / {ml_results['test_samples']}")

            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

            # Confusion Matrix & Feature Importance Row
            col_ml_v1, col_ml_v2 = st.columns([1, 1])
            with col_ml_v1:
                fig_cm = plot_confusion_matrix(ml_results["confusion_matrix"], ml_results["classes"])
                render_chart_card(fig_cm)
            with col_ml_v2:
                fig_fi = plot_feature_importance(ml_results["feature_importances"])
                render_chart_card(fig_fi)

            # Classification Report Expander
            with st.expander("📊 Detailed Per-Class Classification Report Table", expanded=False):
                report_df = pd.DataFrame(ml_results["classification_report"]).transpose()
                st.dataframe(report_df.style.format(precision=3), use_container_width=True)

            st.markdown("<hr style='margin: 24px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)

            # Interactive Student Prediction Simulator
            st.markdown("### 🔮 Interactive 'What-If' Student Predictor")
            st.caption("Simulate how changes in study habits, attendance, and mid-term grades impact estimated final performance.")

            col_sim1, col_sim2, col_sim3, col_sim4 = st.columns(4)
            with col_sim1:
                sim_g1 = st.slider("Period 1 Score (G1)", 0, 20, 12) if include_period_grades else 12
                sim_g2 = st.slider("Period 2 Score (G2)", 0, 20, 12) if include_period_grades else 12
                sim_age = st.slider("Student Age", 15, 22, 16)
            with col_sim2:
                sim_study = st.selectbox("Weekly Study Time", options=[1, 2, 3, 4], index=1, format_func=lambda x: {1: "< 2 hrs", 2: "2-5 hrs", 3: "5-10 hrs", 4: "> 10 hrs"}[x])
                sim_failures = st.selectbox("Past Class Failures", options=[0, 1, 2, 3, 4], index=0)
                sim_absences = st.slider("School Absences", 0, 50, 4)
            with col_sim3:
                sim_medu = st.selectbox("Mother Education", options=[0, 1, 2, 3, 4], index=3, format_func=lambda x: {0: "None", 1: "Primary", 2: "5th-9th", 3: "Secondary", 4: "Higher"}[x])
                sim_fedu = st.selectbox("Father Education", options=[0, 1, 2, 3, 4], index=2, format_func=lambda x: {0: "None", 1: "Primary", 2: "5th-9th", 3: "Secondary", 4: "Higher"}[x])
                sim_higher = st.selectbox("Wants Higher Education", options=["yes", "no"], index=0)
            with col_sim4:
                sim_internet = st.selectbox("Home Internet Access", options=["yes", "no"], index=0)
                sim_schoolsup = st.selectbox("Extra Educational Support", options=["yes", "no"], index=1)
                sim_gender = st.selectbox("Gender", options=["F", "M"], index=0)

            # Build simulation input dict
            sim_input = {
                "G1": sim_g1, "G2": sim_g2, "age": sim_age, "studytime": sim_study,
                "failures": sim_failures, "absences": sim_absences, "Medu": sim_medu,
                "Fedu": sim_fedu, "higher": sim_higher, "internet": sim_internet,
                "schoolsup": sim_schoolsup, "sex": sim_gender, "school": "GP",
                "address": "U", "famsize": "GT3", "Pstatus": "T", "Mjob": "other",
                "Fjob": "other", "reason": "course", "guardian": "mother",
                "traveltime": 1, "famsup": "yes", "paid": "no", "activities": "yes",
                "nursery": "yes", "romantic": "no", "famrel": 4, "freetime": 3,
                "goout": 3, "Dalc": 1, "Walc": 1, "health": 4, "subject": "Mathematics"
            }

            sim_prediction = predict_single_student(
                ml_results["pipeline"],
                sim_input,
                ml_results["feature_columns"],
                num_cols=ml_results.get("numeric_features"),
                cat_cols=ml_results.get("categorical_features")
            )

            # Render Simulator Results
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 2px solid #4F46E5; border-radius: 12px; padding: 18px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <span style="font-size: 0.8rem; font-weight: 700; color: #4F46E5; text-transform: uppercase;">Simulation Prediction Result</span>
                        <h3 style="font-size: 1.35rem; font-weight: 700; color: #0F172A; margin: 4px 0 0 0;">
                            Estimated Outcome: {sim_prediction['predicted_class']}
                        </h3>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Probability Breakdown
            if sim_prediction["probabilities"]:
                st.markdown("#### Estimated Class Probabilities:")
                p_cols = st.columns(len(sim_prediction["probabilities"]))
                for col_p, (cls_name, prob_val) in zip(p_cols, sim_prediction["probabilities"].items()):
                    with col_p:
                        st.metric(cls_name, f"{prob_val}%")

    # =========================================================================
    # PAGE 6 — REPORTS & DATA MANAGEMENT
    # =========================================================================
    with tabs[6]:
        st.subheader("Data Export, Custom Reports & Database Persistence")
        st.caption("Generate downloadable datasets, multi-sheet Excel reports, and save snapshots to SQLite persistent storage.")

        # Data Export Options
        st.markdown("### 📥 Download Filtered Data & Reports")
        col_exp1, col_exp2, col_exp3 = st.columns(3)

        # 1. CSV Download
        with col_exp1:
            csv_buffer = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📄 Download Filtered CSV",
                data=csv_buffer,
                file_name=f"student_performance_filtered_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        # 2. Excel Report Download
        with col_exp2:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                filtered_df.to_excel(writer, sheet_name="Filtered Students", index=False)
                pd.DataFrame([desc_stats]).to_excel(writer, sheet_name="Descriptive Stats", index=False)
                gap_analysis["subject_gaps"].to_excel(writer, sheet_name="Learning Gaps", index=False)
            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="📊 Download Excel Report (.xlsx)",
                data=excel_data,
                file_name=f"student_performance_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # 3. Analytical Summary Markdown/Text Report
        with col_exp3:
            summary_text = f"""# Educational Performance Analytics - Executive Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Dataset: {source_label}

## 1. Key Performance Indicators
- Total Students Analyzed: {len(filtered_df):,}
- Average Score: {desc_stats.get('mean', 0):.2f} / 20 ({desc_stats.get('mean', 0)/20*100:.1f}%)
- Pass Percentage: {desc_stats.get('pass_rate_pct', 0):.1f}% ({desc_stats.get('pass_count', 0)} students)
- Failure Percentage: {desc_stats.get('fail_rate_pct', 0):.1f}% ({desc_stats.get('fail_count', 0)} students)
- At-Risk Students: {int(filtered_df['is_at_risk'].sum())} students ({round(filtered_df['is_at_risk'].mean()*100, 1)}%)
- Average Attendance: {filtered_df['attendance_rate'].mean():.1f}%

## 2. Dynamic Observations
"""
            for ins in generate_overview_insights(filtered_df, desc_stats):
                summary_text += f"- **{ins['title']}**: {ins['text']}\n"

            st.download_button(
                label="📝 Download Executive Summary (.md)",
                data=summary_text.encode("utf-8"),
                file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("<hr style='margin: 20px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)

        # SQLite Persistent Storage Management
        st.markdown("### 🗄️ SQLite Persistent Storage Manager")
        st.caption("Save custom uploaded datasets or current filtered subsets into local SQLite storage for future sessions.")

        col_db1, col_db2 = st.columns([1, 1])

        with col_db1:
            st.markdown("#### Save Current Filtered View to SQLite")
            with st.form("save_to_db_form"):
                save_table_name = st.text_input("Dataset Name", value=f"Cohort_{datetime.now().strftime('%b%d_%H%M')}")
                save_table_desc = st.text_area("Description / Educator Notes", value=f"Filtered cohort snapshot with {len(filtered_df)} students.")
                submit_save = st.form_submit_button("💾 Save Dataset to SQLite")

                if submit_save:
                    if save_table_name.strip():
                        success = save_dataset_to_db(save_table_name.strip(), filtered_df, description=save_table_desc)
                        if success:
                            st.success(f"✓ Dataset '{save_table_name}' saved to SQLite database successfully!")
                        else:
                            st.error("Failed to save dataset to database.")
                    else:
                        st.warning("Please provide a valid dataset name.")

        with col_db2:
            st.markdown("#### Registered Saved Datasets in SQLite")
            saved_tables = list_saved_datasets()
            if saved_tables:
                st.dataframe(pd.DataFrame(saved_tables)[["name", "row_count", "created_at", "description"]], use_container_width=True)
                
                # Delete options
                del_name = st.selectbox("Select dataset to delete", options=[t["name"] for t in saved_tables])
                if st.button("🗑️ Delete Dataset from Database"):
                    del_success = delete_dataset_from_db(del_name)
                    if del_success:
                        st.success(f"Deleted '{del_name}' from database.")
                        st.rerun()
                    else:
                        st.error("Failed to delete dataset.")
            else:
                st.info("No custom datasets saved in SQLite database yet.")

        st.markdown("<hr style='margin: 20px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)

        # Interactive Data Table with Column Selector
        st.markdown("### 🔍 Interactive Student Record Explorer")
        all_cols = list(filtered_df.columns)
        default_visible_cols = [c for c in ["student_id", "subject", "school_name", "gender", "age", "G1", "G2", "G3", "average_score", "performance_category", "attendance_rate", "absences", "risk_level"] if c in all_cols]
        
        selected_display_cols = st.multiselect("Select Columns to Display", options=all_cols, default=default_visible_cols)
        
        if selected_display_cols:
            st.dataframe(filtered_df[selected_display_cols], use_container_width=True, height=400)
        else:
            st.dataframe(filtered_df, use_container_width=True, height=400)

    # =========================================================================
    # ABOUT PAGE
    # =========================================================================
    with tabs[7]:
        render_about_page()

    # Glassmorphic Footer
    render_footer()


if __name__ == "__main__":
    main()
