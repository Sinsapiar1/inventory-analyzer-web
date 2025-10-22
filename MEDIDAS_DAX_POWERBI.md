# 📐 Medidas DAX para Power BI
## Replicar Análisis de Inventarios Negativos

---

## 📋 Instrucciones

Copiar y pegar estas medidas en Power BI Desktop:

```
1. Panel derecho → Campos
2. Click derecho en tabla "InventariosNegativos"
3. "Nueva medida"
4. Copiar código DAX
5. Enter
```

---

## 🎯 KPIs Principales

### Total Pallets
```dax
Total Pallets = 
DISTINCTCOUNT(InventariosNegativos[id_pallet])
```

### Pallets Activos (Última Fecha)
```dax
Pallets Activos = 
VAR UltimaFecha = MAX(InventariosNegativos[fecha_reporte])
RETURN
CALCULATE(
    DISTINCTCOUNT(InventariosNegativos[id_pallet]),
    InventariosNegativos[fecha_reporte] = UltimaFecha
)
```

### Total Cantidad Negativa
```dax
Total Negativo = 
SUM(InventariosNegativos[cantidad_negativa])
```

### Días Promedio de Permanencia
```dax
Días Promedio = 
VAR TablaResumen = 
    SUMMARIZE(
        InventariosNegativos,
        InventariosNegativos[id_pallet],
        "PrimeraFecha", MIN(InventariosNegativos[fecha_reporte]),
        "UltimaFecha", MAX(InventariosNegativos[fecha_reporte])
    )
RETURN
AVERAGEX(
    TablaResumen,
    DATEDIFF([PrimeraFecha], [UltimaFecha], DAY) + 1
)
```

---

## 📊 Análisis de Reincidencias

### Total de Reincidencias
```dax
Total Reincidencias = 
COUNTROWS(
    FILTER(
        SUMMARIZE(
            InventariosNegativos,
            InventariosNegativos[id_pallet],
            "DiasAparicion", DISTINCTCOUNT(InventariosNegativos[fecha_reporte])
        ),
        [DiasAparicion] > 1
    )
)
```

### % Pallets Recurrentes
```dax
% Pallets Recurrentes = 
DIVIDE(
    [Total Reincidencias],
    [Total Pallets],
    0
) * 100
```

### Días de Aparición por Pallet (Columna Calculada)
```dax
Días Aparición = 
CALCULATE(
    DISTINCTCOUNT(InventariosNegativos[fecha_reporte]),
    ALLEXCEPT(InventariosNegativos, InventariosNegativos[id_pallet])
)
```

---

## 📈 Análisis Temporal

### Variación vs Día Anterior
```dax
Variación Diaria = 
VAR FechaSeleccionada = MAX(InventariosNegativos[fecha_reporte])
VAR FechaAnterior = FechaSeleccionada - 1
VAR PalletsHoy = 
    CALCULATE(
        [Total Pallets],
        InventariosNegativos[fecha_reporte] = FechaSeleccionada
    )
VAR PalletsAyer = 
    CALCULATE(
        [Total Pallets],
        InventariosNegativos[fecha_reporte] = FechaAnterior
    )
RETURN
IF(
    ISBLANK(PalletsAyer),
    BLANK(),
    PalletsHoy - PalletsAyer
)
```

### % Variación
```dax
% Variación Diaria = 
VAR Var = [Variación Diaria]
VAR FechaAnterior = MAX(InventariosNegativos[fecha_reporte]) - 1
VAR PalletsAyer = 
    CALCULATE(
        [Total Pallets],
        InventariosNegativos[fecha_reporte] = FechaAnterior
    )
RETURN
IF(
    ISBLANK(PalletsAyer) || PalletsAyer = 0,
    BLANK(),
    DIVIDE(Var, PalletsAyer, 0) * 100
)
```

### Promedio Móvil 7 Días
```dax
Promedio Móvil 7D = 
CALCULATE(
    [Total Pallets],
    DATESINPERIOD(
        Calendario[Date],
        MAX(Calendario[Date]),
        -7,
        DAY
    )
) / 7
```

---

## 🎨 Severidad

