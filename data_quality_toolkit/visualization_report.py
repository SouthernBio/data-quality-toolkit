import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from fpdf import FPDF


class VisualizationEngine:
    """
    Genera gráficos de calidad de datos.
    """
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def missing_values_heatmap(self, df: pd.DataFrame) -> str:
        plt.figure(figsize=(10, 6))
        sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
        plt.title('Missing Values Heatmap')
        filepath = os.path.join(self.output_dir, 'missing_heatmap.png')
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        return filepath

    def correlation_matrix(self, df: pd.DataFrame) -> str:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return None
        plt.figure(figsize=(10, 8))
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Matrix')
        filepath = os.path.join(self.output_dir, 'correlation_matrix.png')
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        return filepath

    def histogram_columns(self, df: pd.DataFrame, columns: list) -> list:
        filepaths = []
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                plt.figure(figsize=(8, 5))
                sns.histplot(df[col].dropna(), kde=True)
                plt.title(f'Histogram of {col}')
                filepath = os.path.join(self.output_dir, f'hist_{col}.png')
                plt.tight_layout()
                plt.savefig(filepath)
                plt.close()
                filepaths.append(filepath)
        return filepaths

    def categorical_distribution(self, df: pd.DataFrame, columns: list) -> list:
        filepaths = []
        for col in columns:
            if col in df.columns and (pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col])):
                plt.figure(figsize=(8, 5))
                sns.countplot(y=df[col], order=df[col].value_counts().index[:10])
                plt.title(f'Top 10 Categories in {col}')
                filepath = os.path.join(self.output_dir, f'cat_{col}.png')
                plt.tight_layout()
                plt.savefig(filepath)
                plt.close()
                filepaths.append(filepath)
        return filepaths


class ReportGenerator:
    """
    Genera reportes exportables (HTML, PDF, Excel) a partir del perfil.
    """
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_html(self, profile: dict, filename: str) -> str:
        filepath = os.path.join(self.output_dir, f"{filename}.html")
        html_content = f"<html><head><title>Data Quality Report</title></head><body>"
        html_content += "<h1>Data Quality Report</h1>"
        html_content += f"<p>Total Rows: {profile.get('total_rows', 0)}</p>"
        html_content += f"<p>Total Columns: {profile.get('total_columns', 0)}</p>"
        html_content += "<h2>Missing Values</h2><pre>" + json.dumps(profile.get('missing_values', {}), indent=2) + "</pre>"
        html_content += "<h2>Outliers</h2><pre>" + json.dumps(profile.get('outliers', {}), indent=2) + "</pre>"
        html_content += "</body></html>"
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        return filepath

    def generate_pdf(self, profile: dict, filename: str) -> str:
        filepath = os.path.join(self.output_dir, f"{filename}.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Data Quality Report", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Total Rows: {profile.get('total_rows', 0)}", ln=True)
        pdf.cell(200, 10, txt=f"Total Columns: {profile.get('total_columns', 0)}", ln=True)
        
        pdf.cell(200, 10, txt="Missing Values:", ln=True)
        for col, data in profile.get('missing_values', {}).items():
            pdf.cell(200, 10, txt=f"  {col}: {data.get('Missing_Count')} ({data.get('Missing_Percent'):.2f}%)", ln=True)

        pdf.output(filepath)
        return filepath

    def generate_excel(self, profile: dict, filename: str) -> str:
        filepath = os.path.join(self.output_dir, f"{filename}.xlsx")
        with pd.ExcelWriter(filepath) as writer:
            pd.DataFrame([{'Total Rows': profile.get('total_rows', 0), 'Total Columns': profile.get('total_columns', 0)}]).to_excel(writer, sheet_name='Summary', index=False)
            
            missing_df = pd.DataFrame.from_dict(profile.get('missing_values', {}), orient='index')
            if not missing_df.empty:
                missing_df.to_excel(writer, sheet_name='Missing Values')
                
            outliers_df = pd.DataFrame(list(profile.get('outliers', {}).items()), columns=['Column', 'Outlier_Count'])
            if not outliers_df.empty:
                outliers_df.to_excel(writer, sheet_name='Outliers', index=False)
        return filepath
