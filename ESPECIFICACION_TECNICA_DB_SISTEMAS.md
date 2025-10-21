# 📋 Especificación Técnica: Base de Datos para Integración ERP

## 🎯 Objetivo

Este documento describe los requisitos técnicos para que el **área de sistemas** genere archivos `.db` (SQLite) compatibles con el **Analizador de Inventarios Negativos v6.3**.

---

## 📦 Información General

**Versión de la App:** 6.3 Database Edition  
**Tipo de Base de Datos:** SQLite 3  
**Extensión del archivo:** `.db`, `.sqlite`, o `.sqlite3`  
**Codificación:** UTF-8  
**Fecha de este documento:** Octubre 2025

---

## 🗄️ Estructura de la Base de Datos

### Tabla Requerida: `inventarios_negativos`

Esta es la **única tabla requerida**. Debe contener los registros de inventarios negativos extraídos del ERP.

```sql
CREATE TABLE inventarios_negativos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL,
    nombre TEXT,
    almacen TEXT,
    id_pallet TEXT NOT NULL,
    cantidad_negativa REAL NOT NULL,
    disponible REAL,
    fecha_reporte DATE NOT NULL,
    archivo_origen TEXT,
    fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📊 Descripción de Columnas

| Columna | Tipo | Requerido | Descripción | Ejemplo |
|---------|------|-----------|-------------|---------|
| **id** | INTEGER | Sí (PK) | Identificador único autoincremental | 1, 2, 3... |
| **codigo** | TEXT | **Sí** | Código del producto/artículo en el ERP | "12345", "PROD001" |
| **nombre** | TEXT | No | Nombre o descripción del producto | "Tornillo M8", "Cable RJ45" |
| **almacen** | TEXT | No | Código o nombre del almacén | "ALM01", "BODEGA_CENTRAL" |
| **id_pallet** | TEXT | **Sí** | Identificador del pallet | "PAL12345", "PLT-001" |
| **cantidad_negativa** | REAL | **Sí** | Cantidad negativa del inventario (debe ser < 0) | -15.0, -23.5 |
| **disponible** | REAL | No | Cantidad disponible (puede ser igual a cantidad_negativa) | -15.0, -23.5 |
| **fecha_reporte** | DATE | **Sí** | Fecha del reporte/extracción desde ERP | "2025-10-21" |
| **archivo_origen** | TEXT | No | Nombre del archivo o proceso origen | "ERP_EXPORT_20251021" |
| **fecha_extraccion** | TIMESTAMP | No | Timestamp de cuando se extrajo el dato | "2025-10-21 16:30:00" |

### Campos Obligatorios (NOT NULL)

**Mínimo requerido para que funcione:**
- ✅ `codigo`
- ✅ `id_pallet`
- ✅ `cantidad_negativa`
- ✅ `fecha_reporte`

**Campos opcionales pero recomendados:**
- `nombre` - Para mejor legibilidad
- `almacen` - Para filtros por ubicación
- `disponible` - Para análisis adicional
- `archivo_origen` - Para trazabilidad
- `fecha_extraccion` - Para auditoría

---

## 🔑 Índices Recomendados (Opcional pero Mejora Rendimiento)

```sql
CREATE INDEX idx_fecha ON inventarios_negativos(fecha_reporte);
CREATE INDEX idx_codigo ON inventarios_negativos(codigo);
CREATE INDEX idx_pallet ON inventarios_negativos(id_pallet);
CREATE INDEX idx_almacen ON inventarios_negativos(almacen);
```

**Beneficio:** Consultas hasta 10x más rápidas con grandes volúmenes de datos.

---

## 📝 Reglas de Negocio

### 1. Solo Inventarios Negativos

**Importante:** La tabla debe contener **SOLO** registros donde `cantidad_negativa < 0`.

```sql
-- Filtro al insertar
INSERT INTO inventarios_negativos (...)
SELECT ...
FROM tabla_erp
WHERE inventario_fisico < 0;  -- Solo negativos
```

### 2. Formato de Fechas

**Formato requerido:** `YYYY-MM-DD` (ISO 8601)

```sql
-- Ejemplos válidos
'2025-10-21'
'2025-01-15'
'2024-12-31'

