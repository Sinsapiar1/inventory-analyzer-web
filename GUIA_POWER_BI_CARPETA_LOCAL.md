# 📊 Guía Power BI: Consolidar Múltiples Excel Automáticamente

## 🎯 Objetivo

Conectar Power BI a una **carpeta local** (o SharePoint) que contiene múltiples archivos Excel y consolidarlos automáticamente en un solo modelo de datos.

---

## 📁 PASO 1: Generar Archivos de Prueba

### Opción A: Usar el Script Python (RECOMENDADO)

```bash
# Ejecutar el script
python generar_archivos_prueba_powerbi.py
```

**Resultado:**
```
📁 Carpeta: ./datos_prueba_powerbi/
📄 Archivos: 30 archivos Excel
📅 Fechas: Últimos 30 días
📊 Registros: 50 por archivo = 1,500 registros totales
```

**Estructura de archivos generados:**

```
datos_prueba_powerbi/
├── inventario_negativo_20251021.xlsx
├── inventario_negativo_20251020.xlsx
├── inventario_negativo_20251019.xlsx
├── ...
└── inventario_negativo_20250921.xlsx
```

---

### Opción B: Crear Archivos Manualmente

Si prefieres hacerlo manual, cada archivo Excel debe tener:

**Nombre:** `inventario_negativo_YYYYMMDD.xlsx`

**Columnas:**

| codigo | nombre | almacen | id_pallet | cantidad_negativa | disponible | fecha_reporte |
|--------|--------|---------|-----------|-------------------|------------|---------------|
| PROD001 | Tornillo M8 | ALM01 | PAL001 | -15.5 | -15.5 | 2025-10-21 |
| PROD002 | Cable RJ45 | ALM02 | PAL002 | -23.0 | -23.0 | 2025-10-21 |

**Tips:**
- ✅ Usa **siempre las mismas columnas** en todos los archivos
- ✅ Mismo **orden de columnas** en todos
- ✅ Mismo **nombre de hoja** (ej: "Inventario" o "Sheet1")
- ✅ **Sin celdas vacías** en los encabezados

---

## 🔌 PASO 2: Conectar Power BI a la Carpeta

### 2.1 Abrir Power BI Desktop

1. Abrir **Power BI Desktop**
2. Click en **Inicio → Obtener datos**
3. Buscar: **"Carpeta"** o **"Folder"**

