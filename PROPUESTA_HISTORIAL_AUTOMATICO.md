# 📋 PROPUESTA: Tab de Historial Automático con Dataverse

## 🎯 Objetivo
Agregar un tercer modo de operación que permita:
- Leer archivos generados automáticamente por Power Automate desde Dataverse
- Conectar con Google Drive para lectura automática
- Procesar cierres diarios sin intervención manual
- Análisis temporal automatizado

---

## 🏗️ Arquitectura Propuesta

### **OPCIÓN 1: Integración con Google Drive API (RECOMENDADA)**

```python
# Nuevo modo en la app
modo = st.sidebar.radio(
    "Selecciona el modo:",
    [
        "📥 Preprocesar Datos ERP",
        "📊 Analizar Inventarios",
        "🤖 Historial Automático Dataverse"  # ← NUEVO
    ]
)
```

#### Flujo del Sistema:
```
Power Automate                Google Drive              Tu App Streamlit
     ↓                             ↓                          ↓
Excel diario    →  Transforma  →  CSV/Excel  →  API  →  Lectura Auto
(D3/Dynamics)      a Dataverse    en carpeta        →  Filtrado
                                                     →  Análisis
                                                     →  Dashboard
```

#### Componentes Necesarios:

1. **Google Drive API Integration**
   ```python
   from google.oauth2.credentials import Credentials
   from googleapiclient.discovery import build
   
   def list_dataverse_files(folder_id):
       """Lista archivos de la carpeta de Dataverse"""
       service = build('drive', 'v3', credentials=creds)
       results = service.files().list(
           q=f"'{folder_id}' in parents",
           orderBy='createdTime desc',
           pageSize=30
       ).execute()
       return results.get('files', [])
   ```

2. **Mapeo de Columnas Dataverse → App**
   ```python
   DATAVERSE_COLUMN_MAPPING = {
       "CompanyId": "Company",
       "InventLocationId": "Warehouse", 
       "ProductId": "Codigo",
       "ProductName_es": "Nombre",
       "LabelId": "ID_Pallet",
       "Stock": "Cantidad_Negativa",
       "CostStock": "Costo"
   }
   ```

3. **Filtrado Automático**
   ```python
   def process_dataverse_file(df):
       # Renombrar columnas
       df = df.rename(columns=DATAVERSE_COLUMN_MAPPING)
       
       # FILTRAR SOLO NEGATIVOS (igual que tu app actual)
       df = df[df["Cantidad_Negativa"] < 0].copy()
       
       # Detectar fecha del archivo
       fecha = detect_date_from_filename(filename)
       df["Fecha_Reporte"] = fecha
       
       return df
   ```

4. **Dashboard Automático**
   - Lectura automática de últimos 30 días
   - Gráficos de evolución temporal
   - Comparación día vs día
   - Alertas automáticas

---

### **OPCIÓN 2: Carga Manual desde Google Drive (MÁS SIMPLE)**

Si no quieres complicarte con OAuth y APIs:

```python
# El usuario descarga manualmente de Google Drive
uploaded_files = st.file_uploader(
    "📁 Subir archivos Dataverse desde Google Drive",
    type=['csv', 'xlsx'],
    accept_multiple_files=True,
    help="Descarga los archivos de Google Drive y súbelos aquí"
)
```

**Ventajas:**
- ✅ Más simple de implementar
- ✅ No requiere autenticación OAuth
- ✅ Funciona igual que tus modos actuales

**Desventajas:**
- ❌ No es "automático" (requiere descarga manual)
- ❌ Usuario debe ir a Google Drive cada vez

---

## 📊 Estructura del Nuevo Tab

### Vista Propuesta:

