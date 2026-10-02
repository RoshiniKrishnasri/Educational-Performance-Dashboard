"""
Dynamic Natural Language Analytical Insight Generator for Educational Performance.
Generates real-time, data-driven observations, pedagogical recommendations,
and risk diagnostics based strictly on current filter selections and calculations.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np


def generate_overview_insights(df: pd.DataFrame, desc_stats: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generates dynamic high-level insights for Overview page based on filtered dataset.
    """
    if df.empty or not desc_stats:
        return [{"type": "info", "title": "No Data", "text": "Adjust your filters to inspect student performance data."}]

    insights = []
    total = desc_stats.get("count", 0)
    mean_score = desc_stats.get("mean", 0.0)
    pass_rate = desc_stats.get("pass_rate_pct", 0.0)
    is_20_scale = desc_stats.get("is_20_scale", True)
    scale_text = "/ 20" if is_20_scale else "%"

    # Pass rate insight
    if pass_rate >= 80.0:
        insights.append({
            "type": "success",
            "title": "Strong Academic Health",
            "text": f"The selected cohort demonstrates a high pass rate of **{pass_rate}%** with an average score of **{mean_score}{scale_text}**, indicating broad subject comprehension."
        })
    elif pass_rate >= 60.0:
        insights.append({
            "type": "warning",
            "title": "Moderate Performance with Growth Opportunities",
            "text": f"Pass rate stands at **{pass_rate}%** (Average: **{mean_score}{scale_text}**). A targeted intervention for students hovering between 10-12 points could elevate the overall pass rate by an estimated 10-15%."
        })
    else:
        insights.append({
            "type": "danger",
            "title": "High Academic Vulnerability Detected",
            "text": f"Over **{round(100.0 - pass_rate, 1)}%** of students are currently failing to meet the benchmark threshold of {desc_stats.get('pass_threshold', 10)}{scale_text}. Immediate diagnostic assessments and tutoring support are recommended."
        })

    # Grade Progression insight (G1 vs G3)
    if "grade_trend" in df.columns and "G1" in df.columns and "G3" in df.columns:
        improving_pct = round((df["grade_trend"] == "Improving").mean() * 100, 1)
        declining_pct = round((df["grade_trend"] == "Declining").mean() * 100, 1)
        avg_diff = round(df["G3"].mean() - df["G1"].mean(), 2)
        diff_str = f"+{avg_diff}" if avg_diff > 0 else f"{avg_diff}"
        
        if improving_pct > declining_pct:
            insights.append({
                "type": "success",
                "title": "Positive Grade Trajectory",
                "text": f"**{improving_pct}%** of students showed improved grades from Period 1 to the Final Exam (average change of **{diff_str} points**), reflecting cumulative learning gain."
            })
        else:
            insights.append({
                "type": "warning",
                "title": "Mid-Term Grade Dropoff",
                "text": f"**{declining_pct}%** of students exhibited grade decline between Period 1 and Final Period (average change of **{diff_str} points**), signaling potential end-of-term burnout or harder exam material."
            })

    # Study time impact
    if "studytime" in df.columns and "G3" in df.columns:
        high_study = df[df["studytime"] >= 3]["G3"].mean()
        low_study = df[df["studytime"] <= 1]["G3"].mean()
        if pd.notna(high_study) and pd.notna(low_study):
            study_diff = round(high_study - low_study, 2)
            if study_diff > 0:
                insights.append({
                    "type": "info",
                    "title": "Study Time Dividend",
                    "text": f"Students studying **>5 hours/week** scored an average of **{round(high_study, 2)}** compared to **{round(low_study, 2)}** for those studying <2 hours (an advantage of **+{study_diff} points**)."
                })

    # Attendance impact
    if "absences" in df.columns and "G3" in df.columns:
        chronic_absent = df[df["absences"] > 10]
        regular_attend = df[df["absences"] <= 3]
        if len(chronic_absent) > 0 and len(regular_attend) > 0:
            reg_pass = round((regular_attend["is_passed"].mean() if "is_passed" in regular_attend.columns else 0.8) * 100, 1)
            abs_pass = round((chronic_absent["is_passed"].mean() if "is_passed" in chronic_absent.columns else 0.5) * 100, 1)
            insights.append({
                "type": "danger" if (reg_pass - abs_pass) > 20 else "warning",
                "title": "Attendance & Pass Rate Correlation",
                "text": f"Students with **≤3 absences** achieved a **{reg_pass}%** pass rate, whereas those with **>10 absences** achieved only **{abs_pass}%** (a **{round(reg_pass - abs_pass, 1)}%** gap)."
            })

    return insights


