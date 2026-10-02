"""
Analytics and Statistical Computation Module for Educational Performance.
Computes descriptive statistics, cohort aggregations, multi-variable correlations,
equity learning gaps, and trend progression metrics.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


def compute_descriptive_stats(df: pd.DataFrame, target_col: str = "G3") -> Dict[str, Any]:
    """
    Calculate comprehensive descriptive statistics for target score and attendance.
    """
    if df.empty or target_col not in df.columns:
        return {}

    series = df[target_col].dropna()
    if len(series) == 0:
        return {}

    q25 = float(series.quantile(0.25))
    q75 = float(series.quantile(0.75))
    iqr = float(q75 - q25)
    mean_val = float(series.mean())
    std_val = float(series.std()) if len(series) > 1 else 0.0
    median_val = float(series.median())
    skew_val = float(series.skew()) if len(series) > 2 else 0.0

    # Pass threshold detection
    max_score = series.max()
    is_20_scale = max_score <= 20.5
    pass_thresh = 10.0 if is_20_scale else 50.0

    passed_count = int((series >= pass_thresh).sum())
    failed_count = int((series < pass_thresh).sum())
    total_count = len(series)
    pass_rate = round((passed_count / total_count) * 100, 2) if total_count > 0 else 0.0
    fail_rate = round((failed_count / total_count) * 100, 2) if total_count > 0 else 0.0

    return {
        "count": total_count,
        "mean": round(mean_val, 2),
        "std": round(std_val, 2),
        "median": round(median_val, 2),
        "min": float(series.min()),
        "max": float(series.max()),
        "q25": round(q25, 2),
        "q75": round(q75, 2),
        "iqr": round(iqr, 2),
        "skewness": round(skew_val, 3),
        "pass_count": passed_count,
        "fail_count": failed_count,
        "pass_rate_pct": pass_rate,
        "fail_rate_pct": fail_rate,
        "is_20_scale": is_20_scale,
        "pass_threshold": pass_thresh
    }


def compute_group_aggregates(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """
    Computes aggregated performance metrics grouped by any column (e.g. subject, gender, school).
    """
    if df.empty or group_col not in df.columns:
        return pd.DataFrame()

    records = []
    max_score = df["G3"].max() if "G3" in df.columns else 20
    is_20_scale = max_score <= 20.5
    pass_thresh = 10.0 if is_20_scale else 50.0

    for group_val, sub_df in df.groupby(group_col, observed=False):
        total_students = len(sub_df)
        if total_students == 0:
            continue

        avg_g1 = sub_df["G1"].mean() if "G1" in sub_df.columns else 0.0
        avg_g2 = sub_df["G2"].mean() if "G2" in sub_df.columns else 0.0
        avg_g3 = sub_df["G3"].mean() if "G3" in sub_df.columns else 0.0
        avg_overall = sub_df["average_score"].mean() if "average_score" in sub_df.columns else avg_g3
        
        passed_students = (sub_df["G3"] >= pass_thresh).sum() if "G3" in sub_df.columns else 0
        pass_rate = round((passed_students / total_students) * 100, 1)
        fail_rate = round(100.0 - pass_rate, 1)
        
        at_risk_count = sub_df["is_at_risk"].sum() if "is_at_risk" in sub_df.columns else 0
        at_risk_pct = round((at_risk_count / total_students) * 100, 1)

        avg_attendance = sub_df["attendance_rate"].mean() if "attendance_rate" in sub_df.columns else 90.0
        avg_absences = sub_df["absences"].mean() if "absences" in sub_df.columns else 0.0

        records.append({
            group_col: str(group_val),
            "Students": total_students,
            "Avg G1": round(avg_g1, 2),
            "Avg G2": round(avg_g2, 2),
            "Avg G3 (Final)": round(avg_g3, 2),
            "Avg Overall": round(avg_overall, 2),
            "Pass Rate (%)": pass_rate,
            "Fail Rate (%)": fail_rate,
            "At-Risk Count": int(at_risk_count),
            "At-Risk (%)": at_risk_pct,
            "Avg Attendance (%)": round(avg_attendance, 1),
            "Avg Absences": round(avg_absences, 1)
        })

    agg_df = pd.DataFrame(records)
    if not agg_df.empty:
        agg_df = agg_df.sort_values(by="Avg G3 (Final)", ascending=False).reset_index(drop=True)
    return agg_df


def compute_correlations(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Computes Pearson correlation matrix for numeric columns and extracts top correlates with G3.
    """
    if df.empty:
        return pd.DataFrame(), []

    numeric_cols = [
        col for col in df.select_dtypes(include=[np.number]).columns
        if col not in ["student_id"] and not col.startswith("is_")
    ]
    
    if len(numeric_cols) < 2:
        return pd.DataFrame(), []

    corr_matrix = df[numeric_cols].corr(method="pearson").round(3)

    top_correlates = []
    if "G3" in corr_matrix.columns:
        g3_corrs = corr_matrix["G3"].drop("G3", errors="ignore").dropna()
        sorted_corrs = g3_corrs.sort_values(ascending=False)
        for col_name, corr_val in sorted_corrs.items():
            top_correlates.append({
                "feature": col_name,
                "correlation": round(corr_val, 3),
                "direction": "Positive" if corr_val > 0 else "Negative",
                "strength": (
                    "Strong" if abs(corr_val) >= 0.5
                    else "Moderate" if abs(corr_val) >= 0.25
                    else "Weak"
                )
            })

    return corr_matrix, top_correlates


