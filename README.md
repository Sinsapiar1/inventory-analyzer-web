# 📊 Analizador de Inventarios Negativos v6.0 Web

Aplicación web profesional para análisis avanzado de inventarios negativos con visualizaciones interactivas y reportes descargables.

## 🚀 Características

- ✅ **Análisis por severidad** basado en magnitud del negativo
- ✅ **Detección de reincidencias** automática
- ✅ **Visualizaciones interactivas** con Plotly
- ✅ **Filtros avanzados** en tiempo real con súper análisis expandido
- ✅ **Mapa de calor dinámico** sin límite de filas (hasta 100+ pallets)
- ✅ **Evolución individual** por pallet día a día
- ✅ **Reportes descargables** (Excel/CSV) con hoja Top N incluida
- ✅ **Interfaz responsiva** optimizada con mejor espaciado y scroll estable
- ✅ **Sistema de caché inteligente** para mejor rendimiento
- ✅ **Desplegable en la nube** con un clic
- ✅ **Descarga de reportes** en Excel/CSV listos para impresión

## 📋 Estructura del Proyecto

```
inventory-analyzer-web/
├── app.py                     # Aplicación Streamlit principal
├── requirements.txt           # Dependencias de Python
├── .streamlit/
│   └── config.toml           # Configuración de Streamlit
├── .gitignore                # Archivos a ignorar en Git
├── README.md                 # Esta documentación
└── Dockerfile                # Container para despliegue (opcional)
```

## 🛠️ Instalación Local

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. **Clonar o descargar el proyecto**
```bash
git clone <tu-repositorio>
cd inventory-analyzer-web
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Mac/Linux
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
streamlit run app.py
```

5. **Abrir en navegador**
   - La aplicación se abrirá automáticamente en `http://localhost:8501`

## 🌐 Despliegue en Streamlit Cloud (GRATUITO)

### Opción 1: Desde GitHub (Recomendado)

1. **Subir código a GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Inventory Analyzer v6.0"
   git branch -M main
   git remote add origin https://github.com/tu-usuario/inventory-analyzer-web.git
   git push -u origin main
   ```

2. **Desplegar en Streamlit Cloud**
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Haz clic en "New app"
   - Conecta tu repositorio de GitHub
   - Selecciona `app.py` como archivo principal
   - Haz clic en "Deploy"

3. **¡Listo!**
   - Tu app estará disponible en: `https://tu-usuario-inventory-analyzer-web-app-xyz.streamlit.app`

### Opción 2: Despliegue Directo

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Arrastra y suelta los archivos del proyecto
3. Selecciona `app.py` como archivo principal
4. Haz clic en "Deploy"

## 📊 Formato de Datos de Entrada

La aplicación espera archivos Excel con la siguiente estructura:

### Columnas Requeridas (nombres flexibles):
- **Código/Código Producto**: Identificador del producto
- **ID de Pallet/ID Pallet**: Identificador del pallet
- **Cantidad/Inventario Físico/Stock**: Cantidad (valores negativos)
- **Nombre/Descripción**: Nombre del producto (opcional)
- **Almacén/Warehouse/Ubicación**: Ubicación del inventario

### Ejemplo de estructura:
```
| Código | Nombre      | ID_Pallet | Almacén | Inventario Físico |
|--------|-------------|-----------|---------|-------------------|
| 12345  | Producto A  | PAL001    | ALM01   | -15               |
| 67890  | Producto B  | PAL002    | ALM02   | -23               |
```

### Nombres de archivo (para detección automática de fecha):
- Formato recomendado: `reporte_all_YYYYMMDD.xlsx`
- Ejemplo: `reporte_all_20240115.xlsx`

## 🎯 Uso de la Aplicación

1. **Subir archivos**: Arrastra archivos Excel en la barra lateral
2. **Configurar parámetros**: Ajusta Top N, hoja de Excel, etc.
3. **Aplicar filtros**: Filtra por almacén, severidad o estado
4. **Ejecutar análisis**: Haz clic en "Ejecutar Análisis"
5. **Explorar resultados**: Navega por pestañas y gráficos
6. **Usar súper análisis**: Aplica filtros avanzados y visualiza gráficos dinámicos
7. **Descargar reportes**: Obtén Excel (con hoja Top N) o CSV con resultados

