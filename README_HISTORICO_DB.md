# 🗄️ Histórico DB - Análisis de Inventario Negativo

## 📋 Tabla de Contenido

1. [Introducción](#-introducción)
2. [Arquitectura de Conexión a Base de Datos](#-arquitectura-de-conexión-a-base-de-datos) ⭐ **IMPORTANTE**
3. [Configuración y Requisitos](#-configuración-y-requisitos)
4. [Estructura de la Base de Datos](#-estructura-de-la-base-de-datos)
5. [Funcionalidades Principales](#-funcionalidades-principales)
6. [Sistema de Optimización de Performance](#-sistema-de-optimización-de-performance)
7. [Filtros y Segmentación](#-filtros-y-segmentación)
8. [Visualizaciones y Análisis](#-visualizaciones-y-análisis)
9. [Exportación de Datos](#-exportación-de-datos)
10. [Troubleshooting](#-troubleshooting)

---

## 📖 Introducción

El módulo **"🗄️ Histórico DB"** es una herramienta de análisis avanzado que permite visualizar y analizar datos históricos de inventario negativo almacenados en una base de datos SQLite hospedada en un **repositorio privado de GitHub**.

### Características Clave

- ✅ **Conexión automática a GitHub** (repositorio privado)
- ✅ **Autenticación segura** con GitHub Personal Access Token
- ✅ **Análisis temporal** con tabla pivote dinámica
- ✅ **Métricas de costos** (CostStock)
- ✅ **Filtros avanzados** (zona, almacén, fecha, productos)
- ✅ **Visualizaciones interactivas** (evolución, distribución, heatmaps)
- ✅ **Exportación completa** a CSV
- ✅ **Performance optimizado** (sistema de 3 niveles)

---

## 🔐 Arquitectura de Conexión a Base de Datos

### ⭐ **IMPORTANTE: Cómo Nuestra App Lee el `.db` desde GitHub**

Esta es la parte más crítica del sistema. La app **NO descarga** el archivo directamente como un archivo estático, sino que utiliza la **GitHub Contents API** para acceder programáticamente a repositorios privados.

### 📊 Flujo Completo de Conexión

```
┌─────────────────────────────────────────────────────────────────┐
│                    INICIO DE LA APP                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Streamlit carga secrets.toml      │
        │  Lee: GITHUB_TOKEN                 │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │  Función: download_and_connect_db()│
        └────────────┬───────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────────┐
   │  1. Construir URL de GitHub Contents API    │
   │     https://api.github.com/repos/           │
   │     Sinsapiar1/alsina-negativos-db/         │
   │     contents/negativos_inventario.db        │
   └──────────────────┬──────────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────────┐
   │  2. Hacer petición HTTP GET con headers:    │
   │     Authorization: token GITHUB_TOKEN       │
   │     Accept: application/vnd.github.v3.raw   │
   └──────────────────┬──────────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────────┐
   │  3. GitHub valida el token                  │
   │     ✅ Token válido → Devuelve contenido    │
   │     ❌ Token inválido → Error 404/403       │
   └──────────────────┬──────────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────────┐
   │  4. Descargar archivo binario (.db)         │
   │     Guardar en archivo temporal             │
   │     /tmp/negativos_inventario_XXXXX.db      │
   └──────────────────┬──────────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────────┐
   │  5. Conectar SQLite a archivo temporal      │
   │     conn = sqlite3.connect(temp_path)       │
   └──────────────────┬──────────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────────┐
   │  6. Leer datos con pandas                   │
   │     df = pd.read_sql_query(query, conn)     │
   └──────────────────┬──────────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────────┐
   │  7. Caché de datos en memoria               │
   │     @st.cache_data(ttl=3600)                │
   │     Válido por 1 hora                       │
   └──────────────────┬──────────────────────────┘
                      │
                      ▼
        ┌────────────────────────────────────┐
        │  DATOS DISPONIBLES PARA ANÁLISIS   │
        └────────────────────────────────────┘
```

### 💻 Código Detallado de Conexión

#### **Función: `download_and_connect_db()`**

```python
def download_and_connect_db():
    """
    Descarga la base de datos desde GitHub (repositorio privado)
    y retorna la ruta del archivo temporal.
    
    IMPORTANTE: Usa GitHub Contents API con autenticación PAT
    NO usa URLs raw.githubusercontent.com (no funciona con privados)
    """
    try:
        # 1. CONFIGURACIÓN DE GITHUB
        GITHUB_OWNER = "Sinsapiar1"
        GITHUB_REPO = "alsina-negativos-db"
        DB_FILENAME = "negativos_inventario.db"
        
        # 2. OBTENER TOKEN DE STREAMLIT SECRETS
        if not hasattr(st, 'secrets') or 'GITHUB_TOKEN' not in st.secrets:
            return None, False, "Token de GitHub no encontrado"
        
        github_token = st.secrets["GITHUB_TOKEN"]
        
        # 3. CONSTRUIR URL DE GITHUB CONTENTS API
        # CRÍTICO: NO usar raw.githubusercontent.com
        api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{DB_FILENAME}"
        
        # 4. CONFIGURAR HEADERS DE AUTENTICACIÓN
        headers = {
            "Authorization": f"token {github_token}",
            # Accept raw: devuelve el contenido binario directo
            "Accept": "application/vnd.github.v3.raw"
        }
        
        # 5. HACER PETICIÓN HTTP
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()  # Lanza excepción si error
        
        # 6. GUARDAR EN ARCHIVO TEMPORAL
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix='.db',
            delete=False,
            prefix='negativos_inventario_'
        ) as tmp_file:
            tmp_file.write(response.content)
            temp_db_path = tmp_file.name
        
        # 7. RETORNAR RUTA DEL ARCHIVO
        return temp_db_path, True, None
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None, False, "Archivo no encontrado o token sin permisos"
        elif e.response.status_code == 403:
            return None, False, "Token sin permisos o rate limit excedido"
        else:
            return None, False, f"Error HTTP: {e}"
    
    except Exception as e:
        return None, False, f"Error general: {str(e)}"
```

#### **Función: `load_historico_data()`**

```python
@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_historico_data(db_path):
    """
    Carga datos desde SQLite a pandas DataFrame.
    
    OPTIMIZACIONES:
    - Lee TODA la tabla inventario (histórico completo)
    - Convierte tipos de datos correctamente
    - Maneja NaN en CostStock sin rellenar con 0
    - Cache en memoria para evitar lecturas repetidas
    """
    try:
        # 1. CONECTAR A SQLITE
        conn = sqlite3.connect(db_path)
        
        # 2. QUERY SQL
        query = """
        SELECT 
            fecha,
            CompanyId,
            InventLocationId,
            ProductId,
            ProductName_es,
            LabelId,
            Stock,
            CostStock
        FROM inventario
        ORDER BY fecha DESC, CompanyId, InventLocationId
        """
        
        # 3. LEER CON PANDAS
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # 4. CONVERTIR TIPOS
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0)
        # NO rellenar CostStock con 0, mantener NaN para detectar problemas
        df['CostStock'] = pd.to_numeric(df['CostStock'], errors='coerce')
        
        return df, True, None
        
    except Exception as e:
        return None, False, f"Error al cargar datos: {str(e)}"
```

### 🔑 ¿Por Qué NO Usar `raw.githubusercontent.com`?

| Método | URL | Funciona con Privados | Autenticación |
|--------|-----|----------------------|---------------|
| ❌ **Raw URL** | `raw.githubusercontent.com/owner/repo/main/file.db` | **NO** | No soportada |
| ✅ **Contents API** | `api.github.com/repos/owner/repo/contents/file.db` | **SÍ** | Token en headers |

**Conclusión:** Para repositorios privados, **SIEMPRE** usar GitHub Contents API.

---

## ⚙️ Configuración y Requisitos

### 1. Crear GitHub Personal Access Token (PAT)

1. Ir a GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click en **"Generate new token (classic)"**
3. Configurar:
   - **Note:** `Streamlit Alsina Inventory Access`
   - **Expiration:** `No expiration` (o según política)
   - **Scopes:** Marcar `repo` (acceso completo a repositorios privados)
4. Click **"Generate token"**
5. **COPIAR TOKEN** (solo se muestra una vez)

### 2. Configurar Token en Streamlit Cloud

#### **Opción A: Streamlit Cloud (Producción)**

1. Ir a tu app en [share.streamlit.io](https://share.streamlit.io)
2. Click en **"⚙️ Settings"** → **"Secrets"**
3. Agregar en el editor:

```toml
GITHUB_TOKEN = "ghp_TU_TOKEN_AQUI_xxxxxxxxxxxxx"
```

4. Click **"Save"**
5. App se reinicia automáticamente

#### **Opción B: Local (Desarrollo)**

Crear archivo `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml
GITHUB_TOKEN = "ghp_TU_TOKEN_AQUI_xxxxxxxxxxxxx"
```

⚠️ **IMPORTANTE:** Agregar `.streamlit/` a `.gitignore`

### 3. Dependencias Python

Agregar a `requirements.txt`:

```txt
streamlit>=1.32.0
pandas>=2.0.0
sqlite3  # (incluido en Python estándar)
requests>=2.31.0
plotly>=5.15.0
```

---

## 📊 Estructura de la Base de Datos

### Tabla: `inventario`

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `id` | INTEGER | Primary Key autoincremental | 1, 2, 3... |
| `fecha` | TEXT | Fecha del registro (YYYY-MM-DD) | `2025-11-14` |
| `CompanyId` | TEXT | Zona/Compañía | `co0`, `es0`, `ae1` |
| `InventLocationId` | TEXT | Código de almacén | `11D`, `25D`, `63D` |
| `ProductId` | TEXT | Código de producto | `44113`, `87947` |
| `ProductName_es` | TEXT | Nombre del producto | `TORNILLO...` |
| `LabelId` | TEXT | ID de pallet | `22000746658` |
| `Stock` | INTEGER | Unidades en stock (negativo = faltante) | `-1230`, `0`, `150` |
| `CostStock` | REAL | Costo asociado al stock | `-15000.50` |
| `created_at` | TIMESTAMP | Timestamp de inserción | `2025-11-14 08:30:00` |

### Lógica de Datos

#### **Stock Negativo**
```
Stock < 0  →  Inventario negativo (faltante)
Stock = 0  →  Sin stock
Stock > 0  →  Inventario disponible
```

#### **CostStock**
```
CostStock < 0  →  Costo asociado a inventario negativo
CostStock = 0  →  Sin costo o costo cero
CostStock = NaN →  Dato no disponible
```

#### **Filtro Maestro de la App**

La app filtra registros con:
```python
(Stock < 0) OR (Stock = 0 AND CostStock < 0)
```

**Incluye:**
- ✅ Todos los `Stock < 0` (con o sin costo)
- ✅ `Stock = 0` con `CostStock < 0` (casos especiales)

**Excluye:**
- ❌ `Stock >= 0` (inventario positivo o cero sin costo)

---

## 🚀 Funcionalidades Principales

### 1. Panel de Control Superior

**Métricas del Último Día Disponible:**

```
┌────────────────────────────────────────────────────────────────┐
│  📅 Análisis del Último Día Disponible: 14 de Noviembre 2025  │
├────────────────────────────────────────────────────────────────┤
│  📋 Registros     │  📅 Días          │  💰 Costo Total        │
│  18,990           │  25               │  $219,416,444          │
├────────────────────────────────────────────────────────────────┤
│  🔢 Productos     │                                            │
│  2,507            │                                            │
└────────────────────────────────────────────────────────────────┘
```

**Cálculos:**
- **Registros:** Total de filas en el último día
- **Días en Histórico:** Días únicos en la base de datos
- **Costo Total Negativo:** `SUM(ABS(CostStock))` donde `CostStock < 0`
- **Productos Únicos:** `COUNT(DISTINCT ProductId)`

### 2. Resumen de Costos por Zona

Tabla agregada con métricas por `CompanyId`:

| Zona | Costo Total ($) | Unidades Negativas | Productos Únicos | Almacenes Únicos |
|------|-----------------|-------------------|------------------|------------------|
| co0 | $181,689,062 | 34,004 | 1,323 | 110 |
| es0 | $9,572,633 | 351,745 | 678 | 1,323 |

**Visualización:**
- Gráfico de barras horizontal
- Ordenado de mayor a menor costo
- Colores por zona

### 3. Tabla Pivote de Comportamiento Diario

**Estructura:**

```
Zona | Código | Nombre | ID_Pallet | Almacén | 2025-10-21 | 2025-10-22 | ... | 2025-11-14
-----|--------|--------|-----------|---------|------------|------------|-----|------------
co0  | 26000  | CHATAR.| SIN_PALLET| 63D     | -35874     | -35874     | ... | -32738
ae1  | 54486  | ADAPTA.| 22000670335| 22D    | -7850      | -7850      | ... | -15190
```

**Características:**
- Cada fila = Producto + Pallet único
- Columnas dinámicas = Fechas disponibles
- Valores = Stock del día (negativos en rojo)
- Celdas vacías = Sin movimiento ese día

---

## ⚡ Sistema de Optimización de Performance

### Sistema de 3 Niveles

La app adapta el renderizado según la cantidad de filas:

#### **NIVEL 1: ≤ 2,000 filas** ✅

```python
# Estilo COMPLETO con gradiente de colores
- Verde claro:  -1 a -10 unidades
- Amarillo:     -11 a -50 unidades
- Naranja:      -51 a -100 unidades
- Rojo:         < -100 unidades

# Características
✅ Colores por gravedad
✅ Filtros dinámicos activos
✅ Performance óptimo
```

#### **NIVEL 2: 2,001 - 5,000 filas** 🔶

```python
# Estilo SIMPLIFICADO (solo celdas vacías)
- Gris claro: Celdas sin datos

# Características
🔶 Solo colorea celdas vacías
✅ Filtros dinámicos activos
✅ Performance bueno
ℹ️ Mensaje informativo al usuario
```

#### **NIVEL 3: > 5,000 filas (incluye "Todas")** ⚠️

```python
# SIN estilos (DataFrame crudo)

# Características
⚠️ Sin colores
❌ NO filtros dinámicos (limitación Streamlit)
🚫 NO se cae la app
⚠️ Advertencia clara
💡 Sugerencia: "Selecciona máximo 5000 filas"
```

### ¿Por Qué Este Límite?

**Limitación de Streamlit:**
- `pandas.DataFrame.style.applymap()` con > 5,000 filas causa `StreamlitAPIException`
- La librería no está optimizada para grandes volúmenes con estilos
- Trade-off necesario: **Estabilidad > Formato**

---

## 🔍 Filtros y Segmentación

### Filtros Disponibles

#### 1. **Solo Negativos** (Checkbox)
```python
if solo_negativos:
    df = df[(df['Stock'] < 0) | 
            ((df['Stock'] == 0) & (df['CostStock'] < 0))]
```

#### 2. **Zona/Compañía** (Multiselect)
- Selección múltiple de `CompanyId`
- Default: Todas seleccionadas
- Relacionado con filtro de almacenes

#### 3. **Almacén** (Multiselect)
- Filtro dinámico según zonas seleccionadas
- Actualiza opciones automáticamente
- Default: Todos los disponibles

#### 4. **Búsqueda de Código** (Text Input)
- Busca en `ProductId` (case-insensitive)
- Filtro parcial (contiene)

#### 5. **Rango de Fechas** (Date Input)
- Desde: Fecha mínima
- Hasta: Fecha máxima
- Default: Todo el rango disponible

#### 6. **Filtros Avanzados** (Expander)

##### **Excluir Códigos**
```python
# Ejemplo: "26000, 54486, 44113"
codigos_excluir = ["26000", "54486", "44113"]
df = df[~df['ProductId'].isin(codigos_excluir)]
```

##### **Solo Incluir Códigos**
```python
# Ejemplo: "87947, 67057"
codigos_incluir = ["87947", "67057"]
df = df[df['ProductId'].isin(codigos_incluir)]
```

##### **Solo Activos en Último Día**
```python
# Filtra productos con movimiento en última fecha
ultima_fecha = df['fecha'].max()
df_ultimo = df[df['fecha'] == ultima_fecha]
productos_activos = df_ultimo['ProductId'].unique()
df = df[df['ProductId'].isin(productos_activos)]
```

---

## 📈 Visualizaciones y Análisis

### 1. Evolución Total Stock Negativo

**Gráfico de Línea Temporal**

```python
# Datos: Suma de stock negativo por fecha
evolution_data = df_filtered.groupby("fecha").agg({
    "Stock": "sum"
}).reset_index()
```

**Interpretación:**
- Tendencia ascendente → Problema empeorando
- Tendencia descendente → Mejora en inventario
- Picos → Días con mayor faltante

### 2. Distribución por Zona (Pie Chart)

**Solo Último Día**

```python
# Datos: Stock negativo por CompanyId
zona_data = df_ultimo[df_ultimo['Stock'] < 0].groupby('CompanyId')['Stock'].sum().abs()
```

**Interpretación:**
- % de cada zona en el total
- Identifica zonas más afectadas

### 3. Top 10 Zonas por Costo

**Gráfico de Barras Horizontal**

```python
# Datos: Costo por zona (último día)
costos_por_zona = df_ultimo[df_ultimo['CostStock'] < 0].groupby('CompanyId')['CostStock'].sum().abs()
```

**Interpretación:**
- Impacto económico por zona
- Priorización de acciones correctivas

### 4. Top 10 Almacenes por Stock Negativo

**Gráfico de Barras Horizontal**

```python
# Datos: Stock negativo por almacén (último día)
almacenes_stock = df_ultimo.groupby('InventLocationId')['Stock'].sum().abs()
```

**Interpretación:**
- Almacenes con mayor faltante
- Foco de auditorías físicas

### 5. Mapa de Calor - Evolución por Pallet

**Heatmap Interactivo**

```python
# Matriz: Pallets × Fechas
# Colores: Escala RdBu_r (rojo = muy negativo)
```

**Controles:**
- Selector de cantidad de pallets (10, 20, 30, 50, 100)
- Hover para ver valores exactos

**Interpretación:**
- Patrones temporales
- Productos con negativos persistentes
- Identificación de casos críticos

---

## 📥 Exportación de Datos

### CSV Completo

**Botón: "📥 Descargar Histórico DB Filtrado COMPLETO (CSV)"**

```python
# IMPORTANTE: Exporta TODOS los registros filtrados
# No respeta el límite de visualización (max_rows_display)

csv_data = historico_pivot_completo.to_csv(index=False)
```

**Contenido del CSV:**

| Columna | Descripción |
|---------|-------------|
| Zona | CompanyId |
| Codigo | ProductId |
| Nombre | ProductName_es |
| ID_Pallet | LabelId (o "SIN_PALLET") |
| Almacen | InventLocationId |
| 2025-10-21 | Stock del día |
| 2025-10-22 | Stock del día |
| ... | ... |
| 2025-11-14 | Stock del día |

**Nombre del archivo:**
```
Historico_DB_Filtrado_YYYYMMDD_HHMM.csv
```

**Ejemplo:**
```
Historico_DB_Filtrado_20251114_1530.csv
```

---

## 🛠️ Troubleshooting

### Error: "404 Client Error: Not Found"

**Causa:** Token sin permisos o URL incorrecta

**Solución:**
1. Verificar que el token tenga scope `repo`
2. Verificar que el repositorio sea `Sinsapiar1/alsina-negativos-db`
3. Verificar que el archivo se llame `negativos_inventario.db`

### Error: "403 Forbidden"

**Causa 1:** Rate limit excedido  
**Solución:** Esperar 1 hora o usar otro token

**Causa 2:** Token expirado  
**Solución:** Generar nuevo token en GitHub

### Error: "Token de GitHub no encontrado"

**Causa:** Secrets no configurado

**Solución:**
1. Ir a Streamlit Cloud → Settings → Secrets
2. Agregar: `GITHUB_TOKEN = "ghp_..."`
3. Guardar y reiniciar app

### Tabla Muestra "SIN formato condicional"

**Causa:** Más de 5,000 filas seleccionadas

**Solución:**
- Seleccionar máximo 5000 filas en el dropdown
- O usar filtros para reducir cantidad de datos

### No Veo Filtros Dinámicos en la Tabla

**Causa:** Más de 5,000 filas (limitación Streamlit)

**Solución:**
- Reducir cantidad de filas con dropdown
- Usar filtros avanzados (zona, almacén, fechas)

### Datos Desactualizados

**Causa:** Caché activo (TTL = 1 hora)

**Solución:**
1. Esperar 1 hora para actualización automática
2. O reiniciar la app en Streamlit Cloud
3. O modificar código para reducir TTL

---

## 📚 Referencias Técnicas

### GitHub Contents API

- **Documentación:** [GitHub REST API - Contents](https://docs.github.com/en/rest/repos/contents)
- **Endpoint:** `GET /repos/{owner}/{repo}/contents/{path}`
- **Header Accept:** `application/vnd.github.v3.raw` (contenido binario)

### Streamlit Secrets

- **Documentación:** [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

### Pandas DataFrame Styling

- **Documentación:** [Pandas Styling](https://pandas.pydata.org/docs/user_guide/style.html)
- **Limitación:** `.style.applymap()` no escala bien > 5,000 filas

---

## 📄 Licencia

Este proyecto y documentación son propiedad de **Alsina Formwork Solutions**.

**Uso interno exclusivamente.**

---

## 📞 Soporte

Para soporte técnico o consultas:

- **Email:** soporte@alsina.com
- **GitHub Issues:** [Crear issue](https://github.com/Sinsapiar1/inventory-analyzer-web/issues)

---

**Versión:** 1.0  
**Fecha:** 14 de Noviembre de 2025  
**Autor:** Equipo de Desarrollo Alsina
