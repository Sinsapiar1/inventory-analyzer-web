import streamlit as st
import streamlit.components.v1 as components
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
import sqlite3
import re

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

    # Convertir Almacen y Nombre a string para evitar problemas de tipos mixtos
    df["Almacen"] = df["Almacen"].astype(str)
    df["Nombre"] = df["Nombre"].astype(str)
    
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
    
    # Severidad por magnitud del negativo - Versión robusta
    magnitudes = np.abs(analisis["Cantidad_Promedio"])
    
    if len(magnitudes) == 0:
        # Sin datos
        analisis["Severidad"] = pd.Series(dtype="category")
    elif magnitudes.nunique() == 1:
        # Todos los valores son iguales
        analisis["Severidad"] = "Medio"
    elif len(magnitudes) < 4:
        # Muy pocos datos: categorización simple
        median_val = magnitudes.median()
        analisis["Severidad"] = magnitudes.apply(
            lambda x: "Crítico" if x > median_val else "Bajo"
        )
    else:
        # Suficientes datos: categorización completa
        try:
            # Intentar con percentiles
            q25, q50, q75 = np.percentile(magnitudes, [25, 50, 75])
            
            # Verificar si hay bins únicos suficientes
            bins = [-1, q25, q50, q75, float("inf")]
            unique_bins = sorted(set(bins))
            
            if len(unique_bins) < 3:
                # No hay suficientes bins únicos, usar categorización simple
                median_val = magnitudes.median()
                analisis["Severidad"] = magnitudes.apply(
                    lambda x: "Alto" if x > median_val * 1.5 else ("Medio" if x > median_val else "Bajo")
                )
            else:
                # Usar pd.qcut que maneja automáticamente los duplicados
                analisis["Severidad"] = pd.qcut(
                    magnitudes,
                    q=[0, 0.25, 0.5, 0.75, 1.0],
                    labels=["Bajo", "Medio", "Alto", "Crítico"],
                    duplicates='drop'
                )
        except Exception:
            # Si todo falla, usar categorización simple por mediana
            median_val = magnitudes.median()
            analisis["Severidad"] = magnitudes.apply(
                lambda x: "Alto" if x > median_val * 1.5 else ("Medio" if x > median_val else "Bajo")
            )
    
    # Estado (activo/resuelto)
    fecha_ultimo = df_total["Fecha_Reporte"].max()
    analisis["Estado"] = np.where(analisis["Ultima_Aparicion"] == fecha_ultimo, "Activo", "Resuelto")
    
    # Score de criticidad
    analisis["Score_Criticidad"] = analisis["Dias_Acumulados"] * np.abs(analisis["Cantidad_Promedio"])
    
    return analisis

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Inventarios Negativos v6.3 Database Edition",
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
    
    /* ===== DISEÑO PROFESIONAL DE TABS - GLASSMORPHISM STYLE ===== */
    
    /* Contenedor principal de tabs con efecto glassmorphism */
    .stTabs [data-baseweb="tab-list"] {
        position: sticky;
        top: 0;
        background: linear-gradient(145deg, 
            rgba(102, 126, 234, 0.12) 0%, 
            rgba(118, 75, 162, 0.08) 50%,
            rgba(102, 126, 234, 0.12) 100%);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        z-index: 999;
        padding: 20px 15px 10px 15px;
        box-shadow: 
            0 4px 16px rgba(102, 126, 234, 0.15),
            0 8px 32px rgba(118, 75, 162, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
        border-radius: 0 0 20px 20px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        margin-bottom: 20px;
        gap: 8px;
    }
    
    /* Tabs individuales con diseño moderno */
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 15px;
        padding: 14px 24px;
        margin: 0 4px;
        border-radius: 12px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 
            0 2px 8px rgba(0, 0, 0, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
        color: #3a3a3a;
        position: relative;
        overflow: hidden;
    }
    
    /* Efecto de brillo en hover */
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.4), 
            transparent);
        transition: left 0.5s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        left: 100%;
    }
    
    /* Tab en estado hover */
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.45);
        transform: translateY(-2px);
        box-shadow: 
            0 4px 16px rgba(102, 126, 234, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(102, 126, 234, 0.4);
    }
    
    /* Tab seleccionado - Efecto premium */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(145deg, 
            rgba(102, 126, 234, 0.95) 0%, 
            rgba(118, 75, 162, 0.9) 100%);
        color: white !important;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 
            0 6px 20px rgba(102, 126, 234, 0.4),
            0 2px 8px rgba(118, 75, 162, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.3),
            inset 0 -1px 0 rgba(0, 0, 0, 0.1);
        transform: translateY(-3px);
    }
    
    /* Animación de pulso sutil para tab activo */
    @keyframes pulse-glow {
        0%, 100% {
            box-shadow: 
                0 6px 20px rgba(102, 126, 234, 0.4),
                0 2px 8px rgba(118, 75, 162, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }
        50% {
            box-shadow: 
                0 6px 24px rgba(102, 126, 234, 0.5),
                0 2px 12px rgba(118, 75, 162, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.4);
        }
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        animation: pulse-glow 3s ease-in-out infinite;
    }
    
    /* Indicador visual debajo del tab activo */
    .stTabs [data-baseweb="tab"][aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 3px;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(102, 126, 234, 0.8), 
            transparent);
        border-radius: 2px;
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
        # Filtrar valores NaN, "nan", "N/A" y vacíos
        if pd.isna(almacen) or str(almacen).lower() in ['nan', 'n/a', 'none', '']:
            continue
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

# ========== NUEVAS FUNCIONES PARA PREPROCESAMIENTO DE ERP ==========

@st.cache_data
def preprocess_erp_raw_data(file_content, filename, sheet_index=0):
    """
    Procesa archivo crudo del ERP y lo convierte al formato esperado

    Mapeo de columnas ERP -> App:
    - Código de artículo -> Código
    - Nombre del producto -> Nombre
    - Almacén -> Almacén
    - Id de pallet -> ID de Pallet
    - Inventario físico -> Inventario Físico
    - Física disponible -> Disponible

    Filtros aplicados:
    - Solo filas con inventario negativo
    - Solo filas con ID de pallet válido (no vacío)
    """
    try:
        # Leer Excel desde el archivo crudo
        df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_index)

        # Guardar df original para stats
        df_original = df.copy()

        # Normalizar nombres de columnas del ERP
        column_mapping = {
            "Código de artículo": "Codigo",
            "Código": "Codigo",
            "Codigo de artículo": "Codigo",
            "Nombre del producto": "Nombre",
            "Nombre": "Nombre",
            "Almacén": "Almacen",
            "Almacen": "Almacen",
            "Id de pallet": "ID_Pallet",
            "ID de Pallet": "ID_Pallet",
            "Id Pallet": "ID_Pallet",
            "Inventario físico": "Inventario_Fisico",
            "Inventario Físico": "Inventario_Fisico",
            "Inventario fisico": "Inventario_Fisico",
            "Física disponible": "Disponible",
            "Fisica disponible": "Disponible",
            "Disponible": "Disponible"
        }

        # Renombrar columnas
        df = df.rename(columns=column_mapping)

        # Verificar que tenemos las columnas esenciales
        required_cols = ["Codigo", "Nombre", "Almacen", "ID_Pallet", "Inventario_Fisico"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            return None, False, f"Faltan columnas requeridas: {', '.join(missing_cols)}", None

        # Filtrar solo negativos en Inventario Físico
        df["Inventario_Fisico"] = pd.to_numeric(df["Inventario_Fisico"], errors='coerce')
        df_negativos = df[df["Inventario_Fisico"] < 0].copy()

        # Filtrar solo filas con ID de pallet válido
        df_negativos = df_negativos[df_negativos["ID_Pallet"].notna()]
        df_negativos = df_negativos[df_negativos["ID_Pallet"].astype(str).str.strip() != ""]

        # Limpiar formato de números (quitar comas y puntos decimales innecesarios)
        for col in ["Codigo", "ID_Pallet"]:
            if col in df_negativos.columns:
                df_negativos[col] = (
                    df_negativos[col]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.split(".").str[0]
                    .str.strip()
                )

        # Convertir Almacen y Nombre a string para evitar problemas de tipos mixtos
        df_negativos["Almacen"] = df_negativos["Almacen"].astype(str)
        df_negativos["Nombre"] = df_negativos["Nombre"].astype(str)

        # Convertir Codigo y ID_Pallet a enteros (como en archivos antiguos)
        df_negativos["Codigo"] = pd.to_numeric(df_negativos["Codigo"], errors='coerce').fillna(0).astype(int)
        df_negativos["ID_Pallet"] = pd.to_numeric(df_negativos["ID_Pallet"], errors='coerce').fillna(0).astype(int)

        # Si hay columna Disponible, agregarla
        if "Disponible" not in df_negativos.columns:
            df_negativos["Disponible"] = df_negativos["Inventario_Fisico"]

        # Renombrar columnas al formato final esperado (igual a archivos antiguos)
        df_final = df_negativos.rename(columns={
            "Codigo": "Código",
            "ID_Pallet": "ID de Pallet",
            "Inventario_Fisico": "Inventario Físico",
            "Almacen": "Almacén"
        })

        # Seleccionar solo columnas necesarias con nombres exactos de archivos antiguos
        final_columns = ["Código", "Nombre", "Almacén", "ID de Pallet", "Inventario Físico", "Disponible"]
        df_final = df_final[[col for col in final_columns if col in df_final.columns]]

        # Estadísticas
        stats = {
            "total_productos": len(df_original),
            "productos_negativos": len(df_negativos),
            "total_inventario_fisico": df_original["Inventario_Fisico"].sum() if "Inventario_Fisico" in df_original.columns else 0,
            "pallets_unicos": df_negativos["ID_Pallet"].nunique() if len(df_negativos) > 0 else 0,
            "fecha_exportacion": datetime.now(),
            "filas_filtradas": len(df_final)
        }

        return df_final, True, None, stats

    except Exception as e:
        return None, False, str(e), None

@st.cache_data
def export_preprocessed_report(df_procesado, stats, fecha_suffix=None):
    """
    Exporta archivo Excel con formato compatible con el resto de la app

    Estructura:
    - Hoja 1: Estadísticas Generales
    - Hoja 2: Datos procesados (negativos con ID pallet)

    Nombre: reporte_all_YYYYMMDD_HHMMSS.xlsx
    """
    buffer = io.BytesIO()

    # Generar nombre de archivo
    if fecha_suffix is None:
        fecha_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"reporte_all_{fecha_suffix}.xlsx"

    try:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book

            # === HOJA 1: Estadísticas Generales ===
            worksheet_stats = workbook.add_worksheet("Estadísticas")

            # Formatos
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'bg_color': '#1F4E78',
                'font_color': 'white',
                'align': 'left',
                'valign': 'vcenter'
            })

            label_format = workbook.add_format({
                'bold': True,
                'align': 'left'
            })

            value_format = workbook.add_format({
                'align': 'left',
                'num_format': '#,##0.00'
            })

            # Escribir título
            worksheet_stats.merge_range('A1:B1', 'Estadísticas Generales', title_format)

            # Escribir estadísticas
            row = 2
            worksheet_stats.write(row, 0, 'Total de Productos', label_format)
            worksheet_stats.write(row, 1, stats['total_productos'], value_format)

            row += 1
            worksheet_stats.write(row, 0, 'Productos con Inventario Negativo', label_format)
            worksheet_stats.write(row, 1, stats['productos_negativos'], value_format)

            row += 1
            worksheet_stats.write(row, 0, 'Total de Inventario Físico', label_format)
            worksheet_stats.write(row, 1, stats['total_inventario_fisico'], value_format)

            row += 1
            worksheet_stats.write(row, 0, 'Pallets Únicos', label_format)
            worksheet_stats.write(row, 1, stats['pallets_unicos'], value_format)

            row += 2
            fecha_formato = stats['fecha_exportacion'].strftime("%d de %B de %Y, %H:%M")
            worksheet_stats.write(row, 0, 'Fecha de Exportación', label_format)
            worksheet_stats.write(row, 1, fecha_formato)

            row += 1
            worksheet_stats.write(row, 0, 'Última Actualización', label_format)
            worksheet_stats.write(row, 1, fecha_formato)

            # Ajustar columnas
            worksheet_stats.set_column('A:A', 35)
            worksheet_stats.set_column('B:B', 25)

            # === HOJA 2: Datos procesados (nombre igual a archivos antiguos) ===
            df_procesado.to_excel(writer, sheet_name="Inventario Completo (Actual)", index=False)

            # Formatear hoja de datos
            worksheet_data = writer.sheets["Inventario Completo (Actual)"]

            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#1F4E78',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })

            # Aplicar formato a encabezados
            for col_num, value in enumerate(df_procesado.columns.values):
                worksheet_data.write(0, col_num, value, header_format)

            # Ajustar anchos
            worksheet_data.set_column('A:A', 12)  # Codigo
            worksheet_data.set_column('B:B', 35)  # Nombre
            worksheet_data.set_column('C:C', 10)  # Almacen
            worksheet_data.set_column('D:D', 18)  # ID_Pallet
            worksheet_data.set_column('E:F', 15)  # Inventario y Disponible

        buffer.seek(0)
        return buffer, filename, True, None

    except Exception as e:
        return None, None, False, str(e)

