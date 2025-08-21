import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime, timedelta
import warnings
from pathlib import Path
import zipfile

warnings.filterwarnings("ignore")

# Configurar pandas para mejor rendimiento
pd.set_option('display.precision', 2)
pd.set_option('mode.chained_assignment', None)

# Funciones auxiliares con caché
@st.cache_data
def process_excel_file(file_content, filename):
    """Procesa un archivo Excel individual"""
    try:
        # Detectar fecha en nombre archivo
        parts = filename.split("_")
        fecha_str = next((p for p in parts if p.isdigit() and len(p) == 8), None)
        
        if fecha_str:
            fecha_reporte = datetime.strptime(fecha_str, "%Y%m%d")
        else:
            fecha_reporte = datetime.now()
        
        # Leer Excel
        df = pd.read_excel(io.BytesIO(file_content), sheet_name=1)  # Segunda hoja por defecto
        df["Fecha_Reporte"] = pd.to_datetime(fecha_reporte)
        df["Archivo_Origen"] = filename
        
        return df, True, None
        
    except Exception as e:
        return None, False, str(e)

@st.cache_data
def normalize_dataframe(df):
    """Normaliza nombres de columnas y limpia datos"""
    # Normalización de columnas
    df = df.rename(columns={
        "Código": "Codigo",
        "Código Producto": "Codigo",
        "ID de Pallet": "ID_Pallet",
        "Inventario Físico": "Cantidad_Negativa",
        "Nombre": "Nombre",
        "Descripción": "Nombre",
        "Almacén": "Almacen",
        "Almacen": "Almacen",
        "Warehouse": "Almacen",
        "Ubicación": "Almacen",
        "Ubicacion": "Almacen",
    })
    
    # Limpiar códigos y pallets
    for col in ["Codigo", "ID_Pallet"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.split(".").str[0]
                .str.strip()
            )
        else:
            df[col] = "N/A"
    
    # Campos obligatorios
    if "Nombre" not in df.columns:
        df["Nombre"] = ""
    if "Almacen" not in df.columns:
        df["Almacen"] = "N/A"
    
    # Cantidad negativa
    if "Cantidad_Negativa" not in df.columns:
        for alt in ["Cantidad", "Qty", "Inventario", "Stock"]:
            if alt in df.columns:
                df["Cantidad_Negativa"] = df[alt]
                break
    
    df["Cantidad_Negativa"] = pd.to_numeric(df["Cantidad_Negativa"], errors="coerce").fillna(0)
    
    # Solo negativos
    df = df[df["Cantidad_Negativa"] < 0].copy()
    
    # ID único pallet
    df["ID_Unico_Pallet"] = df["Codigo"].astype(str) + "_" + df["ID_Pallet"].astype(str)
    
    return df

