import pandas as pd
from data_quality_toolkit.data_ingestion import DataLoader, SchemaValidator
from data_quality_toolkit.data_quality import DataProfiler, RuleValidator
from data_quality_toolkit.visualization_report import VisualizationEngine, ReportGenerator
from data_quality_toolkit.recommendations import RecommendationEngine


class DataQualityToolkit:
    """
    Interfaz principal que orquesta todos los módulos.
    """
    def __init__(self, output_dir="output"):
        self.loader = DataLoader()
        self.validator = SchemaValidator()
        self.profiler = None
        self.visualizer = VisualizationEngine(output_dir)
        self.reporter = ReportGenerator(output_dir)
        self.recommender = RecommendationEngine()
        self.df = None

    def load_data(self, source: str, format: str = "csv", query: str = None) -> pd.DataFrame:
        if format == "csv":
            self.df = self.loader.load_csv(source)
        elif format == "excel":
            self.df = self.loader.load_excel(source)
        elif format == "json":
            self.df = self.loader.load_json(source)
        elif format == "parquet":
            self.df = self.loader.load_parquet(source)
        elif format == "sql":
            if not query:
                raise ValueError("Query is required for SQL format")
            self.df = self.loader.load_sql(source, query)
        else:
            raise ValueError(f"Format {format} not supported")
        return self.df

    def validate_data(self, df: pd.DataFrame = None) -> dict:
        df = df if df is not None else self.df
        if df is None:
            raise ValueError("No data loaded. Call load_data first.")
        columns_valid = self.validator.validate_columns(df)
        types_valid = self.validator.validate_types(df)
        return {
            "columns": columns_valid,
            "types": types_valid
        }

    def profile_data(self, df: pd.DataFrame = None) -> dict:
        df = df if df is not None else self.df
        if df is None:
            raise ValueError("No data loaded. Call load_data first.")
        self.profiler = DataProfiler(df)
        return self.profiler.profile()

    def visualize_data(self, df: pd.DataFrame = None) -> list:
        df = df if df is not None else self.df
        if df is None:
            raise ValueError("No data loaded. Call load_data first.")
        
        filepaths = []
        filepaths.append(self.visualizer.missing_values_heatmap(df))
        filepaths.append(self.visualizer.correlation_matrix(df))
        filepaths.extend(self.visualizer.histogram_columns(df, df.select_dtypes(include=['number']).columns[:5]))
        filepaths.extend(self.visualizer.categorical_distribution(df, df.select_dtypes(include=['object', 'category']).columns[:5]))
        
        return [f for f in filepaths if f is not None]

    def generate_report(self, profile: dict, format: str = "html", filename: str = "report") -> str:
        if format == "html":
            return self.reporter.generate_html(profile, filename)
        elif format == "pdf":
            return self.reporter.generate_pdf(profile, filename)
        elif format == "excel":
            return self.reporter.generate_excel(profile, filename)
        else:
            raise ValueError(f"Format {format} not supported")

    def get_recommendations(self, df: pd.DataFrame = None, rules: list = None) -> dict:
        df = df if df is not None else self.df
        if df is None:
            raise ValueError("No data loaded. Call load_data first.")
        
        return {
            "duplicates": self.recommender.suggest_duplicate_handling(df),
            "imputations": self.recommender.suggest_imputation(df, rules),
            "outliers": self.recommender.suggest_outlier_handling(df),
            "transformations": self.recommender.suggest_transformations(df)
        }

    def apply_custom_rules(self, rules: list, df: pd.DataFrame = None) -> dict:
        df = df if df is not None else self.df
        if df is None:
            raise ValueError("No data loaded. Call load_data first.")
        
        validator = RuleValidator(rules)
        return validator.validate(df)