# ========== NUEVAS FUNCIONES PARA MANEJO DE BASE DE DATOS ==========

def extract_date_from_filename(filename):
    """
    Extrae la fecha del nombre del archivo
    Formato esperado: reporte_all_YYYYMMDD_HHMMSS.xlsx
    """
    try:
        # Buscar patrón de fecha YYYYMMDD
        pattern = r'(\d{8})'
        match = re.search(pattern, filename)
        if match:
            fecha_str = match.group(1)
            fecha = datetime.strptime(fecha_str, "%Y%m%d")
            return fecha
        else:
            # Si no encuentra fecha, usa fecha actual
            return datetime.now()
    except Exception as e:
        return datetime.now()

def convert_excels_to_db(uploaded_files, sheet_index=1, progress_callback=None):
    """
    Convierte múltiples archivos Excel a una base de datos SQLite
    
    Args:
        uploaded_files: Lista de archivos Excel cargados
        sheet_index: Índice de la hoja a leer (por defecto 1 = segunda hoja)
        progress_callback: Función opcional para reportar progreso
    
    Returns:
        buffer: BytesIO con el archivo .db
        stats: Diccionario con estadísticas de conversión
        success: Boolean indicando si tuvo éxito
        error: Mensaje de error si falló
    """
    try:
        # Crear conexión a base de datos en memoria
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Crear tabla para almacenar inventarios
        cursor.execute('''
            CREATE TABLE inventarios_negativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT,
                nombre TEXT,
                almacen TEXT,
                id_pallet TEXT,
                cantidad_negativa REAL,
                disponible REAL,
                fecha_reporte DATE,
                archivo_origen TEXT,
                fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear índices para mejorar rendimiento
        cursor.execute('CREATE INDEX idx_fecha ON inventarios_negativos(fecha_reporte)')
        cursor.execute('CREATE INDEX idx_codigo ON inventarios_negativos(codigo)')
        cursor.execute('CREATE INDEX idx_pallet ON inventarios_negativos(id_pallet)')
        
        total_registros = 0
        archivos_procesados = 0
        archivos_error = 0
        errores_detalle = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                if progress_callback:
                    progress_callback(f"Procesando {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                
                # Leer archivo Excel
                file_content = uploaded_file.read()
                
                # Extraer fecha del nombre del archivo
                fecha_reporte = extract_date_from_filename(uploaded_file.name)
                
                # Leer la hoja especificada
                df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_index)
                
                # Normalizar nombres de columnas (similar a la lógica existente)
                df = df.rename(columns={
                    "Código": "Codigo",
                    "Código Producto": "Codigo",
                    "ID de Pallet": "ID_Pallet",
                    "Inventario Físico": "Cantidad_Negativa",
                    "Nombre": "Nombre",
                    "Descripción": "Nombre",
                    "Almacén": "Almacen",
                    "Almacen": "Almacen",
                    "Disponible": "Disponible",
                    "Física disponible": "Disponible"
                })
                
                # Verificar columnas esenciales
                columnas_requeridas = ["Codigo", "ID_Pallet", "Cantidad_Negativa"]
                if not all(col in df.columns for col in columnas_requeridas):
                    errores_detalle.append(f"{uploaded_file.name}: Faltan columnas requeridas")
                    archivos_error += 1
                    continue
                
                # Limpiar datos
                for col in ["Codigo", "ID_Pallet"]:
                    if col in df.columns:
                        df[col] = (
                            df[col]
                            .astype(str)
                            .str.replace(",", "", regex=False)
                            .str.split(".").str[0]
                            .str.strip()
                        )
                
                # Asegurar que existen columnas opcionales
                if "Nombre" not in df.columns:
                    df["Nombre"] = ""
                if "Almacen" not in df.columns:
                    df["Almacen"] = "N/A"
                if "Disponible" not in df.columns:
                    df["Disponible"] = df["Cantidad_Negativa"]
                
                # Convertir a string para evitar problemas de tipos
                df["Almacen"] = df["Almacen"].astype(str)
                df["Nombre"] = df["Nombre"].astype(str)
                
                # Convertir cantidad a numérico
                df["Cantidad_Negativa"] = pd.to_numeric(df["Cantidad_Negativa"], errors="coerce").fillna(0)
                
                # Filtrar solo negativos
                df_negativos = df[df["Cantidad_Negativa"] < 0].copy()
                
                if len(df_negativos) == 0:
                    if progress_callback:
                        progress_callback(f"  ⚠️ {uploaded_file.name}: Sin registros negativos")
                    continue
                
                # Preparar datos para inserción
                df_negativos["fecha_reporte"] = fecha_reporte.strftime("%Y-%m-%d")
                df_negativos["archivo_origen"] = uploaded_file.name
                
                # Insertar en base de datos
                for _, row in df_negativos.iterrows():
                    cursor.execute('''
                        INSERT INTO inventarios_negativos 
                        (codigo, nombre, almacen, id_pallet, cantidad_negativa, disponible, fecha_reporte, archivo_origen)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(row.get("Codigo", "")),
                        str(row.get("Nombre", "")),
                        str(row.get("Almacen", "N/A")),
                        str(row.get("ID_Pallet", "")),
                        float(row.get("Cantidad_Negativa", 0)),
                        float(row.get("Disponible", 0)),
                        row["fecha_reporte"],
                        row["archivo_origen"]
                    ))
                
                total_registros += len(df_negativos)
                archivos_procesados += 1
                
                if progress_callback:
                    progress_callback(f"  ✅ {uploaded_file.name}: {len(df_negativos)} registros agregados")
                
            except Exception as e:
                archivos_error += 1
                errores_detalle.append(f"{uploaded_file.name}: {str(e)}")
                if progress_callback:
                    progress_callback(f"  ❌ Error en {uploaded_file.name}: {str(e)}")
                continue
        
        conn.commit()
        
        # Guardar base de datos en archivo temporal
        temp_db_path = '/tmp/consolidated_inventory.db'
        disk_conn = sqlite3.connect(temp_db_path)
        
        # Copiar base de datos en memoria a archivo en disco
        conn.backup(disk_conn)
        disk_conn.close()
        conn.close()
        
        # Leer archivo y guardar en buffer
        buffer = io.BytesIO()
        with open(temp_db_path, 'rb') as f:
            buffer.write(f.read())
        
        buffer.seek(0)
        
        # Limpiar archivo temporal
        Path(temp_db_path).unlink(missing_ok=True)
        
        # Estadísticas
        stats = {
            "total_archivos": len(uploaded_files),
            "archivos_procesados": archivos_procesados,
            "archivos_error": archivos_error,
            "total_registros": total_registros,
            "errores_detalle": errores_detalle,
            "fecha_creacion": datetime.now()
        }
        
        return buffer, stats, True, None
        
    except Exception as e:
        return None, None, False, str(e)

