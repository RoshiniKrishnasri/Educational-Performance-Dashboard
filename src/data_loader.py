"""
Data Ingestion and Validation Layer for Educational Performance Analytics.
Handles loading built-in datasets, custom CSV/Excel uploads, delimiter sniffing,
schema validation, and comprehensive data quality metrics calculation.
"""

import io
import os
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


# Standard required and optional educational columns
ESSENTIAL_GRADE_COLUMNS = ["G1", "G2", "G3"]
ALTERNATIVE_GRADE_KEYS = {
    "g1": ["g1", "grade1", "period1", "exam1", "term1_score", "first_period_grade"],
    "g2": ["g2", "grade2", "period2", "exam2", "term2_score", "second_period_grade"],
    "g3": ["g3", "grade3", "period3", "final_grade", "final_score", "total_score", "overall_score", "g3_math", "g3_por"]
}

COLUMN_SYNONYMS = {
    "sex": ["sex", "gender"],
    "age": ["age"],
    "school": ["school", "institution", "campus", "school_name"],
    "studytime": ["studytime", "study_time", "weekly_study_hours", "study_hours"],
    "absences": ["absences", "absence_days", "missed_classes", "days_absent"],
    "failures": ["failures", "past_failures", "failed_classes", "backlogs"],
    "address": ["address", "location", "address_type", "urban_rural"],
    "subject": ["subject", "course", "course_name", "subject_name"]
}


def sniff_delimiter(file_buffer: Union[str, io.BytesIO, io.StringIO]) -> str:
    """Sniff CSV delimiter (supports ';', ',', '\t', '|')."""
    sample = ""
    if isinstance(file_buffer, str):
        with open(file_buffer, "r", encoding="utf-8", errors="ignore") as f:
            sample = f.read(4096)
    else:
        # File-like buffer
        current_pos = file_buffer.tell()
        sample_bytes = file_buffer.read(4096)
        file_buffer.seek(current_pos)
        if isinstance(sample_bytes, bytes):
            sample = sample_bytes.decode("utf-8", errors="ignore")
        else:
            sample = str(sample_bytes)

    # Count occurrences
    semicolons = sample.count(";")
    commas = sample.count(",")
    tabs = sample.count("\t")
    pipes = sample.count("|")

    counts = {";": semicolons, ",": commas, "\t": tabs, "|": pipes}
    best_delimiter = max(counts, key=counts.get)
    return best_delimiter if counts[best_delimiter] > 0 else ","


