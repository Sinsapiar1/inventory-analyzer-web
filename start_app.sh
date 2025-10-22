#!/bin/bash
# Script para iniciar la aplicación de Streamlit correctamente

echo "🔧 Verificando dependencias..."

# Instalar/actualizar dependencias si es necesario
python3 -m pip install -q -r requirements.txt

echo "✅ Dependencias verificadas"
echo ""
echo "🚀 Iniciando Streamlit..."
echo "   La aplicación estará disponible en el puerto 8501"
echo ""

# Iniciar Streamlit
python3 -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0
