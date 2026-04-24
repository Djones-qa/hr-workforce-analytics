"""
Generates realistic HR workforce data for
attrition analysis, performance tracking, and workforce analytics.
"""
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import sqlite3
import os

fake = Faker()
Faker.seed(42)

DEPARTMENTS = [
    "Engineering", "Sales", "Marketing", "HR", "Finance",
    "Operations", "Customer Support", "Legal", "Product", "Data"
]

JOB_LEVELS = ["Junior", "Mid", "Senior", "Lead", "Manager", "Director"]

EDUCATION = ["High School", "Bachelor", "Master", "PhD"]

REASONS_LEFT = [
    "Better Opportunity", "Compensation", "Work-Life Balance",
    "Career Growth", "Relocation", "Management Issues",
    "Company Culture", "Personal Reasons"
]


def generate_employees(num_employees: int = 1000) -> pd.DataFrame:
    """Generate realistic employee data."""
    rng = random.Random(42)
    records = []
    base_date = datetime(2018, 1, 1)

    for i in range(1, num_employees + 1):
        hire_date = base_date + timedelta(days=rng.randint(0, 2000))
        age = rng.randint(22, 62)
        job_level = rng.choice(JOB_LEVELS)
        dept = rng.choice(DEPARTMENTS)

        # Salary based on level and department
        base_salary = {
            "Junior": 45000, "Mid": 65000, "Senior": 90000,
            "Lead": 110000, "Manager": 130000, "Director": 160000
        }[job_level]
        salary = round(base_salary * rng.uniform(0.85, 1.20))

        # Attrition more likely for junior, low salary, long tenure
        tenure_days = (datetime(2024, 12, 31) - hire_date).days
        attrition_prob = 0.15
        if job_level == "Junior":
            attrition_prob += 0.10
        if salary < 55000:
            attrition_prob += 0.08
        if tenure_days > 1800:
            attrition_prob += 0.05

        is_attrited = rng.random() < attrition_prob
        exit_date = None
        reason_left = None

        if is_attrited:
            exit_days = rng.randint(180, tenure_days or 365)
            exit_date = (hire_date + timedelta(days=exit_days)).strftime("%Y-%m-%d")
            reason_left = rng.choice(REASONS_LEFT)

        records.append({
            "employee_id": f"EMP{i:05d}",
            "age": age,
            "gender": rng.choice(["Male", "Female", "Non-Binary"]),
            "race": rng.choice(["White", "Black", "Hispanic",
                                   "Asian", "Other"]),
            "department": dept,
            "job_level": job_level,
            "education": rng.choice(EDUCATION),
            "hire_date": hire_date.strftime("%Y-%m-%d"),
            "exit_date": exit_date,
            "tenure_days": tenure_days,
            "salary": salary,
            "is_attrited": is_attrited,
            "reason_left": reason_left,
            "remote_work": rng.choice([True, False]),
            "overtime": rng.choice([True, False]),
            "satisfaction_score": round(rng.uniform(1, 5), 1),
            "performance_score": round(rng.uniform(1, 5), 1),
            "training_hours": rng.randint(0, 80),
            "absences_days": rng.randint(0, 20),
            "promotions": rng.randint(0, 5),
            "manager_rating": round(rng.uniform(1, 5), 1),
        })
    return pd.DataFrame(records)


def generate_performance_reviews(employees_df: pd.DataFrame) -> pd.DataFrame:
    """Generate annual performance review data."""
    rng = random.Random(42)
    records = []
    for _, emp in employees_df.iterrows():
        num_reviews = rng.randint(1, 5)
        for year in range(2020, 2020 + num_reviews):
            records.append({
                "review_id": f"REV{len(records)+1:06d}",
                "employee_id": emp["employee_id"],
                "review_year": year,
                "performance_rating": round(rng.uniform(1, 5), 1),
                "goals_met_pct": round(rng.uniform(50, 100), 1),
                "skills_rating": round(rng.uniform(1, 5), 1),
                "communication_rating": round(rng.uniform(1, 5), 1),
                "leadership_rating": round(rng.uniform(1, 5), 1),
                "recommended_for_promotion": rng.random() < 0.20,
                "training_completed": rng.randint(0, 40),
            })
    return pd.DataFrame(records)


def generate_training(employees_df: pd.DataFrame) -> pd.DataFrame:
    """Generate employee training records."""
    rng = random.Random(42)
    courses = [
        "Leadership Fundamentals", "Data Analytics", "Communication Skills",
        "Project Management", "Python Programming", "Agile Methodology",
        "Diversity and Inclusion", "Cybersecurity Basics", "Excel Advanced",
        "Customer Service Excellence"
    ]
    records = []
    for _, emp in employees_df.sample(n=700, random_state=42).iterrows():
        num_courses = rng.randint(1, 4)
        for course in rng.sample(courses, min(num_courses, len(courses))):
            records.append({
                "training_id": f"TRN{len(records)+1:06d}",
                "employee_id": emp["employee_id"],
                "course": course,
                "hours": rng.randint(4, 40),
                "score": round(rng.uniform(60, 100), 1),
                "completed": rng.random() < 0.85,
                "year": rng.randint(2020, 2024),
            })
    return pd.DataFrame(records)


def save_to_sqlite(employees_df, reviews_df, training_df,
                   db_path="data/hr.db"):
    """Save all datasets to SQLite."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(db_path)
    employees_df.to_sql("employees", conn, if_exists="replace", index=False)
    reviews_df.to_sql("performance_reviews", conn,
                      if_exists="replace", index=False)
    training_df.to_sql("training", conn, if_exists="replace", index=False)
    conn.close()
    return db_path


def save_to_csv(employees_df, reviews_df, training_df):
    """Save all datasets to CSV."""
    os.makedirs("data", exist_ok=True)
    employees_df.to_csv("data/employees.csv", index=False)
    reviews_df.to_csv("data/performance_reviews.csv", index=False)
    training_df.to_csv("data/training.csv", index=False)
    print("CSVs saved!")
