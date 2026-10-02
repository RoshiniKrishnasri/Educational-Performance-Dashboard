# 🎓 Educational Performance Analytics Dashboard

An interactive, production-ready educational analytics web application built with Python, Streamlit, Plotly, Pandas, Scikit-learn, and SQLite.

The dashboard empowers educators, academic advisors, and school administrators to analyze student performance data, identify learning gaps across demographic and behavioral cohorts, evaluate multi-variable academic drivers, perform machine learning-based performance classification, and export custom reports.

---

### 👤 Developer & Contact
- **Developer**: Roshini Krishna Sri
- **Email**: [roshinikrishnasri@gmail.com](mailto:roshinikrishnasri@gmail.com)
- **GitHub**: [github.com/roshinikrishnasri](https://github.com/roshinikrishnasri)
- **LinkedIn**: [linkedin.com/in/roshinikrishnasri](https://www.linkedin.com/in/roshinikrishnasri)

---

## 🌟 Key Features & Dashboard Pages

### 📌 Page 1 — Executive Overview
- **Dynamic KPI Cards**: Total Students, Average Score (0–20 & %), Pass Percentage, Failure Percentage, At-Risk Student Count, and Average Attendance Rate.
- **Subject-Wise Performance**: Comparison of Mathematics and Portuguese courses with standard error bars and pass rates.
- **Performance Category Distribution**: Donut visualization classifying students into *Excellent (16–20)*, *Good (14–15)*, *Satisfactory (12–13)*, *Needs Improvement (10–11)*, and *Fail/At-Risk (<10)*.
- **Academic Progression**: Box plot distributions tracking period-over-period grades ($G1 \rightarrow G2 \rightarrow G3$).
- **Score Distribution & Density**: Histogram with parametric mean and median benchmarks.
- **Data Quality Auditor**: Ingestion audit displaying total rows, duplicates, missing cells imputed, invalid values coerced, and clean rows.
- **Dynamic Insights**: Automatically generated executive findings reflecting real-time filter states.

### 📈 Page 2 — Comparative Performance Analysis
- **Multidimensional Comparisons**: Drill down by Subject, Gender, Study Time, Attendance Category, Institution, Urban/Rural Address, Parental Education, Internet Access, and Family Support.
- **Flexible Chart Modes**: Switch between Box Plots, Violin Spread Plots, and Aggregated Mean Bar Charts.
- **Cohort Aggregates Table**: Detailed numerical breakdowns with pass rates, failure rates, and at-risk percentages.
- **Correlation Heatmap & Top Drivers**: Pearson correlation matrix with ranked top positive and negative correlates with final scores.

### 👤 Page 3 — Individual Student Dossier
- **Student Search & Selector**: Search by Student ID (e.g., `STU-0012`, `MAT-0005`, `POR-0020`).
- **Student Profile Card**: Demographics, school, attendance, study habits, and risk status.
- **Multidimensional Radar Chart**: Student scores and habits mapped against the overall cohort benchmark.
- **Longitudinal Grade Timeline**: Individual $G1 \rightarrow G2 \rightarrow G3$ trajectory vs. cohort average line.
- **Pedagogical Action Plans**: Tailored intervention strategies generated dynamically based on student performance.
- **Peer Benchmark Comparison**: Side-by-side comparative table against school and cohort benchmarks.

### 🎯 Page 4 — Learning Gap & Academic Equity Analysis
- **Interactive Competency Threshold**: Dynamic slider to test custom pass/fail criteria (5.0 to 18.0 points).
- **Equity Disparity Diagnostics**: Identifies subjects and cohorts lagging behind cohort benchmarks.
- **Underperforming Cohorts Table**: Automated detection of demographic groups with negative score disparities.
- **Dynamic Analytical Observations**: Actionable recommendations for remediation, office hours, and attendance alerts.

### 🤖 Page 5 — Machine Learning Predictive Intelligence
- **Classification Algorithms**:
  - Random Forest Classifier
  - Decision Tree Classifier
  - Logistic Regression
- **Target Selection**: Multi-class Performance Category (5 classes) or Binary Pass/Fail Status.
- **Pipeline Controls**: Configurable train/test split, optional inclusion of early period grades ($G1, G2$), and automatic numerical scaling + one-hot encoding.
- **Comprehensive Evaluation**: Test Accuracy, Precision, Recall, F1-Score, and Interactive Confusion Matrix Heatmap.
- **Top Feature Importance**: Ranked bar chart of top predictive behavioral and academic features.
- **Interactive "What-If" Student Simulator**: Adjust hypothetical student parameters (study hours, absences, previous failures, parental education) to predict outcomes with probability distributions.
- *Strictly labeled with educational estimates disclaimer.*

### 📑 Page 6 — Reports & Database Persistence
- **Filtered Data Export**: Download filtered dataset as standard CSV.
- **Multi-Sheet Excel Report (`.xlsx`)**: Formatted workbook containing student records, descriptive statistics, and learning gap summaries.
- **Executive Summary Document (`.md`)**: Downloadable text report summarizing all analytical findings.
- **Interactive Record Explorer**: Interactive data table with custom column toggles.
- **SQLite Database Persistence**:
  - Save filtered cohorts and custom uploaded datasets to SQLite database.
  - View, manage, and delete saved snapshots across sessions.

---

## 🏗️ Project Architecture

```
Educational Performance Analysis/
│
├── app.py                     # Main Streamlit web application
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
│
├── data/                      # Dataset repository & SQLite database
│   ├── student-mat.csv        # UCI Mathematics course dataset
│   ├── student-por.csv        # UCI Portuguese course dataset
│   ├── student-combined.csv   # Unified multi-subject dataset
│   ├── student.txt            # UCI dataset attribute documentation
│   └── educational_analytics.db # SQLite persistent database
│
├── src/                       # Core analytical & computational backend
│   ├── __init__.py
│   ├── data_loader.py         # CSV/Excel ingestion, delimiter sniffing & quality auditor
│   ├── preprocessing.py       # Cleaning, imputation, feature engineering & categorical mapping
│   ├── analytics.py           # Descriptive statistics, cohort aggregations & learning gaps
│   ├── ml_model.py            # Scikit-learn classification pipelines & what-if simulator
│   ├── insights.py            # Dynamic natural language insight and recommendation engine
│   ├── visualization.py       # Plotly chart generators with unified modern styling
│   └── db.py                  # SQLite database interface & snapshot manager
│
└── components/                # Modular Streamlit UI components
    ├── __init__.py
    ├── filters.py             # Sidebar filtering engine & dataset switcher
    ├── kpis.py                # Responsive glassmorphic KPI cards
    └── charts.py              # Chart layout container wrappers
```

---

## 🚀 Installation & Quick Start

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Clone or Navigate to Project Directory
```bash
cd "c:\Users\roshi\Downloads\REAL_WORLD_PROJECTS\Educational Performance Analysis"
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
The application will automatically open in your default browser at `http://localhost:8501`.

---

## 📊 Dataset Information
This project utilizes the **UCI Student Performance Data Set** (Cortez and Silva, 2008).

### Dataset Attributes:
- **School**: Gabriel Pereira (`GP`) or Mousinho da Silveira (`MS`)
- **Sex**: Female (`F`) or Male (`M`)
- **Age**: 15 to 22
- **Address**: Urban (`U`) or Rural (`R`)
- **Study Time**: Weekly study hours ($1: <2\text{h}, 2: 2\text{-}5\text{h}, 3: 5\text{-}10\text{h}, 4: >10\text{h}$)
- **Failures**: Number of past class failures ($0 \le n \le 4$)
- **Absences**: School absences ($0 \text{ to } 93$)
- **Grades**:
  - `G1`: First period grade ($0 \text{ to } 20$)
  - `G2`: Second period grade ($0 \text{ to } 20$)
  - `G3`: Final grade ($0 \text{ to } 20$, target outcome)

The ingestion layer also accommodates **custom uploaded CSV or Excel files** by automatically mapping column synonyms and validating schemas.

---

## 🧪 Testing & Validation
All calculations, machine learning pipelines, and data transformations are thoroughly unit-tested for stability and zero silent drops.

To verify the backend pipeline via command line:
```bash
python -c "
from src.data_loader import load_builtin_dataset, validate_dataset
from src.preprocessing import preprocess_pipeline
from src.analytics import compute_descriptive_stats, compute_learning_gap_analysis
from src.ml_model import train_performance_classifier

df = load_builtin_dataset('combined')
is_valid, errs, warns, std_df = validate_dataset(df)
clean_df, log = preprocess_pipeline(std_df)
stats = compute_descriptive_stats(clean_df)
gaps = compute_learning_gap_analysis(clean_df)
ml = train_performance_classifier(clean_df)
print('✓ Ingestion Validated:', is_valid)
print('✓ Students Enriched:', len(clean_df))
print('✓ Mean Score:', stats['mean'])
print('✓ ML Accuracy:', ml['accuracy'])
"
```

---

## 🎓 Academic Portfolio & Presentation Note
Designed as an exemplary portfolio project showcasing:
- Data Ingestion & Quality Engineering (Zero silent data loss, automated delimiter detection)
- Advanced Feature Engineering & Aggregation
- Interactive Multi-Page UI Architecture
- Interpretable Machine Learning & Simulation
- Data Persistence using SQLite
- Actionable Pedagogical Intelligence
