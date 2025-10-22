# 📋 Especificación: Archivos para SharePoint
## Para Bot Automático de Inventarios Negativos

---

## 🎯 Resumen Ejecutivo

El bot debe generar **archivos Excel diarios** con inventarios negativos del ERP y guardarlos en una carpeta de SharePoint.

---

## 📁 Estructura de Carpeta SharePoint

### Ubicación Sugerida

```
SharePoint → Sites → [NombreSitio] → Documentos Compartidos → InventariosNegativos
```

**URL ejemplo:**
```
https://tuempresa.sharepoint.com/sites/Operaciones/Shared Documents/InventariosNegativos
```

---

## 📄 Formato de Archivos

### Convención de Nombres

**Formato:** `inventario_negativo_YYYYMMDD.xlsx`

**Ejemplos:**
```
inventario_negativo_20251021.xlsx  ← Hoy
inventario_negativo_20251020.xlsx  ← Ayer
inventario_negativo_20251019.xlsx  ← Anteayer
```

**Importante:**
- ✅ Fecha en formato `YYYYMMDD` (8 dígitos)
- ✅ Sin espacios ni caracteres especiales
- ✅ Extensión `.xlsx` (Excel)
- ✅ Un archivo por día

---

## 📊 Estructura de Datos

### Columnas OBLIGATORIAS

| # | Columna | Tipo | Ejemplo | Descripción |
|---|---------|------|---------|-------------|
| 1 | **codigo** | Texto | "12345" | Código del producto en ERP |
| 2 | **id_pallet** | Texto | "PAL12345" | Identificador único del pallet |
| 3 | **cantidad_negativa** | Número | -15.5 | Cantidad negativa (siempre < 0) |
| 4 | **fecha_reporte** | Fecha | 2025-10-21 | Fecha de la extracción |

---

### Columnas OPCIONALES (Recomendadas)

| # | Columna | Tipo | Ejemplo | Descripción |
|---|---------|------|---------|-------------|
| 5 | **nombre** | Texto | "Tornillo M8" | Nombre/descripción del producto |
| 6 | **almacen** | Texto | "ALM01" | Código del almacén/bodega |
| 7 | **disponible** | Número | -15.5 | Cantidad disponible |

---

### Ejemplo de Archivo Excel

**Hoja:** "Inventario" o "Sheet1" (cualquier nombre, pero siempre el mismo)

| codigo | nombre | almacen | id_pallet | cantidad_negativa | disponible | fecha_reporte |
|--------|--------|---------|-----------|-------------------|------------|---------------|
| PROD001 | Tornillo M8 x 25mm | ALM01 | PAL20251021001 | -15.5 | -15.5 | 2025-10-21 |
| PROD002 | Cable RJ45 Cat6 | ALM02 | PAL20251021002 | -23.0 | -23.0 | 2025-10-21 |
| PROD003 | Conector BNC | ALM01 | PAL20251021003 | -8.75 | -8.75 | 2025-10-21 |
| PROD004 | Resistencia 1K | BODEGA_CENTRAL | PAL20251021004 | -120.0 | -120.0 | 2025-10-21 |

---

## 🤖 Lógica del Bot

### Pseudocódigo

```python
# 1. Conectar a ERP
conexion_erp = conectar_erp()

# 2. Obtener fecha de hoy
fecha_hoy = obtener_fecha_actual()  # Ejemplo: 2025-10-21

# 3. Extraer datos de inventarios negativos
query = """
    SELECT 
        codigo_producto AS codigo,
        nombre_producto AS nombre,
        codigo_almacen AS almacen,
        id_pallet AS id_pallet,
        cantidad AS cantidad_negativa,
        cantidad AS disponible,
        '{fecha_hoy}' AS fecha_reporte
    FROM 
        inventarios_erp
    WHERE 
        cantidad < 0
"""
datos = ejecutar_query(conexion_erp, query)

# 4. Generar nombre de archivo
nombre_archivo = f"inventario_negativo_{fecha_hoy.replace('-', '')}.xlsx"
# Resultado: inventario_negativo_20251021.xlsx

# 5. Guardar Excel
guardar_excel(datos, nombre_archivo, hoja="Inventario")

# 6. Subir a SharePoint
ruta_sharepoint = "https://tuempresa.sharepoint.com/.../InventariosNegativos"
subir_archivo_sharepoint(nombre_archivo, ruta_sharepoint)

# 7. Log de éxito
print(f"✅ Archivo generado: {nombre_archivo}")
print(f"✅ Registros exportados: {len(datos)}")
```

---

## 🔧 Solución Temporal: Fecha en Nombre del Archivo

### Si NO pueden agregar columna `fecha_reporte`

**Workaround:**
- Solo pongan la fecha en el **nombre del archivo**
- Power BI puede extraerla automáticamente