@st.cache_data
def analyze_pallets_data(df_total):
    """Análisis principal de pallets con caché"""
    analisis = df_total.groupby("ID_Unico_Pallet").agg({
        "Codigo": "first",
        "Nombre": "first", 
        "ID_Pallet": "first",
        "Almacen": "first",
        "Fecha_Reporte": ["min", "max", "count"],
        "Cantidad_Negativa": ["mean", "min", "max", "sum"]
    }).reset_index()
    
    analisis.columns = [
        "ID_Unico_Pallet", "Codigo", "Nombre", "ID_Pallet", "Almacen",
        "Primera_Aparicion", "Ultima_Aparicion", "Veces_Reportado", 
        "Cantidad_Promedio", "Cantidad_Minima", "Cantidad_Maxima", "Cantidad_Suma"
    ]
    
    analisis["Dias_Acumulados"] = (analisis["Ultima_Aparicion"] - analisis["Primera_Aparicion"]).dt.days + 1
    
    # Severidad por magnitud del negativo
    magnitudes = np.abs(analisis["Cantidad_Promedio"])
    if len(magnitudes) > 0 and magnitudes.nunique() > 1:
        q25, q50, q75 = np.percentile(magnitudes, [25, 50, 75])
    else:
        v = magnitudes.iloc[0] if len(magnitudes) > 0 else 0
        q25 = q50 = q75 = v
    
    analisis["Severidad"] = pd.cut(
        magnitudes,
        bins=[-1, q25, q50, q75, float("inf")],
        labels=["Bajo", "Medio", "Alto", "Crítico"],
        include_lowest=True
    )
    
    # Estado (activo/resuelto)
    fecha_ultimo = df_total["Fecha_Reporte"].max()
    analisis["Estado"] = np.where(analisis["Ultima_Aparicion"] == fecha_ultimo, "Activo", "Resuelto")
    
    # Score de criticidad
    analisis["Score_Criticidad"] = analisis["Dias_Acumulados"] * np.abs(analisis["Cantidad_Promedio"])
    
    return analisis

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Inventarios Negativos v6.0 Web",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stDataFrame {
        background: white;
        border-radius: 8px;
        padding: 1rem;
    }
    .severity-critical {
        background-color: #ff4444;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .severity-alto {
        background-color: #ff9800;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .severity-medio {
        background-color: #ffb74d;
        color: black;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .severity-bajo {
        background-color: #81c784;
        color: black;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Clase adaptada del análisis
class InventoryAnalyzerWeb:
    def __init__(self):
        self.logger_messages = []
    
    def log(self, message):
        self.logger_messages.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        if 'progress_placeholder' in st.session_state:
            st.session_state.progress_placeholder.text('\n'.join(self.logger_messages[-5:]))
    
    def process_uploaded_files(self, uploaded_files):
        """Procesa archivos subidos y normaliza datos"""
        if not uploaded_files:
            raise ValueError("No se subieron archivos")
        
        self.log(f"Procesando {len(uploaded_files)} archivos...")
        
        all_dfs = []
        for uploaded_file in uploaded_files:
            # Leer el contenido del archivo
            file_content = uploaded_file.read()
            filename = uploaded_file.name
            
            # Usar función cacheada
            df, success, error = process_excel_file(file_content, filename)
            
            if success:
                all_dfs.append(df)
                self.log(f"✅ Procesado: {filename} ({len(df)} registros)")
            else:
                self.log(f"⚠️ Error en {filename}: {error}")
                continue
        
        if not all_dfs:
            raise ValueError("No se pudieron procesar archivos válidos")
        
        df_total = pd.concat(all_dfs, ignore_index=True)
        return self.normalize_data(df_total)
    
    def normalize_data(self, df):
        """Normaliza nombres de columnas y limpia datos"""
        # Usar función cacheada
        normalized_df = normalize_dataframe(df)
        self.log(f"📊 Datos normalizados: {len(normalized_df)} registros negativos")
        return normalized_df
    
    def analyze_pallets(self, df_total):
        """Análisis principal de pallets"""
        self.log("🔍 Analizando pallets...")
        
        # Usar función cacheada
        analisis = analyze_pallets_data(df_total)
        
        self.log(f"✅ Análisis completado: {len(analisis)} pallets únicos")
        return analisis
    
    def create_super_analysis(self, df_total):
        """Crea tabla pivote con evolución temporal"""
        self.log("📈 Creando súper análisis...")
        
        tabla = df_total.pivot_table(
            index=["Codigo", "Nombre", "ID_Pallet", "Almacen"],
            columns="Fecha_Reporte", 
            values="Cantidad_Negativa",
            aggfunc="first"
        ).reset_index()
        
        # Ordenar columnas por fecha
        fecha_cols = sorted([c for c in tabla.columns if isinstance(c, pd.Timestamp)])
        otras = [c for c in tabla.columns if not isinstance(c, pd.Timestamp)]
        tabla = tabla[otras + fecha_cols]
        
        self.log(f"📊 Súper análisis: {tabla.shape[0]} × {tabla.shape[1]}")
        return tabla
    
    def detect_recurrences(self, df_total):
        """Detecta reincidencias"""
        self.log("🔄 Detectando reincidencias...")
        
        reincidencias = []
        for pallet, data in df_total.groupby("ID_Unico_Pallet"):
            fechas = sorted(pd.to_datetime(data["Fecha_Reporte"]).unique())
            if len(fechas) < 2:
                continue
            gaps = np.diff(fechas)
            if any(gap > np.timedelta64(1, "D") for gap in gaps):
                reincidencias.append({
                    "ID_Unico_Pallet": pallet,
                    "Codigo": data["Codigo"].iloc[0],
                    "Nombre": data["Nombre"].iloc[0],
                    "Almacen": data["Almacen"].iloc[0],
                    "Fechas": ", ".join(pd.Series(fechas).dt.strftime("%d-%m-%Y"))
                })
        
        self.log(f"🔄 Reincidencias detectadas: {len(reincidencias)}")
        return pd.DataFrame(reincidencias)

# Función para crear gráficos
@st.cache_data
def create_charts(analisis, super_analisis, top_n=10):
    """Crea gráficos interactivos con Plotly"""
    
    # Verificar que hay datos
    if analisis.empty:
        # Crear gráficos vacíos si no hay datos
        fig1 = go.Figure()
        fig1.add_annotation(text="No hay datos para mostrar", 
                           xref="paper", yref="paper", x=0.5, y=0.5)
        fig1.update_layout(title=f"Top {top_n} Pallets Más Críticos", height=400)
        
        fig2 = go.Figure()
        fig2.add_annotation(text="No hay datos para mostrar", 
                           xref="paper", yref="paper", x=0.5, y=0.5)
        fig2.update_layout(title="Evolución Total de Inventario Negativo", height=400)
        
        fig3 = go.Figure()
        fig3.add_annotation(text="No hay datos para mostrar", 
                           xref="paper", yref="paper", x=0.5, y=0.5)
        fig3.update_layout(title="Distribución por Almacén", height=400)
        
        fig4 = go.Figure()
        fig4.add_annotation(text="No hay datos para mostrar", 
                           xref="paper", yref="paper", x=0.5, y=0.5)
        fig4.update_layout(title="Distribución por Severidad", height=400)
        
        return fig1, fig2, fig3, fig4
    
    # 1. Top N Pallets Críticos - VERSIÓN SIMPLE SIN COLOR PROBLEMÁTICO
    top_critical = analisis.sort_values("Score_Criticidad", ascending=False).head(top_n)
    
    fig1 = px.bar(
        top_critical,
        x="ID_Unico_Pallet",
        y="Score_Criticidad",
        title=f"Top {top_n} Pallets Más Críticos",
        hover_data=["Severidad"] if "Severidad" in top_critical.columns else None
    )
    fig1.update_layout(xaxis_tickangle=-45, height=400)
    
    # 2. Evolución Total por Fecha
    date_cols = [c for c in super_analisis.columns if isinstance(c, pd.Timestamp)]
    if date_cols:
        evolution_data = []
        for fecha in sorted(date_cols):
            total = super_analisis[fecha].sum(skipna=True)
            evolution_data.append({"Fecha": fecha, "Total_Negativo": abs(total)})
        
        evolution_df = pd.DataFrame(evolution_data)
        fig2 = px.line(
            evolution_df,
            x="Fecha",
            y="Total_Negativo",
            title="Evolución Total de Inventario Negativo", 
            markers=True
        )
        fig2.update_traces(line_color="#ff4444", line_width=3)
        fig2.update_layout(height=400)
    else:
        fig2 = go.Figure()
        fig2.add_annotation(text="No hay datos de evolución temporal", 
                           xref="paper", yref="paper", x=0.5, y=0.5)
    
    # 3. Distribución por Almacén
    almacen_totals = {}
    for almacen in super_analisis["Almacen"].dropna().unique():
        subset = super_analisis[super_analisis["Almacen"] == almacen]
        total_almacen = subset[date_cols].sum().sum(skipna=True) if date_cols else 0
        if total_almacen != 0:
            almacen_totals[almacen] = abs(total_almacen)
    
    if almacen_totals:
        fig3 = px.pie(
            values=list(almacen_totals.values()),
            names=list(almacen_totals.keys()),
            title="Distribución por Almacén"
        )
        fig3.update_layout(height=400)
    else:
        fig3 = go.Figure()
        fig3.add_annotation(text="No hay datos por almacén", 
                           xref="paper", yref="paper", x=0.5, y=0.5)
    
    # 4. Distribución por Severidad - VERSIÓN SIMPLE
    if "Severidad" in analisis.columns and not analisis["Severidad"].isna().all():
        severidad_counts = analisis["Severidad"].value_counts()
        
        if len(severidad_counts) > 0:
            fig4 = px.bar(
                x=severidad_counts.index,
                y=severidad_counts.values,
                title="Distribución por Severidad",
                labels={"x": "Severidad", "y": "Cantidad"}
            )
            fig4.update_layout(height=400)
        else:
            fig4 = go.Figure()
            fig4.add_annotation(text="No hay datos de severidad", 
                               xref="paper", yref="paper", x=0.5, y=0.5)
            fig4.update_layout(title="Distribución por Severidad", height=400)
    else:
        fig4 = go.Figure()
        fig4.add_annotation(text="No hay datos de severidad disponibles", 
                           xref="paper", yref="paper", x=0.5, y=0.5)
        fig4.update_layout(title="Distribución por Severidad", height=400)
    
    return fig1, fig2, fig3, fig4

# Función para generar reporte Excel
@st.cache_data
def generate_excel_report(analisis, super_analisis, reincidencias, df_total, top_n=10):
    """Genera reporte Excel descargable con hoja Top N"""
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Escribir hojas principales
        activos = analisis[analisis["Estado"] == "Activo"].copy()
        resueltos = analisis[analisis["Estado"] == "Resuelto"].copy()
        
        activos.to_excel(writer, sheet_name="Problemas Activos", index=False)
        resueltos.to_excel(writer, sheet_name="Resueltos", index=False) 
        reincidencias.to_excel(writer, sheet_name="Reincidencias", index=False)
        super_analisis.to_excel(writer, sheet_name="Super Análisis", index=False)
        df_total.to_excel(writer, sheet_name="Datos Crudos", index=False)
        
        # NUEVA HOJA: Top N
        create_top_n_sheet(writer, super_analisis, analisis, top_n)
        
        # Formato básico para todas las hojas
        workbook = writer.book
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1F4E78',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Aplicar formato a todas las hojas
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_row(0, 22, header_format)
    
    buffer.seek(0)
    return buffer

def create_top_n_sheet(writer, super_analisis, analisis, top_n):
    """Crea hoja dedicada Top N con evolución temporal"""
    workbook = writer.book
    worksheet = workbook.add_worksheet("Top N")
    worksheet.set_zoom(120)
    
    # Obtener Top N por criticidad
    top_data = analisis.sort_values("Score_Criticidad", ascending=False).head(top_n).copy()
    
    # Preparar columnas base
    cols_base = [
        "Rank", "ID_Unico_Pallet", "Codigo", "Nombre", "ID_Pallet", "Almacen",
        "Score_Criticidad", "Dias_Acumulados", "Cantidad_Promedio", "Severidad",
        "Primera_Aparicion", "Ultima_Aparicion", "Estado"
    ]
    
    # Formato de encabezados
    header_format = workbook.add_format({
        'bold': True, 
        'font_size': 11, 
        'bg_color': '#27466B', 
        'font_color': 'white',
        'align': 'center', 
        'valign': 'vcenter', 
        'border': 1
    })
    
    # Escribir encabezados base
    for j, col in enumerate(cols_base):
        worksheet.write(0, j, col, header_format)
    
    # Obtener columnas de fechas del super análisis
    date_cols = [c for c in super_analisis.columns if isinstance(c, pd.Timestamp)]
    
    # Escribir encabezados de fechas
    for j, fecha in enumerate(sorted(date_cols), start=len(cols_base)):
        worksheet.write(0, j, fecha.strftime("%Y-%m-%d"), header_format)
    
    # Preparar mapeo para obtener datos de evolución temporal
    super_copy = super_analisis.copy()
    super_copy["_ID_UNICO_"] = super_copy["Codigo"].astype(str) + "_" + super_copy["ID_Pallet"].astype(str)
    
    # Formatos para datos
    number_format = workbook.add_format({'num_format': '#,##0.00'})
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    
    # Escribir datos del Top N
    for i, (_, row) in enumerate(top_data.iterrows(), start=1):
        # Datos base
        worksheet.write_number(i, 0, i)  # Rank
        worksheet.write(i, 1, row["ID_Unico_Pallet"])
        worksheet.write(i, 2, str(row["Codigo"]))
        worksheet.write(i, 3, str(row["Nombre"]) if pd.notna(row["Nombre"]) else "")
        worksheet.write(i, 4, str(row["ID_Pallet"]))
        worksheet.write(i, 5, str(row["Almacen"]))
        worksheet.write_number(i, 6, float(row["Score_Criticidad"]), number_format)
        worksheet.write_number(i, 7, int(row["Dias_Acumulados"]))
        worksheet.write_number(i, 8, float(row["Cantidad_Promedio"]), number_format)
        worksheet.write(i, 9, str(row["Severidad"]) if pd.notna(row["Severidad"]) else "")
        worksheet.write_datetime(i, 10, pd.to_datetime(row["Primera_Aparicion"]), date_format)
        worksheet.write_datetime(i, 11, pd.to_datetime(row["Ultima_Aparicion"]), date_format)
        worksheet.write(i, 12, str(row["Estado"]))
        
        # Datos de evolución temporal
        fila_super = super_copy[super_copy["_ID_UNICO_"] == row["ID_Unico_Pallet"]]
        if not fila_super.empty:
            row_super = fila_super.iloc[0]
            for j, fecha in enumerate(sorted(date_cols), start=len(cols_base)):
                val = row_super.get(fecha, np.nan)
                if pd.notna(val) and val != "":
                    try:
                        val_num = pd.to_numeric(val, errors='coerce')
                        if pd.notna(val_num):
                            worksheet.write_number(i, j, float(val_num), number_format)
                        else:
                            worksheet.write_blank(i, j, None)
                    except:
                        worksheet.write_blank(i, j, None)
                else:
                    worksheet.write_blank(i, j, None)
    
    # Ajustar anchos de columnas
    worksheet.set_column(0, 0, 6)   # Rank
    worksheet.set_column(1, 1, 24)  # ID_Unico_Pallet
    worksheet.set_column(2, 3, 12)  # Codigo, Nombre
    worksheet.set_column(4, 5, 12)  # ID_Pallet, Almacen
    worksheet.set_column(6, 8, 14)  # Scores y promedios
    worksheet.set_column(9, 9, 10)  # Severidad
    worksheet.set_column(10, 12, 12) # Fechas y estado
    
    # Columnas de evolución temporal
    if date_cols:
        worksheet.set_column(len(cols_base), len(cols_base) + len(date_cols) - 1, 10)

# INTERFAZ PRINCIPAL
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analizador de Inventarios Negativos v6.0 Web</h1>
        <p>Versión profesional desplegable - Análisis avanzado con visualizaciones interactivas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Upload de archivos
        uploaded_files = st.file_uploader(
            "📁 Subir archivos Excel",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            help="Selecciona uno o más reportes de inventario en formato Excel"
        )
        
        # Configuraciones
        top_n = st.slider("🔝 Top N para análisis", 5, 50, 10)
        sheet_index = st.number_input("📋 Índice de hoja Excel", 0, 10, 1)
        
        # Filtros
        st.subheader("🔍 Filtros")
        filter_almacen = st.selectbox("Almacén", ["Todos"] + 
            (list(st.session_state.get('analisis', pd.DataFrame()).get('Almacen', pd.Series()).unique()) 
             if 'analisis' in st.session_state else []))
        
        filter_severidad = st.selectbox("Severidad", ["Todas", "Crítico", "Alto", "Medio", "Bajo"])
        filter_estado = st.selectbox("Estado", ["Todos", "Activo", "Resuelto"])
        
        # Botón de análisis
        analyze_button = st.button("🚀 Ejecutar Análisis", type="primary", use_container_width=True)
    
    # Contenido principal
    if analyze_button and uploaded_files:
        try:
            # Inicializar analizador
            analyzer = InventoryAnalyzerWeb()
            
            # Placeholder para progreso
            progress_placeholder = st.empty()
            st.session_state.progress_placeholder = progress_placeholder
            
            with st.spinner("Procesando archivos..."):
                # Procesar datos
                df_total = analyzer.process_uploaded_files(uploaded_files)
                analisis = analyzer.analyze_pallets(df_total)
                super_analisis = analyzer.create_super_analysis(df_total)
                reincidencias = analyzer.detect_recurrences(df_total)
                
                # Guardar en session state
                st.session_state.df_total = df_total
                st.session_state.analisis = analisis
                st.session_state.super_analisis = super_analisis
                st.session_state.reincidencias = reincidencias
            
            progress_placeholder.success("✅ Análisis completado!")
            
        except Exception as e:
            st.error(f"❌ Error en el análisis: {e}")
            return
    
    # Mostrar resultados si existen datos
    if 'analisis' in st.session_state:
        analisis = st.session_state.analisis
        super_analisis = st.session_state.super_analisis
        reincidencias = st.session_state.reincidencias
        df_total = st.session_state.df_total
        
        # Aplicar filtros
        analisis_filtered = analisis.copy()
        if filter_almacen != "Todos":
            analisis_filtered = analisis_filtered[analisis_filtered["Almacen"] == filter_almacen]
        if filter_severidad != "Todas":
            analisis_filtered = analisis_filtered[analisis_filtered["Severidad"] == filter_severidad]
        if filter_estado != "Todos":
            analisis_filtered = analisis_filtered[analisis_filtered["Estado"] == filter_estado]
        
        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pallets", len(analisis_filtered))
        with col2:
            activos = (analisis_filtered["Estado"] == "Activo").sum()
            st.metric("Activos Hoy", activos)
        with col3:
            dias_prom = round(analisis_filtered["Dias_Acumulados"].mean(), 1) if len(analisis_filtered) > 0 else 0
            st.metric("Días Promedio", dias_prom)
        with col4:
            total_negativo = round(analisis_filtered["Cantidad_Suma"].sum(), 0)
            st.metric("Total Negativo", f"{total_negativo:,.0f}")
        
        # Gráficos
        st.subheader("📈 Visualizaciones")
        fig1, fig2, fig3, fig4 = create_charts(analisis_filtered, super_analisis, top_n)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig3, use_container_width=True)
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
            st.plotly_chart(fig4, use_container_width=True)
        
        # Tablas de datos
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Análisis Principal", "🔄 Reincidencias", "📈 Súper Análisis", "📋 Datos Crudos"])
        
        with tab1:
            st.subheader("Problemas por Severidad")
            
            # Formatear columna de severidad con colores
            def format_severity(val):
                colors = {
                    "Crítico": "background-color: #ff4444; color: white",
                    "Alto": "background-color: #ff9800; color: white", 
                    "Medio": "background-color: #ffb74d; color: black",
                    "Bajo": "background-color: #81c784; color: black"
                }
                return colors.get(val, "")
            
            styled_analisis = analisis_filtered.style.applymap(format_severity, subset=['Severidad'])
            st.dataframe(styled_analisis, use_container_width=True, height=400)
        
        with tab2:
            st.subheader("Reincidencias Detectadas")
            st.dataframe(reincidencias, use_container_width=True, height=400)
        
        with tab3:
            st.subheader("Súper Análisis - Evolución Temporal por Pallet")
            
            # Controles avanzados para Súper Análisis
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                buscar_codigo = st.text_input("🔍 Buscar código:", key="buscar_codigo")
            
            with col2:
                solo_activos = st.checkbox("Solo artículos activos (última fecha)", key="solo_activos")
            
            with col3:
                almacen_super = st.selectbox("Filtrar por almacén:", 
                    ["Todos"] + list(super_analisis["Almacen"].unique()),
                    key="almacen_super")
            
            with col4:
                mostrar_vacios = st.checkbox("Mostrar celdas vacías como 0", key="mostrar_vacios")
            
            # Filtros adicionales en expandible
            with st.expander("🔧 Filtros Avanzados"):
                col1, col2 = st.columns(2)
                
                with col1:
                    codigos_excluir_super = st.text_area(
                        "Códigos a EXCLUIR (separados por comas):",
                        key="codigos_excluir_super",
                        height=60
                    )
                
                with col2:
                    codigos_incluir_super = st.text_area(
                        "Solo INCLUIR códigos (separados por comas):",
                        key="codigos_incluir_super", 
                        height=60
                    )
                
                # Filtro por rango de fechas
                date_cols = [c for c in super_analisis.columns if isinstance(c, pd.Timestamp)]
                if date_cols:
                    fecha_inicio = st.selectbox("Desde fecha:", [None] + sorted(date_cols), key="fecha_inicio")
                    fecha_fin = st.selectbox("Hasta fecha:", [None] + sorted(date_cols), key="fecha_fin")
            
            # Aplicar filtros al súper análisis
            super_filtered = super_analisis.copy()
            
            # Filtro por búsqueda de código
            if buscar_codigo:
                mask = super_filtered["Codigo"].astype(str).str.contains(buscar_codigo, case=False, na=False)
                super_filtered = super_filtered[mask]
            
            # Filtro por almacén
            if almacen_super != "Todos":
                super_filtered = super_filtered[super_filtered["Almacen"] == almacen_super]
            
            # Filtro códigos a excluir
            if codigos_excluir_super.strip():
                codigos_excl = [c.strip() for c in codigos_excluir_super.split(",") if c.strip()]
                super_filtered = super_filtered[~super_filtered["Codigo"].astype(str).isin(codigos_excl)]
            
            # Filtro solo incluir códigos
            if codigos_incluir_super.strip():
                codigos_incl = [c.strip() for c in codigos_incluir_super.split(",") if c.strip()]
                super_filtered = super_filtered[super_filtered["Codigo"].astype(str).isin(codigos_incl)]
            
            # Filtro solo activos (tienen valor en última fecha)
            if solo_activos and date_cols:
                ultima_fecha = max(date_cols)
                super_filtered = super_filtered[super_filtered[ultima_fecha].notna() & (super_filtered[ultima_fecha] != 0)]
            
            # Filtro por rango de fechas
            if date_cols and fecha_inicio and fecha_fin:
                cols_to_show = ["Codigo", "Nombre", "ID_Pallet", "Almacen"]
                date_range = [d for d in sorted(date_cols) if fecha_inicio <= d <= fecha_fin]
                super_filtered = super_filtered[cols_to_show + date_range]
                date_cols = date_range  # Actualizar date_cols para gráficos
            
            # Mostrar información de filtrado con mejor formato
            st.info(f"📋 **Mostrando {len(super_filtered)} de {len(super_analisis)} registros** con los filtros aplicados")
            
            # Procesar datos para visualización
            if mostrar_vacios:
                super_display = super_filtered.fillna(0)
            else:
                super_display = super_filtered.fillna("")
            
            # Función para colorear celdas
            def colorear_super_analisis(val):
                if pd.isna(val) or val == "" or val == 0:
                    return ""
                elif isinstance(val, (int, float)) and val < 0:
                    # Gradiente de rojo según magnitud
                    intensity = min(abs(val) / 100, 1.0)  # Normalizar
                    alpha = 0.3 + (intensity * 0.5)  # Entre 0.3 y 0.8
                    return f"background-color: rgba(255, 68, 68, {alpha}); color: white; font-weight: bold;"
                return ""
            
            # Aplicar estilo y mostrar tabla
            if not super_display.empty:
                styled_super = super_display.style.applymap(colorear_super_analisis)
                st.dataframe(styled_super, use_container_width=True, height=500)
                
                # Estadísticas rápidas - con mejor espaciado
                st.markdown("---")  # Separador visual después de la tabla
                st.markdown("#### 📊 Estadísticas de la Vista Actual")
                
                if date_cols:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_neg = super_display[date_cols].select_dtypes(include=[np.number]).sum().sum()
                        st.metric("Total Negativo", f"{total_neg:,.0f}", help="Suma total de valores negativos visibles")
                    
                    with col2:
                        pallets_activos = len(super_filtered) if solo_activos else len(super_filtered[super_filtered[date_cols].iloc[:, -1].notna()])
                        st.metric("Pallets en Vista", pallets_activos, help="Número de pallets mostrados con los filtros aplicados")
                    
                    with col3:
                        promedio_neg = super_display[date_cols].select_dtypes(include=[np.number]).mean().mean()
                        promedio_display = f"{promedio_neg:.1f}" if pd.notna(promedio_neg) else "N/A"
                        st.metric("Promedio por Celda", promedio_display, help="Promedio de valores en las celdas visibles")
                
                # GRÁFICOS DINÁMICOS - con mejor separación
                st.markdown("---")  # Separador antes de los gráficos
                st.markdown("### 📈 Análisis Visual de Datos Filtrados")
                st.markdown("Visualizaciones interactivas basadas en los datos filtrados mostrados arriba")
                
                # Crear gráficos solo si hay datos con fechas
                if date_cols and len(super_filtered) > 0:
                    
                    # Gráfico 1: Evolución Total de los datos filtrados
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Sumar por fecha todos los valores filtrados
                        evolution_data = []
                        for fecha in sorted(date_cols):
                            # Convertir columna a numérico de forma segura
                            columna = pd.to_numeric(super_display[fecha], errors='coerce')
                            total = columna.sum(skipna=True)
                            if pd.notna(total) and total != 0:
                                evolution_data.append({"Fecha": fecha, "Total": abs(total)})
                        
                        if evolution_data:
                            evo_df = pd.DataFrame(evolution_data)
                            fig_evo = px.line(
                                evo_df, 
                                x="Fecha", 
                                y="Total",
                                title="Evolución Total (Datos Filtrados)",
                                markers=True
                            )
                            fig_evo.update_traces(line_color="#ff4444", line_width=3)
                            fig_evo.update_layout(height=350)
                            st.plotly_chart(fig_evo, use_container_width=True)
                    
                    with col2:
                        # Gráfico 2: Distribución por almacén de datos filtrados
                        almacen_data = {}
                        for almacen in super_filtered["Almacen"].unique():
                            if pd.notna(almacen):
                                subset = super_display[super_display["Almacen"] == almacen]
                                # Convertir todas las columnas de fecha a numéricas y sumar
                                total = 0
                                for fecha in date_cols:
                                    columna_numerica = pd.to_numeric(subset[fecha], errors='coerce')
                                    total += columna_numerica.sum(skipna=True)
                                
                                if total != 0:
                                    almacen_data[almacen] = abs(total)
                        
                        if almacen_data:
                            fig_almacen = px.pie(
                                values=list(almacen_data.values()),
                                names=list(almacen_data.keys()),
                                title="Distribución por Almacén (Filtrado)"
                            )
                            fig_almacen.update_layout(height=350)
                            st.plotly_chart(fig_almacen, use_container_width=True)
                    
                    # Gráfico 3: MAPA DE CALOR EXPANDIDO - SIN LÍMITE DE FILAS
                    if len(date_cols) > 1:
                        st.subheader("🔥 Mapa de Calor - Evolución por Pallet (Expandido)")
                        
                        # Control de filas para mapa de calor
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write("Controla cuántos pallets mostrar en el mapa de calor:")
                        with col2:
                            opciones_heat = [10, 20, 30, 50, 100]
                            if len(super_filtered) not in opciones_heat:
                                opciones_heat.append(len(super_filtered))
                            opciones_heat = sorted([x for x in opciones_heat if x <= len(super_filtered)])
                            
                            max_rows_heat = st.selectbox(
                                "Pallets:", 
                                options=opciones_heat,
                                index=min(2, len(opciones_heat) - 1),
                                key="max_rows_heatmap"
                            )
                        
                        # Preparar datos para heatmap expandido
                        super_filtered_copy = super_filtered.copy()
                        super_filtered_copy['Codigo_Pallet'] = (super_filtered_copy['Codigo'].astype(str) + 
                                                              '_' + super_filtered_copy['ID_Pallet'].astype(str))
                        
                        # Tomar las filas seleccionadas
                        super_heat = super_filtered_copy.head(max_rows_heat)
                        heatmap_data = super_heat.set_index('Codigo_Pallet')[date_cols].copy()
                        
                        # Convertir a numérico
                        for col in heatmap_data.columns:
                            heatmap_data[col] = pd.to_numeric(heatmap_data[col], errors='coerce')
                        
                        # Limpiar datos
                        heatmap_data = heatmap_data.dropna(how='all').fillna(0)
                        
                        if not heatmap_data.empty:
                            # Altura dinámica según número de filas
                            height_map = max(500, len(heatmap_data) * 25)
                            
                            fig_heat = px.imshow(
                                heatmap_data.values,
                                labels=dict(x="Fecha", y="Código_Pallet", color="Cantidad"),
                                x=[d.strftime("%m/%d") for d in sorted(date_cols)],
                                y=heatmap_data.index,
                                title=f"Mapa de Calor - {len(heatmap_data)} Pallets Filtrados",
                                color_continuous_scale="RdBu_r",  # Escala rojo-azul invertida
                                aspect="auto"
                            )
                            fig_heat.update_layout(height=height_map)
                            st.plotly_chart(fig_heat, use_container_width=True)
                            
                            st.info(f"Mostrando {len(heatmap_data)} de {len(super_filtered)} pallets filtrados")
                    
                    # Gráfico 4: EVOLUCIÓN INDIVIDUAL - NUEVO GRÁFICO
                    if len(super_filtered) >= 1:
                        st.subheader("📈 Evolución Individual por Pallet")
                        
                        # Control para líneas de evolución
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write("Líneas de evolución individual (comportamiento día a día):")
                        with col2:
                            max_lines = st.selectbox(
                                "Líneas:", 
                                options=list(range(1, min(16, len(super_filtered) + 1))),
                                index=min(4, len(super_filtered) - 1),
                                key="max_lines_evolution"
                            )
                        
                        # Tomar los primeros N pallets
                        pallets_to_show = super_filtered.head(max_lines)
                        
                        # Crear gráfico de líneas múltiples
                        fig_lines = go.Figure()
                        
                        colors = px.colors.qualitative.Set1[:max_lines]  # Colores distintos
                        
                        for idx, (_, row) in enumerate(pallets_to_show.iterrows()):
                            codigo_pallet = str(row["Codigo"]) + "_" + str(row["ID_Pallet"])
                            
                            # Extraer valores y fechas válidas
                            valores = []
                            fechas_validas = []
                            
                            for fecha in sorted(date_cols):
                                valor = row[fecha]
                                try:
                                    valor_num = pd.to_numeric(valor, errors='coerce')
                                    if pd.notna(valor_num) and valor_num != 0:
                                        valores.append(valor_num)
                                        fechas_validas.append(fecha)
                                except:
                                    continue
                            
                            # Agregar línea si hay datos
                            if valores and fechas_validas:
                                fig_lines.add_trace(go.Scatter(
                                    x=fechas_validas,
                                    y=valores,
                                    mode='lines+markers',
                                    name=codigo_pallet,
                                    line=dict(width=3, color=colors[idx % len(colors)]),
                                    marker=dict(size=6),
                                    hovertemplate="<b>%{fullData.name}</b><br>" +
                                                "Fecha: %{x}<br>" +
                                                "Cantidad: %{y}<br>" +
                                                "<extra></extra>"
                                ))
                        
                        fig_lines.update_layout(
                            title=f"Comportamiento Diario Individual - {max_lines} Pallets",
                            xaxis_title="Fecha",
                            yaxis_title="Cantidad Negativa",
                            height=450,
                            hovermode='x unified',
                            legend=dict(
                                yanchor="top",
                                y=0.99,
                                xanchor="left",
                                x=1.01
                            )
                        )
                        
                        st.plotly_chart(fig_lines, use_container_width=True)
                        
                        # Información adicional
                        st.info(f"Cada línea representa la evolución diaria de un pallet específico. " +
                               f"Mostrando {max_lines} de {len(super_filtered)} pallets filtrados.")
                
                # Botón de descarga específico del súper análisis filtrado
                st.markdown("---")  # Separador antes del botón de descarga
                csv_super = super_display.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar Súper Análisis Filtrado (CSV)",
                    data=csv_super,
                    file_name=f"Super_Analisis_Filtrado_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    help="Descarga los datos filtrados actualmente mostrados en formato CSV"
                )
            else:
                st.warning("No hay datos que coincidan con los filtros aplicados.")
        
        with tab4:
            st.subheader("Datos Crudos Procesados")
            st.dataframe(df_total, use_container_width=True, height=400)
        
        # Descarga de reporte
        st.subheader("💾 Descargar Reporte")
        col1, col2 = st.columns(2)
        
        with col1:
            excel_buffer = generate_excel_report(analisis, super_analisis, reincidencias, df_total, top_n)
            st.download_button(
                label="📊 Descargar Reporte Excel",
                data=excel_buffer,
                file_name=f"Reporte_Inventarios_Negativos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            csv_data = analisis.to_csv(index=False)
            st.download_button(
                label="📄 Descargar CSV",
                data=csv_data,
                file_name=f"Analisis_Pallets_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        # FUNCIONALIDAD DE IMPRESIÓN RESPONSIVA
        st.markdown("---")
        st.subheader("🖨️ Generar Reporte para Impresión")
        
        with st.expander("📋 Configurar y Generar Reporte Imprimible", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                print_kpis = st.checkbox("📈 Incluir KPIs", True, key="kpis_check")
                print_table = st.checkbox("📊 Incluir tabla (Top 20)", True, key="table_check")
                print_reincidencias = st.checkbox("🔄 Incluir reincidencias", True, key="reincid_check")
            with col2:
                paper = st.selectbox("📄 Papel", ["A4", "Letter"], key="paper_select")
                orient = st.selectbox("🔄 Orientación", ["Vertical", "Horizontal"], key="orient_select")
            
            if st.button("👁️ Generar Vista Previa para Impresión", type="primary", key="generate_print"):
                # Filtros aplicados
                filtros = []
                if filter_almacen != "Todos": 
                    filtros.append(f"Almacén: {filter_almacen}")
                if filter_severidad != "Todas": 
                    filtros.append(f"Severidad: {filter_severidad}")
                if filter_estado != "Todos": 
                    filtros.append(f"Estado: {filter_estado}")
                filtros_txt = ", ".join(filtros) if filtros else "Sin filtros aplicados"
                
                # CSS para impresión específica - oculta todo excepto la vista previa
                st.markdown("""
                <style>
                @media print {
                    /* Ocultar sidebar y elementos de navegación */
                    .stSidebar, .stTabs, .stExpander, .stButton, .stSelectbox, .stCheckbox {
                        display: none !important;
                    }
                    
                    /* Ocultar todo lo que NO sea la vista previa */
                    .main .block-container > div:not(.print-report-container) {
                        display: none !important;
                    }
                    
                    /* Mostrar solo el contenedor de la vista previa */
                    .print-report-container {
                        display: block !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    
                    /* Ajustes para impresión */
                    @page {
                        margin: 0.5in;
                        size: A4;
                    }
                    
                    body {
                        font-size: 12px;
                        line-height: 1.4;
                    }
                    
                    /* Ocultar headers de Streamlit */
                    header, .stApp > header, .stDecoration {
                        display: none !important;
                    }
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Contenedor específico para la vista previa de impresión
                st.markdown('<div class="print-report-container">', unsafe_allow_html=True)
                
                # Header del reporte
                st.markdown(f"""
                <div style="text-align: center; border: 2px solid #667eea; padding: 20px; border-radius: 10px; background: white; margin: 20px 0;">
                    <h1 style="color: #667eea; margin: 0;">📊 Reporte de Inventarios Negativos</h1>
                    <h3 style="color: #666; margin: 10px 0;">Sistema de Análisis Avanzado v6.0</h3>
                    <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Filtros aplicados:</strong> {filtros_txt}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # KPIs usando métricas nativas de Streamlit
                if print_kpis:
                    st.subheader("📈 Indicadores Clave de Rendimiento (KPIs)")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    total_pallets = len(analisis_filtered)
                    activos = (analisis_filtered["Estado"] == "Activo").sum() if total_pallets > 0 else 0
                    dias_promedio = round(analisis_filtered["Dias_Acumulados"].mean(), 1) if total_pallets > 0 else 0
                    total_negativo = round(analisis_filtered["Cantidad_Suma"].sum(), 0) if total_pallets > 0 else 0
                    
                    with col1:
                        st.metric("Total de Pallets", total_pallets, help="Registros analizados")
                    with col2:
                        st.metric("Problemas Activos", activos, help="Requieren atención hoy")
                    with col3:
                        st.metric("Días Promedio", dias_promedio, help="Duración del problema")
                    with col4:
                        st.metric("Cantidad Negativa", f"{total_negativo:,.0f}", help="Total acumulado")
                
                # Tabla principal usando dataframe nativo
                if print_table and not analisis_filtered.empty:
                    st.subheader("📊 Análisis Principal - Top 20 Registros Críticos")
                    
                    # Preparar datos para mejor visualización
                    display_columns = ["Codigo", "Nombre", "ID_Pallet", "Almacen", "Severidad", "Dias_Acumulados", "Cantidad_Promedio", "Estado"]
                    table_data = analisis_filtered.head(20)[display_columns].copy()
                    
                    # Formatear columnas para impresión
                    if "Nombre" in table_data.columns:
                        table_data["Nombre"] = table_data["Nombre"].astype(str).apply(lambda x: x[:25] + "..." if len(str(x)) > 25 else str(x))
                    if "Dias_Acumulados" in table_data.columns:
                        table_data["Dias_Acumulados"] = table_data["Dias_Acumulados"].fillna(0).astype(int)
                    if "Cantidad_Promedio" in table_data.columns:
                        table_data["Cantidad_Promedio"] = table_data["Cantidad_Promedio"].round(2)
                    
                    # Renombrar columnas para mejor presentación
                    column_names = {
                        "Codigo": "Código",
                        "Nombre": "Nombre Producto", 
                        "ID_Pallet": "ID Pallet",
                        "Almacen": "Almacén",
                        "Severidad": "Severidad",
                        "Dias_Acumulados": "Días Acum.",
                        "Cantidad_Promedio": "Cant. Promedio",
                        "Estado": "Estado"
                    }
                    table_data = table_data.rename(columns=column_names)
                    
                    st.dataframe(table_data, use_container_width=True, height=400)
                
                # Tabla de reincidencias usando dataframe nativo
                if print_reincidencias and not reincidencias.empty:
                    st.subheader("🔄 Reincidencias Detectadas - Top 15 Casos")
                    
                    # Preparar datos de reincidencias para visualización
                    reincid_display = reincidencias.head(15).copy()
                    if "Nombre" in reincid_display.columns:
                        reincid_display["Nombre"] = reincid_display["Nombre"].astype(str).apply(lambda x: x[:30] + "..." if len(str(x)) > 30 else str(x))
                    if "Fechas" in reincid_display.columns:
                        reincid_display["Fechas"] = reincid_display["Fechas"].astype(str).apply(lambda x: x[:50] + "..." if len(str(x)) > 50 else str(x))
                    
                    # Renombrar columnas
                    reincid_names = {
                        "Codigo": "Código",
                        "Nombre": "Nombre del Producto",
                        "Almacen": "Almacén", 
                        "Fechas": "Fechas de Ocurrencia"
                    }
                    reincid_display = reincid_display.rename(columns=reincid_names)
                    
                    st.dataframe(reincid_display, use_container_width=True, height=300)
                
                # Footer del reporte
                st.markdown(f"""
                <div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 3px solid #667eea; background: #f8f9ff; border-radius: 10px;">
                    <h4 style="color: #667eea; margin: 0;">Analizador de Inventarios Negativos v6.0 Web</h4>
                    <p style="margin: 10px 0;">Reporte generado automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
                    <p style="margin: 5px 0; font-style: italic; color: #666;">Sistema profesional de análisis con detección de reincidencias y clasificación automática por severidad</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Instrucciones de impresión mejoradas y funcionales
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin: 25px 0;">
                    <h3 style="margin-top: 0; text-align: center;">🖨️ Instrucciones para Imprimir</h3>
                    <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 10px;">
                        <ol style="margin: 0; padding-left: 25px; line-height: 1.8;">
                            <li><strong>Presiona Ctrl+P</strong> (Windows/Linux) o <strong>Cmd+P</strong> (Mac)</li>
                            <li><strong>En las opciones de impresión:</strong>
                                <ul style="margin: 10px 0; padding-left: 20px;">
                                    <li>✅ <strong>Activar "Gráficos de fondo"</strong> para ver todos los colores</li>
                                    <li>📄 <strong>Tamaño de papel:</strong> {paper}</li>
                                    <li>🔄 <strong>Orientación:</strong> {orient}</li>
                                    <li>⚙️ <strong>Márgenes:</strong> Ajustar si es necesario</li>
                                </ul>
                            </li>
                            <li><strong>¡Hacer clic en Imprimir!</strong> 🖨️</li>
                        </ol>
                    </div>
                    <p style="text-align: center; margin: 15px 0 0 0; font-style: italic;">
                        💡 <strong>Tip:</strong> El reporte se imprime tal como lo ves en pantalla
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Cerrar contenedor de vista previa
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Mensaje de éxito con animación
                st.balloons()
                st.success("✅ ¡Vista previa generada exitosamente! Ahora al usar Ctrl+P se imprimirá SOLO esta vista previa, no toda la página.")
    
    elif not uploaded_files:
        # Instrucciones de uso
        st.info("""
        👋 **Bienvenido al Analizador de Inventarios Negativos v6.0 Web**
        
        Para comenzar:
        1. 📁 Sube uno o más archivos Excel en la barra lateral
        2. ⚙️ Configura los parámetros de análisis
        3. 🚀 Haz clic en "Ejecutar Análisis"
        4. 📊 Explora los resultados y descarga reportes
        
        **Características:**
        - ✅ Análisis de severidad por magnitud
        - ✅ Detección de reincidencias
        - ✅ Visualizaciones interactivas
        - ✅ Filtros avanzados
        - ✅ Reportes descargables
        - ✅ Interfaz responsiva
        """)

if __name__ == "__main__":
    main()