FROM python:3.10-slim

# Instalar dependencias del sistema operativo
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar el código fuente y scripts
COPY . /app/

# Dar permisos de ejecución al script de construcción
RUN chmod +x /app/build.sh

# Ejecutar el script de construcción para instalar dependencias de Python
RUN /app/build.sh

# Exponer el puerto de Streamlit
EXPOSE 8501

# Punto de entrada predeterminado
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