### Severidad (Columna Calculada)
```dax
Severidad = 
VAR MagnitudActual = ABS(InventariosNegativos[cantidad_negativa])
VAR TodasMagnitudes = 
    CALCULATETABLE(
        VALUES(InventariosNegativos[cantidad_negativa]),
        ALL(InventariosNegativos)
    )
VAR Q25 = PERCENTILE.INC(ABS(TodasMagnitudes), 0.25)
VAR Q50 = PERCENTILE.INC(ABS(TodasMagnitudes), 0.50)
VAR Q75 = PERCENTILE.INC(ABS(TodasMagnitudes), 0.75)
RETURN
SWITCH(
    TRUE(),
    MagnitudActual <= Q25, "Bajo",
    MagnitudActual <= Q50, "Medio",
    MagnitudActual <= Q75, "Alto",
    "Crítico"
)
```

### Pallets por Severidad (Medidas)
```dax
Pallets Críticos = 
CALCULATE(
    [Total Pallets],
    InventariosNegativos[Severidad] = "Crítico"
)

Pallets Alto = 
CALCULATE(
    [Total Pallets],
    InventariosNegativos[Severidad] = "Alto"
)

Pallets Medio = 
CALCULATE(
    [Total Pallets],
    InventariosNegativos[Severidad] = "Medio"
)

Pallets Bajo = 
CALCULATE(
    [Total Pallets],
    InventariosNegativos[Severidad] = "Bajo"
)
```

---

## 📊 Top N Análisis

### Top 10 Productos
```dax
Top 10 Productos = 
VAR Top10Codigos = 
    TOPN(
        10,
        SUMMARIZE(
            InventariosNegativos,
            InventariosNegativos[codigo],
            "TotalPallets", [Total Pallets]
        ),
        [TotalPallets],
        DESC
    )
RETURN
IF(
    SELECTEDVALUE(InventariosNegativos[codigo]) IN VALUES(Top10Codigos[codigo]),
    [Total Pallets],
    BLANK()
)
```

---

## 🏭 Análisis por Almacén

### Almacenes Activos
```dax
Almacenes Activos = 
DISTINCTCOUNT(InventariosNegativos[almacen])
```

### Promedio Negativo por Almacén
```dax
Promedio por Almacén = 
AVERAGEX(
    VALUES(InventariosNegativos[almacen]),
    CALCULATE(SUM(InventariosNegativos[cantidad_negativa]))
)
```

---

## 📅 Tabla Calendario (Crear como tabla nueva)

```dax
Calendario = 
VAR MinFecha = DATE(2024, 1, 1)
VAR MaxFecha = DATE(2025, 12, 31)
RETURN
ADDCOLUMNS(
    CALENDAR(MinFecha, MaxFecha),
    "Año", YEAR([Date]),
    "Año-Mes", FORMAT([Date], "YYYY-MM"),
    "Mes", FORMAT([Date], "MMMM"),
    "Mes Num", MONTH([Date]),
    "Trimestre", "Q" & QUARTER([Date]),
    "Semana Año", WEEKNUM([Date]),
    "Día Semana", FORMAT([Date], "dddd"),
    "Día Num", DAY([Date]),
    "Es Fin Semana", IF(WEEKDAY([Date]) IN {1, 7}, "Sí", "No"),
    "Nombre Corto Mes", FORMAT([Date], "MMM")
)
```

**Relación:** `Calendario[Date]` → `InventariosNegativos[fecha_reporte]`

---

## 🔢 Medidas Auxiliares

### Rango de Fechas
```dax
Rango Fechas = 
"Desde: " & FORMAT(MIN(InventariosNegativos[fecha_reporte]), "DD/MM/YYYY") & 
" hasta: " & FORMAT(MAX(InventariosNegativos[fecha_reporte]), "DD/MM/YYYY")
```

### Total Registros
```dax
Total Registros = 
COUNTROWS(InventariosNegativos)
```

### Cantidad Promedio
```dax
Cantidad Promedio = 
AVERAGE(InventariosNegativos[cantidad_negativa])
```

### Cantidad Mínima (más negativo)
```dax
Más Negativo = 
MIN(InventariosNegativos[cantidad_negativa])
```

---

## 🎯 Indicadores de Tendencia

