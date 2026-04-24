"""
Tests for HR workforce visualizations.
"""
import pytest
import os
import sys
import matplotlib
matplotlib.use("Agg")
sys.path.insert(0, os.path.abspath("."))
from scripts.data_generator import (
    generate_employees, generate_performance_reviews, generate_training
)
from scripts.analytics import predict_attrition_risk
from scripts.visualizations import (
    plot_attrition_by_department, plot_salary_by_gender,
    plot_performance_heatmap, plot_attrition_reasons,
    plot_tenure_distribution, plot_satisfaction_vs_performance,
    plot_diversity_breakdown, plot_attrition_risk
)


def remove_visual_if_exists(filename):
    path = os.path.join("visuals", filename)
    if os.path.exists(path):
        os.remove(path)
    return path


@pytest.fixture(scope="module")
def employees():
    return generate_employees(1000)


@pytest.fixture(scope="module")
def risk_df(employees):
    return predict_attrition_risk(employees)


class TestVisualizations:

    def test_attrition_by_dept_chart_created(self, employees):
        remove_visual_if_exists("01_attrition_by_department.png")
        path = plot_attrition_by_department(employees)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_salary_by_gender_chart_created(self, employees):
        remove_visual_if_exists("02_salary_by_gender.png")
        path = plot_salary_by_gender(employees)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_performance_heatmap_created(self, employees):
        remove_visual_if_exists("03_performance_heatmap.png")
        path = plot_performance_heatmap(employees)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_attrition_reasons_chart_created(self, employees):
        remove_visual_if_exists("04_attrition_reasons.png")
        path = plot_attrition_reasons(employees)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_tenure_distribution_chart_created(self, employees):
        remove_visual_if_exists("05_tenure_distribution.png")
        path = plot_tenure_distribution(employees)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_satisfaction_performance_chart_created(self, employees):
        remove_visual_if_exists("06_satisfaction_vs_performance.png")
        path = plot_satisfaction_vs_performance(employees)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_diversity_breakdown_chart_created(self, employees):
        remove_visual_if_exists("07_diversity_breakdown.png")
        path = plot_diversity_breakdown(employees)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_attrition_risk_chart_created(self, risk_df):
        remove_visual_if_exists("08_attrition_risk.png")
        path = plot_attrition_risk(risk_df)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_all_charts_are_png(self):
        charts = [f for f in os.listdir("visuals") if f.endswith(".png")]
        assert len(charts) >= 8

    def test_all_charts_non_empty(self):
        for f in os.listdir("visuals"):
            if f.endswith(".png"):
                assert os.path.getsize(f"visuals/{f}") > 0
