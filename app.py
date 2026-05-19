# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import os
from data_quality_toolkit.toolkit_interface import DataQualityToolkit
import tempfile

st.set_page_config(page_title="Data Quality Toolkit", layout="wide")

st.title("Data Quality Toolkit")
st.markdown("Herramienta para el análisis automático de calidad de datos, perfilado y recomendaciones de limpieza.")

# Inicialización de la interfaz
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
toolkit = DataQualityToolkit(output_dir=output_dir)

# Inicializar estado de sesión
if "df" not in st.session_state:
    st.session_state.df = None
if "rules" not in st.session_state:
    st.session_state.rules = []
if "columns" not in st.session_state:
    st.session_state.columns = []

st.header("Paso 1: Carga de Datos")
data_source = st.radio("Origen de datos:", ["Archivo Local", "Base de Datos SQL"])

uploaded_file = None
sql_connection_string = ""
sql_query = ""
format_option = ""

if data_source == "Archivo Local":
    uploaded_file = st.file_uploader("Sube tu archivo de datos", type=["csv", "xls", "xlsx", "json", "parquet"])
else:
    sql_connection_string = st.text_input("Cadena de conexión SQL (ej. sqlite:////app/tests/sample.db):")
    sql_query = st.text_area("Consulta SQL (ej. SELECT * FROM data):")

if st.button("Cargar Datos"):
    try:
        with st.spinner("Cargando..."):
            if data_source == "Archivo Local":
                if uploaded_file is not None:
                    # Determinar el formato por la extensión
                    ext = uploaded_file.name.split('.')[-1].lower()
                    if ext in ['xls', 'xlsx']:
                        format_option = 'excel'
                    else:
                        format_option = ext
                        
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name
                    st.session_state.df = toolkit.load_data(tmp_file_path, format=format_option)
                else:
                    st.error("Por favor, suba un archivo.")
            else:
                if sql_connection_string and sql_query:
                    st.session_state.df = toolkit.load_data(sql_connection_string, format="sql", query=sql_query)
                else:
                    st.error("Proporcione la conexión y la consulta SQL.")
            
            if st.session_state.df is not None:
                st.session_state.columns = list(st.session_state.df.columns)
                st.success(f"Datos cargados exitosamente: {len(st.session_state.df)} filas, {len(st.session_state.columns)} columnas.")
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")


if st.session_state.df is not None:
    st.markdown("---")
    st.header("Paso 2: Configuración de Reglas")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Añadir Regla")
        target_col = st.selectbox("Columna a validar:", st.session_state.columns)
        rule_type = st.selectbox("Tipo de regla:", ["numeric", "categorical", "date"])
        
        new_rule = {"column": target_col, "type": rule_type}
        
        allow_nulls = st.checkbox("Permitir valores nulos", value=True)
        new_rule["allow_nulls"] = allow_nulls
        
        if rule_type == "numeric":
            min_val = st.number_input("Valor Mínimo (Opcional)", value=0.0)
            max_val = st.number_input("Valor Máximo (Opcional)", value=100.0)
            use_min = st.checkbox("Aplicar mínimo")
            use_max = st.checkbox("Aplicar máximo")
            if use_min:
                new_rule["min"] = min_val
            if use_max:
                new_rule["max"] = max_val
        elif rule_type == "categorical":
            allowed = st.text_input("Valores permitidos (separados por coma)")
            if allowed:
                new_rule["allowed_values"] = [x.strip() for x in allowed.split(",")]
        elif rule_type == "date":
            date_format = st.text_input("Formato de fecha (ej. %Y-%m-%d, %d/%m/%Y)", value="%Y-%m-%d")
            new_rule["format"] = date_format
            
        if st.button("Añadir Regla"):
            st.session_state.rules = [r for r in st.session_state.rules if r["column"] != target_col]
            st.session_state.rules.append(new_rule)
            st.success("Regla guardada.")
    with col2:
        st.subheader("Reglas Configuradas")
        if not st.session_state.rules:
            st.info("No hay reglas configuradas aún.")
        else:
            for i, r in enumerate(st.session_state.rules):
                st.write(f"**{i+1}. {r['column']}** ({r['type']}): {r}")
            if st.button("Limpiar Reglas"):
                st.session_state.rules = []
                st.rerun()

    st.markdown("---")
    st.header("Paso 3: Análisis y Resultados")
    
    if st.button("Ejecutar Análisis Completo"):
        try:
            with st.spinner("Analizando datos..."):
                toolkit.df = st.session_state.df
                
                # Reglas Personalizadas
                st.subheader("Resultados de Reglas Personalizadas")
                if st.session_state.rules:
                    rule_results = toolkit.apply_custom_rules(st.session_state.rules)
                    res_data = []
                    for col, res in rule_results.items():
                        if "error" in res:
                            res_data.append({"Columna": col, "Estado": "Error", "Detalle": res["error"]})
                        else:
                            status = "✅ Válido" if res["is_valid"] else "❌ Inválido"
                            res_data.append({"Columna": col, "Estado": status, "Detalle": f"{res['violations_count']} violaciones."})
                    st.table(pd.DataFrame(res_data))
                else:
                    st.info("No se configuraron reglas personalizadas.")
                
                # Validación de Esquema
                validation = toolkit.validate_data()
                if not validation["columns"]["is_valid"]:
                    st.warning(f"Se detectaron columnas duplicadas: {validation['columns']['duplicate_columns']}")
                
                # Perfilado
                profile = toolkit.profile_data()
                st.subheader("Resumen del Dataset")
                c1, c2 = st.columns(2)
                c1.metric("Total de Filas", profile["total_rows"])
                c2.metric("Total de Columnas", profile["total_columns"])

                # Visualizaciones
                st.subheader("Visualizaciones")
                plots = toolkit.visualize_data()
                
                tabs = st.tabs(["Mapa de Calor (Nulos)", "Matriz de Correlación", "Histogramas", "Categóricos"])
                
                with tabs[0]:
                    heatmap_path = [p for p in plots if "missing_heatmap" in p]
                    if heatmap_path:
                        st.image(heatmap_path[0])
                
                with tabs[1]:
                    corr_path = [p for p in plots if "correlation_matrix" in p]
                    if corr_path:
                        st.image(corr_path[0])
                
                with tabs[2]:
                    hist_paths = [p for p in plots if "hist_" in p]
                    if hist_paths:
                        for path in hist_paths:
                            st.image(path)
                    else:
                        st.info("No hay columnas numéricas para histogramas.")
                
                with tabs[3]:
                    cat_paths = [p for p in plots if "cat_" in p]
                    if cat_paths:
                        for path in cat_paths:
                            st.image(path)
                    else:
                        st.info("No hay columnas categóricas para mostrar.")
                # Recomendaciones
                st.subheader("Sugerencias de Limpieza")
                recs = toolkit.get_recommendations(rules=st.session_state.rules)
                st.json(recs)
                
                # Generación de reporte
                report_path = toolkit.generate_report(profile, format="html", filename="report_streamlit")
                with open(report_path, "r") as f:
                    st.download_button(
                        label="Descargar Reporte Completo (HTML)",
                        data=f.read(),
                        file_name="reporte_calidad.html",
                        mime="text/html"
                    )

        except Exception as e:
            st.error(f"Error durante el análisis: {str(e)}")