```
╔════════════════════════════════════════════════════════════╗
║  🤖 HISTORIAL AUTOMÁTICO - DATAVERSE                       ║
╚════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────┐
│  📡 CONEXIÓN CON GOOGLE DRIVE                           │
│                                                         │
│  Estado: ✅ Conectado                                   │
│  Carpeta: /Dataverse/Cierres_Diarios                   │
│  Últimos archivos: 15                                   │
│                                                         │
│  [🔄 Actualizar]  [⚙️ Configurar]                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  📅 ARCHIVOS DISPONIBLES (Últimos 30 días)             │
├─────────────────────────────────────────────────────────┤
│  ☑️ dataverse_20241103.csv  (Ayer)      📥 Procesado   │
│  ☑️ dataverse_20241102.csv  (2 días)    📥 Procesado   │
│  ☑️ dataverse_20241101.csv  (3 días)    📥 Procesado   │
│  ☐ dataverse_20241031.csv  (4 días)    ⏳ Pendiente   │
│                                                         │
│  [✅ Procesar Seleccionados]  [📊 Ver Dashboard]        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  📊 RESUMEN RÁPIDO                                      │
├─────────────────────────────────────────────────────────┤
│  Total Productos Negativos: 1,234                       │
│  Almacenes Afectados: 5 (25R, 25D, 26Q, 61D, 612D)    │
│  Tendencia: ⬇️ -15% vs semana pasada                    │
│  Última actualización: Hace 2 horas                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementación Técnica

### Paso 1: Agregar nuevo modo

```python
# En main()
if modo == "🤖 Historial Automático Dataverse":
    st.subheader("🤖 Historial Automático desde Dataverse")
    
    # Opción A: Google Drive API
    if st.checkbox("Conectar con Google Drive"):
        setup_google_drive_connection()
        display_available_files()
    
    # Opción B: Carga manual
    else:
        dataverse_files = st.file_uploader(
            "📁 Subir archivos CSV/Excel de Dataverse",
            type=['csv', 'xlsx'],
            accept_multiple_files=True
        )
        
        if dataverse_files:
            process_dataverse_files(dataverse_files)
```

### Paso 2: Función de procesamiento

```python
def process_dataverse_files(files):
    """Procesa archivos Dataverse con mismo pipeline que tu app"""
    all_data = []
    
    for file in files:
        # Leer archivo
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Detectar fecha
        fecha = extract_date_from_filename(file.name)
        
        # Mapear columnas
        df = df.rename(columns=DATAVERSE_COLUMN_MAPPING)
        
        # FILTRAR SOLO NEGATIVOS
        df = df[df["Stock"] < 0].copy()
        df["Cantidad_Negativa"] = df["Stock"]
        df["Fecha_Reporte"] = fecha
        
        # Crear ID único
        df["ID_Unico_Pallet"] = (
            df["Codigo"].astype(str) + "_" + 
            df["ID_Pallet"].astype(str)
        )
        
        all_data.append(df)
    
    # Combinar todo
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # USAR TU ANÁLISIS EXISTENTE
    analisis = analyze_pallets_data(combined_df)
    super_analisis = create_super_analysis(combined_df)
    reincidencias = detect_recurrences(combined_df)
    
    # Mostrar resultados
    display_automatic_dashboard(analisis, super_analisis, reincidencias)
```

### Paso 3: Dashboard específico

```python
def display_automatic_dashboard(analisis, super_analisis, reincidencias):
    """Dashboard específico para modo automático"""
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Archivos Procesados", len(analisis['archivos']))
    with col2:
        st.metric("Rango de Fechas", f"{fecha_min} - {fecha_max}")
    with col3:
        st.metric("Productos Negativos", len(analisis))
    with col4:
        delta = calculate_delta_vs_previous_day()
        st.metric("vs Día Anterior", f"{delta:+.1f}%")
    
    # Gráfico de evolución diaria
    fig = create_daily_evolution_chart(super_analisis)
    st.plotly_chart(fig, use_container_width=True)
    
    # Alertas automáticas
    if has_critical_issues(analisis):
        st.error("⚠️ ALERTAS CRÍTICAS DETECTADAS")
        display_critical_alerts(analisis)
