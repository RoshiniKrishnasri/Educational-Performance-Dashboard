"""
Home and About Page Components for Educational Performance Dashboard.
Provides interactive Home landing portal and About platform showcase.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_home_page(filtered_df: pd.DataFrame, desc_stats: Dict[str, Any], metadata: Dict[str, Any]) -> None:
    """
    Renders the Home landing page featuring platform overview, key metrics,
    feature highlights, and quick access navigation cards.
    """
    total_students = len(filtered_df)
    mean_score = desc_stats.get("mean", 0.0)
    pass_rate = desc_stats.get("pass_rate", 0.0)
    at_risk_count = desc_stats.get("at_risk_count", 0)
    source_label = metadata.get("source_label", "UCI Student Performance")

    # ── Hero Banner ──
    st.markdown(f"""
    <div class="edu-card" style="padding: 28px; border-radius: 16px; margin-bottom: 24px; background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.12) 50%, rgba(14, 165, 233, 0.15) 100%); border: 1px solid rgba(99, 102, 241, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div style="max-width: 680px;">
                <span class="status-pill pill-blue" style="margin-bottom: 10px; display: inline-block;">🎓 Next-Gen Educational Intelligence</span>
                <h1 style="font-size: 2.2rem; font-weight: 800; margin: 8px 0 12px 0; letter-spacing: -0.02em;">
                    Welcome to EduAnalytics Pro
                </h1>
                <p style="font-size: 1.05rem; opacity: 0.9; line-height: 1.6; margin-bottom: 0;">
                    A comprehensive analytics platform for evaluating student academic trajectories, identifying demographic learning gaps, predicting performance outcomes with machine learning, and prescribing targeted educational interventions.
                </p>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px; min-width: 220px;">
                <div style="background: rgba(15, 23, 42, 0.4); padding: 12px 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="font-size: 0.75rem; text-transform: uppercase; opacity: 0.7; font-weight: 600;">Active Cohort Size</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #818CF8;">{total_students:,} Students</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.4); padding: 12px 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="font-size: 0.75rem; text-transform: uppercase; opacity: 0.7; font-weight: 600;">Cohort Mean Score</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #34D399;">{mean_score:.2f} / 20 ({mean_score/20*100:.1f}%)</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick Overview Metrics Row ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="edu-card" style="padding: 16px; border-radius: 12px; text-align: center;">
            <div style="font-size: 1.8rem; margin-bottom: 4px;">📊</div>
            <div style="font-size: 1.4rem; font-weight: 700;">{source_label}</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">Active Dataset</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="edu-card" style="padding: 16px; border-radius: 12px; text-align: center;">
            <div style="font-size: 1.8rem; margin-bottom: 4px;">✅</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #34D399;">{pass_rate:.1f}%</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">Overall Pass Rate</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="edu-card" style="padding: 16px; border-radius: 12px; text-align: center;">
            <div style="font-size: 1.8rem; margin-bottom: 4px;">⚠️</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #F87171;">{at_risk_count} Students</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">At-Risk Cohort</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="edu-card" style="padding: 16px; border-radius: 12px; text-align: center;">
            <div style="font-size: 1.8rem; margin-bottom: 4px;">🤖</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #A78BFA;">3 Classifiers</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">ML Models Trained</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # ── Platform Feature Modules Grid ──
    st.subheader("💡 Core Platform Features & Modules")

    col_m1, col_m2, col_m3 = st.columns(3)

    with col_m1:
        st.markdown("""
        <div class="edu-card" style="padding: 20px; border-radius: 14px; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 10px;">📌</div>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 8px;">Executive Overview</h3>
            <p style="font-size: 0.88rem; opacity: 0.8; line-height: 1.5; margin-bottom: 12px;">
                High-level dashboard featuring responsive KPI cards, subject comparisons, grade distributions, and automated ingestion quality checks.
            </p>
            <span class="status-pill pill-blue">Key Metrics & Distributions</span>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown("""
        <div class="edu-card" style="padding: 20px; border-radius: 14px; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 10px;">📈</div>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 8px;">Performance Analysis</h3>
            <p style="font-size: 0.88rem; opacity: 0.8; line-height: 1.5; margin-bottom: 12px;">
                Multi-attribute cohort breakdowns by gender, study habits, parental education, attendance, internet access, and correlation heatmaps.
            </p>
            <span class="status-pill pill-green">Cohort & Correlation Engine</span>
        </div>
        """, unsafe_allow_html=True)

    with col_m3:
        st.markdown("""
        <div class="edu-card" style="padding: 20px; border-radius: 14px; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 10px;">👤</div>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 8px;">Student Dossier</h3>
            <p style="font-size: 0.88rem; opacity: 0.8; line-height: 1.5; margin-bottom: 12px;">
                Granular individual student search, multidimensional radar charts, G1 → G2 → G3 progression timelines, and custom intervention plans.
            </p>
            <span class="status-pill pill-yellow">Individual Profile & Radar</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    col_m4, col_m5, col_m6 = st.columns(3)

    with col_m4:
        st.markdown("""
        <div class="edu-card" style="padding: 20px; border-radius: 14px; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🎯</div>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 8px;">Learning Gap Analysis</h3>
            <p style="font-size: 0.88rem; opacity: 0.8; line-height: 1.5; margin-bottom: 12px;">
                Interactive competency threshold testing, equity disparity diagnostics, lagging cohort identification, and targeted remediation guidance.
            </p>
            <span class="status-pill pill-red">Equity & Disparity Diagnostics</span>
        </div>
        """, unsafe_allow_html=True)

    with col_m5:
        st.markdown("""
        <div class="edu-card" style="padding: 20px; border-radius: 14px; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🤖</div>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 8px;">ML Predictive Intelligence</h3>
            <p style="font-size: 0.88rem; opacity: 0.8; line-height: 1.5; margin-bottom: 12px;">
                Train Random Forest, Decision Tree, and Logistic Regression pipelines. Test real-time "What-If" student scenarios with feature importances.
            </p>
            <span class="status-pill pill-blue">Scikit-Learn Classifier & Simulator</span>
        </div>
        """, unsafe_allow_html=True)

    with col_m6:
        st.markdown("""
        <div class="edu-card" style="padding: 20px; border-radius: 14px; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 10px;">📑</div>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 8px;">Reports & SQLite Persistence</h3>
            <p style="font-size: 0.88rem; opacity: 0.8; line-height: 1.5; margin-bottom: 12px;">
                Export filtered CSV datasets, multi-sheet Excel workbooks, executive Markdown summaries, and manage custom database snapshots in SQLite.
            </p>
            <span class="status-pill pill-green">Excel, CSV & Database Manager</span>
        </div>
        """, unsafe_allow_html=True)


def render_about_page() -> None:
    """
    Renders the About page featuring developer profile, project architecture,
    dataset documentation, methodology, and tech stack details.
    """
    # ── Developer Profile Card ──
    st.markdown("""
    <div class="edu-card" style="padding: 28px; border-radius: 16px; margin-bottom: 24px; border-left: 5px solid #6366F1;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
            <div>
                <span class="status-pill pill-blue" style="margin-bottom: 10px; display: inline-block;">👤 Platform Creator & Lead Developer</span>
                <h1 style="font-size: 2rem; font-weight: 800; margin: 4px 0 8px 0; letter-spacing: -0.02em;">
                    Roshini Krishna Sri
                </h1>
                <p style="font-size: 1rem; opacity: 0.85; max-width: 650px; line-height: 1.5; margin-bottom: 16px;">
                    Educational Data Scientist & Full-Stack Python Developer passionate about leveraging machine learning, interactive visual analytics, and data-driven insights to transform educational outcomes.
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center;">
                    <a href="mailto:roshinikrishnasri@gmail.com" target="_blank" class="contact-link" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 8px;">
                        ✉️ <span>roshinikrishnasri@gmail.com</span>
                    </a>
                    <a href="https://github.com/roshinikrishnasri" target="_blank" class="contact-link" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 8px;">
                        💻 <span>GitHub Profile</span>
                    </a>
                    <a href="https://www.linkedin.com/in/roshinikrishnasri" target="_blank" class="contact-link" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 8px;">
                        🔗 <span>LinkedIn Profile</span>
                    </a>
                </div>
            </div>
            <div style="background: rgba(99, 102, 241, 0.1); padding: 20px; border-radius: 14px; border: 1px solid rgba(99, 102, 241, 0.25); text-align: center; min-width: 200px;">
                <div style="font-size: 2.5rem; margin-bottom: 4px;">🎓</div>
                <div style="font-size: 1.1rem; font-weight: 700;">EduAnalytics Pro</div>
                <div style="font-size: 0.8rem; opacity: 0.7;">Version 2.0 (2026)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Project Mission & Tech Stack ──
    col_a1, col_a2 = st.columns([1.2, 1.0])

    with col_a1:
        st.subheader("🎯 Project Purpose & Objectives")
        st.markdown("""
        EduAnalytics Pro was built to bridge the gap between educational raw data and actionable pedagogical interventions. Key objectives include:
        
        - **Early Identification of At-Risk Students**: Leveraging first and second period grades ($G1, G2$) along with attendance and demographic factors to flag students requiring academic support.
        - **Addressing Academic Disparities**: Diagnosing performance gaps across gender, family background, weekly study time, and institution types.
        - **Interpretable Machine Learning**: Providing educators with transparent, explainable ML classifiers rather than black-box models.
        - **Interactive "What-If" Simulation**: Enabling advisors to model how changes in study time, attendance, or tutoring might impact a student's final grade.
        """)

    with col_a2:
        st.subheader("🛠️ Technology Stack")
        st.markdown("""
        <div class="edu-card" style="padding: 20px; border-radius: 14px;">
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <strong>🐍 Python 3.9+</strong>
                    <span class="status-pill pill-blue">Core Engine</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <strong>🚀 Streamlit 1.50</strong>
                    <span class="status-pill pill-green">Web UI Framework</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <strong>📊 Plotly Express & Graph Objects</strong>
                    <span class="status-pill pill-yellow">Interactive Visuals</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <strong>🤖 Scikit-Learn</strong>
                    <span class="status-pill pill-blue">ML Pipelines</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <strong>🐼 Pandas & NumPy</strong>
                    <span class="status-pill pill-green">Data Engineering</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <strong>🗄️ SQLite Database</strong>
                    <span class="status-pill pill-red">Local Persistence</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # ── Dataset Citation & Attribute Reference ──
    st.subheader("📚 Dataset Attribution & Attributes")
    st.markdown("""
    This application utilizes the **UCI Student Performance Data Set** (*Cortez and Silva, 2008*), comprising student achievements in secondary education of two Portuguese schools (**Gabriel Pereira** and **Mousinho da Silveira**).
    """)

    with st.expander("📋 View UCI Dataset Attribute Dictionary", expanded=False):
        st.markdown("""
        | Attribute | Description | Values / Scale |
        |---|---|---|
        | `school` | Student's school | `GP` (Gabriel Pereira) or `MS` (Mousinho da Silveira) |
        | `sex` | Student's gender | `F` (Female) or `M` (Male) |
        | `age` | Student's age | 15 to 22 years |
        | `address` | Home address type | `U` (Urban) or `R` (Rural) |
        | `studytime` | Weekly study time | 1 (<2h), 2 (2-5h), 3 (5-10h), 4 (>10h) |
        | `failures` | Number of past class failures | 0 to 4 |
        | `absences` | Number of school absences | 0 to 93 |
        | `G1` | First period grade | 0 to 20 points |
        | `G2` | Second period grade | 0 to 20 points |
        | `G3` | Final grade outcome | 0 to 20 points |
        | `performance_category` | Academic performance tier | Excellent (16-20), Good (14-15), Satisfactory (12-13), Needs Improvement (10-11), Fail (<10) |
        """)