-- Ejemplos NO válidos
'21-10-2025'  ❌
'10/21/2025'  ❌
'21/Oct/2025' ❌
```

### 3. Valores Nulos

**Permitidos en:**
- `nombre`
- `almacen`
- `disponible`
- `archivo_origen`
- `fecha_extraccion`

**NO permitidos (deben tener valor):**
- `codigo`
- `id_pallet`
- `cantidad_negativa`
- `fecha_reporte`

---

## 🔄 Mapeo desde Tablas ERP

Suponiendo que el ERP tiene una tabla con estructura diferente, aquí está el mapeo:

### Ejemplo de Query SQL para Extraer desde ERP

```sql
CREATE TABLE inventarios_negativos AS
SELECT 
    -- Dejar que SQLite genere el ID automáticamente
    codigo_articulo AS codigo,                    -- ← Mapeo desde ERP
    nombre_producto AS nombre,                    -- ← Mapeo desde ERP
    codigo_almacen AS almacen,                    -- ← Mapeo desde ERP
    id_pallet AS id_pallet,                       -- ← Mapeo desde ERP
    inventario_fisico AS cantidad_negativa,       -- ← Mapeo desde ERP
    fisica_disponible AS disponible,              -- ← Mapeo desde ERP
    DATE('now') AS fecha_reporte,                 -- ← Fecha actual
    'ERP_AUTOMATICO' AS archivo_origen,           -- ← Identificador
    DATETIME('now') AS fecha_extraccion           -- ← Timestamp actual
FROM 
    tabla_inventario_erp                          -- ← Tu tabla en ERP
WHERE 
    inventario_fisico < 0                         -- ✅ FILTRO: Solo negativos
    AND id_pallet IS NOT NULL                     -- ✅ FILTRO: Con pallet válido
    AND id_pallet != '';                          -- ✅ FILTRO: Pallet no vacío
```

### Personaliza el Mapeo

**Reemplaza estos nombres según tu ERP:**

| Columna en App | Nombre en tu ERP | Ejemplo |
|----------------|------------------|---------|
| `codigo` | `codigo_articulo` | "SKU", "ITEM_CODE", "PRODUCT_ID" |
| `nombre` | `nombre_producto` | "DESCRIPTION", "ITEM_NAME" |
| `almacen` | `codigo_almacen` | "WAREHOUSE", "LOCATION_CODE" |
| `id_pallet` | `id_pallet` | "PALLET_ID", "LICENSE_PLATE" |
| `cantidad_negativa` | `inventario_fisico` | "QTY_ON_HAND", "STOCK_QTY" |
| `disponible` | `fisica_disponible` | "AVAILABLE_QTY" |

---

## 🤖 Script de Ejemplo para SQL Server Agent

Si usan **SQL Server**, aquí hay un ejemplo de job que genera el `.db`:

### Paso 1: Exportar a CSV desde SQL Server

```sql
-- Job Step 1: Exportar datos a CSV
DECLARE @sql NVARCHAR(MAX)
DECLARE @fecha_hoy VARCHAR(8) = CONVERT(VARCHAR(8), GETDATE(), 112)  -- YYYYMMDD

SET @sql = '
EXEC xp_cmdshell ''bcp "
SELECT 
    codigo_articulo,
    nombre_producto,
    codigo_almacen,
    id_pallet,
    inventario_fisico,
    fisica_disponible,
    CONVERT(VARCHAR(10), GETDATE(), 120) AS fecha_reporte,
    ''''ERP_EXPORT_'' + ''' + @fecha_hoy + ''' + ''''' AS archivo_origen,
    GETDATE() AS fecha_extraccion
FROM mi_base_datos.dbo.inventario
WHERE inventario_fisico < 0 
  AND id_pallet IS NOT NULL
" queryout C:\temp\inventario_' + @fecha_hoy + '.csv -c -t, -T -S localhost''
'

EXEC sp_executesql @sql
```

### Paso 2: Convertir CSV a SQLite usando Python

```python
#!/usr/bin/env python3
"""
Script para convertir CSV del ERP a SQLite .db
Para SQL Server Agent o Task Scheduler
"""

import sqlite3
import pandas as pd
from datetime import datetime
import sys