def read_db_file(db_file_content):
    """
    Lee un archivo .db y retorna DataFrame similar al proceso de Excel
    
    Args:
        db_file_content: Contenido del archivo .db
    
    Returns:
        df: DataFrame con los datos
        success: Boolean
        error: Mensaje de error si falló
    """
    try:
        # Guardar contenido en archivo temporal
        temp_db_path = '/tmp/temp_inventory.db'
        with open(temp_db_path, 'wb') as f:
            f.write(db_file_content)
        
        # Conectar a base de datos
        conn = sqlite3.connect(temp_db_path)
        
        # Leer datos
        query = '''
            SELECT 
                codigo as Codigo,
                nombre as Nombre,
                almacen as Almacen,
                id_pallet as ID_Pallet,
                cantidad_negativa as Cantidad_Negativa,
                fecha_reporte as Fecha_Reporte,
                archivo_origen as Archivo_Origen
            FROM inventarios_negativos
            ORDER BY fecha_reporte, codigo
        '''
        
        df = pd.read_sql_query(query, conn)
        
        # Convertir fecha_reporte a datetime
        df["Fecha_Reporte"] = pd.to_datetime(df["Fecha_Reporte"])
        
        # Cerrar conexión
        conn.close()
        
        # Limpiar archivo temporal
        Path(temp_db_path).unlink(missing_ok=True)
        
        return df, True, None
        
    except Exception as e:
        return None, False, str(e)

