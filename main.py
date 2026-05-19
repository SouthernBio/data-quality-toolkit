import argparse
import sys
import json
from data_quality_toolkit.toolkit_interface import DataQualityToolkit


def main():
    parser = argparse.ArgumentParser(description="Data Quality Toolkit CLI")
    parser.add_argument("--file", type=str, help="Ruta al archivo de dataset", required=True)
    parser.add_argument("--format", type=str, help="Formato del archivo (csv, excel, json, parquet, sql)", default="csv")
    parser.add_argument("--sql-query", type=str, help="Consulta SQL (requerida si format=sql)")
    parser.add_argument("--report-format", type=str, help="Formato del reporte (html, pdf, excel)", default="html")
    parser.add_argument("--output-dir", type=str, help="Directorio de salida para gráficos y reportes", default="output")
    parser.add_argument("--rules", type=str, help="Ruta al archivo JSON con reglas de calidad", default=None)

    args = parser.parse_args()

    print(f"Iniciando análisis para: {args.file}")
    
    try:
        toolkit = DataQualityToolkit(output_dir=args.output_dir)
        
        # 1. Carga de datos
        print(f"1. Cargando datos (formato: {args.format})...")
        toolkit.load_data(args.file, format=args.format, query=args.sql_query)
        print("Datos cargados exitosamente.")

        # 2. Validación
        print("2. Validando esquema...")
        validation_results = toolkit.validate_data()
        if not validation_results["columns"]["is_valid"]:
            print("Advertencia: Se encontraron columnas duplicadas:", validation_results["columns"]["duplicate_columns"])

        # 3. Profiling
        print("3. Generando perfil de datos...")
        profile = toolkit.profile_data()
        print(f"Filas: {profile['total_rows']}, Columnas: {profile['total_columns']}")

        # 4. Visualización
        print("4. Generando visualizaciones...")
        plots = toolkit.visualize_data()
        print(f"Se generaron {len(plots)} gráficos en {args.output_dir}/")

        # Procesamiento de reglas personalizadas si existen
        rules = None
        if args.rules:
            print(f"-> Cargando reglas desde {args.rules}...")
            with open(args.rules, "r") as f:
                rules = json.load(f)
            
            print("-> Aplicando reglas personalizadas...")
            rule_results = toolkit.apply_custom_rules(rules)
            for col, res in rule_results.items():
                if "error" in res:
                    print(f"  [ERROR] {col}: {res['error']}")
                else:
                    status = "✅ Válido" if res["is_valid"] else "❌ Inválido"
                    print(f"  {status} en {col}: {res['violations_count']} violaciones encontradas.")

        # 5. Recomendaciones
        print("5. Generando recomendaciones...")
        recs = toolkit.get_recommendations(rules=rules)
        with open(f"{args.output_dir}/recommendations.json", "w") as f:
            json.dump(recs, f, indent=4)
        print("Recomendaciones guardadas.")

        # 6. Reporte
        print(f"6. Generando reporte en formato {args.report_format}...")
        report_path = toolkit.generate_report(profile, format=args.report_format, filename="data_quality_report")
        print(f"Reporte generado exitosamente en: {report_path}")

        print("Análisis completado.")

    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
