"""
Preprocessing and Feature Engineering Module for Educational Performance Analytics.
Transforms raw and validated datasets into enriched DataFrames with standardized
labels, attendance rates, grade progression metrics, and performance classifications.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


# Mapping dictionaries for human-readable labels
SCHOOL_MAPPING = {
    "GP": "Gabriel Pereira (GP)",
    "MS": "Mousinho da Silveira (MS)",
    "Gabriel Pereira": "Gabriel Pereira (GP)",
    "Mousinho da Silveira": "Mousinho da Silveira (MS)"
}

SEX_MAPPING = {
    "F": "Female",
    "M": "Male",
    "Female": "Female",
    "Male": "Male",
    "f": "Female",
    "m": "Male"
}

ADDRESS_MAPPING = {
    "U": "Urban",
    "R": "Rural",
    "Urban": "Urban",
    "Rural": "Rural"
}

FAMSIZE_MAPPING = {
    "LE3": "≤ 3 members (Small)",
    "GT3": "> 3 members (Large)",
    "LE": "≤ 3 members (Small)",
    "GT": "> 3 members (Large)"
}

PSTATUS_MAPPING = {
    "T": "Living Together",
    "A": "Living Apart"
}

STUDYTIME_MAPPING = {
    1: "< 2 hours / week",
    2: "2 - 5 hours / week",
    3: "5 - 10 hours / week",
    4: "> 10 hours / week",
    "1": "< 2 hours / week",
    "2": "2 - 5 hours / week",
    "3": "5 - 10 hours / week",
    "4": "> 10 hours / week"
}

EDUCATION_MAPPING = {
    0: "None",
    1: "Primary (4th grade)",
    2: "5th to 9th grade",
    3: "Secondary Education",
    4: "Higher Education",
    "0": "None",
    "1": "Primary (4th grade)",
    "2": "5th to 9th grade",
    "3": "Secondary Education",
    "4": "Higher Education"
}

TRAVELTIME_MAPPING = {
    1: "< 15 min",
    2: "15 - 30 min",
    3: "30 min - 1 hr",
    4: "> 1 hr"
}


def clean_and_impute_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans the dataset by casting types and imputing missing values without silent deletion.
    Tracks all cleaning modifications in a changelog dictionary.
    """
    df_clean = df.copy()
    changelog = {
        "imputed_columns": {},
        "type_conversions": [],
        "rows_cleaned": len(df_clean)
    }

    # Clean string quotes and whitespace
    for col in df_clean.select_dtypes(include=["object"]).columns:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.replace('"', '').str.replace("'", "")

    # Ensure numeric columns
    numeric_candidates = [
        "G1", "G2", "G3", "age", "absences", "failures", "studytime",
        "traveltime", "Medu", "Fedu", "famrel", "freetime", "goout",
        "Dalc", "Walc", "health"
    ]

    for col in numeric_candidates:
        if col in df_clean.columns:
            before_nulls = df_clean[col].isnull().sum()
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            after_nulls = df_clean[col].isnull().sum()
            if after_nulls > before_nulls:
                changelog["type_conversions"].append(f"Converted '{col}' to numeric ({after_nulls - before_nulls} invalid coerced).")

            # Impute missing values with median
            if df_clean[col].isnull().sum() > 0:
                median_val = df_clean[col].median()
                fill_val = median_val if not pd.isna(median_val) else 0
                df_clean[col] = df_clean[col].fillna(fill_val)
                changelog["imputed_columns"][col] = f"Imputed with median: {fill_val}"

    # Impute categorical columns with mode or 'Unknown'
    for col in df_clean.select_dtypes(include=["object"]).columns:
        null_count = df_clean[col].isnull().sum() + (df_clean[col] == "nan").sum() + (df_clean[col] == "").sum()
        if null_count > 0:
            mode_series = df_clean[col][~df_clean[col].isin(["nan", "None", "", None])].mode()
            fill_mode = mode_series[0] if len(mode_series) > 0 else "Unknown"
            df_clean[col] = df_clean[col].replace(["nan", "None", "", None], fill_mode).fillna(fill_mode)
            changelog["imputed_columns"][col] = f"Imputed with mode: {fill_mode}"

    return df_clean, changelog


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineers rich educational performance metrics and standardized categories:
    - Average score across periods
    - Performance category
    - Pass/Fail status
    - Attendance percentage and category
    - Grade progression & trend (G1 -> G2 -> G3)
    - At-risk flags
    - Readable demographic descriptors
    """
    df_feat = df.copy()

    # Identify Grade columns
    has_g1 = "G1" in df_feat.columns
    has_g2 = "G2" in df_feat.columns
    has_g3 = "G3" in df_feat.columns

    # Detect score scale (0-20 vs 0-100)
    max_g3 = df_feat["G3"].max() if has_g3 else 20
    is_20_scale = max_g3 <= 20.5
    pass_threshold = 10.0 if is_20_scale else 50.0

    # 1. Average Score Calculation
    grade_cols = [c for c in ["G1", "G2", "G3"] if c in df_feat.columns]
    if grade_cols:
        df_feat["average_score"] = df_feat[grade_cols].mean(axis=1).round(2)
    else:
        df_feat["average_score"] = df_feat["G3"] if has_g3 else 0.0

    # Normalize to 100% scale
    if is_20_scale:
        df_feat["final_score_pct"] = ((df_feat["G3"] / 20.0) * 100.0).round(1)
        df_feat["average_score_pct"] = ((df_feat["average_score"] / 20.0) * 100.0).round(1)
    else:
        df_feat["final_score_pct"] = df_feat["G3"].round(1)
        df_feat["average_score_pct"] = df_feat["average_score"].round(1)

    # 2. Performance Category
    def assign_performance_cat(score: float, scale_20: bool) -> str:
        if scale_20:
            if score >= 16.0:
                return "Excellent (16-20)"
            elif score >= 14.0:
                return "Good (14-15)"
            elif score >= 12.0:
                return "Satisfactory (12-13)"
            elif score >= 10.0:
                return "Needs Improvement (10-11)"
            else:
                return "Fail / At-Risk (<10)"
        else:
            if score >= 80.0:
                return "Excellent (80-100%)"
            elif score >= 70.0:
                return "Good (70-79%)"
            elif score >= 60.0:
                return "Satisfactory (60-69%)"
            elif score >= 50.0:
                return "Needs Improvement (50-59%)"
            else:
                return "Fail / At-Risk (<50%)"

    df_feat["performance_category"] = df_feat["G3"].apply(lambda s: assign_performance_cat(s, is_20_scale))

    # 3. Pass Status
    df_feat["pass_status"] = np.where(df_feat["G3"] >= pass_threshold, "Passed", "Failed")
    df_feat["is_passed"] = (df_feat["G3"] >= pass_threshold).astype(int)

    # 4. Attendance Calculation
    if "absences" in df_feat.columns:
        # Max reasonable absences in academic term ~ 93 days in UCI dataset
        max_abs = max(93, int(df_feat["absences"].max()))
        df_feat["attendance_rate"] = df_feat["absences"].apply(
            lambda a: max(0.0, min(100.0, round(100.0 * (1.0 - (a / max_abs)), 1)))
        )
    elif "attendance" in df_feat.columns:
        df_feat["attendance_rate"] = pd.to_numeric(df_feat["attendance"], errors="coerce").fillna(85.0).clip(0, 100)
    else:
        df_feat["attendance_rate"] = 90.0

    def assign_attendance_cat(rate: float) -> str:
        if rate >= 90.0:
            return "High (>90%)"
        elif rate >= 75.0:
            return "Moderate (75-90%)"
        else:
            return "Low (<75%)"

    df_feat["attendance_category"] = df_feat["attendance_rate"].apply(assign_attendance_cat)

    # 5. Failure Status
    if "failures" in df_feat.columns:
        df_feat["failure_status"] = df_feat["failures"].apply(
            lambda f: "No Past Failures" if f == 0 else f"{int(f)} Past Failure{'s' if f > 1 else ''}"
        )
    else:
        df_feat["failure_status"] = "No Past Failures"
        df_feat["failures"] = 0

    # 6. Grade Progression & Trend (G1 -> G2 -> G3)
    if has_g1 and has_g3:
        df_feat["grade_change"] = (df_feat["G3"] - df_feat["G1"]).round(2)
        conditions = [
            df_feat["grade_change"] > 0.5,
            df_feat["grade_change"] < -0.5
        ]
        choices = ["Improving", "Declining"]
        df_feat["grade_trend"] = np.select(conditions, choices, default="Consistent")
    else:
        df_feat["grade_change"] = 0.0
        df_feat["grade_trend"] = "Consistent"

    # 7. At-Risk Student Flag
    # Criteria: Failing G3, or attendance < 75%, or has past failures
    abs_condition = (df_feat["absences"] > 15) if "absences" in df_feat.columns else (df_feat["attendance_rate"] < 75)
    df_feat["is_at_risk"] = (
        (df_feat["G3"] < pass_threshold) |
        abs_condition |
        (df_feat["failures"] > 0)
    )
    df_feat["risk_level"] = np.where(
        (df_feat["G3"] < pass_threshold) & (df_feat["failures"] > 0), "Critical Risk",
        np.where(df_feat["is_at_risk"], "Moderate Risk", "Low / On Track")
    )

    # 8. Human-Readable Demographic Labels
    if "school" in df_feat.columns:
        df_feat["school_name"] = df_feat["school"].map(lambda x: SCHOOL_MAPPING.get(str(x), str(x)))
    if "sex" in df_feat.columns:
        df_feat["gender"] = df_feat["sex"].map(lambda x: SEX_MAPPING.get(str(x), str(x)))
    if "address" in df_feat.columns:
        df_feat["address_type"] = df_feat["address"].map(lambda x: ADDRESS_MAPPING.get(str(x), str(x)))
    if "famsize" in df_feat.columns:
        df_feat["famsize_label"] = df_feat["famsize"].map(lambda x: FAMSIZE_MAPPING.get(str(x), str(x)))
    if "Pstatus" in df_feat.columns:
        df_feat["pstatus_label"] = df_feat["Pstatus"].map(lambda x: PSTATUS_MAPPING.get(str(x), str(x)))
    if "studytime" in df_feat.columns:
        df_feat["studytime_label"] = df_feat["studytime"].map(lambda x: STUDYTIME_MAPPING.get(int(x) if str(x).isdigit() else str(x), f"{x} hrs"))

    # Parent Education Average
    if "Medu" in df_feat.columns and "Fedu" in df_feat.columns:
        df_feat["parent_avg_edu"] = ((df_feat["Medu"] + df_feat["Fedu"]) / 2.0).round(2)
        df_feat["medu_label"] = df_feat["Medu"].map(lambda x: EDUCATION_MAPPING.get(int(x) if str(x).isdigit() else str(x), str(x)))
        df_feat["fedu_label"] = df_feat["Fedu"].map(lambda x: EDUCATION_MAPPING.get(int(x) if str(x).isdigit() else str(x), str(x)))

    # Alcohol Consumption composite
    if "Dalc" in df_feat.columns and "Walc" in df_feat.columns:
        df_feat["alcohol_avg"] = ((df_feat["Dalc"] * 5 + df_feat["Walc"] * 2) / 7.0).round(2)

    return df_feat


def preprocess_pipeline(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    End-to-end preprocessing pipeline.
    Returns the enriched DataFrame ready for analytical exploration and ML modeling.
    """
    clean_df, changelog = clean_and_impute_dataset(raw_df)
    enriched_df = engineer_features(clean_df)
    return enriched_df, changelog
