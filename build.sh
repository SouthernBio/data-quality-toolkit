#!/bin/bash
# Script de construcción para instalar dependencias de Python
set -e

echo "Instalando dependencias de Python desde requirements.txt..."
pip install --no-cache-dir -r /app/requirements.txt
echo "Instalación completada."
