# 🗄️ Guía Rápida: Base de Datos en Analizador de Inventarios v6.3

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [¿Por qué usar Base de Datos?](#por-qué-usar-base-de-datos)
3. [Paso a Paso: Consolidar Excel → Base de Datos](#paso-a-paso-consolidar-excel--base-de-datos)
4. [Paso a Paso: Analizar desde Base de Datos](#paso-a-paso-analizar-desde-base-de-datos)
5. [Agregar Datos Nuevos](#agregar-datos-nuevos)
6. [Preguntas Frecuentes](#preguntas-frecuentes)
7. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

La versión 6.3 del Analizador de Inventarios introduce la capacidad de **consolidar múltiples archivos Excel en una base de datos SQLite** (archivo `.db`), permitiendo:

- ✅ Manejar 100+ archivos Excel históricos fácilmente
- ✅ Análisis más rápido (un solo archivo vs. múltiples Excel)
- ✅ Preparación para integración con ERP del área de sistemas
- ✅ Mantener todo el historial en un solo archivo compacto

---

## ¿Por qué usar Base de Datos?

### Antes (Solo Excel)

```
📁 Inventarios/
├── 📄 reporte_all_20251001.xlsx
├── 📄 reporte_all_20251002.xlsx
├── 📄 reporte_all_20251003.xlsx
├── 📄 ... (100+ archivos)
└── 📄 reporte_all_20251031.xlsx

Problemas:
- ❌ Difícil de manejar 100+ archivos
- ❌ Subir todos cada vez que quieres analizar
- ❌ Lento con muchos archivos
- ❌ Difícil de compartir
```

### Ahora (Con Base de Datos)

```
📁 Inventarios/
└── 💾 inventarios_octubre_2025.db (un solo archivo)

Ventajas:
- ✅ Un solo archivo consolidado
- ✅ Carga más rápida
- ✅ Fácil de compartir y respaldar
- ✅ Preparado para ERP
```

---

## Paso a Paso: Consolidar Excel → Base de Datos

### Objetivo
Convertir múltiples archivos Excel en un solo archivo `.db`.

### Paso 1: Preparar Archivos

1. Reúne todos los archivos Excel que quieres consolidar
2. Verifica que tengan el formato correcto:
   - Nombre: `reporte_all_YYYYMMDD_*.xlsx`
   - Segunda hoja: "Inventario Completo (Actual)"
   - Columnas: Código, Nombre, Almacén, ID de Pallet, Inventario Físico

**Ejemplo de nombres válidos:**
```
✅ reporte_all_20251021_131737.xlsx
✅ reporte_all_20251020_142619.xlsx
✅ inventario_20251019.xlsx
❌ reporte_sin_fecha.xlsx (sin fecha en nombre)
```

### Paso 2: Abrir la Aplicación

1. Inicia la aplicación (local o en la nube)
2. En la **barra lateral izquierda**, busca **"🎯 Modo de Operación"**
3. Selecciona **"🗄️ Consolidar Excel → Base de Datos"**

### Paso 3: Configurar Parámetros

1. **📋 Índice de hoja a procesar:**
   - Por defecto: `1` (segunda hoja)
   - Ajusta si tus datos están en otra hoja

2. **💾 Nombre del archivo .db:**
   - Por defecto: `inventarios_consolidados_YYYYMMDD.db`
   - Personaliza según tu necesidad (ejemplo: `inventarios_octubre_2025.db`)

### Paso 4: Subir Archivos Excel

1. Haz clic en **"📁 Subir archivos Excel para consolidar"**
2. Selecciona todos los archivos que quieres consolidar
   - Puedes seleccionar 100+ archivos a la vez
   - Usa Ctrl+A para seleccionar todos en una carpeta
3. Espera a que carguen (verás el contador de archivos)

### Paso 5: Iniciar Consolidación

1. Haz clic en **"🚀 Iniciar Consolidación"**
2. Verás el progreso en tiempo real:
   ```
   10:30:45 - Procesando 1/150: reporte_all_20251001.xlsx
   10:30:45 -   ✅ reporte_all_20251001.xlsx: 25 registros agregados
   10:30:46 - Procesando 2/150: reporte_all_20251002.xlsx
   ...
   ```

3. Al terminar, verás estadísticas:
   ```
   ┌──────────────────┬──────────────┬─────────────┬──────────────────┐
   │ Total Archivos   │ Procesados   │ Con Errores │ Total Registros  │
   ├──────────────────┼──────────────┼─────────────┼──────────────────┤
   │      150         │     148      │      2      │      3,542       │
   └──────────────────┴──────────────┴─────────────┴──────────────────┘
   ```

### Paso 6: Descargar Archivo .db

1. Haz clic en **"📥 Descargar Archivo .db"**
2. El archivo se descargará a tu carpeta de descargas
3. Guarda este archivo en un lugar seguro

**¡Listo!** Ya tienes tu base de datos consolidada.

---

## Paso a Paso: Analizar desde Base de Datos

### Objetivo
Analizar inventarios usando el archivo `.db` consolidado.

### Paso 1: Abrir Modo de Análisis

1. En la **barra lateral izquierda**, busca **"🎯 Modo de Operación"**
2. Selecciona **"💾 Analizar desde Base de Datos"**

### Paso 2: Subir Archivo .db

1. Haz clic en **"📁 Subir archivo .db consolidado"**
2. Selecciona el archivo `.db` que descargaste anteriormente
3. Espera a que cargue

### Paso 3: Configurar Análisis

En la **barra lateral**, configura:

1. **🔝 Top N para análisis:** (5-50)
   - Cuántos pallets más críticos mostrar

2. **🔍 Filtros:**
   - **Almacén:** Específico o "Todos"
   - **Severidad:** Crítico, Alto, Medio, Bajo o "Todas"
   - **Estado:** Activo, Resuelto o "Todos"

### Paso 4: Ejecutar Análisis

1. Haz clic en **"🚀 Ejecutar Análisis desde DB"**
2. Espera mientras procesa (será más rápido que con múltiples Excel)
3. Verás mensaje de éxito

### Paso 5: Explorar Resultados

**KPIs Principales:**
```
┌─────────────┬──────────────┬──────────────┬─────────────┐
│ Total       │ Activos Hoy  │ Días         │ Total       │
│ Pallets     │              │ Promedio     │ Negativo    │
└─────────────┴──────────────┴──────────────┴─────────────┘
```

**Gráficos:**
- Top N Pallets Críticos
- Evolución Total
- Distribución por Almacén
- Distribución por Severidad

**Tabs:**
1. **📊 Análisis Principal:** Tabla completa con severidades
2. **🔄 Reincidencias:** Pallets que reaparecen
3. **📈 Súper Análisis:** Evolución temporal con filtros avanzados
4. **📋 Datos Crudos:** Registros sin procesar

### Paso 6: Descargar Reportes

En la parte inferior:

1. **📊 Descargar Reporte Excel:**
   - 6 hojas con análisis completo
   - Listo para imprimir

2. **📄 Descargar CSV:**
   - Tabla de análisis principal
   - Para procesamiento externo

---

## Agregar Datos Nuevos

### Escenario
Tienes un archivo `.db` del mes pasado y nuevos archivos Excel del mes actual.

### Opción 1: Análisis Temporal (Sin Guardar)

**Usa esto si solo quieres analizar sin actualizar el .db permanentemente.**

1. Modo: **"💾 Analizar desde Base de Datos"**
2. Sube el archivo `.db` existente
3. Marca **"➕ Agregar más archivos Excel a esta base de datos"**
4. Sube los nuevos archivos Excel
5. Haz clic en **"🚀 Ejecutar Análisis desde DB"**
6. El análisis incluirá todos los datos (históricos + nuevos)

**Resultado:** Análisis completo, pero el `.db` original no se modifica.

### Opción 2: Actualización Permanente (Regenerar .db)

**Usa esto si quieres actualizar el .db permanentemente.**

1. Modo: **"🗄️ Consolidar Excel → Base de Datos"**
2. Sube **TODOS** los archivos Excel (históricos + nuevos)
   - Puedes incluir los archivos que ya estaban en el .db anterior
   - Agrega los nuevos archivos del mes actual
3. Haz clic en **"🚀 Iniciar Consolidación"**
4. Descarga el nuevo archivo `.db`

**Resultado:** Nuevo archivo `.db` con todos los datos actualizados.

---

## Preguntas Frecuentes

### ¿Qué formato deben tener los archivos Excel?

**Nombre del archivo:**
- Formato: `reporte_all_YYYYMMDD_HHMMSS.xlsx`
- Ejemplo: `reporte_all_20251021_131737.xlsx`
- La fecha (YYYYMMDD) es obligatoria para extracción automática

**Contenido:**
- Segunda hoja (índice 1): "Inventario Completo (Actual)"
- Columnas requeridas:
  - Código / Código Producto
  - Nombre / Descripción
  - Almacén / Warehouse
  - ID de Pallet / Pallet ID
  - Inventario Físico / Cantidad

### ¿Cuántos archivos puedo consolidar?

**Límite teórico:** Sin límite específico.

**Límite práctico:**
- **Navegador:** Hasta ~500 archivos (por memoria del navegador)
- **Tamaño total:** Hasta 200 MB por defecto (configurable)
- **Recomendación:** 50-200 archivos por consolidación

**Si tienes 500+ archivos:**
- Consolida en lotes (ejemplo: por trimestre)
- Luego consolida los `.db` resultantes

### ¿Qué pasa si un archivo tiene error?

El sistema es robusto:
- ✅ Continúa con los demás archivos
- ✅ Reporta el error específico
- ✅ Muestra estadísticas de errores al final
- ✅ Genera el `.db` con los archivos exitosos

**Ejemplo de reporte:**
```
⚠️ Ver detalles de errores (2 archivos)
- reporte_all_20251005.xlsx: Falta columna "Código"
- reporte_all_20251010.xlsx: Hoja no encontrada
```

### ¿Puedo usar archivos .db del área de sistemas?

**¡Sí!** La aplicación está preparada para recibir archivos `.db` de cualquier fuente, incluyendo:
- ✅ `.db` generados por esta misma aplicación
- ✅ `.db` generados por scripts del ERP
- ✅ `.db` creados manualmente (si siguen la estructura correcta)

**Requisitos:**
- Tabla: `inventarios_negativos`
- Columnas mínimas: codigo, nombre, almacen, id_pallet, cantidad_negativa, fecha_reporte

### ¿Cómo verifico qué datos tiene mi archivo .db?

**Opción 1: Usar la aplicación**
1. Modo: "💾 Analizar desde Base de Datos"
2. Sube el `.db`
3. Ejecuta análisis
4. Ve a tab "📋 Datos Crudos"

**Opción 2: Herramienta externa**
- Descarga [DB Browser for SQLite](https://sqlitebrowser.org/)
- Abre el archivo `.db`
- Explora la tabla `inventarios_negativos`

---

## Solución de Problemas

### Error: "No se pudieron procesar archivos válidos"

**Causa:** Ningún archivo tiene el formato correcto.

**Solución:**
1. Verifica que los archivos sean `.xlsx` o `.xls`
2. Verifica que tengan la segunda hoja con datos
3. Verifica que tengan las columnas requeridas
4. Verifica que el índice de hoja sea correcto (por defecto: 1)

---

### Error: "Error al leer la base de datos"

**Causa:** El archivo `.db` está corrupto o tiene formato incorrecto.

**Solución:**
1. Regenera el archivo `.db` desde los Excel originales
2. Verifica que el archivo se descargó completamente
3. Asegúrate de que el archivo es un `.db` generado por esta aplicación

---

### No se extraen fechas correctamente

**Causa:** El nombre del archivo no tiene el formato esperado.

**Solución:**
1. Renombra los archivos para incluir fecha en formato YYYYMMDD
2. Ejemplo: `inventario.xlsx` → `inventario_20251021.xlsx`
3. Si no es posible, el sistema usará la fecha actual

**Formato válido del nombre:**
```
✅ reporte_all_20251021_131737.xlsx
✅ inventario_20251015.xlsx
✅ stock_negativo_20251010.xlsx
❌ reporte_octubre.xlsx (sin fecha)
❌ inv_2025-10-21.xlsx (formato incorrecto, debe ser YYYYMMDD sin guiones)
```

---

### El archivo .db es muy grande

**Causa:** Muchos registros o archivos duplicados.

**Solución:**
1. **Elimina duplicados:** Asegúrate de no consolidar el mismo archivo dos veces
2. **Filtra datos:** Modifica el procesamiento para incluir solo datos recientes
3. **Divide el historial:** Crea varios `.db` por período (ejemplo: uno por mes)

**Tamaños esperados:**
- 100 archivos × 30 registros = ~1-2 MB
- 500 archivos × 50 registros = ~5-10 MB
- 1000 archivos × 100 registros = ~15-25 MB

---

### Quiero editar o eliminar datos del .db

**Solución Actual (v6.3):**
La aplicación no tiene editor de `.db` integrado.

**Opciones:**
1. **Regenerar .db:** Excluye los archivos Excel que no quieres
2. **Usar DB Browser for SQLite:** Herramienta externa para editar
   - Descarga: https://sqlitebrowser.org/
   - Abre el `.db`
   - Edita la tabla `inventarios_negativos`
   - Guarda cambios

**Próximamente (v6.4):**
Se planea agregar funcionalidades de edición directa desde la aplicación.

---

## 🎯 Casos de Uso Recomendados

### Caso 1: Primera Consolidación

**Situación:** Tienes 180 archivos Excel de 6 meses.

**Pasos:**
1. Modo: "🗄️ Consolidar Excel → Base de Datos"
2. Sube todos los 180 archivos
3. Nombre: `inventarios_2024_H2.db`
4. Consolida
5. Descarga `.db`

**Resultado:** 1 archivo de ~10 MB con todo el historial.

---

### Caso 2: Análisis Mensual

**Situación:** Necesitas analizar los últimos 30 días.

**Pasos:**
1. Modo: "💾 Analizar desde Base de Datos"
2. Sube el `.db` consolidado
3. Configura filtros si es necesario
4. Ejecuta análisis
5. Explora resultados

**Resultado:** Análisis completo en segundos.

---

### Caso 3: Actualización Quincenal

**Situación:** Cada 15 días llegan nuevos archivos Excel.

**Opción A - Análisis Rápido (sin guardar):**
1. Modo: "💾 Analizar desde Base de Datos"
2. Sube `.db` anterior
3. Marca "➕ Agregar más archivos Excel"
4. Sube nuevos Excel
5. Analiza

**Opción B - Actualización Permanente:**
1. Modo: "🗄️ Consolidar Excel → Base de Datos"
2. Sube Excel anteriores + nuevos
3. Genera nuevo `.db`
4. Reemplaza el anterior

---

## 📞 Soporte

Si tienes problemas:

1. **Consulta esta guía** primero
2. **Revisa README.md** para más detalles
3. **Revisa CHANGELOG_v6.3.md** para cambios técnicos
4. **Contacta soporte** si persiste el problema

---

## 🚀 Siguientes Pasos

Ahora que conoces las funcionalidades de base de datos:

1. ✅ Consolida tu historial de Excel en un `.db`
2. ✅ Analiza desde el `.db` para ver la diferencia de velocidad
3. ✅ Comparte esta guía con tu equipo
4. ✅ Prepárate para recibir archivos `.db` del área de sistemas

---

**¡Éxito con tus análisis! 🎉**

---

*Desarrollado por: Raúl Pivet Álvarez*  
*Versión: 6.3 Database Edition*  
*Fecha: Octubre 2025*
