# 📏 Límites de Archivos .db según Plataforma de Despliegue

## 🎯 Resumen Rápido

| Plataforma | Límite de Upload | Límite de Almacenamiento | Recomendación |
|------------|-----------------|--------------------------|---------------|
| **Streamlit Cloud** | 200 MB | ~1 GB (app completa) | ✅ Óptimo para archivos < 100 MB |
| **GitHub Codespaces** | 200 MB (config) | Ilimitado | ✅ Ideal para desarrollo |
| **Render** | 500 MB | 10 GB (Free tier) | ✅ Buena opción |
| **Railway** | Sin límite específico | 5 GB (Free tier) | ✅ Excelente |
| **Heroku** | 500 MB | 512 MB (Free) / 1 GB+ (Paid) | ⚠️ Limitado |
| **VPS Propio** | Ilimitado | Según plan | ✅ Máximo control |

---

## 📊 Streamlit Cloud (GRATUITO - Recomendado)

### Límites
- **Upload de archivo:** 200 MB por defecto (configurable en `config.toml`)
- **Tamaño de app total:** ~1 GB (incluye código + datos + dependencias)
- **Memoria RAM:** 1 GB (Free tier)
- **CPU:** Compartida

### Recomendación para Archivos .db
✅ **Ideal:** Archivos < 100 MB  
⚠️ **Aceptable:** Archivos 100-200 MB  
❌ **No recomendado:** Archivos > 200 MB

### Configuración para Aumentar Límite
```toml
# .streamlit/config.toml o config.toml
[server]
maxUploadSize = 500  # En MB (máximo recomendado: 500 MB)
```

**Nota:** Aunque puedas configurar 500 MB, el rendimiento puede degradarse con archivos muy grandes.

### Estimación de Tamaño de .db

| Registros | Tamaño Aproximado .db | Equivalente en Excel |
|-----------|----------------------|----------------------|
| 1,000 | ~200 KB | 10 archivos pequeños |
| 10,000 | ~2 MB | 100 archivos pequeños |
| 50,000 | ~10 MB | 500 archivos pequeños |
| 100,000 | ~20 MB | 1,000 archivos pequeños |
| 500,000 | ~100 MB | 5,000 archivos pequeños |
| 1,000,000 | ~200 MB | 10,000 archivos pequeños |

**Tu caso (79 archivos con ~7,400 registros):**
- Tamaño esperado: **~1.5-3 MB** ✅ Perfecto para Streamlit Cloud

---

## 🚀 GitHub Codespaces

### Límites
- **Upload:** Configurado en la app (200 MB por defecto)
- **Almacenamiento:** Ilimitado (incluido en GitHub)
- **Memoria RAM:** Variable según plan (default: 4 GB)

### Ideal Para
✅ Desarrollo y pruebas  
✅ Archivos de cualquier tamaño  
✅ No apto para producción (se apaga después de inactividad)

---

## 🎨 Render (GRATUITO)

### Límites Free Tier
- **Upload:** 500 MB
- **Almacenamiento:** 10 GB
- **Memoria RAM:** 512 MB
- **Inactividad:** App se apaga después de 15 min sin uso

### Recomendación
✅ **Excelente alternativa a Streamlit Cloud**  
✅ Soporta archivos más grandes  
⚠️ Puede ser más lento en arranque

**Configuración:**
```bash
# render.yaml
services:
  - type: web
    name: inventory-analyzer
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT
```

---

## 🚂 Railway (GRATUITO con créditos)

### Límites Free Tier
- **Upload:** Sin límite explícito
- **Almacenamiento:** 5 GB
- **Memoria RAM:** 512 MB - 8 GB (según plan)
- **Créditos mensuales:** $5 USD gratis

### Recomendación
✅ **Muy buena opción**  
✅ Generoso con almacenamiento  
✅ Rápido y confiable

**Nota:** Los $5 de crédito alcanzan para ~500 horas de ejecución al mes.

---

## 🟪 Heroku (LIMITADO en Free Tier)

### Límites Free Tier
- **Upload:** 500 MB
- **Almacenamiento (slug size):** 512 MB
- **Memoria RAM:** 512 MB
- **Dyno sleep:** Se apaga después de 30 min sin uso

### Recomendación
⚠️ **No recomendado para archivos grandes**  
✅ OK para archivos < 50 MB

---

## 💻 VPS Propio (AWS, DigitalOcean, Linode)

### Límites
- **Upload:** Lo que configures
- **Almacenamiento:** Según el plan contratado
- **Memoria RAM:** Según el plan
- **CPU:** Dedicada

### Recomendación
✅ **Ideal si tienes presupuesto**  
✅ Control total  
✅ Sin límites de tamaño

**Costos aproximados:**
- DigitalOcean Droplet básico: $5-10 USD/mes
- AWS EC2 t2.micro: ~$10 USD/mes
- Linode: $5 USD/mes

---

## 📈 Escenarios Reales

