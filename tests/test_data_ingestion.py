# pyrefly: ignore [missing-import]
import pytest
import pandas as pd
import os
import sqlite3
from data_quality_toolkit.data_ingestion import DataLoader, SchemaValidator


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35]
    })


@pytest.fixture
def data_loader():
    return DataLoader()


@pytest.fixture
def schema_validator():
    return SchemaValidator()


def test_load_csv_success(data_loader, sample_data, tmpdir):
    filepath = os.path.join(tmpdir, "test.csv")
    sample_data.to_csv(filepath, index=False)
    df = data_loader.load_csv(filepath)
    pd.testing.assert_frame_equal(df, sample_data)


def test_load_excel_success(data_loader, sample_data, tmpdir):
    filepath = os.path.join(tmpdir, "test.xlsx")
    sample_data.to_excel(filepath, index=False)
    df = data_loader.load_excel(filepath)
    pd.testing.assert_frame_equal(df, sample_data)


def test_load_json_success(data_loader, sample_data, tmpdir):
    filepath = os.path.join(tmpdir, "test.json")
    sample_data.to_json(filepath, orient="records")
    df = data_loader.load_json(filepath)
    pd.testing.assert_frame_equal(df, sample_data)


def test_load_parquet_success(data_loader, sample_data, tmpdir):
    filepath = os.path.join(tmpdir, "test.parquet")
    sample_data.to_parquet(filepath, index=False)
    df = data_loader.load_parquet(filepath)
    pd.testing.assert_frame_equal(df, sample_data)


def test_load_sql_success(data_loader, sample_data, tmpdir):
    filepath = os.path.join(tmpdir, "test.db")
    conn_str = f"sqlite:///{filepath}"
    engine = sqlite3.connect(filepath)
    sample_data.to_sql("users", engine, index=False)
    engine.close()
    
    df = data_loader.load_sql(conn_str, "SELECT * FROM users")
    pd.testing.assert_frame_equal(df, sample_data)


def test_validate_columns_no_duplicates(schema_validator, sample_data):
    result = schema_validator.validate_columns(sample_data)
    assert result["total_columns"] == 3
    assert result["duplicate_columns"] == []
    assert result["is_valid"] is True


def test_validate_columns_with_duplicates(schema_validator):
    df = pd.DataFrame([[1, 2, 3]], columns=["A", "B", "A"])
    result = schema_validator.validate_columns(df)
    assert result["total_columns"] == 3
    assert "A" in result["duplicate_columns"]
    assert result["is_valid"] is False


def test_validate_types_correct(schema_validator, sample_data):
    result = schema_validator.validate_types(sample_data)
    assert "id" in result["types"]
    assert len(result["mixed_type_columns"]) == 0


def test_validate_types_incorrect(schema_validator):
    df = pd.DataFrame({
        "mixed": [1, "two", 3.0]
    })
    result = schema_validator.validate_types(df)
    assert "mixed" in result["mixed_type_columns"]
