# Data Quality Toolkit

Toolkit para automatizar el análisis de calidad de datos, perfilamiento y generación de recomendaciones.

## Características
- Soporte para múltiples formatos: CSV, Excel, JSON, Parquet, SQL.
- Generación automática de métricas (valores nulos, duplicados, outliers).
- Generación de reportes en HTML, PDF y Excel.
- Recomendaciones de limpieza automáticas.
- Empaquetado en Docker.

## Instalación y Ejecución con Docker Compose (Recomendado)

La forma más sencilla de levantar el toolkit (tanto CLI como Interfaz Web) es utilizando Docker:

1. Instalar Docker y Docker Compose.
2. Iniciar la aplicación web:

```bash
docker compose up --build
```

3. Abrir el navegador web en `http://localhost:8501`.

Para ejecutar la CLI vía Docker Compose:

```bash
docker compose run --rm toolkit-cli --file tests/sample.csv --format csv
```

## Uso de la CLI

El punto de entrada principal es `main.py`.

```bash
python main.py --file <dataset> --format <formato> --report-format <formato_reporte>
```

**Ejemplo:**
```bash
python main.py --file my_data.csv --format csv --report-format html --output-dir reports/
```

### Argumentos
- `--file`: Ruta al archivo de datos (Requerido).
- `--format`: Formato del archivo (Opciones: `csv`, `excel`, `json`, `parquet`, `sql`. Por defecto: `csv`).
- `--sql-query`: Consulta SQL (Solo requerido si el formato es `sql`).
- `--report-format`: Formato de salida del reporte (Opciones: `html`, `pdf`, `excel`. Por defecto: `html`).
- `--output-dir`: Directorio donde se guardarán los gráficos y reportes generados.
- `--rules`: Ruta a un archivo JSON con reglas de validación de calidad.

### Especificar Reglas Personalizadas

Al igual que en la interfaz web, se pueden aplicar reglas de calidad estrictas en la CLI pasándolas mediante un archivo JSON. El motor evaluará rangos, tipos, formatos de fechas y la permisión de nulos.

**Ejemplo de `rules.json`**:
```json
[
  {
    "column": "age",
    "type": "numeric",
    "allow_nulls": false,
    "min": 0,
    "max": 100
  },
  {
    "column": "status",
    "type": "categorical",
    "allow_nulls": true,
    "allowed_values": ["active", "inactive"]
  },
  {
    "column": "created_at",
    "type": "date",
    "allow_nulls": false,
    "format": "%Y-%m-%d"
  }
]
```

**Ejecución**:

```bash
python main.py --file data.csv --rules rules.json
```
