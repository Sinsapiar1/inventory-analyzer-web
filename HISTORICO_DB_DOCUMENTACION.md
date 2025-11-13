# 📊 Documentación Completa: Histórico DB

## 📑 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Actualización Automática](#actualización-automática)
3. [Configuración Inicial](#configuración-inicial)
4. [Estructura de Datos](#estructura-de-datos)
5. [Funcionalidades](#funcionalidades)
6. [Guía de Uso](#guía-de-uso)
7. [Arquitectura Técnica](#arquitectura-técnica)
8. [Optimización y Performance](#optimización-y-performance)
9. [Solución de Problemas](#solución-de-problemas)
10. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🎯 Descripción General

### ¿Qué es Histórico DB?

**Histórico DB** es un módulo avanzado de análisis de inventario negativo que se conecta directamente a una base de datos SQLite alojada en GitHub. Este módulo permite visualizar, analizar y exportar datos históricos de stock negativo con una perspectiva temporal completa.

### Propósito Principal

- **Análisis Temporal**: Visualizar la evolución del stock negativo día a día
- **Trazabilidad Completa**: Seguimiento de productos específicos a nivel de pallet
- **Análisis por Zona/Almacén**: Identificar patrones geográficos y operacionales
- **Toma de Decisiones**: Datos precisos para acciones correctivas y preventivas
- **Exportación de Datos**: Facilitar análisis externos y reportes personalizados

### Diferencias con otros módulos

| Característica | Histórico DB | Analizar Inventarios |
|----------------|--------------|----------------------|
| **Fuente de datos** | Base de datos SQLite (GitHub) | Archivos Excel locales |
| **Actualización** | Automática (diaria) | Manual (usuario sube archivo) |
| **Alcance temporal** | Histórico completo (23+ días) | Solo datos del archivo actual |
| **Nivel de detalle** | Producto + Pallet + Fecha | Producto + Pallet |
| **Dimensiones** | Zona, Almacén, Costos, Stock | Según estructura del Excel |
| **Visualizaciones** | Evolución temporal, mapas de calor | Análisis de snapshot |

---

## 🔄 Actualización Automática

### Funcionamiento del Sistema

El módulo **Histórico DB** se conecta a un repositorio privado de GitHub que contiene una base de datos SQLite (`negativos_inventario.db`). Esta base de datos se actualiza automáticamente mediante un proceso programado.

#### Flujo de Actualización

```
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: Sistema Interno                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Extracción diaria de datos de inventario           │  │
│  │ • Procesamiento y limpieza de datos                  │  │
│  │ • Identificación de stock negativo                   │  │
│  │ • Cálculo de costos                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 2: GitHub Repository (Privado)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Repo: Sinsapiar1/alsina-negativos-db                │  │
│  │ Archivo: negativos_inventario.db                     │  │
│  │ • Actualización automática (diaria)                 │  │
│  │ • Versionamiento automático (Git)                   │  │
│  │ • Respaldo histórico completo                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 3: Streamlit App                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Usuario abre tab "🗄️ Histórico DB"               │  │
│  │ • App descarga .db desde GitHub (vía API)           │  │
│  │ • Conexión SQLite en memoria temporal               │  │
│  │ • Caché de datos (10 minutos)                       │  │
│  │ • Visualización interactiva                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Frecuencia de Actualización

- **Base de Datos**: Actualización diaria (programada)
- **Caché de Streamlit**: Refresco automático cada 10 minutos
- **Datos Mostrados**: Siempre los más recientes disponibles en GitHub

#### Ventajas del Sistema

✅ **Sin intervención manual**: Los datos se actualizan automáticamente  
✅ **Versionamiento**: GitHub guarda el historial de cambios  
✅ **Seguridad**: Repositorio privado con autenticación  
✅ **Escalabilidad**: Puede crecer sin afectar el rendimiento  
✅ **Trazabilidad**: Cada cambio queda registrado  
✅ **Respaldo**: GitHub actúa como backup automático  

---

## 🔧 Configuración Inicial

### Requisitos Previos

1. **Cuenta de GitHub** con acceso al repositorio privado `Sinsapiar1/alsina-negativos-db`
2. **Personal Access Token (PAT)** de GitHub con permisos de lectura
3. **Despliegue en Streamlit Cloud** (o configuración local de secrets)

### Paso 1: Crear GitHub Personal Access Token

#### 1.1 Acceder a GitHub Settings

1. Iniciar sesión en [GitHub](https://github.com)
2. Hacer clic en tu foto de perfil (esquina superior derecha)
3. Seleccionar **Settings**
4. En el menú lateral izquierdo, ir a **Developer settings**
5. Seleccionar **Personal access tokens** → **Tokens (classic)**

#### 1.2 Generar Nuevo Token

1. Hacer clic en **Generate new token** → **Generate new token (classic)**
2. Configurar el token:
   - **Note**: `Streamlit Inventory Analyzer - Read DB`
   - **Expiration**: `No expiration` (o período deseado)
   - **Scopes**: Marcar **SOLO** `repo` (Full control of private repositories)
3. Hacer clic en **Generate token**
4. **⚠️ IMPORTANTE**: Copiar el token inmediatamente (no se volverá a mostrar)

#### 1.3 Formato del Token

El token tendrá un formato similar a:
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Paso 2: Configurar en Streamlit Cloud

#### 2.1 Acceder a Streamlit Cloud

1. Ir a [share.streamlit.io](https://share.streamlit.io/)
2. Localizar tu aplicación: `inventory-analyzer-web`
3. Hacer clic en el menú de tres puntos (**⋮**)
4. Seleccionar **Settings**

#### 2.2 Añadir Secret

1. En el menú lateral, seleccionar **Secrets**
2. En el editor de texto, añadir:

```toml
[secrets]
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

3. Reemplazar `ghp_xxx...` con tu token real
4. Hacer clic en **Save**
5. La aplicación se reiniciará automáticamente

### Paso 3: Verificar Configuración

#### 3.1 Prueba de Conexión

1. Abrir la aplicación en Streamlit Cloud
2. En el sidebar, seleccionar **🗄️ Histórico DB**
3. Verificar que aparezca:
   - ✅ Banner superior con fecha actualizada
   - ✅ Métricas de "Información de la Base de Datos"
   - ✅ Panel de filtros interactivos
   - ✅ NO debe aparecer error de red o autenticación

#### 3.2 Indicadores de Éxito

- **Banner superior**: Muestra fecha real (ej: `Última Actualización: 2025-11-12`)
- **Total Registros**: Número > 400,000
- **Días con Datos**: Número > 20
- **Sin mensajes de error**: No aparece "Error de red" o "404 Client Error"

#### 3.3 Solución de Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `404 Client Error: Not Found` | Token inválido o sin permisos | Regenerar token con scope `repo` |
| `401 Unauthorized` | Token no configurado | Verificar secrets en Streamlit Cloud |
| `Error conectando a la base de datos` | Token expirado | Crear nuevo token sin expiración |
| `No se encontró el archivo` | Ruta incorrecta | Verificar repo: `Sinsapiar1/alsina-negativos-db` |

---

## 📊 Estructura de Datos

### Base de Datos SQLite

**Archivo**: `negativos_inventario.db`  
**Tabla principal**: `inventario`  
**Motor**: SQLite 3  
**Encoding**: UTF-8  

### Esquema de la Tabla `inventario`

| Columna | Tipo | Descripción | Ejemplo | Nullable |
|---------|------|-------------|---------|----------|
| `id` | INTEGER | Identificador único (Primary Key) | 1, 2, 3... | NO |
| `fecha` | TEXT | Fecha del registro (formato YYYY-MM-DD) | `2025-11-12` | NO |
| `CompanyId` | TEXT | Código de la compañía/zona | `61D`, `62R`, `63D` | NO |
| `InventLocationId` | TEXT | Código del almacén | `ALM-001`, `BOD-CENTRAL` | NO |
| `ProductId` | TEXT | Código del producto | `67312`, `87947` | NO |
| `ProductName_es` | TEXT | Nombre del producto en español | `PORTAPUNTAL 120X80 GALVANIZADO` | SÍ |
| `LabelId` | TEXT | Identificador del pallet | `PAL-12345`, `NULL` | SÍ |
| `Stock` | INTEGER | Cantidad de stock (negativos son déficit) | `-150`, `200` | NO |
| `CostStock` | REAL | Costo total del stock (Stock × Costo Unitario) | `-12500.50` | SÍ |
| `created_at` | TIMESTAMP | Fecha/hora de creación del registro | `2025-11-12 08:30:00` | NO |

### Consideraciones Importantes

#### Stock Negativo
- **Valores negativos** indican **déficit** o **faltante** de inventario
- **Valores positivos** son inventario disponible (generalmente filtrados en este módulo)
- **Valor 0** indica inventario equilibrado

#### CostStock
- Calculado como: `Stock × Costo_Unitario`
- Para stock negativo: el costo también es negativo
- **En el análisis se muestra en valor absoluto** para facilitar interpretación
- **⚠️ IMPORTANTE**: Para análisis de costos, **solo se considera el último día**

#### LabelId (ID de Pallet)
- Puede ser `NULL` para productos sin asignación de pallet
- Productos sin `LabelId` se muestran como `"SIN_PALLET"`
- **No se pierden registros**: todos los productos se incluyen en el análisis

#### Alcance Temporal Típico
- **Mínimo**: 20 días de historia
- **Máximo**: Depende del proceso de carga
- **Actualización**: Diaria (nuevo registro por día)

### Ejemplo de Registros

```sql
id  | fecha      | CompanyId | InventLocationId | ProductId | ProductName_es                  | LabelId    | Stock | CostStock  | created_at
----|------------|-----------|------------------|-----------|--------------------------------|------------|-------|------------|-------------------
1   | 2025-11-12 | 61D       | ALM-NORTE        | 67312     | PORTAPUNTAL 120X80 GALVANIZADO | PAL-00123  | -150  | -18750.00  | 2025-11-12 08:00:00
2   | 2025-11-12 | 61D       | ALM-NORTE        | 87947     | CONTENEDOR ALSINA 120X80X60    | PAL-00456  | -44   | -5146.00   | 2025-11-12 08:00:00
3   | 2025-11-12 | 62R       | BOD-CENTRAL      | 87538     | ALUFORM VIGA SECUNDARIA 5"     | NULL       | -8    | -611.00    | 2025-11-12 08:00:00
4   | 2025-11-11 | 61D       | ALM-NORTE        | 67312     | PORTAPUNTAL 120X80 GALVANIZADO | PAL-00123  | -145  | -18125.00  | 2025-11-11 08:00:00
```

### Volumen de Datos Esperado

| Métrica | Valor Típico |
|---------|--------------|
| **Total Registros** | 400,000 - 500,000 |
| **Registros por Día** | 18,000 - 20,000 |
| **Días de Historia** | 23 - 30 |
| **Productos Únicos** | 2,500 - 3,000 |
| **Almacenes Activos** | 50 - 80 |
| **Zonas/Compañías** | 10 - 15 |
| **Tamaño del Archivo .db** | 20 - 50 MB |

---

## ⚙️ Funcionalidades

### 1. 🎨 Banner Informativo Profesional

**Ubicación**: Parte superior del módulo

#### Contenido
- **Título**: "Análisis Histórico desde Base de Datos"
- **Última Actualización**: Fecha del registro más reciente en la BD
- **Diseño**: Gradiente profesional con animación sutil

#### Información Técnica Desplegable
Al hacer clic, muestra:
- Repositorio de GitHub
- Archivo de base de datos
- Tabla utilizada
- Tipo de repositorio (Privado)
- Estado de autenticación

---

### 2. 🎯 Panel de Control Principal

**Ubicación**: Primera sección del dashboard

#### Métricas Clave

| Métrica | Descripción | Cálculo | Ejemplo |
|---------|-------------|---------|---------|
| **Total Registros** | Cantidad total de registros en BD | COUNT(*) | 446,040 |
| **Días con Datos** | Días únicos en el histórico | COUNT(DISTINCT fecha) | 23 |
| **Costo Total Negativo** | Impacto económico (último día) | SUM(ABS(CostStock)) WHERE Stock < 0 AND fecha = MAX(fecha) | $4,200,086,519 |
| **Productos Únicos** | Cantidad de productos diferentes | COUNT(DISTINCT ProductId) | 2,721 |

#### Visualización
- **4 tarjetas métricas** (`st.metric`)
- **Diseño responsivo** en columnas
- **Tooltips informativos** en cada métrica
- **Formato numérico** con separadores de miles

---

### 3. 🔍 Panel de Filtros Interactivos

**Ubicación**: Barra lateral (sidebar) y sección principal

#### Filtros Disponibles

##### 3.1 Filtro de Zonas (CompanyId)
- **Tipo**: Multiselección
- **Comportamiento**: 
  - Por defecto: Todas las zonas seleccionadas
  - Selección múltiple: Permite elegir una o varias zonas
  - Dinámica: Al cambiar zonas, los almacenes se actualizan automáticamente
- **Indicador visual**: Badge con cantidad de zonas seleccionadas

##### 3.2 Filtro de Almacenes (InventLocationId)
- **Tipo**: Multiselección dinámica
- **Comportamiento**:
  - **Relacionado con Zonas**: Solo muestra almacenes de zonas seleccionadas
  - Por defecto: Todos los almacenes disponibles
  - Se deshabilita si no hay zonas seleccionadas
- **Indicador visual**: Badge con cantidad de almacenes

##### 3.3 Filtro de Rango de Fechas
- **Desde fecha**: Selectbox con fechas disponibles
- **Hasta fecha**: Selectbox con fechas disponibles
- **Validación**: "Hasta" no puede ser anterior a "Desde"
- **Por defecto**: Rango completo disponible

##### 3.4 Búsqueda por Código de Producto
- **Tipo**: Input de texto
- **Comportamiento**: Búsqueda parcial (contiene)
- **Sensibilidad**: Case-insensitive
- **Ejemplo**: `"67312"` encuentra todos los productos con ese código

##### 3.5 Límite de Filas a Mostrar
- **Opciones**: 100, 500, 1000, 2000, "Todas"
- **Por defecto**: 500 filas
- **⚠️ IMPORTANTE**: Este límite **SOLO afecta la visualización en pantalla**
- **Exportación CSV**: Siempre incluye **TODOS** los registros (sin límite)

##### 3.6 Filtros Avanzados (Desplegable)

###### Excluir Códigos
- **Formato**: Códigos separados por comas
- **Ejemplo**: `67312, 87947, 87538`
- **Uso**: Remover productos específicos del análisis

###### Incluir SOLO Códigos
- **Formato**: Códigos separados por comas
- **Ejemplo**: `67312, 87947`
- **Uso**: Análisis exclusivo de productos específicos
- **⚠️ Nota**: Si se usa, ignora "Excluir Códigos"

###### Solo Productos Activos (Último Día)
- **Tipo**: Checkbox
- **Comportamiento**: Filtra productos con stock ≠ 0 en la fecha más reciente
- **Uso**: Excluir productos que ya se regularizaron

#### Indicadores de Estado

| Indicador | Color | Significado |
|-----------|-------|-------------|
| ✅ Verde | Success | Filtros aplicados correctamente |
| ⚠️ Amarillo | Warning | Advertencia (ej: sin zonas seleccionadas) |
| ℹ️ Azul | Info | Información adicional |

---

### 4. 💰 Resumen de Costos por Zona

**Ubicación**: Sección superior del dashboard

#### Visualización 1: Top 10 Zonas por Impacto Económico
- **Tipo**: Gráfico de barras horizontales
- **Datos**: Las 10 zonas con mayor costo negativo
- **Fecha**: Último día disponible
- **Color**: Rojo (#ff6b6b) para destacar impacto
- **Interactividad**: Hover muestra valores exactos

#### Visualización 2: Métricas Top 5 Zonas
- **Formato**: 5 tarjetas métricas compactas
- **Contenido por zona**:
  - Código de zona
  - Costo total en formato monetario
- **Ordenamiento**: De mayor a menor impacto

#### Tabla Detallada: Resumen por Zona
Columnas:
1. **Zona** (CompanyId)
2. **Productos** (COUNT DISTINCT ProductId)
3. **Pallets** (COUNT DISTINCT LabelId, excluyendo SIN_PALLET)
4. **Stock Negativo (Último Día)** (SUM Stock WHERE Stock < 0)
5. **Costo Total (Último Día)** (SUM ABS(CostStock) WHERE Stock < 0)

**Formato**:
- Números con separadores de miles
- Costos en formato monetario: `$X,XXX,XXX`
- Índice oculto para mejor legibilidad

---

### 5. 📊 Comparativa entre Almacenes Seleccionados

**Ubicación**: Sección media del dashboard  
**Condición**: Solo visible si hay almacenes filtrados

#### Gráfico 1: Unidades Negativas por Almacén
- **Tipo**: Barras horizontales
- **Datos**: Stock negativo total (último día) por almacén
- **Color**: Azul (#4ecdc4)
- **Ordenamiento**: Descendente (mayor a menor)
- **Uso**: Identificar almacenes con mayor déficit de unidades

#### Gráfico 2: Impacto Económico por Almacén
- **Tipo**: Barras horizontales
- **Datos**: Costo total negativo (último día) por almacén
- **Color**: Rojo (#ff6b6b)
- **Ordenamiento**: Descendente
- **Uso**: Priorizar acciones por impacto financiero

#### Tabla Comparativa Detallada
Columnas:
1. **Almacén** (InventLocationId)
2. **Zona** (CompanyId)
3. **Productos Únicos** (COUNT DISTINCT ProductId)
4. **Pallets Únicos** (COUNT DISTINCT LabelId)
5. **Stock Negativo** (SUM Stock WHERE Stock < 0)
6. **Costo Total** (SUM ABS(CostStock))

**Características**:
- Ordenada por Costo Total (descendente)
- Formato numérico con separadores
- Ancho completo (`use_container_width=True`)

---

### 6. 📅 Tabla de Comportamiento Diario (Principal)

**Ubicación**: Sección central del dashboard  
**Importancia**: ⭐⭐⭐⭐⭐ (Funcionalidad核心)

#### Estructura de la Tabla

**Columnas Fijas**:
1. **⚠️ Nivel** (opcional): Indica si es "🔴 CRÍTICO" (< -100 unidades)
2. **Zona**: CompanyId
3. **Código**: ProductId
4. **Nombre**: ProductName_es
5. **ID_Pallet**: LabelId (o "SIN_PALLET")
6. **Almacén**: InventLocationId

**Columnas Dinámicas de Fechas**:
- Una columna por cada fecha en el rango filtrado
- Formato: `YYYY-MM-DD`
- Contenido: Stock del producto en esa fecha
- **Celdas vacías**: Producto no tenía movimiento ese día (color personalizable)

**Columna Opcional**:
- **Total_Historico**: Suma de todas las fechas (si se activa)

#### Controles Interactivos

##### Control 1: Resaltar Críticos
- **Tipo**: Checkbox
- **Por defecto**: Activado
- **Efecto**: 
  - Añade columna "⚠️ Nivel"
  - Marca con "🔴 CRÍTICO" productos con < -100 unidades en último día
  - Reordena tabla con críticos al principio

##### Control 2: Ordenar Por
- **Opciones**:
  - **Más Negativo (Último Día)**: Ascendente por stock del último día
  - **Código (A-Z)**: Alfabético por ProductId
  - **Nombre (A-Z)**: Alfabético por ProductName_es
  - **Almacén**: Alfabético por InventLocationId
- **Por defecto**: Más Negativo

##### Control 3: Mostrar Columna de Totales
- **Tipo**: Checkbox
- **Por defecto**: Desactivado
- **Efecto**: Añade columna "Total_Historico" con suma de todas las fechas
- **Uso**: Ver impacto acumulado

##### Control 4: Color Celdas Vacías
- **Tipo**: Color picker
- **Por defecto**: `#f0f0f0` (gris claro)
- **Efecto**: Personalizar color de fondo de celdas sin datos
- **Uso**: Distinguir visualmente días sin movimiento

#### Formato de Celdas

| Condición | Formato | Ejemplo |
|-----------|---------|---------|
| Valor negativo | Números rojos, negritas | **-150** |
| Valor positivo | Números verdes | 50 |
| Celda vacía (NA) | Fondo coloreado | (vacío) |
| Producto crítico | Columna "🔴 CRÍTICO" | 🔴 CRÍTICO |

#### Banner Informativo
Encima de la tabla:
```
📋 Mostrando X de Y registros únicos (producto + pallet)
    | ⚠️ Z productos sin ID de pallet
    | 🔴 W registros críticos
```

#### Guía de Lectura (Desplegable)
Expander con instrucciones:
- Cómo interpretar valores negativos
- Significado de celdas vacías
- Uso de filtros de tabla
- Tips de navegación
- Interpretación de columna "Total Histórico"

#### Performance
- **Límite de visualización**: 500 filas por defecto (configurable)
- **Datos completos**: Se mantienen en memoria para exportación
- **Estilos**: Solo en columnas de fechas para optimizar

---

### 7. 📊 Resumen de Datos Filtrados

**Ubicación**: Después de la tabla principal

#### Métricas Calculadas

| Métrica | Descripción | Base de Datos |
|---------|-------------|---------------|
| **Total Stock Negativo (Último Día)** | Suma de unidades negativas en la fecha más reciente | `df_filtered_ultimo` |
| **Impacto Económico** | Costo total negativo del último día | `df_filtered_ultimo` |
| **Registros Únicos (Producto + Pallet)** | Combinaciones únicas visibles | `historico_pivot_completo` |
| **Productos Únicos** | Cantidad de productos diferentes | `historico_pivot_completo` |
| **Almacenes Activos** | Cantidad de almacenes con datos | `historico_pivot_completo` |
| **Zonas Activas** | Cantidad de zonas/compañías | `historico_pivot_completo` |
| **Rango Temporal** | Fechas desde-hasta | `fecha_cols_hist` |
| **Días de Datos** | Cantidad de días en el rango | `len(fecha_cols_hist)` |

#### Visualización
- **8 tarjetas** distribuidas en 2 filas de 4 columnas
- **Diseño responsivo**
- **Tooltips** explicativos en cada métrica

---

### 8. 📈 Análisis Visual de Datos Filtrados

**Ubicación**: Sección de visualizaciones  
**Condición**: Solo visible si hay datos filtrados

#### Visualización 1: Evolución Total Stock Negativo
- **Tipo**: Gráfico de línea
- **Eje X**: Fechas (ordenadas)
- **Eje Y**: Total de stock negativo (valor absoluto)
- **Color**: Rojo (#ff4444)
- **Marcadores**: Activados para ver cada día
- **Uso**: Ver tendencia general (¿mejora o empeora?)

#### Visualización 2: Distribución por Zona/Compañía
- **Tipo**: Gráfico de torta (pie chart)
- **Datos**: Stock negativo total por zona (todas las fechas)
- **Interactividad**: Hover para porcentajes y valores
- **Uso**: Identificar zonas con mayor participación

#### Visualización 3: Top 10 Zonas por Costo
- **Tipo**: Barras horizontales
- **Datos**: Costos del **último día** por zona
- **Color**: Rojo (#ff6b6b)
- **Título**: Incluye la fecha del análisis
- **Uso**: Priorización por impacto financiero

#### Visualización 4: Top 10 Almacenes por Stock Negativo
- **Tipo**: Barras horizontales
- **Datos**: Stock negativo acumulado (todas las fechas)
- **Color**: Turquesa (#4ecdc4)
- **Uso**: Identificar ubicaciones problemáticas

#### Visualización 5: Mapa de Calor - Evolución por Pallet
- **Tipo**: Heatmap (mapa de calor)
- **Eje X**: Fechas
- **Eje Y**: Código_Pallet (ProductId + LabelId)
- **Color**: Escala RdBu_r (rojo = negativo fuerte, azul = positivo)
- **Control**: Selector de cantidad de pallets (10, 20, 30, 50, 100)
- **Altura dinámica**: Se ajusta según cantidad de pallets
- **Uso**: Ver patrones temporales de productos específicos

#### Visualización 6: Evolución Individual por Pallet
- **Tipo**: Líneas múltiples superpuestas
- **Control**: Selector de cantidad de líneas (1-15)
- **Colores**: Paleta Set1 (distintos para cada producto)
- **Interactividad**: Hover con nombre completo del producto
- **Leyenda**: Código_Pallet
- **Uso**: Seguimiento detallado de productos críticos

---

### 9. 📥 Exportación de Datos

**Ubicación**: Sección final del dashboard

#### Características de la Exportación

##### Formato
- **Tipo de archivo**: CSV (Comma-Separated Values)
- **Encoding**: UTF-8
- **Separador**: Coma (`,`)
- **Decimales**: Punto (`.`)

##### Contenido del CSV

**⚠️ CRÍTICO**: El CSV incluye **TODOS** los registros filtrados, sin límite de filas.

**Columnas exportadas**:
1. Todas las columnas fijas (Zona, Código, Nombre, ID_Pallet, Almacén)
2. Todas las columnas de fechas del rango seleccionado
3. Columna "_Es_Critico" (si está activada)
4. Columna "Total_Historico" (si está activada)

##### Nombre del Archivo
Formato: `Historico_DB_Filtrado_YYYYMMDD_HHMM.csv`

Ejemplo: `Historico_DB_Filtrado_20251112_1430.csv`

##### Banner Informativo
Antes del botón de descarga:
```
📊 El CSV incluirá TODOS los X,XXX registros (sin límite de filas)
```

##### Botón de Descarga
- **Label**: "📥 Descargar Histórico DB Filtrado COMPLETO (CSV)"
- **Tooltip**: Indica la cantidad exacta de registros
- **Ancho**: Completo (`use_container_width=True`)

#### Casos de Uso del CSV

1. **Análisis Avanzado**: Importar a Excel, Power BI, Tableau
2. **Reportes Ejecutivos**: Crear presentaciones personalizadas
3. **Auditorías**: Documentación de estados históricos
4. **Integraciones**: Conectar con otros sistemas
5. **Respaldo**: Guardar snapshot para comparaciones futuras

#### Verificación de Integridad

Para verificar que el CSV contiene todos los datos:

```python
# En Python
import pandas as pd
df = pd.read_csv("Historico_DB_Filtrado_20251112_1430.csv")
print(f"Total filas: {len(df)}")
print(f"Columnas: {list(df.columns)}")
```

```excel
# En Excel
=COUNTA(A:A)-1  // Cuenta filas (menos encabezado)
```

---

## 📖 Guía de Uso

### Caso de Uso 1: Análisis de Zona Específica

**Objetivo**: Analizar el stock negativo de la zona "61D" en los últimos 7 días.

#### Pasos:

1. **Abrir el módulo**
   - En el sidebar, seleccionar **🗄️ Histórico DB**

2. **Configurar filtros**
   - En "Selecciona zonas", deseleccionar todas y elegir solo **61D**
   - En "Almacenes", dejar todos seleccionados (se filtran automáticamente)
   - En "Desde fecha", seleccionar hace 7 días
   - En "Hasta fecha", dejar la más reciente

3. **Analizar métricas**
   - Revisar "Total Stock Negativo (Último Día)"
   - Revisar "Impacto Económico"

4. **Revisar tabla**
   - Activar "🔴 Resaltar críticos"
   - Ordenar por "Más Negativo (Último Día)"
   - Identificar productos con mayor déficit

5. **Analizar tendencia**
   - Ir a "📈 Análisis Visual de Datos Filtrados"
   - Ver gráfico "Evolución Total Stock Negativo"
   - ¿La tendencia sube o baja?

6. **Exportar para reporte**
   - Ir a "📥 Exportación de Datos"
   - Descargar CSV
   - Abrir en Excel para crear gráficos personalizados

---

### Caso de Uso 2: Seguimiento de Producto Específico

**Objetivo**: Ver la evolución temporal del producto "67312" (PORTAPUNTAL).

#### Pasos:

1. **Buscar producto**
   - En el filtro "🔍 Buscar código", ingresar: `67312`

2. **Revisar todas las zonas**
   - En "Selecciona zonas", dejar todas seleccionadas
   - Esto muestra el producto en todos los almacenes

3. **Analizar tabla**
   - La tabla mostrará solo las filas de ese producto
   - Ver columnas de fechas: ¿hay patrón?
   - Activar "➕ Mostrar columna de totales" para ver impacto acumulado

4. **Ver gráfico individual**
   - Ir a "📈 Evolución Individual por Pallet"
   - Ajustar selector de líneas según cantidad de pallets
   - Ver trayectoria de cada pallet del producto

5. **Identificar almacén crítico**
   - En "Top 10 Almacenes por Stock Negativo"
   - Ver qué almacén tiene mayor déficit de este producto

---

### Caso de Uso 3: Comparar Dos Almacenes

**Objetivo**: Comparar el stock negativo entre "61D" y "61R".

#### Pasos:

1. **Seleccionar zonas**
   - En "Selecciona zonas", elegir **61D** y **61R**

2. **Ver comparativa**
   - Ir a "📊 Comparativa entre Almacenes Seleccionados"
   - Ver gráfico "Unidades Negativas por Almacén"
   - Ver gráfico "Impacto Económico por Almacén"

3. **Analizar diferencias**
   - En la tabla comparativa, revisar:
     - ¿Qué almacén tiene más productos únicos?
     - ¿Qué almacén tiene mayor costo?
     - ¿Qué almacén tiene más pallets afectados?

4. **Exportar datos**
   - Descargar CSV
   - En Excel, crear tabla dinámica por almacén

---

### Caso de Uso 4: Identificar Productos sin Pallet

**Objetivo**: Encontrar productos que no tienen asignación de pallet.

#### Pasos:

1. **Sin filtros específicos**
   - Dejar todas las zonas y almacenes seleccionados

2. **Revisar banner informativo**
   - Encima de la tabla principal:
   - Leer: "⚠️ X productos sin ID de pallet"

3. **Buscar en tabla**
   - En la tabla, buscar filas donde **ID_Pallet** = `"SIN_PALLET"`
   - Estos son los productos sin asignación

4. **Analizar impacto**
   - En "Resumen de Datos Filtrados", ver si el stock sin pallet es significativo

5. **Exportar listado**
   - Descargar CSV
   - En Excel, filtrar por `ID_Pallet = "SIN_PALLET"`
   - Crear listado para asignación de pallets

---

### Caso de Uso 5: Reporte Ejecutivo Mensual

**Objetivo**: Crear un reporte completo del último mes para la gerencia.

#### Pasos:

1. **Configurar rango**
   - En "Desde fecha", seleccionar hace 30 días
   - En "Hasta fecha", seleccionar fecha más reciente

2. **Capturar métricas clave**
   - **Panel de Control Principal**:
     - Total registros
     - Costo Total Negativo
     - Productos Únicos
   - **Resumen de Datos Filtrados**:
     - Total Stock Negativo
     - Impacto Económico

3. **Exportar visualizaciones**
   - Tomar screenshots de:
     - "Top 10 Zonas por Costo"
     - "Evolución Total Stock Negativo"
     - "Distribución por Zona/Compañía"

4. **Descargar datos**
   - Exportar CSV completo
   - En Excel/Power BI:
     - Crear tabla dinámica por zona
     - Crear gráfico de tendencia
     - Calcular % de cambio mensual

5. **Crear presentación**
   - Incluir:
     - Resumen ejecutivo (métricas clave)
     - Análisis de tendencia (¿mejora o empeora?)
     - Top 5 zonas críticas
     - Top 5 productos críticos
     - Recomendaciones

---

## 🏗️ Arquitectura Técnica

### Stack Tecnológico

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Frontend** | Streamlit | ≥1.32.0 | Interfaz web interactiva |
| **Base de Datos** | SQLite | 3.x | Almacenamiento de datos |
| **Procesamiento** | Pandas | ≥2.0.0 | Manipulación de datos |
| **Visualizaciones** | Plotly | ≥5.15.0 | Gráficos interactivos |
| **HTTP Client** | Requests | ≥2.31.0 | Descarga de .db desde GitHub |
| **Almacenamiento** | GitHub | - | Repositorio de BD |
| **Autenticación** | GitHub PAT | - | Acceso a repo privado |
| **Deployment** | Streamlit Cloud | - | Hosting de la app |

### Flujo de Datos Detallado

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. USUARIO ABRE TAB "🗄️ Histórico DB"                            │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│  2. STREAMLIT VERIFICA CACHÉ                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  @st.cache_data(ttl=600)  # 10 minutos                       │  │
│  │  def load_historico_data():                                  │  │
│  │      ¿Existe en caché y no expiró?                           │  │
│  │      ✅ SÍ  → Retornar DataFrame desde caché (rápido)        │  │
│  │      ❌ NO  → Continuar al paso 3                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│  3. DESCARGAR .db DESDE GITHUB                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  download_and_connect_db()                                   │  │
│  │  1. Leer GitHub Token desde st.secrets["GITHUB_TOKEN"]      │  │
│  │  2. Construir URL de GitHub Contents API:                   │  │
│  │     https://api.github.com/repos/                            │  │
│  │     Sinsapiar1/alsina-negativos-db/contents/                 │  │
│  │     negativos_inventario.db                                  │  │
│  │  3. Headers: Authorization: token {GITHUB_TOKEN}            │  │
│  │  4. GET request a GitHub API                                │  │
│  │  5. Parsear JSON response                                   │  │
│  │  6. Extraer "download_url" del JSON                         │  │
│  │  7. GET request a download_url (archivo binario)           │  │
│  │  8. Guardar en archivo temporal (tempfile)                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│  4. CONECTAR A SQLITE Y CARGAR DATOS                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. sqlite3.connect(temp_db_path)                           │  │
│  │  2. SQL Query:                                              │  │
│  │     SELECT * FROM inventario                                │  │
│  │     ORDER BY fecha DESC, CompanyId, ProductId               │  │
│  │  3. pd.read_sql_query(query, conn)                         │  │
│  │  4. Cerrar conexión                                        │  │
│  │  5. Eliminar archivo temporal                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│  5. TRANSFORMACIÓN Y LIMPIEZA                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. Convertir columna 'fecha' a datetime                    │  │
│  │  2. Convertir 'Stock' a numeric (coerce errors)             │  │
│  │  3. Convertir 'CostStock' a numeric (coerce errors)         │  │
│  │  4. Rellenar LabelId vacíos con "SIN_PALLET"               │  │
│  │  5. Crear columna 'Zona' = CompanyId                        │  │
│  │  6. Crear columna 'Almacen' = InventLocationId              │  │
│  │  7. Guardar en caché (@st.cache_data)                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│  6. APLICAR FILTROS DE USUARIO                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  df_filtered = df_historico.copy()                          │  │
│  │  1. Filtrar por Stock < 0 (solo negativos)                  │  │
│  │  2. Filtrar por zonas seleccionadas                         │  │
│  │  3. Filtrar por almacenes seleccionados                     │  │
│  │  4. Filtrar por rango de fechas                             │  │
│  │  5. Filtrar por código de producto (búsqueda)               │  │
│  │  6. Excluir códigos (si aplica)                             │  │
│  │  7. Incluir solo códigos (si aplica)                        │  │
│  │  8. Solo activos último día (si aplica)                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│  7. CREAR TABLA PIVOTE                                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  pivot_table(                                               │  │
│  │      values='Stock',                                        │  │
│  │      index=['CompanyId', 'ProductId', 'ProductName_es',     │  │
│  │              'LabelId', 'InventLocationId'],                │  │
│  │      columns='fecha',                                       │  │
│  │      aggfunc='sum'                                          │  │
│  │  )                                                          │  │
│  │  Resultado: Tabla con fechas como columnas                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│  8. SEPARAR DATAFRAMES PARA DISPLAY Y EXPORTACIÓN                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  historico_pivot_completo = pivot.copy()  # TODOS          │  │
│  │  historico_pivot_display = pivot.head(500)  # LIMITADO     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│  9. RENDERIZAR INTERFAZ                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. Banner informativo                                      │  │
│  │  2. Panel de control (métricas)                             │  │
│  │  3. Resumen de costos por zona                              │  │
│  │  4. Comparativa entre almacenes                             │  │
│  │  5. Tabla de comportamiento diario (display)                │  │
│  │  6. Resumen de datos filtrados                              │  │
│  │  7. Análisis visual (gráficos)                              │  │
│  │  8. Botón de exportación (completo)                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│  10. USUARIO INTERACTÚA                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  - Cambiar filtros → Rerun desde paso 6                    │  │
│  │  - Descargar CSV → Usar historico_pivot_completo           │  │
│  │  - Cambiar límite de filas → Solo afecta display           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Funciones Clave del Código

#### 1. `download_and_connect_db()`

```python
@st.cache_data(ttl=600)  # Caché de 10 minutos
def download_and_connect_db():
    """
    Descarga el archivo .db desde GitHub usando Contents API
    para autenticación con repositorios privados.
    
    Returns:
        sqlite3.Connection: Conexión a la base de datos temporal
    
    Raises:
        Exception: Si hay error de red o autenticación
    """
```

**Lógica**:
1. Obtener token desde `st.secrets`
2. Construir URL de GitHub Contents API
3. Request con autenticación
4. Parsear JSON y extraer `download_url`
5. Descargar archivo binario
6. Guardar en `tempfile.NamedTemporaryFile`
7. Conectar con `sqlite3.connect()`

#### 2. `load_historico_data()`

```python
@st.cache_data(ttl=600)
def load_historico_data():
    """
    Carga y transforma datos desde la base de datos SQLite.
    
    Returns:
        pd.DataFrame: DataFrame con datos limpios y transformados
    
    Raises:
        Exception: Si hay error en la conexión o query SQL
    """
```

**Transformaciones**:
- `pd.to_datetime(df['fecha'])`
- `pd.to_numeric(df['Stock'], errors='coerce')`
- `df['LabelId'].fillna('SIN_PALLET')`
- Crear columnas auxiliares (`Zona`, `Almacen`)

#### 3. Creación de Tabla Pivote

```python
historico_pivot = df_filtered.pivot_table(
    values='Stock',
    index=['CompanyId', 'ProductId', 'ProductName_es', 'LabelId', 'InventLocationId'],
    columns='fecha',
    aggfunc='sum',
    fill_value=None
).reset_index()
```

**Por qué `fill_value=None`**:
- Mantener celdas vacías como `None`/`NA`
- Distinguir "sin movimiento" de "stock = 0"
- Aplicar estilos visuales a celdas vacías

#### 4. Separación Display/Completo

```python
# Guardar COMPLETO antes de limitar
historico_pivot_completo = historico_pivot.copy()

# Limitar SOLO para display
if max_rows_display != "Todas":
    historico_pivot_display = historico_pivot_completo.head(max_rows_display)
else:
    historico_pivot_display = historico_pivot_completo
```

**Razón crítica**:
- **Display**: Performance en pantalla (500 filas)
- **Completo**: Métricas correctas y exportación completa
- **Problema anterior**: Limitar el DF principal causaba pérdida de datos

---

## ⚡ Optimización y Performance

### Estrategias de Caché

#### Caché de Descarga de BD

```python
@st.cache_data(ttl=600)  # 10 minutos
def download_and_connect_db():
    ...
```

**Beneficios**:
- Primera carga: ~5-10 segundos
- Cargas subsecuentes: ~0.5 segundos
- Reduce tráfico de red
- Menos requests a GitHub API

**TTL (Time To Live)**:
- **600 segundos** = 10 minutos
- Balance entre datos frescos y performance
- Ajustable según frecuencia de actualización de la BD

#### Caché de Datos Procesados

```python
@st.cache_data(ttl=600)
def load_historico_data():
    ...
```

**Beneficios**:
- Evita re-procesamiento en cada filtro
- Transformaciones de datos solo una vez
- Conversiones de tipos solo una vez

### Límite de Filas para Display

**Estrategia de dos DataFrames**:

| Aspecto | Display (limitado) | Completo |
|---------|-------------------|----------|
| **Uso** | Visualización en pantalla | Métricas y exportación |
| **Filas** | 100-2000 (configurable) | Todas (sin límite) |
| **Performance** | Rápido (< 1 seg) | Variable según filtros |
| **Memoria** | Baja | Media-Alta |

**Impacto**:
- **Sin límite**: 18,000 filas → 8-10 segundos render
- **Con límite 500**: 18,000 filas → 1-2 segundos render
- **Métricas**: Siempre correctas (usan completo)
- **Exportación**: Siempre completa (sin límite)

### Optimizaciones de Pandas

#### 1. Conversiones de Tipo Explícitas

```python
df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce')
df['fecha'] = pd.to_datetime(df['fecha'])
```

**Por qué**:
- SQLite puede retornar strings
- Operaciones numéricas requieren tipos correctos
- `errors='coerce'` evita crashes por datos inválidos

#### 2. Filtrado Escalonado

```python
# Orden óptimo de filtros (de más restrictivo a menos)
df = df[df['Stock'] < 0]  # Reduce ~50%
df = df[df['CompanyId'].isin(zonas)]  # Reduce ~20-80% adicional
df = df[df['fecha'] >= fecha_desde]  # Reduce ~10-50% adicional
```

**Por qué**:
- Filtros más restrictivos primero reducen datos temprano
- Menos operaciones sobre datasets grandes
- Memory footprint más bajo

#### 3. Uso de `copy()` Estratégico

```python
# CORRECTO
historico_pivot_completo = historico_pivot.copy()
historico_pivot_display = historico_pivot_completo.head(500)

# INCORRECTO (SettingWithCopyWarning)
historico_pivot_display = historico_pivot.head(500)
historico_pivot_display['nueva_col'] = ...  # ⚠️ Warning!
```

### Optimizaciones de Streamlit

#### 1. Uso Mínimo de `st.rerun()`

**Evitado en versión actual**:
- `st.rerun()` reinicia toda la app
- Causa flickering visual
- Pérdida temporal de estado

**Alternativa**:
- Filtros nativos de Streamlit (`st.multiselect`, `st.selectbox`)
- Reactivos automáticamente
- Sin rerun manual

#### 2. Estilos Solo en Columnas Necesarias

```python
# SOLO en columnas de fechas
styled_pivot = historico_pivot_display.style.applymap(
    highlight_empty_cells,
    subset=fecha_cols_str  # ← Solo estas columnas
)
```

**Por qué**:
- Aplicar estilos a toda la tabla es lento
- Solo las fechas necesitan color de fondo

#### 3. Visualizaciones Condicionales

```python
if fecha_cols_str and len(historico_pivot_completo) > 0:
    # Renderizar gráficos solo si hay datos
```

**Por qué**:
- Evita crashes por DataFrames vacíos
- Reduce renders innecesarios

### Monitoreo de Performance

#### Herramientas Disponibles

1. **Streamlit Profiler** (desarrollo local):
   ```bash
   streamlit run app.py --server.enableProfiler=true
   ```

2. **Timer manual** (en desarrollo):
   ```python
   import time
   start = time.time()
   # ... código ...
   print(f"Tiempo: {time.time() - start:.2f}s")
   ```

3. **Métricas de Streamlit Cloud**:
   - Settings → Analytics
   - Ver tiempos de carga
   - Identificar cuellos de botella

---

## 🔧 Solución de Problemas

### Problema 1: Error 404 - Not Found

#### Síntoma
```
❌ Error conectando a la base de datos
Error de red: 404 Client Error: Not Found for url: ...
```

#### Causas Posibles
1. Token de GitHub no configurado
2. Token sin permisos `repo`
3. Token expirado
4. Ruta del repositorio incorrecta

#### Solución

**Paso 1**: Verificar que el token existe
```python
# En Streamlit Cloud: Settings → Secrets
# Debe existir:
[secrets]
GITHUB_TOKEN = "ghp_..."
```

**Paso 2**: Regenerar token con permisos correctos
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Marcar **solo** `repo` (Full control of private repositories)
4. Generate token
5. Copiar y actualizar en Streamlit secrets

**Paso 3**: Reiniciar app
- En Streamlit Cloud: ⋮ → Reboot app

---

### Problema 2: Datos Desactualizados

#### Síntoma
- La fecha en el banner es antigua
- Los datos no reflejan cambios recientes

#### Causas Posibles
1. Caché de Streamlit no expiró (TTL 10 min)
2. Base de datos en GitHub no se actualizó

#### Solución

**Opción 1**: Esperar 10 minutos
- El caché expira automáticamente

**Opción 2**: Limpiar caché manualmente
1. En la app, presionar `C` en el teclado
2. Menú → Clear cache
3. Recargar página

**Opción 3**: Forzar reboot
- En Streamlit Cloud: ⋮ → Reboot app

**Verificar BD en GitHub**:
1. Ir a `https://github.com/Sinsapiar1/alsina-negativos-db`
2. Ver "Latest commit"
3. Verificar fecha de `negativos_inventario.db`

---

### Problema 3: Exportación CSV con Menos Filas

#### Síntoma
- CSV descargado tiene menos filas de lo esperado
- Métricas en pantalla no coinciden con CSV

#### Causa
- **YA CORREGIDO** en última versión
- Versiones antiguas: límite de display afectaba exportación

#### Solución

**Verificar versión**:
1. Ver banner informativo antes del botón de descarga
2. Debe decir: `"📊 El CSV incluirá TODOS los X,XXX registros"`

**Si el banner no aparece**:
1. Actualizar repositorio:
   ```bash
   git pull origin main
   ```
2. Reiniciar app en Streamlit Cloud

**Verificar integridad del CSV**:
```python
import pandas as pd
df = pd.read_csv("Historico_DB_Filtrado_*.csv")
print(f"Filas en CSV: {len(df)}")
# Debe coincidir con "Total Registros" en la app
```

---

### Problema 4: KeyError en Visualizaciones

#### Síntoma
```
KeyError: "None of [Timestamp(...)] are in the [columns]"
```

#### Causa
- **YA CORREGIDO** en última versión
- Desajuste entre nombres de columnas (Timestamp vs String)

#### Solución

**Verificar versión**:
- Última versión convierte timestamps a strings (`YYYY-MM-DD`)

**Si persiste el error**:
1. Actualizar código:
   ```bash
   git pull origin main
   ```
2. Limpiar caché: Menú → Clear cache
3. Recargar app

---

### Problema 5: Discrepancia en Unidades

#### Síntoma
- Suma manual de unidades no coincide con métricas de la app
- Diferencia especialmente en productos sin `LabelId`

#### Causa
- **YA CORREGIDO** en última versión
- Versiones antiguas: productos sin `LabelId` se perdían en pivot

#### Solución Implementada

**Relleno de LabelId**:
```python
df_filtered["LabelId"] = df_filtered["LabelId"].fillna("SIN_PALLET")
```

**Verificar**:
- Banner bajo la tabla debe mostrar: `"⚠️ X productos sin ID de pallet"`
- Si X > 0, esos productos están incluidos en el análisis

**Validar suma**:
```python
# En la app, las unidades deben calcularse así:
df_ultimo = df[df['fecha'] == fecha_max]
total = df_ultimo[df_ultimo['Stock'] < 0]['Stock'].sum()
print(abs(total))  # Debe coincidir con métrica en pantalla
```

---

### Problema 6: Discrepancia en Costos

#### Síntoma
- Costos en app no coinciden con cálculo manual
- Costos parecen sumados de múltiples días

#### Causa
- **YA CORREGIDO** en última versión
- Versiones antiguas: sumaban costos de todos los días

#### Solución Implementada

**Filtro a último día**:
```python
# TODAS las métricas de costo ahora usan:
df_filtered_ultimo = df_filtered[df_filtered["fecha"] == fecha_max]
costo_total = abs(df_filtered_ultimo[df_filtered_ultimo["Stock"] < 0]["CostStock"].sum())
```

**Verificar**:
- Título de gráfico de costos debe incluir fecha: `"💰 Top 10 Zonas por Costo (2025-11-12)"`
- Métrica "Costo Total Negativo" se calcula del último día

---

### Problema 7: Filtros No Funcionan

#### Síntoma
- Cambiar filtros no actualiza datos
- Multiselect no responde

#### Causas Posibles
1. Error de JavaScript en el navegador
2. Caché del navegador corrupta
3. Versión antigua de Streamlit

#### Solución

**Paso 1**: Limpiar caché del navegador
- Chrome: Ctrl+Shift+Del → Borrar caché
- Firefox: Ctrl+Shift+Del → Borrar caché

**Paso 2**: Probar en ventana incógnito
- Ctrl+Shift+N (Chrome) o Ctrl+Shift+P (Firefox)

**Paso 3**: Verificar versión de Streamlit
```python
# En requirements.txt, debe ser:
streamlit>=1.32.0
```

**Paso 4**: Reiniciar app
- Streamlit Cloud: ⋮ → Reboot app

---

### Problema 8: App Muy Lenta

#### Síntoma
- Carga inicial > 15 segundos
- Cambiar filtros tarda > 5 segundos

#### Diagnóstico

**1. Verificar cantidad de datos**:
- Si "Total Registros" > 500,000 → Considerar optimización de BD

**2. Verificar límite de filas**:
- En "Límite de filas a mostrar", usar **500** (no "Todas")

**3. Verificar filtros**:
- Filtrar por zona específica reduce carga
- Reducir rango de fechas (ej: últimos 7 días)

#### Solución

**Opción 1**: Optimizar filtros
```python
# En lugar de:
zonas = todas_las_zonas  # 15 zonas

# Usar:
zonas = ["61D", "61R"]  # Solo 2 zonas
```

**Opción 2**: Ajustar TTL de caché
```python
# En app.py, reducir TTL:
@st.cache_data(ttl=300)  # 5 minutos en lugar de 10
```

**Opción 3**: Upgrade de plan en Streamlit Cloud
- Plan gratuito: CPU limitada
- Plan Team/Enterprise: Más recursos

---

## ❓ Preguntas Frecuentes

### General

**P: ¿Con qué frecuencia se actualizan los datos?**  
R: La base de datos en GitHub se actualiza diariamente. La app tiene un caché de 10 minutos, por lo que verás los datos actualizados dentro de ese período.

**P: ¿Puedo usar este módulo sin conexión a Internet?**  
R: No, el módulo requiere conexión para descargar la base de datos desde GitHub.

**P: ¿Los datos son en tiempo real?**  
R: No son en tiempo real. Son datos del último proceso de carga (usualmente del día anterior o mismo día, dependiendo del horario de actualización).

---

### Datos y Análisis

**P: ¿Por qué algunos productos no tienen ID de pallet?**  
R: Algunos productos no están asignados a pallets específicos en el sistema fuente. Se muestran como "SIN_PALLET" y se incluyen en todos los análisis.

**P: ¿Qué significa una celda vacía en la tabla?**  
R: Significa que ese producto/pallet no tenía movimiento (ni positivo ni negativo) en esa fecha específica.

**P: ¿Los costos son del último día o acumulados?**  
R: **Todos los costos mostrados en el dashboard son del último día disponible**. El costo acumulado no tiene sentido en inventario, ya que queremos saber el impacto actual, no histórico.

**P: ¿Por qué mis sumas manuales no coinciden?**  
R: Asegúrate de:
1. Usar solo stock negativo (`Stock < 0`)
2. Filtrar por el **último día** para costos
3. Incluir productos con `LabelId = "SIN_PALLET"`
4. Usar valor absoluto para costos (`ABS(CostStock)`)

---

### Filtros y Visualización

**P: ¿Por qué cuando cambio zonas, los almacenes se resetean?**  
R: Es el comportamiento esperado. Los almacenes están relacionados con zonas, por lo que al cambiar zonas, solo se muestran los almacenes de esas zonas.

**P: ¿Puedo guardar mis filtros?**  
R: No actualmente. Al recargar la app, los filtros vuelven a sus valores por defecto (todas las zonas/almacenes).

**P: ¿Qué significa "Resaltar críticos"?**  
R: Marca productos con más de -100 unidades negativas en el último día. Son los más urgentes de atender.

**P: ¿Por qué el Mapa de Calor solo muestra X pallets?**  
R: Por performance. Puedes ajustar la cantidad con el selector (10, 20, 30, 50, 100 pallets).

---

### Exportación

**P: ¿El CSV incluye todos los datos filtrados?**  
R: **SÍ**. El CSV siempre incluye **TODOS** los registros filtrados, sin límite de filas. El "Límite de filas a mostrar" solo afecta la pantalla.

**P: ¿Qué formato tiene el CSV?**  
R: UTF-8, separado por comas (`,`), decimales con punto (`.`), compatible con Excel, Power BI, Tableau, etc.

**P: ¿Puedo automatizar la descarga del CSV?**  
R: No directamente desde la app. Pero podrías:
1. Descargar la BD de GitHub directamente (con script Python)
2. Procesar con Pandas
3. Generar CSV automáticamente

---

### Técnico

**P: ¿Dónde se almacena la base de datos?**  
R: En un repositorio privado de GitHub: `Sinsapiar1/alsina-negativos-db`. Se descarga temporalmente al abrir el módulo y se elimina al cerrar.

**P: ¿Cómo manejo el GitHub Token de forma segura?**  
R: **NUNCA** lo incluyas en el código. Usa siempre `st.secrets` en Streamlit Cloud o archivo `.streamlit/secrets.toml` en local (que debe estar en `.gitignore`).

**P: ¿Puedo modificar la base de datos desde la app?**  
R: No. La app es de **solo lectura**. La actualización de la BD se hace por proceso externo.

**P: ¿Qué pasa si dos usuarios usan la app simultáneamente?**  
R: Cada usuario tiene su propia sesión y caché independiente. No hay interferencia entre usuarios.

---

### Errores Comunes

**P: Veo "Error de red: 404"**  
R: Tu GitHub Token no está configurado correctamente o no tiene permisos `repo`. Ver [Configuración Inicial](#configuración-inicial).

**P: La app está muy lenta**  
R: 
1. Reduce el "Límite de filas a mostrar" a 500
2. Filtra por zonas/almacenes específicos
3. Reduce el rango de fechas

**P: Los datos no se actualizan**  
R: 
1. Espera 10 minutos (TTL del caché)
2. O presiona `C` en el teclado → Clear cache

---

## 📝 Resumen Ejecutivo

### Lo Esencial en 60 Segundos

**Histórico DB** es un módulo profesional para analizar stock negativo con perspectiva temporal:

✅ **Conexión automática** a base de datos SQLite en GitHub (privado)  
✅ **Actualización diaria** sin intervención manual  
✅ **23+ días** de historial completo  
✅ **Análisis multi-dimensional**: Zona, Almacén, Producto, Pallet, Fecha  
✅ **Visualizaciones interactivas**: Evolución, mapas de calor, comparativas  
✅ **Exportación completa** a CSV (todos los datos, sin límites)  
✅ **Caché inteligente** (10 min) para máxima performance  
✅ **Filtros relacionados** tipo Power BI  

### Configuración Mínima Requerida

1. **GitHub PAT** con scope `repo`
2. **Agregar token** a Streamlit secrets:
   ```toml
   GITHUB_TOKEN = "ghp_..."
   ```
3. **Listo** ✅

### Casos de Uso Principales

| Caso de Uso | Tiempo | Valor |
|-------------|--------|-------|
| 📊 Análisis de zona específica | 2 min | Identificar productos críticos |
| 🔍 Seguimiento de producto | 3 min | Ver evolución temporal completa |
| ⚖️ Comparar almacenes | 5 min | Priorizar acciones por ubicación |
| 📈 Reporte ejecutivo mensual | 15 min | Datos para decisiones estratégicas |
| 📥 Exportar para análisis avanzado | 1 min | CSV completo para Excel/Power BI |

---

## 📚 Recursos Adicionales

### Documentación Relacionada

- **README.md**: Información general de la aplicación
- **CHANGELOG_v6.1.md**: Historial de cambios y versiones
- **config.toml**: Configuración de la aplicación
- **requirements.txt**: Dependencias de Python

### Enlaces Útiles

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Documentation](https://plotly.com/python/)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### Contacto y Soporte

Para reportar problemas o sugerir mejoras:
1. Crear issue en GitHub
2. Incluir:
   - Descripción del problema
   - Pasos para reproducir
   - Screenshots si aplica
   - Datos (sin información sensible)

---

## 📄 Licencia y Términos

Esta documentación corresponde al módulo **Histórico DB** del **Inventory Analyzer Web**.

**Versión de la Documentación**: 1.0  
**Última Actualización**: 2025-11-13  
**Autor**: [Tu Nombre/Organización]  

---

**🎉 ¡Gracias por usar Histórico DB!**

*Para cualquier duda, consulta esta documentación o contacta al equipo de soporte.*