def csv_to_sqlite(csv_path, db_path):
    """Convierte CSV exportado del ERP a SQLite .db"""
    
    # Leer CSV
    df = pd.read_csv(csv_path)
    
    # Renombrar columnas al formato esperado
    df = df.rename(columns={
        'codigo_articulo': 'codigo',
        'nombre_producto': 'nombre',
        'codigo_almacen': 'almacen',
        'id_pallet': 'id_pallet',
        'inventario_fisico': 'cantidad_negativa',
        'fisica_disponible': 'disponible',
        'fecha_reporte': 'fecha_reporte',
        'archivo_origen': 'archivo_origen',
        'fecha_extraccion': 'fecha_extraccion'
    })
    
    # Validaciones
    assert (df['cantidad_negativa'] < 0).all(), "Hay valores no negativos"
    assert df['codigo'].notna().all(), "Hay códigos nulos"
    assert df['id_pallet'].notna().all(), "Hay pallets nulos"
    
    # Crear base de datos SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventarios_negativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            nombre TEXT,
            almacen TEXT,
            id_pallet TEXT NOT NULL,
            cantidad_negativa REAL NOT NULL,
            disponible REAL,
            fecha_reporte DATE NOT NULL,
            archivo_origen TEXT,
            fecha_extraccion TIMESTAMP
        )
    ''')
    
    # Crear índices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fecha ON inventarios_negativos(fecha_reporte)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_codigo ON inventarios_negativos(codigo)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pallet ON inventarios_negativos(id_pallet)')
    
    # Insertar datos
    df.to_sql('inventarios_negativos', conn, if_exists='append', index=False)
    
    # Commit y cerrar
    conn.commit()
    conn.close()
    
    print(f"✅ Archivo {db_path} creado exitosamente")
    print(f"   Registros: {len(df)}")
    return True

if __name__ == '__main__':
    fecha_hoy = datetime.now().strftime('%Y%m%d')
    csv_file = f'C:\\temp\\inventario_{fecha_hoy}.csv'
    db_file = f'C:\\exportaciones\\inventarios_{fecha_hoy}.db'
    
    csv_to_sqlite(csv_file, db_file)
```

---

## 🔄 Actualización Incremental (Día a Día)

Para **actualizar el mismo archivo .db** día a día (en lugar de crear uno nuevo cada día):

### Opción 1: Agregar solo nuevos registros

```python
def actualizar_db_incremental(db_path, nuevos_datos_csv):
    """Agrega nuevos datos sin duplicar"""
    
    conn = sqlite3.connect(db_path)
    df = pd.read_csv(nuevos_datos_csv)
    
    # Procesar y renombrar columnas (igual que arriba)
    # ...
    
    # Agregar solo los nuevos
    df.to_sql('inventarios_negativos', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()
```

### Opción 2: Reemplazar datos de una fecha específica

```sql
-- Primero eliminar datos de la fecha
DELETE FROM inventarios_negativos 
WHERE fecha_reporte = '2025-10-21';

-- Luego insertar los nuevos
INSERT INTO inventarios_negativos (...)
VALUES (...);
```

---

## ✅ Validación del Archivo .db

Antes de enviar el archivo, valida que cumple con los requisitos:

### Script de Validación

```python
#!/usr/bin/env python3
"""Valida que el archivo .db cumple con las especificaciones"""

import sqlite3
import sys

def validar_db(db_path):
    """Valida estructura y datos del archivo .db"""
    
    errores = []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar que existe la tabla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventarios_negativos'")
        if not cursor.fetchone():
            errores.append("❌ Tabla 'inventarios_negativos' no existe")
            return errores
        
        # 2. Verificar columnas requeridas
        cursor.execute("PRAGMA table_info(inventarios_negativos)")
        columnas = {row[1] for row in cursor.fetchall()}
        
        requeridas = {'codigo', 'id_pallet', 'cantidad_negativa', 'fecha_reporte'}
        faltantes = requeridas - columnas
        if faltantes:
            errores.append(f"❌ Faltan columnas: {faltantes}")
        
        # 3. Verificar que hay datos
        cursor.execute("SELECT COUNT(*) FROM inventarios_negativos")
        count = cursor.fetchone()[0]
        if count == 0:
            errores.append("⚠️ La tabla está vacía")
        else:
            print(f"✅ {count} registros encontrados")
        
        # 4. Verificar valores negativos
        cursor.execute("SELECT COUNT(*) FROM inventarios_negativos WHERE cantidad_negativa >= 0")
        no_negativos = cursor.fetchone()[0]
        if no_negativos > 0:
            errores.append(f"❌ {no_negativos} registros tienen cantidad_negativa >= 0")
        
        # 5. Verificar nulos en campos requeridos
        cursor.execute("SELECT COUNT(*) FROM inventarios_negativos WHERE codigo IS NULL")
        if cursor.fetchone()[0] > 0:
            errores.append("❌ Hay registros con 'codigo' nulo")
        
        cursor.execute("SELECT COUNT(*) FROM inventarios_negativos WHERE id_pallet IS NULL")
        if cursor.fetchone()[0] > 0:
            errores.append("❌ Hay registros con 'id_pallet' nulo")
        
        # 6. Verificar formato de fechas
        cursor.execute("SELECT fecha_reporte FROM inventarios_negativos LIMIT 1")
        fecha_ejemplo = cursor.fetchone()[0]
        print(f"✅ Formato de fecha ejemplo: {fecha_ejemplo}")
        
        conn.close()
        
        if not errores:
            print("\n✅ ¡VALIDACIÓN EXITOSA! El archivo cumple con todos los requisitos.")
            return True
        else:
            print("\n❌ ERRORES ENCONTRADOS:")
            for error in errores:
                print(f"   {error}")
            return False
            
    except Exception as e:
        errores.append(f"❌ Error al abrir archivo: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python validar_db.py ruta/al/archivo.db")
        sys.exit(1)
    
    db_file = sys.argv[1]
    validar_db(db_file)
```

**Uso:**
```bash
python validar_db.py inventarios_20251021.db
```

---

## 📤 Entrega del Archivo

### Nombre del Archivo

**Formato recomendado:**
```
inventarios_YYYYMMDD.db
inventarios_consolidado_YYYYMMDD.db
```

**Ejemplos:**
```
inventarios_20251021.db
inventarios_consolidado_20251021.db
inventarios_mes_octubre_2025.db
```

### Ubicación de Entrega

Opciones:
1. **Compartir en red**: `\\servidor\compartido\inventarios\`
2. **Email** (si es < 10 MB)
3. **SharePoint / OneDrive**
4. **FTP / SFTP**
5. **API REST** (para automatización avanzada)

---

## 🧪 Archivo de Prueba

Para validar la integración, el área de sistemas debería:

1. **Generar un archivo .db de prueba** con 5-10 registros
2. **Enviar al usuario** para validar
3. **Usuario prueba** en la app
4. **Si funciona**, proceder con producción

### Datos de Prueba (SQL)

```sql
INSERT INTO inventarios_negativos 
    (codigo, nombre, almacen, id_pallet, cantidad_negativa, disponible, fecha_reporte, archivo_origen)
VALUES 
    ('PROD001', 'Producto Prueba 1', 'ALM01', 'PAL001', -10.0, -10.0, '2025-10-21', 'PRUEBA'),
    ('PROD002', 'Producto Prueba 2', 'ALM02', 'PAL002', -15.5, -15.5, '2025-10-21', 'PRUEBA'),
    ('PROD003', 'Producto Prueba 3', 'ALM01', 'PAL003', -5.0, -5.0, '2025-10-21', 'PRUEBA'),
    ('PROD004', 'Producto Prueba 4', 'ALM03', 'PAL004', -20.0, -20.0, '2025-10-21', 'PRUEBA'),
    ('PROD005', 'Producto Prueba 5', 'ALM02', 'PAL005', -8.0, -8.0, '2025-10-21', 'PRUEBA');
```

---

## 📞 Soporte y Contacto

**Responsable de la App:** Raúl Pivet  
**Email:** [tu-email]  
**Documentación:** Ver `GUIA_BASE_DE_DATOS.md` para uso de la app

**Preguntas del Área de Sistemas:**
- ¿Dudas sobre estructura de la tabla? → Revisar sección "Estructura de la Base de Datos"
- ¿Problemas con mapeo? → Revisar sección "Mapeo desde Tablas ERP"
- ¿Validación falla? → Ejecutar script de validación

---

## ✅ Checklist para el Área de Sistemas

Antes de entregar el primer archivo .db en producción:

- [ ] Tabla `inventarios_negativos` creada con estructura correcta
- [ ] Columnas requeridas: `codigo`, `id_pallet`, `cantidad_negativa`, `fecha_reporte`
- [ ] Solo registros con `cantidad_negativa < 0`
- [ ] Formato de fecha: `YYYY-MM-DD`
- [ ] Sin valores nulos en columnas obligatorias
- [ ] Índices creados (opcional pero recomendado)
- [ ] Archivo .db validado con script de validación
- [ ] Archivo de prueba enviado y aprobado por usuario
- [ ] Proceso automatizado documentado
- [ ] Frecuencia de actualización definida (diaria, semanal, etc.)

---

## 🎯 Resumen Ejecutivo

**Para que el área de sistemas genere archivos .db compatibles, necesitan:**

1. ✅ Crear tabla `inventarios_negativos` con estructura especificada
2. ✅ Mapear columnas del ERP a los nombres requeridos
3. ✅ Filtrar solo registros negativos (`cantidad_negativa < 0`)
4. ✅ Usar formato de fecha ISO: `YYYY-MM-DD`
5. ✅ Validar el archivo antes de entregar
6. ✅ Generar archivo con nombre descriptivo: `inventarios_YYYYMMDD.db`

**Resultado esperado:** Archivo `.db` listo para usar directamente en la app sin procesamiento adicional.

---

**Versión del Documento:** 1.0  
**Fecha:** Octubre 2025  
**Compatibilidad:** Analizador de Inventarios v6.3+
