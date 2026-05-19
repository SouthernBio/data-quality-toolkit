import pytest
import pandas as pd
import os
from data_quality_toolkit.toolkit_interface import DataQualityToolkit

@pytest.fixture
def sample_csv(tmpdir):
    filepath = os.path.join(tmpdir, "test.csv")
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": ["x", "y", "z"]
    })
    df.to_csv(filepath, index=False)
    return filepath

@pytest.fixture
def toolkit(tmpdir):
    return DataQualityToolkit(output_dir=str(tmpdir))

def test_load_data_cli(toolkit, sample_csv):
    df = toolkit.load_data(sample_csv, format="csv")
    assert not df.empty
    assert list(df.columns) == ["A", "B"]

def test_validate_data_cli(toolkit, sample_csv):
    toolkit.load_data(sample_csv, format="csv")
    result = toolkit.validate_data()
    assert result["columns"]["is_valid"] is True

def test_profile_data_cli(toolkit, sample_csv):
    toolkit.load_data(sample_csv, format="csv")
    profile = toolkit.profile_data()
    assert profile["total_rows"] == 3
    assert profile["total_columns"] == 2

def test_visualize_data_cli(toolkit, sample_csv):
    toolkit.load_data(sample_csv, format="csv")
    filepaths = toolkit.visualize_data()
    assert len(filepaths) > 0
    for fp in filepaths:
        assert os.path.exists(fp)

def test_generate_report_cli(toolkit, sample_csv):
    toolkit.load_data(sample_csv, format="csv")
    profile = toolkit.profile_data()
    filepath = toolkit.generate_report(profile, format="html", filename="test_report")
    assert os.path.exists(filepath)
    assert filepath.endswith(".html")

def test_get_recommendations_cli(toolkit, sample_csv):
    toolkit.load_data(sample_csv, format="csv")
    recs = toolkit.get_recommendations()
    assert "imputations" in recs
    assert "outliers" in recs
    assert "transformations" in recs
