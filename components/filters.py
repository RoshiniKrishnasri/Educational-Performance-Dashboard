"""
Sidebar Filters Component for Educational Performance Analytics Dashboard.
Provides interactive controls for data source selection, multi-attribute filtering,
student search, and dynamic filter resets.
"""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import streamlit as st
from src.data_loader import load_builtin_dataset, load_raw_dataset, validate_dataset
from src.db import list_saved_datasets, load_dataset_from_db
from src.preprocessing import preprocess_pipeline


def render_sidebar_filters(default_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
    """
    Renders sidebar filters and returns the filtered DataFrame, filter states, and data quality metrics.
    """
    st.sidebar.markdown("""
    <div class="sidebar-brand">
        <h2 class="sidebar-brand-title">
            🎓 EduAnalytics Pro
        </h2>
        <p class="sidebar-brand-sub">Interactive Performance Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Dataset Selection Section
    st.sidebar.subheader("📁 Data Source")
    
    saved_dbs = list_saved_datasets()
    db_dataset_names = [d["name"] for d in saved_dbs] if saved_dbs else []

    source_options = [
        "UCI Combined (Math & Portuguese)",
        "UCI Mathematics Course (395)",
        "UCI Portuguese Course (649)",
        "Upload Custom CSV / Excel"
    ]
    if db_dataset_names:
        source_options.append("Saved in SQLite Database")

    selected_source = st.sidebar.selectbox(
        "Select Dataset",
        options=source_options,
        index=0,
        help="Choose built-in UCI educational datasets, upload a custom CSV, or load from SQLite database."
    )

    raw_df = None
    source_label = selected_source

    if selected_source == "UCI Combined (Math & Portuguese)":
        raw_df = load_builtin_dataset("combined")
    elif selected_source == "UCI Mathematics Course (395)":
        raw_df = load_builtin_dataset("math")
    elif selected_source == "UCI Portuguese Course (649)":
        raw_df = load_builtin_dataset("portuguese")
    elif selected_source == "Saved in SQLite Database":
        if db_dataset_names:
            db_choice = st.sidebar.selectbox("Choose Saved Dataset", options=db_dataset_names)
            raw_df = load_dataset_from_db(db_choice)
            source_label = f"SQLite: {db_choice}"
        else:
            st.sidebar.info("No datasets saved in SQLite yet.")
            raw_df = load_builtin_dataset("combined")
    else:  # Custom Upload
        uploaded_file = st.sidebar.file_uploader(
            "Upload Student CSV / Excel",
            type=["csv", "xlsx", "xls"],
            help="Upload a student performance dataset (UCI format or custom educational columns)."
        )
        if uploaded_file is not None:
            raw_df = load_raw_dataset(uploaded_file, file_type="excel" if uploaded_file.name.endswith((".xlsx", ".xls")) else "csv")
            source_label = f"Uploaded: {uploaded_file.name}"
        else:
            st.sidebar.info("ℹ️ Using default combined dataset until a file is uploaded.")
            raw_df = load_builtin_dataset("combined")

    # Validate Schema
    is_valid, errors, warnings, standardized_df = validate_dataset(raw_df)
    
    if not is_valid:
        for err in errors:
            st.sidebar.error(f"❌ {err}")
        return pd.DataFrame(), {}, {"errors": errors, "warnings": warnings}

    if warnings:
        with st.sidebar.expander("⚠️ Ingestion Notices", expanded=False):
            for w in warnings:
                st.caption(f"• {w}")

    # Preprocess & Enrich Features
    enriched_df, changelog = preprocess_pipeline(standardized_df)

    # 2. Filter Controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Cohort Filters")

    # Reset button
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("filter_"):
                del st.session_state[key]
        st.rerun()

    filtered_df = enriched_df.copy()
    filter_state = {}

    # Subject Filter
    if "subject" in enriched_df.columns:
        subjects = sorted(list(enriched_df["subject"].dropna().unique()))
        selected_subjects = st.sidebar.multiselect(
            "Course / Subject",
            options=subjects,
            default=subjects,
            key="filter_subjects"
        )
        if selected_subjects:
            filtered_df = filtered_df[filtered_df["subject"].isin(selected_subjects)]
            filter_state["subjects"] = selected_subjects

    # School Filter
    if "school_name" in enriched_df.columns:
        schools = ["All"] + sorted(list(enriched_df["school_name"].dropna().unique()))
        selected_school = st.sidebar.selectbox("School / Institution", options=schools, key="filter_school")
        if selected_school != "All":
            filtered_df = filtered_df[filtered_df["school_name"] == selected_school]
            filter_state["school"] = selected_school

    # Gender Filter
    if "gender" in enriched_df.columns:
        genders = ["All"] + sorted(list(enriched_df["gender"].dropna().unique()))
        selected_gender = st.sidebar.selectbox("Gender", options=genders, key="filter_gender")
        if selected_gender != "All":
            filtered_df = filtered_df[filtered_df["gender"] == selected_gender]
            filter_state["gender"] = selected_gender

    # Age Range Slider
    if "age" in enriched_df.columns:
        min_age = int(enriched_df["age"].min())
        max_age = int(enriched_df["age"].max())
        if min_age < max_age:
            age_range = st.sidebar.slider(
                "Age Range",
                min_value=min_age,
                max_value=max_age,
                value=(min_age, max_age),
                key="filter_age"
            )
            filtered_df = filtered_df[(filtered_df["age"] >= age_range[0]) & (filtered_df["age"] <= age_range[1])]
            filter_state["age_range"] = age_range

    # Study Time Filter
    if "studytime_label" in enriched_df.columns:
        study_options = ["All"] + sorted(list(enriched_df["studytime_label"].dropna().unique()))
        selected_study = st.sidebar.selectbox("Study Time (Weekly)", options=study_options, key="filter_studytime")
        if selected_study != "All":
            filtered_df = filtered_df[filtered_df["studytime_label"] == selected_study]
            filter_state["studytime"] = selected_study

    # Performance Category Filter
    if "performance_category" in enriched_df.columns:
        perf_cats = sorted(list(enriched_df["performance_category"].dropna().unique()))
        selected_perf = st.sidebar.multiselect(
            "Performance Category",
            options=perf_cats,
            default=perf_cats,
            key="filter_perf_cats"
        )
        if selected_perf:
            filtered_df = filtered_df[filtered_df["performance_category"].isin(selected_perf)]
            filter_state["performance_category"] = selected_perf

    # Attendance Category Filter
    if "attendance_category" in enriched_df.columns:
        att_cats = ["All"] + sorted(list(enriched_df["attendance_category"].dropna().unique()))
        selected_att = st.sidebar.selectbox("Attendance Category", options=att_cats, key="filter_attendance")
        if selected_att != "All":
            filtered_df = filtered_df[filtered_df["attendance_category"] == selected_att]
            filter_state["attendance"] = selected_att

    # Additional Factors in an Expander
    with st.sidebar.expander("⚙️ Advanced Demographic Filters", expanded=False):
        if "address_type" in enriched_df.columns:
            addr_options = ["All"] + sorted(list(enriched_df["address_type"].dropna().unique()))
            sel_addr = st.selectbox("Address Location", options=addr_options, key="filter_address")
            if sel_addr != "All":
                filtered_df = filtered_df[filtered_df["address_type"] == sel_addr]
                filter_state["address"] = sel_addr

        if "internet" in enriched_df.columns:
            internet_opts = ["All", "yes", "no"]
            sel_net = st.selectbox("Internet Access at Home", options=internet_opts, key="filter_internet")
            if sel_net != "All":
                filtered_df = filtered_df[filtered_df["internet"].astype(str).str.lower() == sel_net]
                filter_state["internet"] = sel_net

        if "schoolsup" in enriched_df.columns:
            sup_opts = ["All", "yes", "no"]
            sel_sup = st.selectbox("Extra Educational Support", options=sup_opts, key="filter_schoolsup")
            if sel_sup != "All":
                filtered_df = filtered_df[filtered_df["schoolsup"].astype(str).str.lower() == sel_sup]
                filter_state["schoolsup"] = sel_sup

    # Student Search Box
    st.sidebar.markdown("---")
    search_query = st.sidebar.text_input(
        "🔎 Quick Student ID Search",
        placeholder="e.g. STU-0012 or MAT-0005",
        key="filter_student_search"
    ).strip()

    if search_query:
        id_mask = filtered_df["student_id"].astype(str).str.contains(search_query, case=False, na=False)
        filtered_df = filtered_df[id_mask]
        filter_state["search_query"] = search_query

    # Sidebar Footer stats
    st.sidebar.markdown(f"""
    <div class="sidebar-stats-box">
        <b>Active Dataset:</b> {source_label}<br>
        <b>Matching Students:</b> {len(filtered_df):,} / {len(enriched_df):,} ({len(filtered_df)/len(enriched_df)*100:.1f}%)
    </div>
    <div class="sidebar-contact-box">
        <div class="contact-title">👤 <span>Developer Contact</span></div>
        <div class="contact-links">
            <a href="mailto:roshinikrishnasri@gmail.com" target="_blank" class="contact-link">
                ✉️ <span>roshinikrishnasri@gmail.com</span>
            </a>
            <a href="https://github.com/roshinikrishnasri" target="_blank" class="contact-link">
                💻 <span>GitHub Profile</span>
            </a>
            <a href="https://www.linkedin.com/in/roshinikrishnasri" target="_blank" class="contact-link">
                🔗 <span>LinkedIn Profile</span>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    metadata = {
        "raw_df": raw_df,
        "enriched_df": enriched_df,
        "source_label": source_label,
        "changelog": changelog,
        "warnings": warnings,
        "errors": errors
    }

    return filtered_df, filter_state, metadata
