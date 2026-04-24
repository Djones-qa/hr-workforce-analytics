"""
Tests for HR workforce data generation.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.abspath("."))
from scripts.data_generator import (
    generate_employees, generate_performance_reviews,
    generate_training, save_to_sqlite, save_to_csv
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


class TestEmployeeGeneration:

    def test_correct_employee_count(self, employees):
        assert len(employees) == 1000

    def test_employee_ids_unique(self, employees):
        assert employees["employee_id"].nunique() == 1000

    def test_age_within_valid_range(self, employees):
        assert employees["age"].between(22, 62).all()

    def test_no_null_values_in_critical_fields(self, employees):
        critical = ["employee_id", "department", "job_level",
                    "salary", "hire_date"]
        for col in critical:
            assert employees[col].isnull().sum() == 0

    def test_salary_is_positive(self, employees):
        assert (employees["salary"] > 0).all()

    def test_attrition_rate_reasonable(self, employees):
        rate = employees["is_attrited"].mean()
        assert 0.10 <= rate <= 0.45

    def test_satisfaction_within_range(self, employees):
        assert employees["satisfaction_score"].between(1, 5).all()

    def test_performance_within_range(self, employees):
        assert employees["performance_score"].between(1, 5).all()

    def test_job_level_values_valid(self, employees):
        from scripts.data_generator import JOB_LEVELS
        assert set(employees["job_level"].unique()).issubset(set(JOB_LEVELS))

    def test_department_values_valid(self, employees):
        from scripts.data_generator import DEPARTMENTS
        assert set(employees["department"].unique()).issubset(set(DEPARTMENTS))

    def test_is_attrited_is_boolean(self, employees):
        assert employees["is_attrited"].dtype == bool

    def test_attrited_employees_have_reason(self, employees):
        attrited = employees[employees["is_attrited"] == True]
        assert attrited["reason_left"].isnull().sum() == 0


class TestReviewGeneration:

    def test_reviews_generated(self, reviews):
        assert len(reviews) > 0

    def test_review_ids_unique(self, reviews):
        assert reviews["review_id"].nunique() == len(reviews)

    def test_performance_rating_within_range(self, reviews):
        assert reviews["performance_rating"].between(1, 5).all()

    def test_goals_met_within_range(self, reviews):
        assert reviews["goals_met_pct"].between(50, 100).all()

    def test_review_year_within_range(self, reviews):
        assert reviews["review_year"].between(2020, 2024).all()


class TestTrainingGeneration:

    def test_training_generated(self, training):
        assert len(training) > 0

    def test_training_ids_unique(self, training):
        assert training["training_id"].nunique() == len(training)

    def test_score_within_range(self, training):
        assert training["score"].between(60, 100).all()

    def test_hours_positive(self, training):
        assert (training["hours"] > 0).all()

    def test_completed_is_boolean(self, training):
        assert training["completed"].dtype == bool


class TestDataPersistence:

    def test_save_to_csv(self, employees, reviews, training):
        save_to_csv(employees, reviews, training)
        assert os.path.exists("data/employees.csv")
        assert os.path.exists("data/performance_reviews.csv")
        assert os.path.exists("data/training.csv")

    def test_save_to_sqlite(self, employees, reviews, training):
        path = save_to_sqlite(employees, reviews, training)
        assert os.path.exists(path)