### Escenario 1: 79 Archivos Excel (~7,400 registros)
**Tu caso actual:**
- Tamaño .db: ~1.5 MB ✅
- **Plataformas viables:** Todas
- **Recomendación:** Streamlit Cloud (gratis)

---

### Escenario 2: 1 Año de Datos (~90,000 registros)
**Estimación:**
- 365 archivos Excel
- Tamaño .db: ~18 MB ✅
- **Plataformas viables:** Todas
- **Recomendación:** Streamlit Cloud o Render

---

### Escenario 3: 5 Años de Datos (~450,000 registros)
**Estimación:**
- 1,825 archivos Excel
- Tamaño .db: ~90 MB ✅
- **Plataformas viables:** Todas
- **Recomendación:** Railway o Render (más margen)

---

### Escenario 4: 10 Años de Datos (~900,000 registros)
**Estimación:**
- 3,650 archivos Excel
- Tamaño .db: ~180 MB ⚠️
- **Plataformas viables:** Railway, Render, VPS
- **Recomendación:** Railway (5 GB de storage)

---

### Escenario 5: Datos Masivos (>1,000,000 registros)
**Estimación:**
- Tamaño .db: >200 MB ❌
- **Plataformas viables:** VPS propio
- **Recomendación:** 
  - VPS con PostgreSQL
  - O dividir datos por año
  - O usar paginación/filtros

---

## 🛠️ Optimización de Tamaño

### 1. Comprimir el Archivo .db

```bash
# Después de generar el .db
sqlite3 inventarios.db "VACUUM;"

# Esto puede reducir 20-30% el tamaño
```

### 2. Eliminar Datos Antiguos

```sql
-- Mantener solo últimos 2 años
DELETE FROM inventarios_negativos 
WHERE fecha_reporte < DATE('now', '-2 years');

VACUUM;
```

### 3. Dividir por Período

```python
# Crear archivos .db separados por año
inventarios_2023.db  # ~20 MB
inventarios_2024.db  # ~20 MB
inventarios_2025.db  # ~20 MB
```

**En la app:** Subir el archivo del año que quieres analizar.

---

## 🔧 Configuración Recomendada para Producción

### Opción 1: Streamlit Cloud (Gratis, Archivos < 100 MB)

```toml
# config.toml
[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### Opción 2: Railway (Archivos < 500 MB)

```toml
# config.toml
[server]
maxUploadSize = 500
port = $PORT

[browser]
serverAddress = "0.0.0.0"
```

### Opción 3: VPS Propio (Sin límites)

```toml
# config.toml
[server]
maxUploadSize = 2000  # 2 GB
port = 8501
address = "0.0.0.0"

[browser]
serverAddress = "tu-dominio.com"
```

---

## 📊 Monitoreo de Tamaño

### Script para Verificar Tamaño de .db

```python
import os

def check_db_size(db_path):
    """Verifica el tamaño del archivo .db"""
    size_bytes = os.path.getsize(db_path)
    size_mb = size_bytes / (1024 * 1024)
    
    print(f"Tamaño del archivo: {size_mb:.2f} MB")
    
    if size_mb < 50:
        print("✅ Óptimo para todas las plataformas")
    elif size_mb < 100:
        print("✅ Bueno para Streamlit Cloud")
    elif size_mb < 200:
        print("⚠️ Límite para Streamlit Cloud, ok para Railway/Render")
    else:
        print("❌ Requiere VPS o dividir datos")
    
    return size_mb

# Uso
check_db_size("inventarios_20251021.db")
```

---

## 💡 Recomendación Final

**Para tu caso (79 archivos, ~1.5 MB):**

1. ✅ **Usa Streamlit Cloud** (gratis, perfecto para tu tamaño)
2. ✅ Configura `maxUploadSize = 200` en `config.toml`
3. ✅ A medida que crezca, considera:
   - < 100 MB: Sigue en Streamlit Cloud
   - 100-500 MB: Migra a Railway o Render
   - > 500 MB: VPS propio o divide por año

**Para el área de sistemas:**
- Archivos .db diarios: ~100-500 KB cada uno
- Consolidado anual: ~10-20 MB
- Sin problemas de tamaño

---

## 📞 Resumen por Pregunta

### "¿Los archivos .db tienen límite de peso cuando esté desplegado?"

**Respuesta corta:** Sí, pero depende de la plataforma.

**Tu caso específico:**
- Archivo .db actual: ~1.5 MB
- **No tienes problema en NINGUNA plataforma** ✅
- Incluso con 5 años de datos (~90 MB) seguirás sin problemas

**Límite práctico en Streamlit Cloud:**
- Por defecto: 200 MB
- Configurable hasta: 500 MB
- Recomendado: < 100 MB para mejor rendimiento

**Conclusión:** Con tus 79 archivos no te preocupes, tienes mucho margen. 🎉

---

**Última actualización:** Octubre 2025  
**Versión del documento:** 1.0
