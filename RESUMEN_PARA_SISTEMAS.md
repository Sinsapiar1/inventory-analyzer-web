# 📋 Resumen Rápido para el Área de Sistemas

## 🎯 Objetivo

Generar archivos `.db` (SQLite) con inventarios negativos que sean compatibles con el Analizador de Inventarios v6.3.

---

## ✅ Requisitos Mínimos

### 1. Estructura de la Tabla

```sql
CREATE TABLE inventarios_negativos (
    codigo TEXT NOT NULL,           -- ← Código del producto
    id_pallet TEXT NOT NULL,        -- ← ID del pallet
    cantidad_negativa REAL NOT NULL,-- ← Cantidad (debe ser < 0)
    fecha_reporte DATE NOT NULL,    -- ← Fecha en formato YYYY-MM-DD
    nombre TEXT,                    -- Opcional: Nombre del producto
    almacen TEXT                    -- Opcional: Código de almacén
);
```

### 2. Mapeo desde ERP

**Tu tabla ERP → Tabla requerida:**

```sql
SELECT 
    codigo_articulo AS codigo,
    id_pallet AS id_pallet,
    inventario_fisico AS cantidad_negativa,
    CONVERT(VARCHAR(10), GETDATE(), 120) AS fecha_reporte,  -- SQL Server
    -- O: DATE('now') para SQLite
    -- O: CURDATE() para MySQL
    nombre_producto AS nombre,
    codigo_almacen AS almacen
FROM tu_tabla_inventario
WHERE inventario_fisico < 0  -- Solo negativos
  AND id_pallet IS NOT NULL;
```

### 3. Reglas Importantes

✅ **Solo registros negativos** (`cantidad_negativa < 0`)  
✅ **Formato de fecha:** `YYYY-MM-DD` (ejemplo: `2025-10-21`)  
✅ **Sin valores nulos** en: codigo, id_pallet, cantidad_negativa, fecha_reporte  
✅ **Nombre del archivo:** `inventarios_YYYYMMDD.db`

---

## 🚀 Ejemplo Rápido en Python

```python
import sqlite3
import pandas as pd

# 1. Leer datos del ERP (CSV, SQL, etc.)
df = pd.read_csv('datos_erp.csv')

# 2. Filtrar solo negativos
df = df[df['inventario_fisico'] < 0]

# 3. Renombrar columnas
df = df.rename(columns={
    'codigo_articulo': 'codigo',
    'id_pallet': 'id_pallet',
    'inventario_fisico': 'cantidad_negativa',
    'fecha': 'fecha_reporte'
})

# 4. Guardar a SQLite
conn = sqlite3.connect('inventarios_20251021.db')
df.to_sql('inventarios_negativos', conn, if_exists='replace', index=False)
conn.close()
```

---

## 📁 Archivos de Referencia

1. **`ESPECIFICACION_TECNICA_DB_SISTEMAS.md`** - Documentación completa (20+ páginas)
2. **`ejemplo_generacion_db_sistemas.py`** - Script ejecutable de ejemplo
3. Este archivo - Resumen rápido

---

## ✅ Checklist Antes de Entregar

- [ ] Tabla `inventarios_negativos` existe
- [ ] Solo registros con cantidad < 0
- [ ] Formato de fecha: YYYY-MM-DD
- [ ] Sin nulos en campos obligatorios
- [ ] Archivo probado en la app

---

## 📞 Contacto

**Responsable:** Raúl Pivet  
**Email:** [tu-email]

**¿Dudas?** Revisar `ESPECIFICACION_TECNICA_DB_SISTEMAS.md`
