"""
Machine Learning Performance Classification and Feature Importance Module.
Supports Logistic Regression, Decision Tree, and Random Forest classification with
reproducible pipelines, multi-metric evaluation, confusion matrices, and interactive simulation.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


def prepare_features_and_target(
    df: pd.DataFrame,
    target_type: str = "category",  # 'category' or 'pass_fail'
    include_earlier_grades: bool = True
) -> Tuple[pd.DataFrame, pd.Series, List[str], List[str]]:
    """
    Selects valid features and target variable from the dataset.
    """
    df_model = df.copy()

    # Target definition
    if target_type == "pass_fail":
        target_col = "pass_status"
        if target_col not in df_model.columns:
            df_model[target_col] = np.where(df_model["G3"] >= 10, "Passed", "Failed")
    else:
        target_col = "performance_category"

    y = df_model[target_col]

    # Exclude leakage / identifiers / target columns
    leakage_cols = [
        "student_id", "G3", "final_score", "final_score_pct", "average_score",
        "average_score_pct", "performance_category", "pass_status", "is_passed",
        "is_at_risk", "risk_level", "grade_change", "grade_trend"
    ]
    if not include_earlier_grades:
        leakage_cols.extend(["G1", "G2"])

    feature_cols = [c for c in df_model.columns if c not in leakage_cols]

    X = df_model[feature_cols]

    # Identify numeric vs categorical
    numeric_features = []
    categorical_features = []
    for col in X.columns:
        if pd.api.types.is_numeric_dtype(X[col]):
            numeric_features.append(col)
        else:
            categorical_features.append(col)

    return X, y, numeric_features, categorical_features


def train_performance_classifier(
    df: pd.DataFrame,
    model_name: str = "Random Forest",
    target_type: str = "category",
    test_size: float = 0.25,
    random_state: int = 42,
    include_earlier_grades: bool = True,
    hyperparams: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Builds, trains, and evaluates a performance classification pipeline.
    Returns complete metrics, confusion matrix, feature importances, and trained pipeline.
    """
    if df.empty or len(df) < 15:
        return {"error": "Insufficient data to train machine learning model (minimum 15 records required)."}

    X, y, num_cols, cat_cols = prepare_features_and_target(
        df, target_type=target_type, include_earlier_grades=include_earlier_grades
    )

    if len(y.unique()) < 2:
        return {"error": "Target variable has only 1 class in the current filtered dataset. Please broaden filters."}

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y if len(y.unique()) <= 5 else None
    )

    # Preprocessing Pipeline
    transformers = []
    if num_cols:
        transformers.append(("num", StandardScaler(), num_cols))
    if cat_cols:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols))

    preprocessor = ColumnTransformer(transformers=transformers)

    # Model instantiation
    hp = hyperparams or {}
    if model_name == "Logistic Regression":
        clf = LogisticRegression(
            C=hp.get("C", 1.0),
            max_iter=hp.get("max_iter", 1000),
            random_state=random_state
        )
    elif model_name == "Decision Tree":
        clf = DecisionTreeClassifier(
            max_depth=hp.get("max_depth", 6),
            min_samples_split=hp.get("min_samples_split", 5),
            random_state=random_state
        )
    else:  # Random Forest
        clf = RandomForestClassifier(
            n_estimators=hp.get("n_estimators", 100),
            max_depth=hp.get("max_depth", 8),
            random_state=random_state
        )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", clf)
    ])

    # Train
    pipeline.fit(X_train, y_train)

    # Predict
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)

    # Metrics
    classes = sorted(list(y.unique()))
    acc = round(float(accuracy_score(y_test, y_pred_test)), 4)
    train_acc = round(float(accuracy_score(y_train, y_pred_train)), 4)
    prec = round(float(precision_score(y_test, y_pred_test, average="weighted", zero_division=0)), 4)
    rec = round(float(recall_score(y_test, y_pred_test, average="weighted", zero_division=0)), 4)
    f1 = round(float(f1_score(y_test, y_pred_test, average="weighted", zero_division=0)), 4)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred_test, labels=classes)
    
    # Classification report dict
    report = classification_report(y_test, y_pred_test, labels=classes, output_dict=True, zero_division=0)

    # Feature Importance extraction
    feature_importances = []
    try:
        encoded_features = []
        if num_cols:
            encoded_features.extend(num_cols)
        if cat_cols:
            cat_encoder = pipeline.named_steps["preprocessor"].named_transformers_["cat"]
            encoded_cat_names = cat_encoder.get_feature_names_out(cat_cols)
            encoded_features.extend(list(encoded_cat_names))

        if hasattr(clf, "feature_importances_"):
            importances = clf.feature_importances_
            fi_df = pd.DataFrame({
                "feature": encoded_features,
                "importance": importances
            }).sort_values(by="importance", ascending=False)
            feature_importances = fi_df.head(15).to_dict(orient="records")

        elif hasattr(clf, "coef_"):
            # Logistic Regression coefficients
            avg_coef = np.mean(np.abs(clf.coef_), axis=0) if clf.coef_.ndim > 1 else np.abs(clf.coef_)
            fi_df = pd.DataFrame({
                "feature": encoded_features,
                "importance": avg_coef
            }).sort_values(by="importance", ascending=False)
            feature_importances = fi_df.head(15).to_dict(orient="records")
    except Exception as e:
        print(f"Feature importance calculation note: {e}")

    return {
        "model_name": model_name,
        "target_type": target_type,
        "classes": classes,
        "accuracy": acc,
        "train_accuracy": train_acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "confusion_matrix": cm,
        "classification_report": report,
        "feature_importances": feature_importances,
        "test_size": test_size,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "pipeline": pipeline,
        "feature_columns": list(X.columns),
        "numeric_features": num_cols,
        "categorical_features": cat_cols
    }


def predict_single_student(
    pipeline: Pipeline,
    student_input: Dict[str, Any],
    feature_cols: List[str],
    num_cols: Optional[List[str]] = None,
    cat_cols: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Runs prediction for a single interactive student simulator input.
    Ensures strict type coercion for numeric and categorical features to prevent
    scikit-learn OneHotEncoder and NumPy ufunc errors.
    """
    num_set = set(num_cols) if num_cols else set()
    cat_set = set(cat_cols) if cat_cols else set()

    # Build input dictionary with strict type defaults
    row_data = {}
    for col in feature_cols:
        val = student_input.get(col, None)
        if col in num_set:
            try:
                row_data[col] = float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                row_data[col] = 0.0
        elif col in cat_set:
            row_data[col] = str(val) if val is not None else ""
        else:
            # Fallback heuristic if num_cols/cat_cols missing
            if isinstance(val, (int, float, np.number)):
                row_data[col] = float(val)
            elif isinstance(val, str):
                row_data[col] = val
            else:
                row_data[col] = 0.0 if val is None else str(val)

    input_df = pd.DataFrame([row_data])[feature_cols]

    # Explicit dtype enforcement
    for col in input_df.columns:
        if num_cols and col in num_set:
            input_df[col] = input_df[col].astype(float)
        elif cat_cols and col in cat_set:
            input_df[col] = input_df[col].astype(str)

    pred_class = pipeline.predict(input_df)[0]
    probabilities = {}
    if hasattr(pipeline, "predict_proba"):
        probs = pipeline.predict_proba(input_df)[0]
        classes = pipeline.classes_
        for cls_name, prob in zip(classes, probs):
            probabilities[str(cls_name)] = round(float(prob) * 100, 1)

    return {
        "predicted_class": pred_class,
        "probabilities": probabilities
    }