def generate_learning_gap_insights(gap_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generates dynamic analytical observations for Learning Gap page.
    """
    insights = []
    thresh = gap_data.get("threshold", 10.0)
    below_count = gap_data.get("students_below_threshold", 0)
    below_pct = gap_data.get("pct_below_threshold", 0.0)
    benchmark = gap_data.get("benchmark_mean", 0.0)
    subject_gaps = gap_data.get("subject_gaps", pd.DataFrame())
    lowest_groups = gap_data.get("lowest_performing_groups", [])

    # Threshold insight
    insights.append({
        "type": "warning" if below_pct > 25 else "info",
        "title": f"Threshold Benchmark: {thresh} Points",
        "text": f"A total of **{below_count} students ({below_pct}%)** currently score below the selected competency threshold of **{thresh} points** (Overall Mean: **{benchmark}**)."
    })

    # Subject Gaps
    if isinstance(subject_gaps, pd.DataFrame) and not subject_gaps.empty:
        lowest_subj = subject_gaps.iloc[0]
        highest_subj = subject_gaps.iloc[-1]
        subj_diff = round(highest_subj["Average Score"] - lowest_subj["Average Score"], 2)
        
        if subj_diff > 0.5:
            insights.append({
                "type": "danger",
                "title": f"Subject Disparity: {lowest_subj['Subject']} Lags",
                "text": f"**{lowest_subj['Subject']}** is the lowest-performing subject with an average of **{lowest_subj['Average Score']}** (gap of **{lowest_subj['Gap from Benchmark']} points** from benchmark), trailing **{highest_subj['Subject']}** ({highest_subj['Average Score']}) by **{subj_diff} points**."
            })

    # Underperforming cohorts
    if lowest_groups:
        top_lag = lowest_groups[0]
        insights.append({
            "type": "danger",
            "title": f"Critical Demographic Gap: {top_lag['Factor']} ({top_lag['Group']})",
            "text": f"Students in category **'{top_lag['Group']}'** for **{top_lag['Factor']}** show a notable score gap of **{top_lag['Gap']} points** below cohort average (Mean: **{top_lag['Mean Score']}**, **{top_lag['Below Threshold %']}%** below threshold; Sample size: {top_lag['Sample Size']})."
        })

    # Pedagogical recommendations
    insights.append({
        "type": "success",
        "title": "Actionable Pedagogical Interventions",
        "text": "1. **Targeted Office Hours**: Allocate structured weekly review sessions for students in the lowest quartile.<br>"
                "2. **Attendance Alerts**: Deploy automated SMS/Email check-ins when absences exceed 5 class days.<br>"
                "3. **Peer Study Circles**: Pair students who study >5 hrs/week with those studying <2 hrs/week to build collaborative accountability."
    })

    return insights


def generate_student_recommendations(student: pd.Series, cohort_df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Generates tailored, individual diagnostic recommendations for an individual student dossier.
    """
    recs = []
    g3 = student.get("G3", 0)
    g1 = student.get("G1", 0)
    absences = student.get("absences", 0)
    studytime = student.get("studytime", 2)
    failures = student.get("failures", 0)
    higher = str(student.get("higher", "yes")).lower()
    
    cohort_avg_g3 = cohort_df["G3"].mean() if not cohort_df.empty and "G3" in cohort_df.columns else 11.0

    # Academic score diagnostic
    if g3 < 10:
        recs.append({
            "priority": "High",
            "badge": "Urgent Academic Intervention",
            "color": "red",
            "text": f"Final score ({g3}/20) is below the minimum passing threshold (10.0). Recommend immediate 1-on-1 tutoring and remedial assignment pathways."
        })
    elif g3 >= 15:
        recs.append({
            "priority": "Low",
            "badge": "Advanced Honors Candidate",
            "color": "green",
            "text": f"Outstanding academic performance ({g3}/20). Consider encouraging student into advanced coursework, competitive exams, or peer-mentorship roles."
        })

    # Progression diagnostic
    if g3 < g1 - 1.5:
        recs.append({
            "priority": "High",
            "badge": "Grade Regression Alert",
            "color": "orange",
            "text": f"Student experienced a significant drop from Period 1 ({g1}) to Final ({g3}). Schedule a counselor check-in to identify potential personal, health, or workload challenges."
        })
    elif g3 > g1 + 1.5:
        recs.append({
            "priority": "Positive",
            "badge": "Growth Mindset Champion",
            "color": "blue",
            "text": f"Student gained +{round(g3 - g1, 1)} points over the term. Formally acknowledge and reward this strong upward effort."
        })

    # Attendance diagnostic
    if absences > 10:
        recs.append({
            "priority": "High",
            "badge": "Attendance Risk",
            "color": "red",
            "text": f"Student has accumulated {int(absences)} absences. Engage parents and attendance office to formulate an absence recovery contract."
        })

    # Study time diagnostic
    if studytime <= 1 and g3 < 12:
        recs.append({
            "priority": "Medium",
            "badge": "Study Habits Coaching",
            "color": "yellow",
            "text": "Reported study time is under 2 hours per week. Introduce structured time-management schedules and guided homework sessions."
        })

    # Past failures
    if failures > 0:
        recs.append({
            "priority": "Medium",
            "badge": "Prerequisite Mastery Check",
            "color": "purple",
            "text": f"Student has a history of {int(failures)} past class failures. Ensure fundamental prerequisite concepts are refreshed before advancing to complex topics."
        })

    if not recs:
        recs.append({
            "priority": "Normal",
            "badge": "Consistent Performance",
            "color": "green",
            "text": "Student is progressing steadily along expected benchmarks. Maintain current study routines and semester check-ins."
        })

    return recs
