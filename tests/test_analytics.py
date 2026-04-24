"""
Tests for HR analytics calculations.
"""
import pytest
import pandas as pd
import sys, os
sys.path.insert(0, os.path.abspath("."))
from scripts.data_generator import (
    generate_employees, generate_performance_reviews,
    generate_training, save_to_sqlite
)
from scripts.analytics import (
    calculate_attrition_metrics, calculate_salary_equity,
    calculate_performance_metrics, calculate_diversity_metrics,
    predict_attrition_risk, run_sql_queries
)


@pytest.fixture(scope="module")
def employees():
    return generate_employees(1000)


@pytest.fixture(scope="module")
def reviews(employees):
    return generate_performance_reviews(employees)


@pytest.fixture(scope="module")
def training(employees):
    return generate_training(employees)


@pytest.fixture(scope="module")
def db(employees, reviews, training):
    save_to_sqlite(employees, reviews, training)
    return "data/hr.db"


class TestAttritionMetrics:

    def test_returns_dict(self, employees):
        result = calculate_attrition_metrics(employees)
        assert isinstance(result, dict)

    def test_has_required_keys(self, employees):
        result = calculate_attrition_metrics(employees)
        required = ["total_employees", "total_attrited",
                    "overall_attrition_rate", "by_department",
                    "by_job_level", "by_reason"]
        for key in required:
            assert key in result

    def test_total_matches_dataframe(self, employees):
        result = calculate_attrition_metrics(employees)
        assert result["total_employees"] == len(employees)

    def test_attrition_rate_within_range(self, employees):
        result = calculate_attrition_metrics(employees)
        assert 0 <= result["overall_attrition_rate"] <= 100

    def test_by_department_has_all_depts(self, employees):
        result = calculate_attrition_metrics(employees)
        assert len(result["by_department"]) == 10

    def test_reasons_only_for_attrited(self, employees):
        result = calculate_attrition_metrics(employees)
        total_reasons = result["by_reason"]["count"].sum()
        assert total_reasons == result["total_attrited"]


class TestSalaryEquity:

    def test_returns_dataframe(self, employees):
        result = calculate_salary_equity(employees)
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self, employees):
        result = calculate_salary_equity(employees)
        for col in ["gender", "job_level", "avg_salary", "salary_gap_pct"]:
            assert col in result.columns

    def test_avg_salary_positive(self, employees):
        result = calculate_salary_equity(employees)
        assert (result["avg_salary"] > 0).all()


class TestPerformanceMetrics:

    def test_returns_dataframe(self, employees):
        result = calculate_performance_metrics(employees)
        assert isinstance(result, pd.DataFrame)

    def test_returns_all_departments(self, employees):
        result = calculate_performance_metrics(employees)
        assert len(result) == 10

    def test_avg_performance_within_range(self, employees):
        result = calculate_performance_metrics(employees)
        assert result["avg_performance"].between(1, 5).all()

    def test_avg_satisfaction_within_range(self, employees):
        result = calculate_performance_metrics(employees)
        assert result["avg_satisfaction"].between(1, 5).all()


class TestDiversityMetrics:

    def test_returns_dict(self, employees):
        result = calculate_diversity_metrics(employees)
        assert isinstance(result, dict)

    def test_gender_distribution_sums_to_100(self, employees):
        result = calculate_diversity_metrics(employees)
        assert abs(result["gender_distribution"].sum() - 100) < 1

    def test_race_distribution_sums_to_100(self, employees):
        result = calculate_diversity_metrics(employees)
        assert abs(result["race_distribution"].sum() - 100) < 1

    def test_remote_work_pct_within_range(self, employees):
        result = calculate_diversity_metrics(employees)
        assert 0 <= result["remote_work_pct"] <= 100


class TestAttritionRiskPrediction:

    def test_returns_dataframe(self, employees):
        result = predict_attrition_risk(employees)
        assert isinstance(result, pd.DataFrame)

    def test_risk_score_within_range(self, employees):
        result = predict_attrition_risk(employees)
        assert result["risk_score"].between(0, 1).all()

    def test_risk_level_values_valid(self, employees):
        result = predict_attrition_risk(employees)
        valid = {"Low", "Medium", "High"}
        actual = set(result["risk_level"].dropna().astype(str).unique())
        assert actual.issubset(valid)

    def test_sorted_by_risk_descending(self, employees):
        result = predict_attrition_risk(employees)
        scores = result["risk_score"].tolist()
        assert scores == sorted(scores, reverse=True)


class TestSQLQueries:

    def test_all_queries_return_results(self, db):
        results = run_sql_queries(db)
        expected = ["attrition_by_department", "salary_by_gender_level",
                    "top_performers", "attrition_reasons",
                    "remote_work_impact", "training_effectiveness"]
        for key in expected:
            assert key in results
            assert len(results[key]) > 0

    def test_attrition_by_dept_has_all_depts(self, db):
        results = run_sql_queries(db)
        assert len(results["attrition_by_department"]) == 10

    def test_top_performers_returns_20(self, db):
        results = run_sql_queries(db)
        assert len(results["top_performers"]) <= 20
