#!/bin/bash
# Script para facilitar la ejecución del proyecto

cd services/api

case "$1" in
  install)
    echo "📦 Instalando dependencias..."
    uv sync
    ;;
  seed)
    echo "🌱 Cargando datos iniciales..."
    uv run python seed.py
    ;;
  api)
    echo "🚀 Iniciando API..."
    python main.py
    ;;
  *)
    echo "Uso: ./run.sh [install|seed|api]"
    echo ""
    echo "Comandos disponibles:"
    echo "  install  - Instalar dependencias"
    echo "  seed     - Cargar datos iniciales"
    echo "  api      - Iniciar servidor API"
    ;;
esac