**Ejemplo:**
```
Archivo: inventario_negativo_20251021.xlsx

Columnas en Excel:
| codigo | nombre | almacen | id_pallet | cantidad_negativa | disponible |
|--------|--------|---------|-----------|-------------------|------------|
| ... | ... | ... | ... | ... | ... |

Power BI extrae fecha del nombre: 2025-10-21
```

**Ventaja:** Más simple para implementar

**Desventaja:** Si mueven/renombran archivo, se pierde la fecha

---

## 📋 Reglas de Negocio

### 1. Solo Inventarios Negativos

```sql
WHERE cantidad < 0
```

**Importante:** NO incluir cantidades positivas o cero

---

### 2. Un Archivo por Día

**NO hacer:**
```
❌ inventario_negativo.xlsx  (sobreescribe cada día)
❌ inventario_20251021_v1.xlsx, inventario_20251021_v2.xlsx  (múltiples versiones)
```

**SÍ hacer:**
```
✅ inventario_negativo_20251021.xlsx  (único por día)
✅ inventario_negativo_20251022.xlsx  (siguiente día)
```

---

### 3. Formato de Fecha

**En columna `fecha_reporte`:**
```
Formato Excel: Fecha (Date)
Formato texto: YYYY-MM-DD
Ejemplos válidos:
  ✅ 2025-10-21
  ✅ 2025-10-01
  ✅ 2024-12-31

Ejemplos inválidos:
  ❌ 21/10/2025
  ❌ 21-10-2025
  ❌ 10/21/2025
```

**En nombre de archivo:**
```
Formato: YYYYMMDD (sin separadores)
Ejemplos válidos:
  ✅ 20251021
  ✅ 20251001
  ✅ 20241231

Ejemplos inválidos:
  ❌ 2025-10-21
  ❌ 21102025
  ❌ 102125
```

---

## 🕐 Programación del Bot

### Frecuencia

**Recomendado:** Diario

**Horario sugerido:**
```
6:00 AM - 7:00 AM (antes de inicio de jornada)
```

**Razón:** 
- Datos frescos al empezar el día
- Power BI puede actualizarse a las 7:30 AM
- Usuarios ven dashboard actualizado a las 8:00 AM

---

### Manejo de Errores

```python
try:
    # Generar y subir archivo
    generar_archivo_inventarios()
    
except ErrorConexionERP:
    enviar_alerta("No se pudo conectar al ERP")
    
except ErrorSinDatos:
    # Si no hay negativos, ¿subir archivo vacío o no subir?
    # RECOMENDACIÓN: Subir archivo con 0 registros
    generar_archivo_vacio()
    
except ErrorSharePoint:
    # Guardar localmente como backup
    guardar_local_backup()
    enviar_alerta("No se pudo subir a SharePoint")
```

---

## 📁 Ejemplo de Código Python (Bot)

### Con pandas y openpyxl

```python
import pandas as pd
from datetime import datetime
import pyodbc  # Para conectar a SQL Server / ERP

def generar_archivo_diario():
    # 1. Fecha de hoy
    fecha_hoy = datetime.now().date()
    fecha_str = fecha_hoy.strftime('%Y-%m-%d')
    fecha_archivo = fecha_hoy.strftime('%Y%m%d')
    
    # 2. Conectar a ERP (ejemplo SQL Server)
    conexion = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=servidor_erp;DATABASE=erp_db;UID=user;PWD=pass'
    )
    
    # 3. Query para extraer negativos
    query = f"""
        SELECT 
            codigo_producto AS codigo,
            nombre_producto AS nombre,
            codigo_almacen AS almacen,
            pallet_id AS id_pallet,
            cantidad_stock AS cantidad_negativa,
            cantidad_stock AS disponible,
            '{fecha_str}' AS fecha_reporte
        FROM 
            vw_inventario_actual
        WHERE 
            cantidad_stock < 0
    """
    
    # 4. Extraer datos
    df = pd.read_sql(query, conexion)
    conexion.close()
    
    # 5. Validar datos
    if len(df) == 0:
        print("⚠️ No hay inventarios negativos hoy")
        # Crear DataFrame vacío con columnas correctas
        df = pd.DataFrame(columns=['codigo', 'nombre', 'almacen', 'id_pallet', 
                                    'cantidad_negativa', 'disponible', 'fecha_reporte'])
    
    # 6. Nombre de archivo
    nombre_archivo = f"inventario_negativo_{fecha_archivo}.xlsx"
    
    # 7. Guardar Excel
    df.to_excel(nombre_archivo, index=False, sheet_name='Inventario')
    
    print(f"✅ Archivo generado: {nombre_archivo}")
    print(f"📊 Registros: {len(df)}")
    
    return nombre_archivo

# Ejecutar
archivo = generar_archivo_diario()
```

---

### Con Power Automate (Low-code)