def load_raw_dataset(source: Union[str, io.BytesIO], file_type: str = "csv") -> pd.DataFrame:
    """
    Load raw dataset from filepath or uploaded file buffer.
    Automatically handles encodings and delimiters.
    """
    if file_type == "excel" or (isinstance(source, str) and (source.endswith(".xlsx") or source.endswith(".xls"))):
        return pd.read_excel(source)
    
    # Handle CSV
    delimiter = sniff_delimiter(source)
    try:
        df = pd.read_csv(source, sep=delimiter, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(source, sep=delimiter, encoding="latin-1")
    except Exception:
        # Fallback to python engine
        df = pd.read_csv(source, sep=None, engine="python", encoding="utf-8", on_bad_lines="skip")
        
    return df


def load_builtin_dataset(dataset_key: str = "combined") -> pd.DataFrame:
    """
    Load one of the built-in datasets:
    - 'combined': Math and Portuguese unified dataset (1,044 rows)
    - 'math': Math course dataset (395 rows)
    - 'portuguese': Portuguese course dataset (649 rows)
    """
    if dataset_key == "math":
        filepath = os.path.join(DATA_DIR, "student-mat.csv")
        df = load_raw_dataset(filepath)
        df["subject"] = "Mathematics"
        if "student_id" not in df.columns:
            df["student_id"] = [f"MAT-{i+1:04d}" for i in range(len(df))]
        return df

    elif dataset_key == "portuguese":
        filepath = os.path.join(DATA_DIR, "student-por.csv")
        df = load_raw_dataset(filepath)
        df["subject"] = "Portuguese"
        if "student_id" not in df.columns:
            df["student_id"] = [f"POR-{i+1:04d}" for i in range(len(df))]
        return df

    else:
        # Combined dataset
        filepath_comb = os.path.join(DATA_DIR, "student-combined.csv")
        if os.path.exists(filepath_comb):
            df = pd.read_csv(filepath_comb)
            return df
        
        # Build if not existing
        df_mat = load_builtin_dataset("math")
        df_por = load_builtin_dataset("portuguese")
        df_combined = pd.concat([df_mat, df_por], ignore_index=True)
        df_combined["student_id"] = [f"STU-{i+1:04d}" for i in range(len(df_combined))]
        df_combined.to_csv(filepath_comb, index=False)
        return df_combined


def match_column_aliases(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Standardize column names to canonical names using synonyms dictionary.
    Returns standardized dataframe and mapping used.
    """
    df_copy = df.copy()
    col_mapping = {}
    normalized_cols = {col.lower().strip().replace(" ", "_"): col for col in df.columns}

    # Match canonical keys
    for canonical, synonyms in COLUMN_SYNONYMS.items():
        if canonical in df_copy.columns:
            continue
        for syn in synonyms:
            if syn in normalized_cols:
                original_name = normalized_cols[syn]
                df_copy.rename(columns={original_name: canonical}, inplace=True)
                col_mapping[original_name] = canonical
                break

    # Match Grade keys
    for canonical, synonyms in ALTERNATIVE_GRADE_KEYS.items():
        canon_upper = canonical.upper()
        if canon_upper in df_copy.columns:
            continue
        for syn in synonyms:
            if syn in normalized_cols:
                original_name = normalized_cols[syn]
                df_copy.rename(columns={original_name: canon_upper}, inplace=True)
                col_mapping[original_name] = canon_upper
                break

    return df_copy, col_mapping


def validate_dataset(df: pd.DataFrame) -> Tuple[bool, List[str], List[str], pd.DataFrame]:
    """
    Validate uploaded or loaded dataset schema.
    Returns:
        is_valid: bool
        errors: List of fatal errors that prevent dashboard rendering
        warnings: List of non-fatal warnings (e.g., missing optional demographics)
        standardized_df: DataFrame with standardized column names
    """
    errors: List[str] = []
    warnings: List[str] = []

    if df is None or df.empty:
        errors.append("Uploaded dataset is empty or could not be read.")
        return False, errors, warnings, df

    # Standardize column names
    standardized_df, mapping = match_column_aliases(df)

    # Check for grade columns
    found_grades = [g for g in ["G1", "G2", "G3"] if g in standardized_df.columns]
    
    if "G3" not in standardized_df.columns and len(found_grades) == 0:
        # Check if single score column exists
        score_candidates = [c for c in standardized_df.columns if "score" in c.lower() or "grade" in c.lower() or "mark" in c.lower()]
        if score_candidates:
            standardized_df["G3"] = standardized_df[score_candidates[0]]
            warnings.append(f"Mapped column '{score_candidates[0]}' as final target grade 'G3'.")
        else:
            errors.append(
                f"Missing critical grade/performance columns. Required at least 'G3' (Final Grade) or standard grade columns: {ESSENTIAL_GRADE_COLUMNS}. Found columns: {list(df.columns)}"
            )

    # Check for G1 and G2 fallback
    if "G1" not in standardized_df.columns and "G3" in standardized_df.columns:
        standardized_df["G1"] = standardized_df["G3"]
        warnings.append("G1 (Period 1 Grade) not found; defaulted to G3 for multi-period analytics.")
    if "G2" not in standardized_df.columns and "G3" in standardized_df.columns:
        standardized_df["G2"] = standardized_df["G3"]
        warnings.append("G2 (Period 2 Grade) not found; defaulted to G3 for multi-period analytics.")

    # Check for subject column
    if "subject" not in standardized_df.columns:
        standardized_df["subject"] = "General"
        warnings.append("Subject column not found; assigned 'General' to all records.")

    # Check for student ID
    if "student_id" not in standardized_df.columns:
        standardized_df["student_id"] = [f"STU-{i+1:04d}" for i in range(len(standardized_df))]

    is_valid = len(errors) == 0
    return is_valid, errors, warnings, standardized_df


def analyze_data_quality(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform comprehensive data quality audit.
    Calculates total rows, duplicates, missing values, invalid values, and quality index.
    """
    total_rows = len(raw_df)
    total_cols = len(raw_df.columns)
    duplicate_rows = int(raw_df.duplicated().sum())

    # Missing values breakdown
    missing_by_col = raw_df.isnull().sum().to_dict()
    total_missing_cells = int(raw_df.isnull().sum().sum())
    columns_with_missing = {k: int(v) for k, v in missing_by_col.items() if v > 0}

    # Check invalid numerical values (e.g. negative grades, grades > 20 if max <= 20 or > 100, negative absences)
    invalid_counts = 0
    invalid_details = []

    for grade_col in ["G1", "G2", "G3"]:
        if grade_col in cleaned_df.columns:
            # Ensure numeric
            numeric_series = pd.to_numeric(cleaned_df[grade_col], errors="coerce")
            neg_count = int((numeric_series < 0).sum())
            over_count = int((numeric_series > 100).sum())
            if neg_count > 0:
                invalid_counts += neg_count
                invalid_details.append(f"{neg_count} negative scores in {grade_col}")
            if over_count > 0:
                invalid_counts += over_count
                invalid_details.append(f"{over_count} scores > 100 in {grade_col}")

    if "absences" in cleaned_df.columns:
        abs_numeric = pd.to_numeric(cleaned_df["absences"], errors="coerce")
        neg_abs = int((abs_numeric < 0).sum())
        if neg_abs > 0:
            invalid_counts += neg_abs
            invalid_details.append(f"{neg_abs} negative absences")

    cleaned_rows = len(cleaned_df)
    total_cells = total_rows * total_cols if total_rows > 0 else 1
    clean_cells = max(0, total_cells - total_missing_cells - invalid_counts)
    quality_score = round((clean_cells / total_cells) * 100, 1)

    return {
        "total_rows": total_rows,
        "total_columns": total_cols,
        "duplicate_rows": duplicate_rows,
        "total_missing_cells": total_missing_cells,
        "columns_with_missing": columns_with_missing,
        "invalid_values_count": invalid_counts,
        "invalid_details": invalid_details,
        "cleaned_rows": cleaned_rows,
        "quality_score_pct": quality_score,
        "is_perfect_quality": (duplicate_rows == 0 and total_missing_cells == 0 and invalid_counts == 0)
    }