```

---

## 🌟 Ventajas de Esta Solución

### Para Ti:
✅ **Reutiliza TODO tu código existente** (análisis, gráficos, reportes)
✅ **Misma lógica de negocio** (inventarios negativos)
✅ **Se integra perfectamente** con tus tabs actuales
✅ **Modular**: Puedes empezar simple y mejorar después

### Para la Empresa:
✅ **Automatización real**: Power Automate → Google Drive → App
✅ **Historial automático**: 30 días sin esfuerzo
✅ **Alertas diarias**: Detección automática de problemas
✅ **Reduce trabajo manual**: De horas a minutos

---

## 📦 Dependencias Adicionales

```txt
# Para Google Drive (si usas Opción 1)
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.100.0

# Ya las tienes:
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.15.0
```

---

## 🚀 Plan de Implementación

### Fase 1: MVP Básico (1-2 horas)
1. Agregar tercer modo en sidebar
2. Carga manual de archivos CSV/Excel
3. Mapeo de columnas Dataverse → App
4. Reutilizar análisis existente
5. Dashboard básico

### Fase 2: Google Drive Manual (30 min)
1. Usuario conecta Google Drive manualmente
2. Descarga archivos y los sube
3. Mismo flujo que Fase 1

### Fase 3: Google Drive Automático (2-3 horas)
1. Implementar OAuth con Google
2. Listar archivos de carpeta específica
3. Descarga automática
4. Procesamiento en background

### Fase 4: Mejoras (opcional)
1. Notificaciones por email
2. Scheduled runs (con GitHub Actions)
3. Base de datos para histórico
4. API REST

---

## 🎯 Recomendación Final

**EMPEZAR CON OPCIÓN 2 (Carga Manual)**

**Por qué:**
- ✅ Implementación en 1-2 horas
- ✅ Sin complejidad de OAuth
- ✅ Validas la idea primero
- ✅ Si funciona bien, pasas a Opción 1

**Flujo recomendado:**
```
Día 1: Usuario descarga de Google Drive → Sube a app → Analiza
Día 2-7: Usa la función, ve si le gusta
Día 8+: Si le gusta, implementas conexión automática
```

---

## 💬 Respuestas a tus Preguntas

### ¿Se puede adaptar mi app con otro tab?
**SÍ, perfectamente.** Tu app ya es modular con tabs.

### ¿Puedo conectarlo a Google Drive?
**SÍ, de dos formas:**
- Simple: Carga manual
- Avanzada: Google Drive API

### ¿Puedo leer archivos Dataverse de Power Automate?
**SÍ.** Son CSV o Excel estándar, solo necesitas mapear columnas.

### ¿Hay mejor opción que Power Automate?
**Power Automate está perfecto para tu caso:**
- ✅ Ya lo conoces
- ✅ Se integra con Dynamics 365
- ✅ Genera archivos automáticamente
- ✅ Puede subirlos a Google Drive

**Alternativas (más complejas):**
- Power BI con API REST
- Azure Data Factory
- Python script con SQL directo a Dataverse

---

## 📝 Próximos Pasos Sugeridos

1. **Validar estructura del archivo Dataverse**
   - ¿Power Automate ya genera CSV o Excel?
   - ¿Qué columnas tiene exactamente?
   - ¿Incluye fecha en el nombre del archivo?

2. **Definir flujo de Power Automate**
   - Frecuencia: ¿Diaria a qué hora?
   - Destino: ¿Carpeta específica en Google Drive?
   - Formato: ¿CSV, XLSX, o ambos?

3. **Implementar MVP**
   - Agregar tercer tab
   - Probar con un archivo de ejemplo
   - Validar que el análisis funciona

4. **Iterar**
   - Mejorar dashboard
   - Agregar alertas
   - Automatizar conexión

---

**¿Te gusta esta propuesta? ¿Quieres que empiece a implementar el MVP?** 🚀
