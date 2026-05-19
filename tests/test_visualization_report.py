# pyrefly: ignore [missing-import]
import pytest
import pandas as pd
import os
from data_quality_toolkit.visualization_report import VisualizationEngine, ReportGenerator

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Alice", "Eve"],
        "age": [25, 30, 35, 40, 45],
        "salary": [50000, 60000, 70000, 80000, 90000]
    })

@pytest.fixture
def profile_data():
    return {
        "total_rows": 5,
        "total_columns": 4,
        "missing_values": {"age": {"Missing_Count": 0, "Missing_Percent": 0.0}},
        "outliers": {"salary": 0}
    }

@pytest.fixture
def output_dir(tmpdir):
    return str(tmpdir)

@pytest.fixture
def visualization_engine(output_dir):
    return VisualizationEngine(output_dir=output_dir)

@pytest.fixture
def report_generator(output_dir):
    return ReportGenerator(output_dir=output_dir)

def test_missing_values_heatmap_generation(visualization_engine, sample_data):
    filepath = visualization_engine.missing_values_heatmap(sample_data)
    assert os.path.exists(filepath)
    assert filepath.endswith("missing_heatmap.png")

def test_correlation_matrix_generation(visualization_engine, sample_data):
    filepath = visualization_engine.correlation_matrix(sample_data)
    assert os.path.exists(filepath)
    assert filepath.endswith("correlation_matrix.png")

def test_histogram_generation(visualization_engine, sample_data):
    filepaths = visualization_engine.histogram_columns(sample_data, ["age", "salary"])
    assert len(filepaths) == 2
    for filepath in filepaths:
        assert os.path.exists(filepath)

def test_categorical_distribution_plot(visualization_engine, sample_data):
    filepaths = visualization_engine.categorical_distribution(sample_data, ["name"])
    assert len(filepaths) == 1
    assert os.path.exists(filepaths[0])

def test_generate_html_report(report_generator, profile_data):
    filepath = report_generator.generate_html(profile_data, "test_report")
    assert os.path.exists(filepath)
    assert filepath.endswith(".html")
    with open(filepath, 'r') as f:
        content = f.read()
        assert "Data Quality Report" in content

def test_generate_pdf_report(report_generator, profile_data):
    filepath = report_generator.generate_pdf(profile_data, "test_report")
    assert os.path.exists(filepath)
    assert filepath.endswith(".pdf")

def test_generate_excel_report(report_generator, profile_data):
    filepath = report_generator.generate_excel(profile_data, "test_report")
    assert os.path.exists(filepath)
    assert filepath.endswith(".xlsx")
    df = pd.read_excel(filepath, sheet_name='Summary')
    assert df.iloc[0]['Total Rows'] == 5