### Tendencia (vs mes anterior)
```dax
Tendencia = 
VAR MesActual = [Total Pallets]
VAR MesAnterior = 
    CALCULATE(
        [Total Pallets],
        DATEADD(Calendario[Date], -1, MONTH)
    )
RETURN
SWITCH(
    TRUE(),
    ISBLANK(MesAnterior), "Sin datos",
    MesActual > MesAnterior, "📈 Aumentó",
    MesActual < MesAnterior, "📉 Disminuyó",
    "➡️ Igual"
)
```

### Índice de Mejora
```dax
Índice Mejora = 
VAR PrimerMes = 
    CALCULATE(
        [Total Pallets],
        FIRSTDATE(Calendario[Date])
    )
VAR UltimoMes = 
    CALCULATE(
        [Total Pallets],
        LASTDATE(Calendario[Date])
    )
RETURN
IF(
    PrimerMes = 0,
    BLANK(),
    DIVIDE(UltimoMes - PrimerMes, PrimerMes, 0) * 100
)
```

---

## 📊 Formatos Condicionales (para usar en visuales)

### Color por Severidad (Medida)
```dax
Color Severidad = 
VAR Sev = SELECTEDVALUE(InventariosNegativos[Severidad])
RETURN
SWITCH(
    Sev,
    "Crítico", "#FF0000",    // Rojo
    "Alto", "#FF6B00",       // Naranja oscuro
    "Medio", "#FFA500",      // Naranja
    "Bajo", "#FFD700",       // Amarillo
    "#CCCCCC"                // Gris por defecto
)
```

### Alerta (por cantidad)
```dax
Alerta = 
VAR Cant = SUM(InventariosNegativos[cantidad_negativa])
RETURN
SWITCH(
    TRUE(),
    Cant < -100, "🔴 Crítico",
    Cant < -50, "🟠 Alto",
    Cant < -20, "🟡 Medio",
    "🟢 Bajo"
)
```

---

## 💡 Tips de Uso

### 1. Crear Jerarquía de Fechas

```
Calendario
├── Año
│   ├── Trimestre
│   │   ├── Mes
│   │   │   └── Date
```

**Cómo:**
1. Click derecho en `Calendario[Año]`
2. "Crear jerarquía"
3. Arrastrar Trimestre, Mes, Date dentro

### 2. Ordenar Meses

```dax
// Mes ordenado por número
Mes [Ordenar por: Mes Num]
```

### 3. Formato de Medidas

| Medida | Formato |
|--------|---------|
| Total Pallets | Número entero |
| Total Negativo | Número decimal (2 decimales) |
| % Variación | Porcentaje (1 decimal) |
| Días Promedio | Número entero |

---

## 🎨 Visualizaciones Recomendadas

### Dashboard Principal

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Card        │ Card        │ Card        │ Card        │
│ Total       │ Activos     │ Días        │ Total       │
│ Pallets     │ Hoy         │ Promedio    │ Negativo    │
└─────────────┴─────────────┴─────────────┴─────────────┘

┌───────────────────────────────┬─────────────────────────┐
│ Line Chart                    │ Pie Chart               │
│ Evolución Temporal            │ Por Severidad           │
│ X: fecha_reporte              │ Valores: Total Pallets  │
│ Y: Total Pallets              │ Leyenda: Severidad      │
└───────────────────────────────┴─────────────────────────┘

┌───────────────────────────────┬─────────────────────────┐
│ Bar Chart                     │ Donut Chart             │
│ Top 10 Productos              │ Por Almacén             │
│ Y: codigo (Top 10)            │ Valores: Total Pallets  │
│ X: Total Pallets              │ Leyenda: almacen        │
└───────────────────────────────┴─────────────────────────┘
```

---

## ✅ Checklist de Implementación

- [ ] ✅ Crear tabla `Calendario`
- [ ] ✅ Crear relación con `InventariosNegativos`
- [ ] ✅ Copiar columna calculada `Severidad`
- [ ] ✅ Copiar columna calculada `Días Aparición`
- [ ] ✅ Copiar medidas KPIs básicos (4 medidas)
- [ ] ✅ Copiar medidas de reincidencias (3 medidas)
- [ ] ✅ Copiar medidas temporales (3 medidas)
- [ ] ✅ Copiar medidas de severidad (4 medidas)
- [ ] ✅ Configurar formatos de medidas
- [ ] ✅ Crear jerarquía de fechas
- [ ] ✅ Probar con datos de prueba

---

**¡Todas estas medidas replican exactamente tu app Streamlit en Power BI! 🎉**