## 📈 Funcionalidades de Análisis

### KPIs Principales
- Total de pallets únicos
- Pallets activos (aparecen en último reporte)
- Días promedio en negativo
- Total cantidad negativa

### Análisis de Severidad
- **Crítico**: Valores muy negativos (percentil 75+)
- **Alto**: Valores negativos altos (percentil 50-75)
- **Medio**: Valores negativos medios (percentil 25-50)
- **Bajo**: Valores negativos bajos (percentil 0-25)

### Detección de Reincidencias
- Identifica pallets que aparecen, desaparecen y vuelven a aparecer
- Rastrea patrones temporales problemáticos

### Súper Análisis Avanzado
**Filtros disponibles:**
- Búsqueda por código específico
- Solo artículos activos (última fecha)
- Filtro por almacén
- Códigos a excluir/incluir (lista separada por comas)
- Rango de fechas personalizable
- Mostrar celdas vacías como cero

**Gráficos dinámicos:**
- **Evolución Total**: Suma de valores filtrados por fecha
- **Distribución por Almacén**: Solo datos filtrados
- **Mapa de Calor Expandido**: Hasta 100+ pallets con altura dinámica
- **Evolución Individual**: Líneas de comportamiento día a día por pallet

### Visualizaciones
1. **Top N Pallets Críticos**: Ranking por score de criticidad
2. **Evolución Temporal**: Tendencia del total negativo
3. **Distribución por Almacén**: Participación de cada ubicación
4. **Distribución por Severidad**: Conteo por nivel de criticidad

### Reportes Excel Mejorados
**Hojas incluidas:**
- Problemas Activos
- Resueltos  
- Reincidencias
- Super Análisis
- Datos Crudos
- **Top N** (nuevo): Ranking con evolución temporal completa

### Reportes para Impresión
**Descargas optimizadas:**
- ✅ **Excel completo**: Incluye todas las hojas (Activos, Resueltos, Reincidencias, Super Análisis, Top N)
- ✅ **CSV filtrado**: Exporta solo los datos visibles con filtros aplicados
- ✅ **Formato profesional**: Reportes listos para abrir e imprimir directamente
- ✅ **Hoja Top N**: Ranking de pallets más críticos con evolución temporal completa

**Recomendación para impresión:**
1. Descarga el reporte Excel con el botón "📊 Descargar Reporte Excel"
2. Abre el archivo y selecciona la hoja que necesitas imprimir
3. Usa Excel para configurar formato de impresión (márgenes, orientación, etc.)
4. ¡Listo para imprimir con formato profesional!

## 🔧 Configuración Avanzada

### Configuración Mínima (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
maxUploadSize = 200
```

### Variables de Entorno (.env)
```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_THEME_PRIMARY_COLOR=#667eea
STREAMLIT_THEME_BACKGROUND_COLOR=#ffffff
```

## 🚀 Otros Métodos de Despliegue

### Railway
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login y deploy
railway login
railway init
railway up
```