```
Trigger: Recurrence (Diario a las 6:00 AM)
  ↓
Action: Execute SQL query (en ERP)
  Query: SELECT ... WHERE cantidad < 0
  ↓
Action: Create Excel table
  Table: Resultado de query anterior
  ↓
Action: Create file (SharePoint)
  Site: https://tuempresa.sharepoint.com/sites/Operaciones
  Folder: /InventariosNegativos
  File name: inventario_negativo_@{utcNow('yyyyMMdd')}.xlsx
  File content: Output del paso anterior
  ↓
Action: Send email (si hay error)
```

---

## 🔍 Validación de Archivos

### Checklist Post-Generación

```python
def validar_archivo(archivo_path):
    df = pd.read_excel(archivo_path)
    
    # 1. Verificar columnas obligatorias
    columnas_requeridas = ['codigo', 'id_pallet', 'cantidad_negativa', 'fecha_reporte']
    for col in columnas_requeridas:
        assert col in df.columns, f"❌ Falta columna: {col}"
    
    # 2. Verificar que todas las cantidades son negativas
    assert (df['cantidad_negativa'] < 0).all(), "❌ Hay cantidades no negativas"
    
    # 3. Verificar que no hay nulls en columnas clave
    assert df['codigo'].notna().all(), "❌ Hay códigos nulos"
    assert df['id_pallet'].notna().all(), "❌ Hay pallets nulos"
    
    # 4. Verificar formato de fecha
    assert pd.api.types.is_datetime64_any_dtype(df['fecha_reporte']), "❌ Fecha no es tipo Date"
    
    print("✅ Archivo válido")
    return True
```

---

## 📊 Métricas de Monitoreo

### Logs Recomendados

```
[2025-10-21 06:00:05] ▶️ Inicio de proceso
[2025-10-21 06:00:10] ✅ Conexión ERP exitosa
[2025-10-21 06:00:45] ✅ Query ejecutado: 487 registros extraídos
[2025-10-21 06:00:50] ✅ Archivo generado: inventario_negativo_20251021.xlsx
[2025-10-21 06:00:55] ✅ Archivo subido a SharePoint
[2025-10-21 06:01:00] ✅ Proceso completado (55 segundos)
```

### Dashboard de Monitoreo (Opcional)

| Métrica | Valor |
|---------|-------|
| Última ejecución | 2025-10-21 06:01:00 |
| Estado | ✅ Exitoso |
| Registros exportados | 487 |
| Tiempo de ejecución | 55 seg |
| Archivo generado | inventario_negativo_20251021.xlsx |
| Tamaño archivo | 45 KB |

---

## 🚨 Alertas

### Cuándo Enviar Alerta

| Condición | Severidad | Acción |
|-----------|-----------|--------|
| No se pudo conectar a ERP | 🔴 Crítico | Email inmediato a TI + Operaciones |
| No hay datos negativos (0 registros) | 🟡 Advertencia | Email informativo a Operaciones |
| Error al subir a SharePoint | 🟠 Alto | Email a TI, guardar backup local |
| Ejecución tarda > 10 min | 🟡 Advertencia | Log para investigar |

---

## ✅ Checklist de Implementación

### Para Sistemas

- [ ] ✅ Crear carpeta en SharePoint: `/InventariosNegativos`
- [ ] ✅ Dar permisos de escritura al bot/service account
- [ ] ✅ Configurar conexión a ERP (credenciales, firewall)
- [ ] ✅ Desarrollar query SQL para extraer negativos
- [ ] ✅ Implementar generación de archivo Excel
- [ ] ✅ Implementar subida a SharePoint
- [ ] ✅ Configurar ejecución programada (6:00 AM)
- [ ] ✅ Configurar logs y monitoreo
- [ ] ✅ Configurar alertas por email
- [ ] ✅ Probar con datos reales
- [ ] ✅ Generar 5-10 archivos de prueba (diferentes fechas)
- [ ] ✅ Validar con Power BI (que pueda leer y consolidar)
- [ ] ✅ Documentar proceso interno

---

## 📧 Entregables

### Fase 1: Pruebas (Esta semana)

```
✅ 10 archivos Excel de prueba
✅ Diferentes fechas (últimos 10 días)
✅ Subidos a carpeta SharePoint
✅ Validación de lectura en Power BI
```

### Fase 2: Automatización (Próximas 2 semanas)

```
✅ Bot funcionando en ambiente productivo
✅ Ejecución diaria exitosa
✅ Dashboard de monitoreo
✅ Documentación técnica
```

---

## 🔗 Recursos

**Documentos relacionados:**
- `GUIA_POWER_BI_CARPETA_LOCAL.md` - Cómo Power BI leerá estos archivos
- `MEDIDAS_DAX_POWERBI.md` - Análisis en Power BI
- `generar_archivos_prueba_powerbi.py` - Script para generar archivos de prueba

---

## 💬 Contacto

**Para dudas técnicas:**
- [Tu nombre/área]
- [Email/Teams]

**Timeline:**
- Archivos de prueba: [Fecha límite]
- Bot en producción: [Fecha límite]

---

**¡Éxito con la implementación! 🚀**