![Get Data - Folder](https://docs.microsoft.com/en-us/power-bi/connect-data/media/desktop-connect-to-folder/folder-icon.png)

---

### 2.2 Seleccionar la Carpeta

**Ruta de ejemplo:**

```
Windows: C:\Users\TuUsuario\datos_prueba_powerbi
Mac: /Users/TuUsuario/datos_prueba_powerbi
Linux: /home/usuario/datos_prueba_powerbi
```

**Importante:**
- ✅ Seleccionar la **carpeta** (no un archivo individual)
- ✅ Power BI escaneará **todos** los archivos dentro

---

### 2.3 Filtrar Archivos

Power BI mostrará **todos** los archivos de la carpeta. Necesitas filtrar:

```powerquery
// En Power Query Editor:
// Filtrar solo archivos .xlsx
1. Click en filtro de columna "Extension"
2. Seleccionar solo: ".xlsx"

// O filtrar por nombre
1. Click en filtro de columna "Name"
2. Filtro de texto → Contiene: "inventario"
```

---

### 2.4 Combinar Archivos (CLAVE)

**Esto es lo que consolida automáticamente todos los Excel:**

```
1. En la columna "Content", verás un ícono de tabla
2. Click en el botón "Combine Files" (Combinar archivos)
   (Aparece arriba o al hacer click derecho)
3. Power BI mostrará preview del primer archivo
4. Selecciona la hoja correcta (ej: "Inventario" o "Sheet1")
5. Click "OK"
```

**¡MAGIA! 🎉**

Power BI creará automáticamente:
- ✅ Una función que lee cualquier archivo con esa estructura
- ✅ Una consulta que aplica esa función a TODOS los archivos
- ✅ Una tabla consolidada con TODOS los datos

---

## 🛠️ PASO 3: Transformar Datos (Power Query)

### 3.1 Agregar Fecha de Captura (del nombre del archivo)

```powerquery
// Extraer fecha del nombre del archivo
// Ejemplo: "inventario_negativo_20251021.xlsx" → "2025-10-21"

= Table.AddColumn(
    #"Previous Step", 
    "Fecha_Archivo", 
    each Date.FromText(
        Text.Middle([Source.Name], 20, 4) & "-" &  // Año
        Text.Middle([Source.Name], 24, 2) & "-" &  // Mes
        Text.Middle([Source.Name], 26, 2)          // Día
    )
)
```

**Alternativa más simple:**

```powerquery
// Si el archivo ya tiene columna "fecha_reporte", úsala directamente
// No necesitas extraer del nombre
= #"Previous Step"
```

---

### 3.2 Eliminar Columnas Innecesarias

Power BI agregará columnas de metadata del archivo que no necesitas:

```powerquery
// Eliminar columnas:
= Table.RemoveColumns(
    #"Previous Step",
    {"Source.Name", "Folder Path", "Attributes", "Date accessed", "Date modified", "Date created"}
)
```

**Mantener solo:**
- codigo
- nombre
- almacen
- id_pallet
- cantidad_negativa
- disponible
- fecha_reporte (o Fecha_Archivo)

---

### 3.3 Cambiar Tipos de Datos

```powerquery
// Asegurar tipos correctos
= Table.TransformColumnTypes(
    #"Previous Step",
    {
        {"codigo", type text},
        {"nombre", type text},
        {"almacen", type text},
        {"id_pallet", type text},
        {"cantidad_negativa", type number},
        {"disponible", type number},
        {"fecha_reporte", type date}
    }
)
```

---

### 3.4 Filtrar Solo Negativos (por si acaso)

```powerquery
// Asegurar que solo haya valores negativos
= Table.SelectRows(
    #"Previous Step",
    each [cantidad_negativa] < 0
)
```

---

## 📊 PASO 4: Crear Modelo de Datos

### 4.1 Tabla Principal: `InventariosNegativos`

Ya la tienes de Power Query. Renombrarla si es necesario:

```
Click derecho en la consulta → Rename → "InventariosNegativos"
```

---

### 4.2 Tabla Calendario (Importante para análisis temporal)

```dax
// Crear nueva tabla en Power BI
Calendario = 
ADDCOLUMNS(
    CALENDAR(
        DATE(2024, 1, 1),
        DATE(2025, 12, 31)
    ),
    "Año", YEAR([Date]),
    "Mes", FORMAT([Date], "MMMM"),
    "Mes Num", MONTH([Date]),
    "Trimestre", "Q" & FORMAT([Date], "Q"),
    "Día Semana", FORMAT([Date], "dddd"),
    "Día Num", DAY([Date])
)
```

**Relación:**
```
Calendario[Date] → InventariosNegativos[fecha_reporte]
```

---

## 📐 PASO 5: Crear Medidas DAX

### 5.1 KPIs Básicos

```dax
// Total de Pallets Únicos
Total Pallets = 
DISTINCTCOUNT(InventariosNegativos[id_pallet])

// Pallets Activos (última fecha)
Pallets Activos Hoy = 
VAR UltimaFecha = MAX(InventariosNegativos[fecha_reporte])
RETURN
CALCULATE(
    DISTINCTCOUNT(InventariosNegativos[id_pallet]),
    InventariosNegativos[fecha_reporte] = UltimaFecha
)

// Total Cantidad Negativa
Total Negativo = 
SUM(InventariosNegativos[cantidad_negativa])

// Promedio Negativo
Promedio Negativo = 
AVERAGE(InventariosNegativos[cantidad_negativa])

// Total Productos Únicos
Total Productos = 
DISTINCTCOUNT(InventariosNegativos[codigo])
```

---

### 5.2 Análisis Temporal

```dax
// Días Promedio de Permanencia
Días Promedio = 
VAR TablaAgg = 
    SUMMARIZE(
        InventariosNegativos,
        InventariosNegativos[id_pallet],
        "Primera Fecha", MIN(InventariosNegativos[fecha_reporte]),
        "Última Fecha", MAX(InventariosNegativos[fecha_reporte])
    )
RETURN
AVERAGEX(
    TablaAgg,
    DATEDIFF([Primera Fecha], [Última Fecha], DAY) + 1
)

// Reincidencias (Pallets que aparecen en múltiples fechas)
Pallets Recurrentes = 
COUNTROWS(
    FILTER(
        SUMMARIZE(
            InventariosNegativos,
            InventariosNegativos[id_pallet],
            "Días Aparición", DISTINCTCOUNT(InventariosNegativos[fecha_reporte])
        ),
        [Días Aparición] > 1
    )
)
```

---

### 5.3 Severidad (Replicar tu lógica de Streamlit)

```dax
// Severidad por Pallet (columna calculada)
Severidad = 
VAR MagnitudActual = ABS(InventariosNegativos[cantidad_negativa])
VAR TablaMagnitudes = ALL(InventariosNegativos[cantidad_negativa])
VAR Q25 = PERCENTILE.INC(ABS(TablaMagnitudes), 0.25)
VAR Q50 = PERCENTILE.INC(ABS(TablaMagnitudes), 0.50)
VAR Q75 = PERCENTILE.INC(ABS(TablaMagnitudes), 0.75)
RETURN
SWITCH(
    TRUE(),
    MagnitudActual <= Q25, "Bajo",
    MagnitudActual <= Q50, "Medio",
    MagnitudActual <= Q75, "Alto",
    "Crítico"
)

// O como medida:
% Pallets Críticos = 
DIVIDE(
    COUNTROWS(
        FILTER(
            InventariosNegativos,
            InventariosNegativos[Severidad] = "Crítico"
        )
    ),
    COUNTROWS(InventariosNegativos),
    0
) * 100
```

---

### 5.4 Comparaciones Temporales

```dax
// Variación vs Día Anterior
Variación Diaria = 
VAR FechaActual = MAX(InventariosNegativos[fecha_reporte])
VAR FechaAnterior = FechaActual - 1
VAR CantidadHoy = 
    CALCULATE(
        [Total Pallets],
        InventariosNegativos[fecha_reporte] = FechaActual
    )
VAR CantidadAyer = 
    CALCULATE(
        [Total Pallets],
        InventariosNegativos[fecha_reporte] = FechaAnterior
    )
RETURN
CantidadHoy - CantidadAyer

// Variación Porcentual
% Variación = 
DIVIDE(
    [Variación Diaria],
    CALCULATE(
        [Total Pallets],
        InventariosNegativos[fecha_reporte] = MAX(InventariosNegativos[fecha_reporte]) - 1
    ),
    0
) * 100
```

---

## 🎨 PASO 6: Diseñar Dashboard

### Página 1: Overview General

**KPIs (Cards):**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total       │ Activos     │ Días        │ Total       │
│ Pallets     │ Hoy         │ Promedio    │ Negativo    │
│ [Medida]    │ [Medida]    │ [Medida]    │ [Medida]    │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Gráficos:**

1. **Evolución Temporal** (Line Chart)
   - Eje X: `fecha_reporte`
   - Eje Y: `Total Pallets`
   - Línea: `Total Negativo`

2. **Top 10 Productos Problemáticos** (Bar Chart)
   - Eje Y: `codigo` (Top 10)
   - Eje X: `Total Pallets`
   - Color: `Severidad`

3. **Distribución por Almacén** (Pie Chart)
   - Leyenda: `almacen`
   - Valores: `Total Pallets`

4. **Pallets por Severidad** (Stacked Bar)
   - Eje Y: `Severidad`
   - Eje X: `Count of id_pallet`

---

### Página 2: Análisis Detallado

**Tabla Dinámica:**

| Código | Nombre | Almacén | Total Pallets | Cantidad Promedio | Severidad |
|--------|--------|---------|---------------|-------------------|-----------|
| ... | ... | ... | ... | ... | ... |

**Filtros (Slicers):**
- Fecha (Date Range)
- Almacén (List)
- Severidad (List)
- Código (Searchable dropdown)

---

### Página 3: Reincidencias

**Matrix Visual:**

| Código | Fecha 1 | Fecha 2 | Fecha 3 | ... | Total Días |
|--------|---------|---------|---------|-----|------------|
| PROD001 | -15.5 | -12.3 | -18.0 | ... | 15 días |

**Heatmap:**
- Eje X: `fecha_reporte`
- Eje Y: `codigo`
- Valores: `cantidad_negativa`
- Color: Escala de severidad

---

## 🔄 PASO 7: Actualización Automática

### Cuando agregues nuevos archivos a la carpeta

```
1. Power BI Desktop → Inicio → Actualizar
   O
2. Presionar F5

Power BI automáticamente:
✅ Escanea la carpeta
✅ Detecta nuevos archivos
✅ Aplica las transformaciones
✅ Consolida todo
✅ Actualiza visuales
```

**¡NO necesitas cambiar NADA en Power Query!**

---

### Publicar en Power BI Service (Online)

```
1. Power BI Desktop → Archivo → Publicar
2. Seleccionar workspace
3. Publicar

En Power BI Service:
4. Configurar actualización programada:
   - Settings → Scheduled refresh
   - Frecuencia: Diaria (ej: 7:00 AM)
   
IMPORTANTE para carpeta local:
- Instalar Power BI Gateway
- Configurar Gateway para acceder a la carpeta local
```

---

## 🔄 PASO 8: Migrar a SharePoint (Cuando esté listo)

### Es MUY FÁCIL cambiar de carpeta local a SharePoint:

```powerquery
// En Power Query Editor:
1. Click en paso "Source" (primer paso)
2. Ver fórmula actual:
   = Folder.Files("C:\Users\...\datos_prueba_powerbi")
   
3. Cambiar a SharePoint:
   = SharePoint.Files(
       "https://tuempresa.sharepoint.com/sites/SiteName/Shared Documents/InventariosNegativos"
   )
   
4. Click "OK"
5. Autenticar con cuenta Office 365
6. ¡Listo! Todo lo demás funciona igual
```

**El resto del código NO cambia:**
- ✅ Filtros: igual
- ✅ Transformaciones: igual
- ✅ Medidas DAX: igual
- ✅ Visuales: igual

---

## 📋 Script Power Query Completo

```powerquery
let
    // 1. Conectar a carpeta (cambiar ruta según tu caso)
    Source = Folder.Files("C:\datos_prueba_powerbi"),
    
    // 2. Filtrar solo archivos Excel
    FiltrarExcel = Table.SelectRows(Source, each [Extension] = ".xlsx"),
    
    // 3. Filtrar por nombre (opcional)
    FiltrarNombre = Table.SelectRows(FiltrarExcel, each Text.Contains([Name], "inventario")),
    
    // 4. Invocar función de combinación personalizada
    // (Power BI crea esto automáticamente al hacer "Combine Files")
    InvokeCustomFunction = Table.AddColumn(FiltrarNombre, "Transform File", each #"Transform File"([Content])),
    
    // 5. Expandir columnas del archivo
    ExpandirDatos = Table.ExpandTableColumn(InvokeCustomFunction, "Transform File", 
        {"codigo", "nombre", "almacen", "id_pallet", "cantidad_negativa", "disponible", "fecha_reporte"}),
    
    // 6. Eliminar columnas innecesarias
    EliminarColumnas = Table.RemoveColumns(ExpandirDatos, 
        {"Content", "Folder Path", "Attributes", "Date accessed", "Date modified", "Date created"}),
    
    // 7. Renombrar columna de nombre de archivo
    RenombrarArchivo = Table.RenameColumns(EliminarColumnas, {{"Name", "archivo_origen"}}),
    
    // 8. Extraer fecha del nombre del archivo (backup por si no viene en los datos)
    AgregarFechaArchivo = Table.AddColumn(RenombrarArchivo, "Fecha_Archivo", 
        each Date.FromText(
            Text.Middle([archivo_origen], 20, 4) & "-" &
            Text.Middle([archivo_origen], 24, 2) & "-" &
            Text.Middle([archivo_origen], 26, 2)
        )),
    
    // 9. Usar fecha_reporte si existe, sino fecha del archivo
    AgregarFechaFinal = Table.AddColumn(AgregarFechaArchivo, "fecha_final",
        each if [fecha_reporte] <> null then [fecha_reporte] else [Fecha_Archivo]),
    
    // 10. Eliminar columnas temporales
    LimpiarColumnas = Table.RemoveColumns(AgregarFechaFinal, {"fecha_reporte", "Fecha_Archivo"}),
    
    // 11. Renombrar fecha final
    RenombrarFecha = Table.RenameColumns(LimpiarColumnas, {{"fecha_final", "fecha_reporte"}}),
    
    // 12. Cambiar tipos de datos
    CambiarTipos = Table.TransformColumnTypes(RenombrarFecha, {
        {"codigo", type text},
        {"nombre", type text},
        {"almacen", type text},
        {"id_pallet", type text},
        {"cantidad_negativa", type number},
        {"disponible", type number},
        {"fecha_reporte", type date},
        {"archivo_origen", type text}
    }),
    
    // 13. Filtrar solo negativos
    FiltrarNegativos = Table.SelectRows(CambiarTipos, each [cantidad_negativa] < 0),
    
    // 14. Ordenar por fecha y código
    Ordenar = Table.Sort(FiltrarNegativos, {{"fecha_reporte", Order.Descending}, {"codigo", Order.Ascending}})
in
    Ordenar
```

---

## ✅ Checklist Final

### Antes de diseñar dashboard:

- [ ] ✅ Carpeta con archivos Excel creada
- [ ] ✅ Power BI conectado a carpeta
- [ ] ✅ Archivos combinados automáticamente
- [ ] ✅ Columna `fecha_reporte` existe
- [ ] ✅ Todos los archivos tienen mismas columnas
- [ ] ✅ Tipos de datos correctos
- [ ] ✅ Tabla Calendario creada
- [ ] ✅ Relación Calendario ↔ InventariosNegativos
- [ ] ✅ Medidas DAX básicas creadas

### Pruebas:

- [ ] ✅ Agregar 1 archivo nuevo → Actualizar → Verifica que aparece
- [ ] ✅ Modificar 1 archivo → Actualizar → Verifica cambios
- [ ] ✅ Eliminar 1 archivo → Actualizar → Verifica que desaparece
- [ ] ✅ Visuales se actualizan correctamente

---

## 🎯 Ventajas de Este Método

| Ventaja | Descripción |
|---------|-------------|
| **Automático** | Solo "Actualizar" para procesar nuevos archivos |
| **Escalable** | Funciona con 10 o 10,000 archivos |
| **Flexible** | Mismo método para carpeta local o SharePoint |
| **Rápido** | Power BI optimiza lectura en paralelo |
| **Mantenible** | Una vez configurado, no necesitas tocarlo |

---

## 💡 Tips Finales

### 1. Rendimiento

Si tienes **muchos archivos** (100+):

```powerquery
// Agregar parámetro para filtrar fechas
// Solo procesar últimos N días
= Table.SelectRows(
    FiltrarExcel,
    each [Date modified] >= Date.AddDays(DateTime.LocalNow(), -90)
)
```

### 2. Validación

Agregar columna de validación:

```powerquery
= Table.AddColumn(
    #"Previous Step",
    "Es_Valido",
    each [cantidad_negativa] < 0 and [id_pallet] <> null and [codigo] <> null
)
```

Luego filtrar por `Es_Valido = true`

### 3. Metadata

Agregar columnas útiles:

```powerquery
= Table.AddColumn(#"Previous Step", "Año_Mes", each Date.ToText([fecha_reporte], "yyyy-MM"))
= Table.AddColumn(#"Previous Step", "Semana_Año", each Date.WeekOfYear([fecha_reporte]))
```

---

## 🚀 ¡Listo para Empezar!

**Orden de ejecución:**

```
1. Ejecutar: generar_archivos_prueba_powerbi.py
2. Abrir Power BI Desktop
3. Obtener datos → Carpeta → Seleccionar carpeta
4. Combinar archivos
5. Aplicar transformaciones (copiar script M)
6. Crear tabla Calendario
7. Crear medidas DAX
8. Diseñar dashboard
9. Probar agregar archivos nuevos
10. Publicar en Power BI Service
```

**Cuando SharePoint esté listo:**
```
11. Cambiar Source en Power Query
12. Re-autenticar
13. ¡Todo funciona igual!
```

---

**¿Dudas? ¡Pregunta! 😊**