import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np


class MetricsCalculator:
    """
    Calcula métricas de calidad de datos.
    """
    def missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100
        result = pd.DataFrame({'Missing_Count': missing, 'Missing_Percent': missing_pct})
        return result

    def duplicates(self, df: pd.DataFrame) -> int:
        return df.duplicated().sum()

    def unique_values(self, df: pd.DataFrame) -> pd.DataFrame:
        unique = df.nunique()
        unique_pct = (unique / len(df)) * 100
        result = pd.DataFrame({'Unique_Count': unique, 'Unique_Percent': unique_pct})
        return result

    def outliers(self, df: pd.DataFrame) -> dict:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outliers_dict = {}
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
            outliers_dict[col] = len(outliers)
        return outliers_dict

    def column_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.describe(include='all').transpose()


class DataProfiler:
    """
    Genera un perfil resumido del dataset.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.metrics = MetricsCalculator()
    
    def profile(self) -> dict:
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'missing_values': self.metrics.missing_values(self.df).to_dict(orient='index'),
            'duplicate_rows': int(self.metrics.duplicates(self.df)),
            'unique_values': self.metrics.unique_values(self.df).to_dict(orient='index'),
            'outliers': self.metrics.outliers(self.df),
        }


class RuleValidator:
    """
    Valida los datos basándose en reglas específicas proporcionadas por el usuario.
    """
    def __init__(self, rules: list):
        self.rules = rules

    def validate(self, df: pd.DataFrame) -> dict:
        results = {}
        for rule in self.rules:
            col = rule.get("column")
            if col not in df.columns:
                results[col] = {"error": f"Columna '{col}' no encontrada."}
                continue

            rule_type = rule.get("type")
            allow_nulls = rule.get("allow_nulls", True)
            violations = 0

            # Validación de Nulos
            if not allow_nulls:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    violations += null_count

            if rule_type == "numeric":
                min_val = rule.get("min")
                max_val = rule.get("max")
                
                # Convert to numeric, errors='coerce' turns non-numeric to NaN
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                
                if min_val is not None:
                    violators = df[(numeric_series < float(min_val)) & df[col].notnull()]
                    violations += len(violators)
                if max_val is not None:
                    violators = df[(numeric_series > float(max_val)) & df[col].notnull()]
                    violations += len(violators)
                    
            elif rule_type == "categorical":
                allowed_values = rule.get("allowed_values", [])
                if allowed_values:
                    violators = df[~df[col].isin(allowed_values) & df[col].notnull()]
                    violations = len(violators)
            
            elif rule_type == "date":
                date_format = rule.get("format")
                if date_format:
                    # Convert to datetime with specific format
                    converted = pd.to_datetime(df[col], format=date_format, errors='coerce')
                    violators = df[converted.isnull() & df[col].notnull()]
                    violations = len(violators)
            
            results[col] = {
                "rule": rule,
                "violations_count": violations,
                "is_valid": violations == 0
            }
        
        return results
