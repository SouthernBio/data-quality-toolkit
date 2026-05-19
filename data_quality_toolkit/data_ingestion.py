import pandas as pd
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
import os


class DataLoader:
    """
    Clase responsable de cargar datasets desde distintos formatos.
    """
    def load_csv(self, filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo {filepath} no existe.")
        return pd.read_csv(filepath)

    def load_excel(self, filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo {filepath} no existe.")
        return pd.read_excel(filepath)

    def load_json(self, filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo {filepath} no existe.")
        return pd.read_json(filepath)

    def load_parquet(self, filepath: str) -> pd.DataFrame:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo {filepath} no existe.")
        return pd.read_parquet(filepath)

    def load_sql(self, connection_string: str, query: str) -> pd.DataFrame:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn)


class SchemaValidator:
    """
    Valida estructura básica del dataset: columnas duplicadas, tipos inconsistentes.
    """
    def validate_columns(self, df: pd.DataFrame) -> dict:
        columns = df.columns.tolist()
        duplicates = set([col for col in columns if columns.count(col) > 1])
        return {
            "total_columns": len(columns),
            "duplicate_columns": list(duplicates),
            "is_valid": len(duplicates) == 0
        }

    def validate_types(self, df: pd.DataFrame) -> dict:
        types = df.dtypes.astype(str).to_dict()
        return {
            "types": types,
            "mixed_type_columns": [col for col in df.columns if df[col].apply(type).nunique() > 1]
        }