### Render
1. Conecta tu repositorio en [render.com](https://render.com)
2. Selecciona "Web Service"
3. Comando de build: `pip install -r requirements.txt`
4. Comando de start: `streamlit run app.py --server.port=$PORT`

### Heroku
```bash
# Crear Procfile
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Desplegar
heroku create tu-app-name
git push heroku main
```

## 🐳 Docker (Opcional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Construir y ejecutar
docker build -t inventory-analyzer .
docker run -p 8501:8501 inventory-analyzer
```

## 🛠️ Solución de Problemas

### Error: "No module named 'streamlit'"
```bash
pip install streamlit
```

### Error: "File upload too large"
- Aumenta `maxUploadSize` en `.streamlit/config.toml`
- O usa archivos más pequeños

### Error: "Memory issues"
- Reduce el número de archivos procesados simultáneamente
- Considera usar muestreo de datos para pruebas

### Error: "Serialization of dataframe to Arrow table was unsuccessful"
- Esto es normal, la aplicación maneja automáticamente la conversión de tipos
- No afecta la funcionalidad

### Problemas de codificación
- Asegúrate de que los archivos Excel estén en formato UTF-8
- Revisa nombres de columnas por caracteres especiales

### ✅ Problemas Resueltos (v6.1)

**Scroll/Navegación:**
- ✅ **RESUELTO**: Problema de scroll que movía la pantalla al activar "Solo artículos activos" en Súper Análisis
- ✅ **Implementado**: Ancla de posición y session_state para mantener el scroll estable
- ✅ **Mejorado**: Tabs con posición sticky para mejor navegación

**Reportes:**
- ✅ **SOLUCIONADO**: Función de impresión problemática removida
- ✅ **ALTERNATIVA**: Descargas de Excel/CSV optimizadas para impresión profesional
- ✅ **INCLUIDO**: Hoja Top N con formato listo para imprimir

**Responsividad:**
- ✅ **Optimizado**: Espaciado mejorado entre secciones del Súper Análisis
- ✅ **Estabilizado**: Headers bien posicionados y separados visualmente
- ✅ **Mejorado**: Métricas muestran "N/A" en lugar de "nan"

**Rendimiento:**
- ✅ **Optimizado**: Sistema de caché implementado para funciones pesadas
- ✅ **Mejorado**: Dependencias actualizadas para mejor compatibilidad
- ✅ **Acelerado**: Despliegue más rápido con versiones flexibles

## 💡 Casos de Uso Avanzados

### Análisis de Código Específico
1. Ve a la pestaña "Súper Análisis"
2. Busca el código en "Buscar código"
3. Observa los gráficos dinámicos que se generan automáticamente
4. Usa el mapa de calor para ver patrones temporales

### Análisis por Almacén
1. Filtra por almacén específico en el súper análisis
2. Marca "Solo artículos activos" para casos actuales
3. Observa la distribución en el gráfico de pastel
4. Descarga CSV filtrado para análisis detallado

### Seguimiento de Evolución Individual
1. Aplica filtros para reducir a 5-15 pallets
2. Observa el gráfico de "Evolución Individual"
3. Cada línea muestra el comportamiento día a día
4. Identifica patrones de mejora o empeoramiento

## 📞 Soporte

Para reportar problemas o solicitar funcionalidades:
1. Revisa la documentación
2. Verifica el formato de datos de entrada
3. Consulta los logs en la aplicación
4. Crea un issue en GitHub (si aplica)

## 🔄 Actualizaciones

### v6.1 - Correcciones y Mejoras de Estabilidad (Actual)
- ✅ **FIX CRÍTICO**: Problema de scroll en Súper Análisis corregido completamente
- ✅ **Navegación estable**: Implementación de ancla y session_state para evitar saltos de pantalla
- ✅ **Función de impresión removida**: Reemplazada por descargas optimizadas de Excel/CSV
- ✅ **Tabs mejorados**: Posición sticky para mejor experiencia de navegación
- ✅ **UX mejorada**: Sin más refreshes inesperados en filtros del Súper Análisis

### v6.0 - Migración Web con Súper Análisis
- ✅ Interfaz web completa con Streamlit
- ✅ Visualizaciones interactivas con Plotly
- ✅ Despliegue en la nube optimizado
- ✅ Manejo de archivos upload/download
- ✅ Filtros en tiempo real
- ✅ Súper análisis con filtros avanzados
- ✅ Mapa de calor expandido (sin límite de filas)
- ✅ Evolución individual por pallet
- ✅ Hoja Top N en reportes Excel
- ✅ Gráficos dinámicos que se actualizan con filtros
- ✅ Identificación correcta Código_ID_Pallet en visualizaciones
- ✅ **Sistema de caché inteligente** para mejor rendimiento
- ✅ **Interfaz responsiva mejorada** con mejor espaciado
- ✅ **Optimizaciones de despliegue** (dependencias flexibles, caché de funciones)

### Próximas características
- 🔄 Base de datos para histórico
- 🔄 Autenticación de usuarios
- 🔄 API REST para integración
- 🔄 Notificaciones automáticas
- 🔄 Dashboard ejecutivo avanzado
- 🔄 Exportación de gráficos como imágenes
- 🔄 Reportes PDF personalizables

---

**¡Tu aplicación está lista para el mundo! 🌍**

Desarrollado por: [RAUL PIVET]  
Versión: 6.1 Web (Stable)  
Última actualización: Octubre 2025