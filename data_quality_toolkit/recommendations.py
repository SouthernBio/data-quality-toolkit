import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np


class RecommendationEngine:
    """
    Sugiere acciones de limpieza y transformación basadas en métricas de calidad.
    """
    def suggest_imputation(self, df: pd.DataFrame, rules: list = None) -> dict:
        suggestions = {}
        missing = df.isnull().sum()
        
        rules_dict = {}
        if rules:
            for r in rules:
                rules_dict[r["column"]] = r

        for col in df.columns:
            if missing[col] > 0:
                rule = rules_dict.get(col, {})
                allow_nulls = rule.get("allow_nulls", True)
                
                missing_pct = (missing[col] / len(df)) * 100
                
                if missing_pct > 50:
                    suggestions[col] = f"Eliminar columna (más del 50% de valores faltantes: {missing_pct:.2f}%)"
                elif not allow_nulls:
                    suggestions[col] = "Eliminar las filas con valores nulos, dado que la regla estricta no permite nulos."
                elif pd.api.types.is_numeric_dtype(df[col]):
                    suggestions[col] = "Imputar con la mediana o la media"
                else:
                    suggestions[col] = "Imputar con la moda (valor más frecuente)"
        return suggestions

    def suggest_duplicate_handling(self, df: pd.DataFrame) -> dict:
        duplicates = df.duplicated().sum()
        suggestions = {}
        if duplicates > 0:
            suggestions["dataset"] = f"Se detectaron {duplicates} filas duplicadas exactas. Se recomienda eliminarlas ('df.drop_duplicates()') para evitar sesgos estadísticos, a menos que se trate de transacciones o eventos independientes sin identificador único."
        return suggestions

    def suggest_outlier_handling(self, df: pd.DataFrame) -> dict:
        suggestions = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            if len(outliers) > 0:
                suggestions[col] = f"Considerar aplicar Winsorization o transformar con logaritmo (se detectaron {len(outliers)} outliers)"
        return suggestions

    def suggest_transformations(self, df: pd.DataFrame) -> dict:
        suggestions = {}
        for col in df.columns:
            if pd.api.types.is_object_dtype(df[col]):
                unique_pct = df[col].nunique() / len(df) * 100
                if unique_pct < 5:
                    suggestions[col] = "Transformar a tipo categórico para optimizar memoria"
                elif df[col].nunique() == 2:
                    suggestions[col] = "Codificar usando One-Hot Encoding o booleanos"
            elif pd.api.types.is_numeric_dtype(df[col]):
                skewness = df[col].skew()
                if abs(skewness) > 1:
                    suggestions[col] = f"La distribución está muy sesgada (skewness: {skewness:.2f}). Considerar transformación logarítmica o Box-Cox"
        return suggestions
