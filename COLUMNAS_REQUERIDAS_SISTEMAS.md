# 📋 Columnas Requeridas para Archivo .db (Sistemas)

## 🎯 Resumen Ejecutivo

El archivo `.db` debe tener **UNA tabla** llamada: `inventarios_negativos`

---

## ✅ Columnas OBLIGATORIAS (Mínimo)

| Columna | Tipo | Ejemplo | Descripción |
|---------|------|---------|-------------|
| **codigo** | TEXTO | "12345" | Código del producto en ERP |
| **id_pallet** | TEXTO | "PAL12345" | Identificador del pallet |
| **cantidad_negativa** | NÚMERO | -15.0 | Cantidad negativa (siempre < 0) |
| **fecha_reporte** | FECHA | "2025-10-21" | Fecha del reporte |

---

## 📊 Columnas OPCIONALES (Recomendadas)

| Columna | Tipo | Ejemplo | Descripción |
|---------|------|---------|-------------|
| **nombre** | TEXTO | "Tornillo M8" | Nombre del producto |
| **almacen** | TEXTO | "ALM01" | Código del almacén |
| **disponible** | NÚMERO | -15.0 | Cantidad disponible |

---

## 📝 SQL Mínimo

```sql
CREATE TABLE inventarios_negativos (
    codigo TEXT NOT NULL,
    id_pallet TEXT NOT NULL,
    cantidad_negativa REAL NOT NULL,
    fecha_reporte DATE NOT NULL,
    nombre TEXT,
    almacen TEXT,
    disponible REAL
);
```

---

## 🔍 Reglas Importantes

1. ✅ Solo incluir registros **negativos** (`cantidad_negativa < 0`)
2. ✅ `fecha_reporte` en formato: `YYYY-MM-DD` (ej: `2025-10-21`)
3. ✅ Archivo con extensión: `.db` o `.sqlite`
4. ✅ Codificación: UTF-8

---

## 📧 Email para Sistemas (Copiar y Pegar)

```
Asunto: Requerimiento - Archivo .db Inventarios Negativos

Hola equipo de Sistemas,

Necesito que me generen un archivo .db (SQLite) con los inventarios negativos 
del ERP. El archivo debe contener:

TABLA: inventarios_negativos

COLUMNAS OBLIGATORIAS:
- codigo (texto)
- id_pallet (texto)  
- cantidad_negativa (número, siempre negativo)
- fecha_reporte (fecha YYYY-MM-DD)

COLUMNAS OPCIONALES:
- nombre (texto)
- almacen (texto)
- disponible (número)

REGLA: Solo incluir registros donde el inventario sea negativo (< 0)

FORMATO: Archivo .db o .sqlite con codificación UTF-8

¿Es posible? Adjunto especificación técnica completa: ESPECIFICACION_TECNICA_DB_SISTEMAS.md

Gracias,
[Tu nombre]
```

---

## 📎 Documentos Completos

Para más detalles, ver:
- `ESPECIFICACION_TECNICA_DB_SISTEMAS.md` - Especificación completa
- `ejemplo_generacion_db_sistemas.py` - Código de ejemplo
- `RESUMEN_PARA_SISTEMAS.md` - Resumen técnico

---

**¿Dudas?** Mostrarles `ESPECIFICACION_TECNICA_DB_SISTEMAS.md` que tiene ejemplos y código SQL completo.