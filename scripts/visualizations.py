"""
HR workforce analytics visualizations.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import warnings

sns.set_theme(style="darkgrid")
os.makedirs("visuals", exist_ok=True)

COLORS = {
    "blue": "#1B4F8A",
    "green": "#2ECC71",
    "red": "#E74C3C",
    "orange": "#F39C12",
    "purple": "#9B59B6",
    "teal": "#1ABC9C",
    "gray": "#95A5A6",
}


def save(fig, name):
    path = f"visuals/{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_attrition_by_department(employees_df):
    """Bar chart — attrition rate by department."""
    dept_attr = employees_df.groupby("department")[
        "is_attrited"].mean().sort_values(ascending=False) * 100
    fig, ax = plt.subplots(figsize=(13, 6))
    colors = [COLORS["red"] if r > 25 else COLORS["orange"]
              if r > 18 else COLORS["green"]
              for r in dept_attr.values]
    bars = ax.bar(dept_attr.index, dept_attr.values, color=colors, alpha=0.85)
    ax.axhline(y=dept_attr.mean(), color=COLORS["gray"],
               linestyle="--", linewidth=2,
               label=f"Average: {dept_attr.mean():.1f}%")
    for bar, val in zip(bars, dept_attr.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                f"{val:.1f}%", ha="center", fontsize=9, fontweight="bold")
    ax.set_title("Employee Attrition Rate by Department",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Attrition Rate (%)")
    plt.xticks(rotation=30, ha="right")
    ax.legend()
    return save(fig, "01_attrition_by_department")


def plot_salary_by_gender(employees_df):
    """Box plot — salary distribution by gender."""
    fig, ax = plt.subplots(figsize=(11, 6))
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"vert: bool will be deprecated in a future version\. Use orientation: \{'vertical', 'horizontal'\} instead\.",
            category=PendingDeprecationWarning,
        )
        sns.boxplot(data=employees_df, x="job_level", y="salary",
                    hue="gender", palette=["#1B4F8A", "#E74C3C", "#2ECC71"],
                    order=["Junior", "Mid", "Senior", "Lead",
                           "Manager", "Director"],
                    ax=ax)
    ax.set_title("Salary Distribution by Job Level and Gender",
                 fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Job Level")
    ax.set_ylabel("Salary ($)")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    return save(fig, "02_salary_by_gender")


def plot_performance_heatmap(employees_df):
    """Heatmap — avg performance by dept and job level."""
    pivot = employees_df.pivot_table(
        values="performance_score",
        index="department",
        columns="job_level",
        aggfunc="mean"
    ).round(2)
    col_order = ["Junior", "Mid", "Senior", "Lead", "Manager", "Director"]
    pivot = pivot.reindex(columns=[c for c in col_order if c in pivot.columns])
    fig, ax = plt.subplots(figsize=(13, 8))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="Blues",
                ax=ax, linewidths=0.5, vmin=1, vmax=5)
    ax.set_title("Average Performance Score by Department and Job Level",
                 fontsize=13, fontweight="bold", pad=15)
    return save(fig, "03_performance_heatmap")


def plot_attrition_reasons(employees_df):
    """Horizontal bar — attrition reasons."""
    reasons = employees_df[employees_df["is_attrited"] == True][
        "reason_left"].value_counts()
    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.barh(reasons.index, reasons.values,
                   color=COLORS["orange"], alpha=0.85)
    for bar, val in zip(bars, reasons.values):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=9, fontweight="bold")
    ax.set_title("Employee Attrition Reasons",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Employees")
    return save(fig, "04_attrition_reasons")


def plot_tenure_distribution(employees_df):
    """Histogram — tenure distribution by attrition status."""
    fig, ax = plt.subplots(figsize=(12, 6))
    stayed = employees_df[employees_df["is_attrited"] == False]["tenure_days"] / 365
    left = employees_df[employees_df["is_attrited"] == True]["tenure_days"] / 365
    ax.hist(stayed, bins=30, alpha=0.6, color=COLORS["blue"],
            label="Stayed", density=True)
    ax.hist(left, bins=30, alpha=0.6, color=COLORS["red"],
            label="Left", density=True)
    ax.set_title("Tenure Distribution — Stayed vs Attrited Employees",
                 fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Tenure (Years)")
    ax.set_ylabel("Density")
    ax.legend()
    return save(fig, "05_tenure_distribution")


def plot_satisfaction_vs_performance(employees_df):
    """Scatter — satisfaction vs performance colored by attrition."""
    fig, ax = plt.subplots(figsize=(11, 7))
    stayed = employees_df[employees_df["is_attrited"] == False]
    left = employees_df[employees_df["is_attrited"] == True]
    ax.scatter(stayed["satisfaction_score"], stayed["performance_score"],
               alpha=0.4, color=COLORS["blue"], s=20, label="Stayed")
    ax.scatter(left["satisfaction_score"], left["performance_score"],
               alpha=0.4, color=COLORS["red"], s=20, label="Attrited")
    ax.set_title("Satisfaction vs Performance — Stayed vs Attrited",
                 fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Satisfaction Score")
    ax.set_ylabel("Performance Score")
    ax.legend()
    return save(fig, "06_satisfaction_vs_performance")


def plot_diversity_breakdown(employees_df):
    """Pie charts — gender and race diversity."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    gender = employees_df["gender"].value_counts()
    race = employees_df["race"].value_counts()
    colors1 = [COLORS["blue"], COLORS["red"], COLORS["green"]]
    colors2 = [COLORS["blue"], COLORS["orange"], COLORS["green"],
               COLORS["purple"], COLORS["teal"]]
    axes[0].pie(gender.values, labels=gender.index,
                colors=colors1[:len(gender)], autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"edgecolor": "white", "linewidth": 2})
    axes[0].set_title("Gender Distribution",
                      fontsize=13, fontweight="bold")
    axes[1].pie(race.values, labels=race.index,
                colors=colors2[:len(race)], autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"edgecolor": "white", "linewidth": 2})
    axes[1].set_title("Race/Ethnicity Distribution",
                      fontsize=13, fontweight="bold")
    fig.suptitle("Workforce Diversity Breakdown",
                 fontsize=14, fontweight="bold", y=1.02)
    return save(fig, "07_diversity_breakdown")


def plot_attrition_risk(risk_df):
    """Bar chart — attrition risk level distribution."""
    risk_counts = risk_df["risk_level"].value_counts()
    colors = [COLORS["green"] if r == "Low" else
              COLORS["orange"] if r == "Medium" else
              COLORS["red"] for r in risk_counts.index]
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(risk_counts.index, risk_counts.values,
                  color=colors, alpha=0.85)
    for bar, val in zip(bars, risk_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 2,
                str(val), ha="center", fontsize=11, fontweight="bold")
    ax.set_title("Employee Attrition Risk Distribution",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Risk Level")
    ax.set_ylabel("Number of Employees")
    return save(fig, "08_attrition_risk")