def compute_learning_gap_analysis(df: pd.DataFrame, threshold: float = 10.0) -> Dict[str, Any]:
    """
    Calculates learning gaps across subjects, demographics, and study factors.
    Identifies lowest performing cohorts and students falling below selected threshold.
    """
    if df.empty or "G3" not in df.columns:
        return {
            "benchmark_mean": 0.0,
            "benchmark_median": 0.0,
            "threshold": threshold,
            "students_below_threshold": 0,
            "pct_below_threshold": 0.0,
            "subject_gaps": pd.DataFrame(),
            "demographic_gaps": {},
            "lowest_performing_groups": []
        }

    overall_mean = float(df["G3"].mean())
    overall_median = float(df["G3"].median())
    total_students = len(df)

    # Students below threshold
    below_thresh_mask = df["G3"] < threshold
    below_thresh_count = int(below_thresh_mask.sum())
    below_thresh_pct = round((below_thresh_count / total_students) * 100, 1)

    # Subject Gaps
    subject_gaps = []
    if "subject" in df.columns:
        for subj, sub_df in df.groupby("subject"):
            subj_mean = float(sub_df["G3"].mean())
            gap = round(subj_mean - overall_mean, 2)
            subj_below = int((sub_df["G3"] < threshold).sum())
            subj_below_pct = round((subj_below / len(sub_df)) * 100, 1)
            subject_gaps.append({
                "Subject": subj,
                "Student Count": len(sub_df),
                "Average Score": round(subj_mean, 2),
                "Gap from Benchmark": gap,
                "Below Threshold Count": subj_below,
                "Below Threshold (%)": subj_below_pct
            })
    subject_gaps_df = pd.DataFrame(subject_gaps)
    if not subject_gaps_df.empty:
        subject_gaps_df = subject_gaps_df.sort_values(by="Gap from Benchmark", ascending=True).reset_index(drop=True)

    # Demographic & Environmental Disparities
    demo_columns = ["gender", "school_name", "address_type", "studytime_label", "attendance_category", "internet", "higher", "schoolsup"]
    demographic_gaps = {}
    underperforming_cohorts = []

    for col in demo_columns:
        if col in df.columns:
            group_stats = []
            for g_name, g_df in df.groupby(col):
                g_mean = float(g_df["G3"].mean())
                g_gap = round(g_mean - overall_mean, 2)
                g_below = int((g_df["G3"] < threshold).sum())
                g_below_pct = round((g_below / len(g_df)) * 100, 1)
                
                group_stats.append({
                    "Group": str(g_name),
                    "Count": len(g_df),
                    "Mean": round(g_mean, 2),
                    "Gap": g_gap,
                    "Below Thresh %": g_below_pct
                })

                if g_gap < -0.4 and len(g_df) >= 10:
                    underperforming_cohorts.append({
                        "Factor": col.replace("_", " ").title(),
                        "Group": str(g_name),
                        "Mean Score": round(g_mean, 2),
                        "Gap": g_gap,
                        "Below Threshold %": g_below_pct,
                        "Sample Size": len(g_df)
                    })
            demographic_gaps[col] = group_stats

    # Sort underperforming cohorts by largest negative gap
    underperforming_cohorts = sorted(underperforming_cohorts, key=lambda x: x["Gap"])

    return {
        "benchmark_mean": round(overall_mean, 2),
        "benchmark_median": round(overall_median, 2),
        "threshold": threshold,
        "students_below_threshold": below_thresh_count,
        "pct_below_threshold": below_thresh_pct,
        "subject_gaps": subject_gaps_df,
        "demographic_gaps": demographic_gaps,
        "lowest_performing_groups": underperforming_cohorts
    }
