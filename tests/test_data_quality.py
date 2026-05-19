# pyrefly: ignore [missing-import]
import pytest
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
from data_quality_toolkit.data_quality import MetricsCalculator, DataProfiler, RuleValidator


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "id": [1, 2, 2, 4, 5],
        "name": ["Alice", "Bob", "Bob", None, "Eve"],
        "age": [25, 30, 30, 150, 22] # 150 is an outlier
    })


@pytest.fixture
def metrics_calculator():
    return MetricsCalculator()


def test_missing_values_calculation(metrics_calculator, sample_data):
    result = metrics_calculator.missing_values(sample_data)
    assert result.loc["name", "Missing_Count"] == 1
    assert result.loc["name", "Missing_Percent"] == 20.0
    assert result.loc["id", "Missing_Count"] == 0


def test_duplicate_rows_detection(metrics_calculator, sample_data):
    assert metrics_calculator.duplicates(sample_data) == 1


def test_unique_values_count(metrics_calculator, sample_data):
    result = metrics_calculator.unique_values(sample_data)
    assert result.loc["id", "Unique_Count"] == 4
    assert result.loc["name", "Unique_Count"] == 3


def test_outliers_detection(metrics_calculator, sample_data):
    result = metrics_calculator.outliers(sample_data)
    assert "age" in result
    assert result["age"] == 1 # The value 150


def test_column_statistics_numeric(metrics_calculator, sample_data):
    result = metrics_calculator.column_stats(sample_data)
    assert "mean" in result.columns
    assert "std" in result.columns


def test_column_statistics_categorical(metrics_calculator, sample_data):
    result = metrics_calculator.column_stats(sample_data)
    assert "unique" in result.columns


def test_profile_data_structure(sample_data):
    profiler = DataProfiler(sample_data)
    result = profiler.profile()
    assert result["total_rows"] == 5
    assert result["total_columns"] == 3
    assert "missing_values" in result
    assert "duplicate_rows" in result
    assert "unique_values" in result
    assert "outliers" in result


def test_rule_validator_numeric():
    df = pd.DataFrame({"age": [10, 20, 30, 150]})
    rules = [{"column": "age", "type": "numeric", "min": 0, "max": 100}]
    validator = RuleValidator(rules)
    res = validator.validate(df)
    assert not res["age"]["is_valid"]
    assert res["age"]["violations_count"] == 1


def test_rule_validator_categorical():
    df = pd.DataFrame({"status": ["active", "inactive", "deleted", "active"]})
    rules = [{"column": "status", "type": "categorical", "allowed_values": ["active", "inactive"]}]
    validator = RuleValidator(rules)
    res = validator.validate(df)
    assert not res["status"]["is_valid"]
    assert res["status"]["violations_count"] == 1


def test_rule_validator_date():
    df = pd.DataFrame({"date_col": ["2023-01-01", "01/02/2023", "2023-12-31"]})
    rules = [{"column": "date_col", "type": "date", "format": "%Y-%m-%d"}]
    validator = RuleValidator(rules)
    res = validator.validate(df)
    assert not res["date_col"]["is_valid"]
    assert res["date_col"]["violations_count"] == 1 # "01/02/2023" fails the %Y-%m-%d format