def save_db_to_file(buffer, filename=None):
    """
    Prepara el archivo .db para descarga
    
    Args:
        buffer: BytesIO con contenido de la DB
        filename: Nombre del archivo (opcional)
    
    Returns:
        buffer: Buffer listo para descarga
        filename: Nombre del archivo
    """
    if filename is None:
        filename = f"inventarios_consolidados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    return buffer, filename

# INTERFAZ PRINCIPAL
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analizador de Inventarios Negativos v6.3 Database Edition</h1>
        <p>Premium Edition - Con consolidación de datos y preprocesador ERP integrado</p>
    </div>
    """, unsafe_allow_html=True)

    # ========== NUEVO: MODO DE OPERACIÓN ==========
    st.sidebar.title("🎯 Modo de Operación")
    modo = st.sidebar.radio(
        "Selecciona el modo:",
        [
            "📥 Preprocesar Datos ERP", 
            "📊 Analizar Inventarios",
            "🗄️ Consolidar Excel → Base de Datos",
            "💾 Analizar desde Base de Datos"
        ],
        help="Preprocesar: Transforma datos crudos del ERP | Analizar: Procesa reportes ya formateados | Consolidar: Convierte múltiples Excel a .db | Analizar DB: Lee desde archivo .db"
    )

    st.sidebar.markdown("---")

    # ========== MODO 1: PREPROCESADOR ERP ==========
    if modo == "📥 Preprocesar Datos ERP":
        st.subheader("📥 Preprocesador de Datos ERP")
        st.info("""
        **Este módulo transforma los datos crudos del ERP** en el formato requerido para el análisis.

        **Proceso:**
        1. Sube el archivo Excel crudo del ERP
        2. El sistema filtra automáticamente:
           - ✅ Solo inventarios negativos
           - ✅ Solo registros con ID de pallet válido
        3. Genera un archivo descargable listo para análisis
        """)

        # Upload del archivo ERP
        erp_file = st.file_uploader(
            "📁 Subir archivo crudo del ERP",
            type=['xlsx', 'xls'],
            help="Archivo Excel directo del ERP con todas las columnas originales",
            key="erp_uploader"
        )

        # Configuración
        col1, col2 = st.columns(2)
        with col1:
            sheet_number_erp = st.number_input(
                "📋 Número de hoja a procesar",
                min_value=1,
                max_value=10,
                value=1,
                help="La hoja del Excel donde están los datos (1 = primera hoja, 2 = segunda hoja, etc.)"
            )
            # Convertir a índice (restar 1 porque Python usa índices base 0)
            sheet_idx_erp = sheet_number_erp - 1

        with col2:
            fecha_manual = st.date_input(
                "📅 Fecha del reporte",
                value=datetime.now(),
                help="Se usará para el nombre del archivo exportado"
            )

        if erp_file:
            st.markdown("---")
            st.subheader("📊 Vista Previa y Procesamiento")

            # Procesar archivo
            file_content = erp_file.read()
            df_procesado, success, error, stats = preprocess_erp_raw_data(
                file_content,
                erp_file.name,
                sheet_idx_erp
            )

            if success and df_procesado is not None:
                # Mostrar estadísticas
                st.success("✅ Archivo procesado exitosamente")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Productos (Original)", stats['total_productos'])
                with col2:
                    st.metric("Productos Negativos", stats['productos_negativos'])
                with col3:
                    st.metric("Pallets Únicos", stats['pallets_unicos'])
                with col4:
                    st.metric("Filas Procesadas", stats['filas_filtradas'])

                # Tabs para vista previa
                tab_preview, tab_stats = st.tabs(["📋 Datos Procesados", "📊 Estadísticas Detalladas"])

                with tab_preview:
                    st.dataframe(df_procesado.head(100), width='stretch')
                    st.caption(f"Mostrando primeras 100 de {len(df_procesado)} filas")

                with tab_stats:
                    st.markdown("### Resumen del Filtrado")
                    st.write(f"- **Filas originales**: {stats['total_productos']:,}")
                    st.write(f"- **Filas con inventario negativo**: {stats['productos_negativos']:,}")
                    st.write(f"- **Filas con ID pallet válido**: {stats['filas_filtradas']:,}")
                    st.write(f"- **Total inventario físico**: {stats['total_inventario_fisico']:,.2f}")

                    # Distribución por almacén
                    if 'Almacén' in df_procesado.columns:
                        st.markdown("### Distribución por Almacén")
                        almacen_counts = df_procesado['Almacén'].value_counts()
                        st.bar_chart(almacen_counts)

                # Botón de descarga
                st.markdown("---")
                st.subheader("💾 Descargar Archivo Procesado")

                fecha_str = fecha_manual.strftime("%Y%m%d")
                hora_str = datetime.now().strftime("%H%M%S")
                fecha_suffix = f"{fecha_str}_{hora_str}"

                buffer, filename, export_success, export_error = export_preprocessed_report(
                    df_procesado,
                    stats,
                    fecha_suffix
                )

                if export_success:
                    st.download_button(
                        label="📥 Descargar Reporte Procesado",
                        data=buffer,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width='stretch'
                    )

                    st.success(f"""
                    ✅ **Archivo listo para descarga**: `{filename}`

                    **Siguiente paso**:
                    1. Descarga este archivo
                    2. Cambia al modo "📊 Analizar Inventarios"
                    3. Sube este archivo junto con reportes de otras fechas para análisis temporal
                    """)
                else:
                    st.error(f"❌ Error al generar archivo: {export_error}")

            else:
                st.error(f"❌ Error al procesar archivo: {error}")
                st.info("""
                **Posibles causas:**
                - El archivo no tiene las columnas esperadas
                - La hoja seleccionada no existe
                - El formato de datos no es el correcto

                **Columnas requeridas:**
                - Código de artículo (o similar)
                - Nombre del producto
                - Almacén
                - Id de pallet
                - Inventario físico
                """)

    # ========== MODO 3: CONSOLIDAR EXCEL → BASE DE DATOS ==========
    elif modo == "🗄️ Consolidar Excel → Base de Datos":
        st.subheader("🗄️ Consolidar Múltiples Excel en Base de Datos")
        st.info("""
        **Este módulo consolida múltiples archivos Excel históricos en un solo archivo .db**

        **Proceso:**
        1. Sube todos los archivos Excel que deseas consolidar (100+)
        2. Selecciona el número de hoja donde están los datos (por defecto: **Hoja 2** = "Inventario Completo (Actual)")
        3. El sistema extrae automáticamente:
           - ✅ Datos de la hoja seleccionada
           - ✅ Fecha del nombre del archivo (formato: reporte_all_YYYYMMDD)
           - ✅ Solo registros con inventario negativo
        4. Genera un archivo .db consolidado descargable
        5. Puedes agregar más archivos Excel más tarde usando el modo "💾 Analizar desde Base de Datos"
        
        **Nota:** Si tus datos están en una hoja diferente, cambia el "Número de hoja a procesar" abajo.
        """)

        # Upload de archivos Excel
        excel_files = st.file_uploader(
            "📁 Subir archivos Excel para consolidar",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            help="Selecciona todos los archivos Excel históricos que deseas consolidar",
            key="consolidate_uploader"
        )

        # Configuración
        col1, col2 = st.columns(2)
        with col1:
            sheet_number = st.number_input(
                "📋 Número de hoja a procesar",
                min_value=1,
                max_value=10,
                value=2,
                help="La hoja del Excel donde están los datos (por defecto: 2 = 'Inventario Completo (Actual)')"
            )
            # Convertir a índice (restar 1 porque Python usa índices base 0)
            sheet_idx_consolidate = sheet_number - 1

        with col2:
            db_filename = st.text_input(
                "💾 Nombre del archivo .db",
                value=f"inventarios_consolidados_{datetime.now().strftime('%Y%m%d')}.db",
                help="Nombre del archivo de base de datos a generar"
            )

        if excel_files:
            st.markdown("---")
            st.subheader(f"📊 Consolidando {len(excel_files)} archivos")

            # Botón para procesar
            if st.button("🚀 Iniciar Consolidación", type="primary", use_container_width=True):
                progress_placeholder = st.empty()
                log_placeholder = st.empty()
                
                logs = []
                
                def progress_callback(message):
                    logs.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
                    log_placeholder.text('\n'.join(logs[-10:]))  # Mostrar últimas 10 líneas
                
                with st.spinner("Procesando archivos..."):
                    buffer, stats, success, error = convert_excels_to_db(
                        excel_files,
                        sheet_idx_consolidate,
                        progress_callback
                    )
                
                if success and buffer is not None:
                    st.success("✅ Consolidación completada exitosamente!")
                    
                    # Mostrar estadísticas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Archivos", stats['total_archivos'])
                    with col2:
                        st.metric("Procesados", stats['archivos_procesados'], 
                                delta=None if stats['archivos_procesados'] == stats['total_archivos'] else f"-{stats['archivos_error']}")
                    with col3:
                        st.metric("Con Errores", stats['archivos_error'])
                    with col4:
                        st.metric("Total Registros", stats['total_registros'])
                    
                    # Mostrar errores si los hay
                    if stats['errores_detalle']:
                        with st.expander("⚠️ Ver detalles de errores"):
                            for error_msg in stats['errores_detalle']:
                                st.warning(error_msg)
                    
                    st.markdown("---")
                    st.subheader("💾 Descargar Base de Datos Consolidada")
                    
                    # Preparar descarga
                    st.download_button(
                        label="📥 Descargar Archivo .db",
                        data=buffer.getvalue(),
                        file_name=db_filename,
                        mime="application/x-sqlite3",
                        use_container_width=True
                    )
                    
                    st.success(f"""
                    ✅ **Archivo listo para descarga**: `{db_filename}`

                    **Siguiente paso:**
                    1. Descarga este archivo .db
                    2. Cambia al modo "💾 Analizar desde Base de Datos"
                    3. Sube este archivo .db para realizar análisis temporal
                    4. También puedes agregar más archivos Excel a esta base de datos más tarde
                    """)
                else:
                    st.error(f"❌ Error en la consolidación: {error}")

    # ========== MODO 4: ANALIZAR DESDE BASE DE DATOS ==========
    elif modo == "💾 Analizar desde Base de Datos":
        st.subheader("💾 Analizar Inventarios desde Base de Datos")
        st.info("""
        **Este módulo analiza inventarios desde un archivo .db consolidado**

        **Ventajas:**
        - ✅ Carga más rápida que múltiples Excel
        - ✅ Todos los datos históricos en un solo archivo
        - ✅ Mismo análisis que el modo Excel
        - ✅ Puedes agregar más datos Excel a la DB existente
        """)

        # Upload del archivo .db
        db_file = st.file_uploader(
            "📁 Subir archivo .db consolidado",
            type=['db', 'sqlite', 'sqlite3'],
            help="Archivo de base de datos generado en el modo 'Consolidar Excel → Base de Datos'",
            key="db_analyzer_uploader"
        )

        # Opción para agregar más Excel a la DB
        add_more_excel = st.checkbox(
            "➕ Agregar más archivos Excel a esta base de datos",
            help="Permite agregar nuevos archivos Excel al archivo .db existente"
        )

        if add_more_excel and db_file:
            additional_files = st.file_uploader(
                "📁 Archivos Excel adicionales",
                type=['xlsx', 'xls'],
                accept_multiple_files=True,
                help="Archivos Excel nuevos para agregar a la base de datos",
                key="additional_excel_uploader"
            )
            
            if additional_files:
                st.info(f"Se agregarán {len(additional_files)} archivos adicionales a la base de datos")

        # Sidebar para configuración
        with st.sidebar:
            st.header("⚙️ Configuración")
            
            # Configuraciones (igual que el modo Excel)
            top_n = st.slider("🔝 Top N para análisis", 5, 50, 10)
            
            # Filtros
            st.subheader("🔍 Filtros")
            filter_almacen = st.selectbox("Almacén", ["Todos"] +
                (list(st.session_state.get('analisis', pd.DataFrame()).get('Almacen', pd.Series()).unique())
                 if 'analisis' in st.session_state else []))

            filter_severidad = st.selectbox("Severidad", ["Todas", "Crítico", "Alto", "Medio", "Bajo"])
            filter_estado = st.selectbox("Estado", ["Todos", "Activo", "Resuelto"])

            # Botón de análisis
            analyze_button_db = st.button("🚀 Ejecutar Análisis desde DB", type="primary", use_container_width=True)

        # Contenido principal
        if analyze_button_db and db_file:
            try:
                # Leer contenido del archivo .db
                db_content = db_file.read()
                
                # Leer datos desde la base de datos
                with st.spinner("Leyendo base de datos..."):
                    df_total, success, error = read_db_file(db_content)
                
                if not success or df_total is None:
                    st.error(f"❌ Error al leer la base de datos: {error}")
                else:
                    # Normalizar datos (usar la función existente)
                    analyzer = InventoryAnalyzerWeb()
                    progress_placeholder = st.empty()
                    st.session_state.progress_placeholder = progress_placeholder
                    
                    df_total_normalized = analyzer.normalize_data(df_total)
                    
                    # Si hay archivos adicionales, procesarlos y agregarlos
                    if add_more_excel and 'additional_files' in locals() and additional_files:
                        with st.spinner("Procesando archivos adicionales..."):
                            df_additional = analyzer.process_uploaded_files(additional_files)
                            df_total_normalized = pd.concat([df_total_normalized, df_additional], ignore_index=True)
                            st.success(f"✅ Agregados {len(additional_files)} archivos Excel adicionales")
                    
                    # Continuar con el análisis normal
                    with st.spinner("Analizando datos..."):
                        analisis = analyzer.analyze_pallets(df_total_normalized)
                        super_analisis = analyzer.create_super_analysis(df_total_normalized)
                        reincidencias = analyzer.detect_recurrences(df_total_normalized)

                        # Guardar en session state
                        st.session_state.df_total = df_total_normalized
                        st.session_state.analisis = analisis
                        st.session_state.super_analisis = super_analisis
                        st.session_state.reincidencias = reincidencias

                    progress_placeholder.success("✅ Análisis completado desde base de datos!")

            except Exception as e:
                st.error(f"❌ Error en el análisis: {e}")
                import traceback
                st.error(traceback.format_exc())

        # Mostrar resultados si existen datos (reutilizar la lógica del modo Excel)
        if 'analisis' in st.session_state:
            # Aquí se reutiliza toda la lógica de visualización del modo Excel
            # Inyectar JavaScript GLOBAL para scroll estable (igual que en modo Excel)
            components.html("""
                <script>
                (function() {
                    function saveScrollPosition() {
                        const scrollPos = window.parent.scrollY || window.parent.pageYOffset;
                        sessionStorage.setItem('streamlit_scroll_pos', scrollPos);
                    }
                    
                    function restoreScrollPosition() {
                        const savedPos = sessionStorage.getItem('streamlit_scroll_pos');
                        if (savedPos && savedPos !== '0') {
                            requestAnimationFrame(function() {
                                window.parent.scrollTo({
                                    top: parseInt(savedPos),
                                    behavior: 'auto'
                                });
                            });
                        }
                    }
                    
                    let scrollTimeout;
                    window.parent.addEventListener('scroll', function() {
                        clearTimeout(scrollTimeout);
                        scrollTimeout = setTimeout(saveScrollPosition, 50);
                    }, { passive: true });
                    
                    restoreScrollPosition();
                    setTimeout(restoreScrollPosition, 100);
                    setTimeout(restoreScrollPosition, 300);
                    setTimeout(restoreScrollPosition, 500);
                })();
                </script>
            """, height=0)
            
            # Usar las mismas visualizaciones que el modo Excel
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
            
            # Nota sobre la fuente de datos
            st.success(f"""
            🗄️ **Fuente de datos**: Base de datos consolidada  
            📅 **Registros totales**: {len(df_total):,}  
            🗓️ **Rango de fechas**: {df_total['Fecha_Reporte'].min().strftime('%Y-%m-%d')} a {df_total['Fecha_Reporte'].max().strftime('%Y-%m-%d')}
            """)
            
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
                st.dataframe(styled_analisis, width='stretch', height=400)
            
            with tab2:
                st.subheader("Reincidencias Detectadas")
                st.dataframe(reincidencias, width='stretch', height=400)
            
            with tab3:
                st.subheader("Súper Análisis - Evolución Temporal por Pallet")
                st.info("💡 Esta vista muestra la evolución temporal de cada pallet. Usa los filtros para explorar los datos.")
            
            with tab4:
                st.subheader("Datos Crudos Procesados")
                st.dataframe(df_total, width='stretch', height=400)
            
            # Descarga de reporte
            st.subheader("💾 Descargar Reporte")
            col1, col2 = st.columns(2)
            
            with col1:
                excel_buffer = generate_excel_report(analisis, super_analisis, reincidencias, df_total, top_n)
                st.download_button(
                    label="📊 Descargar Reporte Excel",
                    data=excel_buffer,
                    file_name=f"Reporte_Inventarios_DB_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                csv_data = analisis.to_csv(index=False)
                st.download_button(
                    label="📄 Descargar CSV",
                    data=csv_data,
                    file_name=f"Analisis_DB_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )

    # ========== MODO 2: ANÁLISIS DE INVENTARIOS (ORIGINAL) ==========
    else:
        # Sidebar para configuración
        with st.sidebar:
            st.header("⚙️ Configuración")

            # Upload de archivos
            uploaded_files = st.file_uploader(
                "📁 Subir archivos Excel o Base de Datos (.db)",
                type=['xlsx', 'xls', 'db', 'sqlite', 'sqlite3'],
                accept_multiple_files=True,
                help="Selecciona archivos Excel o un archivo .db consolidado"
            )

            # Configuraciones
            top_n = st.slider("🔝 Top N para análisis", 5, 50, 10)
            sheet_number_analyze = st.number_input(
                "📋 Número de hoja Excel", 
                1, 10, 2,
                help="La hoja del Excel donde están los datos (2 = 'Inventario Completo (Actual)')"
            )
            # Convertir a índice
            sheet_index = sheet_number_analyze - 1

            # Filtros
            st.subheader("🔍 Filtros")
            filter_almacen = st.selectbox("Almacén", ["Todos"] +
                (list(st.session_state.get('analisis', pd.DataFrame()).get('Almacen', pd.Series()).unique())
                 if 'analisis' in st.session_state else []))

            filter_severidad = st.selectbox("Severidad", ["Todas", "Crítico", "Alto", "Medio", "Bajo"])
            filter_estado = st.selectbox("Estado", ["Todos", "Activo", "Resuelto"])

            # Botón de análisis
            analyze_button = st.button("🚀 Ejecutar Análisis", type="primary", width='stretch')

        # Contenido principal
        if analyze_button and uploaded_files:
            try:
                # Inicializar analizador
                analyzer = InventoryAnalyzerWeb()

                # Placeholder para progreso
                progress_placeholder = st.empty()
                st.session_state.progress_placeholder = progress_placeholder

                with st.spinner("Procesando archivos..."):
                    # Separar archivos .db de archivos Excel
                    db_files = [f for f in uploaded_files if f.name.endswith(('.db', '.sqlite', '.sqlite3'))]
                    excel_files = [f for f in uploaded_files if f.name.endswith(('.xlsx', '.xls'))]
                    
                    all_dataframes = []
                    
                    # Procesar archivos .db si hay
                    if db_files:
                        for db_file in db_files:
                            analyzer.log(f"Leyendo base de datos: {db_file.name}")
                            db_content = db_file.read()
                            df_from_db, success, error = read_db_file(db_content)
                            
                            if success and df_from_db is not None:
                                all_dataframes.append(df_from_db)
                                analyzer.log(f"✅ {db_file.name}: {len(df_from_db)} registros")
                            else:
                                analyzer.log(f"❌ Error en {db_file.name}: {error}")
                    
                    # Procesar archivos Excel si hay
                    if excel_files:
                        df_from_excel = analyzer.process_uploaded_files(excel_files)
                        all_dataframes.append(df_from_excel)
                    
                    # Combinar todos los datos
                    if all_dataframes:
                        df_total = pd.concat(all_dataframes, ignore_index=True)
                    else:
                        raise ValueError("No se pudieron procesar archivos válidos")
                    
                    # Normalizar datos
                    df_total = analyzer.normalize_data(df_total)
                    
                    # Continuar con análisis
                    analisis = analyzer.analyze_pallets(df_total)
                    super_analisis = analyzer.create_super_analysis(df_total)
                    reincidencias = analyzer.detect_recurrences(df_total)

                    # Guardar en session state
                    st.session_state.df_total = df_total
                    st.session_state.analisis = analisis
                    st.session_state.super_analisis = super_analisis
                    st.session_state.reincidencias = reincidencias

                # Mensaje de éxito personalizado
                if db_files and excel_files:
                    progress_placeholder.success(f"✅ Análisis completado: {len(db_files)} archivo(s) .db + {len(excel_files)} archivo(s) Excel")
                elif db_files:
                    progress_placeholder.success(f"✅ Análisis completado desde {len(db_files)} archivo(s) .db")
                else:
                    progress_placeholder.success("✅ Análisis completado!")

            except Exception as e:
                st.error(f"❌ Error en el análisis: {e}")
                import traceback
                st.error(traceback.format_exc())
                return

        # Mostrar resultados si existen datos
        if 'analisis' in st.session_state:
            # Inyectar JavaScript GLOBAL para scroll estable (se carga una sola vez al inicio)
            components.html("""
                <script>
                (function() {
                    // Función para guardar posición del scroll
                    function saveScrollPosition() {
                        const scrollPos = window.parent.scrollY || window.parent.pageYOffset;
                        sessionStorage.setItem('streamlit_scroll_pos', scrollPos);
                    }
                    
                    // Función para restaurar posición del scroll
                    function restoreScrollPosition() {
                        const savedPos = sessionStorage.getItem('streamlit_scroll_pos');
                        if (savedPos && savedPos !== '0') {
                            requestAnimationFrame(function() {
                                window.parent.scrollTo({
                                    top: parseInt(savedPos),
                                    behavior: 'auto'
                                });
                            });
                        }
                    }
                    
                    // Guardar posición constantemente al hacer scroll
                    let scrollTimeout;
                    window.parent.addEventListener('scroll', function() {
                        clearTimeout(scrollTimeout);
                        scrollTimeout = setTimeout(saveScrollPosition, 50);
                    }, { passive: true });
                    
                    // Restaurar posición inmediatamente al cargar
                    restoreScrollPosition();
                    
                    // También restaurar después de un pequeño delay (para asegurar que DOM esté listo)
                    setTimeout(restoreScrollPosition, 100);
                    setTimeout(restoreScrollPosition, 300);
                    setTimeout(restoreScrollPosition, 500);
                    
                    // Detectar cambios en elementos interactivos y guardar posición
                    function attachListeners() {
                        // Checkboxes
                        const checkboxes = window.parent.document.querySelectorAll('input[type="checkbox"]');
                        checkboxes.forEach(function(cb) {
                            if (!cb.hasScrollListener) {
                                cb.addEventListener('change', saveScrollPosition);
                                cb.hasScrollListener = true;
                            }
                        });
                        
                        // Selectboxes
                        const selects = window.parent.document.querySelectorAll('select');
                        selects.forEach(function(sel) {
                            if (!sel.hasScrollListener) {
                                sel.addEventListener('change', saveScrollPosition);
                                sel.hasScrollListener = true;
                            }
                        });
                        
                        // Input fields
                        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
                        inputs.forEach(function(inp) {
                            if (!inp.hasScrollListener) {
                                inp.addEventListener('focus', saveScrollPosition);
                                inp.hasScrollListener = true;
                            }
                        });
                    }
                    
                    // Adjuntar listeners inmediatamente
                    attachListeners();
                    
                    // Re-adjuntar listeners después de cambios en el DOM
                    setTimeout(attachListeners, 500);
                    setTimeout(attachListeners, 1000);
                    setTimeout(attachListeners, 2000);
                    
                    // Observer para detectar cambios en el DOM y re-adjuntar listeners
                    const observer = new MutationObserver(function(mutations) {
                        attachListeners();
                    });
                    
                    observer.observe(window.parent.document.body, {
                        childList: true,
                        subtree: true
                    });
                })();
                </script>
            """, height=0)
            
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
                st.dataframe(styled_analisis, width='stretch', height=400)
            
            with tab2:
                st.subheader("Reincidencias Detectadas")
                st.dataframe(reincidencias, width='stretch', height=400)
            
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
                    st.dataframe(styled_super, width='stretch', height=500)
                    
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
                st.dataframe(df_total, width='stretch', height=400)
            
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
            
            # Nota informativa sobre reportes
            st.markdown("---")
            st.info("""
            💡 **Tip de Reportes:** 
            - Utiliza los botones de descarga de Excel o CSV arriba para obtener reportes completos y formateados
            - El reporte Excel incluye múltiples hojas con análisis detallados, incluyendo la hoja "Top N" con evolución temporal
            - Los archivos descargados son ideales para impresión y análisis offline
            """)

        if not uploaded_files:
            # Instrucciones de uso
            st.info("""
            👋 **Bienvenido al Analizador de Inventarios Negativos v6.3 Database Edition**
            
            Para comenzar:
            1. 📁 Sube archivos Excel **o** un archivo .db en la barra lateral
            2. ⚙️ Configura los parámetros de análisis
            3. 🚀 Haz clic en "Ejecutar Análisis"
            4. 📊 Explora los resultados y descarga reportes
            
            **Características:**
            - ✅ Análisis de severidad por magnitud
            - ✅ Detección de reincidencias
            - ✅ Visualizaciones interactivas
            - ✅ Filtros avanzados con scroll estable
            - ✅ Reportes descargables listos para imprimir
            - ✅ Interfaz responsiva y optimizada
            
            **Nuevo en v6.3:**
            - 🗄️ Acepta archivos Excel **Y** archivos .db
            - 💾 Puedes combinar archivos .db + Excel en el mismo análisis
            - 🗄️ Consolida múltiples Excel en base de datos .db
            - ➕ Agregar nuevos Excel a .db existente
            - 📅 Extracción automática de fechas del nombre de archivo
            - 🚀 Preparado para integración con ERP del área de sistemas
            """)

if __name__ == "__main__":
    main()
