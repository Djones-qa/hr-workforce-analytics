"""
HR workforce analytics engine —
attrition analysis, salary equity, performance, and diversity metrics.
"""
import pandas as pd
import numpy as np
import sqlite3


def calculate_attrition_metrics(employees_df: pd.DataFrame) -> dict:
    """Calculate overall and segmented attrition metrics."""
    total = len(employees_df)
    attrited = employees_df["is_attrited"].sum()

    by_dept = employees_df.groupby("department")["is_attrited"].agg(
        ["sum", "count", "mean"]
    ).rename(columns={"sum": "attrited", "count": "total",
                      "mean": "attrition_rate"})
    by_dept["attrition_rate"] = by_dept["attrition_rate"].round(3)

    by_level = employees_df.groupby("job_level")["is_attrited"].agg(
        ["sum", "count", "mean"]
    ).rename(columns={"sum": "attrited", "count": "total",
                      "mean": "attrition_rate"})
    by_level["attrition_rate"] = by_level["attrition_rate"].round(3)

    by_reason = employees_df[employees_df["is_attrited"] == True][
        "reason_left"
    ].value_counts().reset_index()
    by_reason.columns = ["reason", "count"]

    return {
        "total_employees": total,
        "total_attrited": int(attrited),
        "overall_attrition_rate": round(attrited / total * 100, 2),
        "by_department": by_dept.reset_index(),
        "by_job_level": by_level.reset_index(),
        "by_reason": by_reason,
    }


def calculate_salary_equity(employees_df: pd.DataFrame) -> pd.DataFrame:
    """Analyze salary equity across gender and race."""
    gender_salary = employees_df.groupby(
        ["department", "gender", "job_level"]
    )["salary"].agg(["mean", "median", "count"]).round(0).reset_index()
    gender_salary.columns = ["department", "gender", "job_level",
                              "avg_salary", "median_salary", "count"]

    dept_avg = employees_df.groupby("department")["salary"].mean()
    gender_salary["dept_avg_salary"] = gender_salary["department"].map(dept_avg)
    gender_salary["salary_gap_pct"] = (
        (gender_salary["avg_salary"] - gender_salary["dept_avg_salary"]) /
        gender_salary["dept_avg_salary"] * 100
    ).round(2)
    return gender_salary


def calculate_performance_metrics(employees_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate performance metrics by department."""
    perf = employees_df.groupby("department").agg(
        avg_performance=("performance_score", "mean"),
        avg_satisfaction=("satisfaction_score", "mean"),
        avg_manager_rating=("manager_rating", "mean"),
        avg_training_hours=("training_hours", "mean"),
        avg_absences=("absences_days", "mean"),
        total_promotions=("promotions", "sum"),
        overtime_pct=("overtime", "mean"),
    ).round(2).reset_index()
    return perf.sort_values("avg_performance", ascending=False)


def calculate_diversity_metrics(employees_df: pd.DataFrame) -> dict:
    """Calculate workforce diversity metrics."""
    gender_dist = (employees_df["gender"].value_counts(normalize=True) * 100).round(2)
    race_dist = (employees_df["race"].value_counts(normalize=True) * 100).round(2)
    education_dist = (employees_df["education"].value_counts(normalize=True) * 100).round(2)

    leadership = employees_df[employees_df["job_level"].isin(["Manager", "Director"])]
    leadership_gender = (leadership["gender"].value_counts(normalize=True) * 100).round(2)
    leadership_race = (leadership["race"].value_counts(normalize=True) * 100).round(2)

    return {
        "gender_distribution": gender_dist,
        "race_distribution": race_dist,
        "education_distribution": education_dist,
        "leadership_gender": leadership_gender,
        "leadership_race": leadership_race,
        "remote_work_pct": round(employees_df["remote_work"].mean() * 100, 2),
    }


def predict_attrition_risk(employees_df: pd.DataFrame) -> pd.DataFrame:
    """Score each employee for attrition risk."""
    df = employees_df.copy()
    df["risk_score"] = (
        (1 - df["satisfaction_score"] / 5) * 0.30 +
        (1 - df["performance_score"] / 5) * 0.20 +
        (df["absences_days"] / 20).clip(0, 1) * 0.15 +
        (df["overtime"].astype(int)) * 0.15 +
        (1 - df["manager_rating"] / 5) * 0.20
    ).round(3)

    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-0.01, 0.3, 0.6, 1.01],
        labels=["Low", "Medium", "High"]
    )
    return df[["employee_id", "department", "job_level",
               "salary", "tenure_days", "risk_score",
               "risk_level"]].sort_values("risk_score", ascending=False)


def run_sql_queries(db_path: str = "data/hr.db") -> dict:
    """Run HR SQL investigation queries."""
    conn = sqlite3.connect(db_path)
    queries = {
        "attrition_by_department": """
            SELECT department,
                   COUNT(*) as total,
                   SUM(is_attrited) as attrited,
                   ROUND(100.0 * SUM(is_attrited) / COUNT(*), 2)
                   as attrition_rate_pct,
                   ROUND(AVG(salary), 0) as avg_salary
            FROM employees
            GROUP BY department
            ORDER BY attrition_rate_pct DESC
        """,
        "salary_by_gender_level": """
            SELECT gender, job_level,
                   COUNT(*) as employees,
                   ROUND(AVG(salary), 0) as avg_salary,
                   ROUND(MIN(salary), 0) as min_salary,
                   ROUND(MAX(salary), 0) as max_salary
            FROM employees
            GROUP BY gender, job_level
            ORDER BY job_level, gender
        """,
        "top_performers": """
            SELECT employee_id, department, job_level,
                   salary, performance_score,
                   satisfaction_score, promotions
            FROM employees
            WHERE performance_score >= 4.5
            ORDER BY performance_score DESC
            LIMIT 20
        """,
        "attrition_reasons": """
            SELECT reason_left,
                   COUNT(*) as count,
                   ROUND(AVG(salary), 0) as avg_salary,
                   ROUND(AVG(tenure_days), 0) as avg_tenure_days
            FROM employees
            WHERE is_attrited = 1
            GROUP BY reason_left
            ORDER BY count DESC
        """,
        "remote_work_impact": """
            SELECT remote_work,
                   COUNT(*) as employees,
                   ROUND(AVG(satisfaction_score), 2) as avg_satisfaction,
                   ROUND(AVG(performance_score), 2) as avg_performance,
                   ROUND(100.0 * SUM(is_attrited) / COUNT(*), 2)
                   as attrition_rate_pct
            FROM employees
            GROUP BY remote_work
        """,
        "training_effectiveness": """
            SELECT e.department,
                   COUNT(DISTINCT t.employee_id) as trained_employees,
                   ROUND(AVG(t.score), 2) as avg_training_score,
                   ROUND(AVG(e.performance_score), 2) as avg_performance,
                   ROUND(AVG(t.hours), 1) as avg_training_hours
            FROM training t
            JOIN employees e ON t.employee_id = e.employee_id
            WHERE t.completed = 1
            GROUP BY e.department
            ORDER BY avg_performance DESC
        """,
    }
    results = {}
    for name, query in queries.items():
        results[name] = pd.read_sql_query(query, conn)
    conn.close()
    return results
