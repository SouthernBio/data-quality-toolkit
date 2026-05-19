# pyrefly: ignore [missing-import]
import pytest
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
from data_quality_toolkit.recommendations import RecommendationEngine


@pytest.fixture
def recommendation_engine():
    return RecommendationEngine()


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "name": ["Alice", "Bob", "Charlie", "Alice", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"],
        "age": [25, 30, 35, 40, 45, None, None, None, None, None], # 50% missing
        "salary": [50000, 60000, 70000, 80000, 90000, 55000, 65000, 75000, 85000, 1000000], # 1 outlier
        "gender": ["F", "M", "M", "F", "F", "M", "F", "F", "M", "F"] # Categorical, low cardinality
    })


def test_suggest_imputation_for_missing_values(recommendation_engine, sample_data):
    # Add a column with >50% missing
    sample_data["lots_of_missing"] = [1, None, None, None, None, None, None, None, None, None]
    
    # Introduce a missing value in 'name'
    sample_data.loc[0, "name"] = None
    
    rules = [
        {"column": "age", "allow_nulls": False},
        {"column": "name", "allow_nulls": False}
    ]
    
    suggestions = recommendation_engine.suggest_imputation(sample_data, rules)
    assert "age" in suggestions
    assert "Eliminar las filas con valores nulos" in suggestions["age"]
    
    # 'name' has allow_nulls=False, should recommend deleting
    assert "name" in suggestions
    assert "Eliminar las filas con valores nulos" in suggestions["name"]
    
    assert "lots_of_missing" in suggestions
    assert "Eliminar columna" in suggestions["lots_of_missing"]


def test_suggest_duplicate_handling(recommendation_engine):
    df = pd.DataFrame({"id": [1, 1, 2], "val": ["A", "A", "B"]})
    suggestions = recommendation_engine.suggest_duplicate_handling(df)
    assert "dataset" in suggestions
    assert "duplicadas exactas" in suggestions["dataset"]


def test_suggest_outlier_handling(recommendation_engine, sample_data):
    suggestions = recommendation_engine.suggest_outlier_handling(sample_data)
    assert "salary" in suggestions
    assert "outliers" in suggestions["salary"]


def test_suggest_transformations_for_numeric(recommendation_engine, sample_data):
    # Create highly skewed data
    skewed_df = pd.DataFrame({"skewed_col": [1, 1, 1, 1, 2, 2, 3, 4, 100, 1000]})
    suggestions = recommendation_engine.suggest_transformations(skewed_df)
    assert "skewed_col" in suggestions
    assert "sesgada" in suggestions["skewed_col"]


def test_suggest_transformations_for_categorical(recommendation_engine, sample_data):
    suggestions = recommendation_engine.suggest_transformations(sample_data)
    assert "gender" in suggestions
    assert "categórico" in suggestions["gender"] or "One-Hot" in suggestions["gender"]
