# 🚀 Guía de Despliegue en Streamlit Cloud

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Archivos Necesarios](#archivos-necesarios)
3. [Pasos de Despliegue](#pasos-de-despliegue)
4. [Configuración Avanzada](#configuración-avanzada)
5. [Límites y Consideraciones](#límites-y-consideraciones)
6. [Verificación Post-Despliegue](#verificación-post-despliegue)
7. [Troubleshooting](#troubleshooting)
8. [Actualización de la App](#actualización-de-la-app)

---

## 📝 Requisitos Previos

### 1. Cuenta de GitHub

- ✅ Tener una cuenta activa en [GitHub](https://github.com)
- ✅ Repositorio público o privado con el código de la app
- ✅ Rama lista para desplegar (puede ser `main` o esta rama de desarrollo)

### 2. Cuenta de Streamlit Cloud

- ✅ Crear cuenta gratuita en [share.streamlit.io](https://share.streamlit.io)
- ✅ Conectar tu cuenta de GitHub con Streamlit Cloud
- ✅ Autorizar acceso a tus repositorios

### 3. Repositorio Configurado

Tu repositorio debe contener **como mínimo**:

```
📦 tu-repositorio/
├── 📄 app.py                  # ← Aplicación principal
├── 📄 requirements.txt        # ← Dependencias
└── 📄 README.md               # ← Documentación (opcional pero recomendado)
```

---

## 📁 Archivos Necesarios

### 1. `app.py` ✅ (YA EXISTE)

**Ubicación:** Raíz del repositorio

```python
# Tu aplicación Streamlit
import streamlit as st
# ... resto del código
```

**Estado:** ✅ Listo para desplegar

---

### 2. `requirements.txt` ✅ (YA EXISTE)

**Ubicación:** Raíz del repositorio

**Contenido actual:**

```txt
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
python-dateutil>=2.8.0
```

**Estado:** ✅ Completo y actualizado

**Notas:**
- Todas las dependencias están especificadas
- Versiones compatibles con Streamlit Cloud
- Python 3.9+ soportado automáticamente

---

### 3. `.streamlit/config.toml` ⚠️ (OPCIONAL)

**Ubicación:** `.streamlit/config.toml` (carpeta oculta)

**Propósito:** Configuración personalizada de la app

**Contenido recomendado:**

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[client]
showErrorDetails = true
toolbarMode = "auto"
```

**Crear este archivo (opcional):**

```bash
mkdir -p .streamlit
cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
maxMessageSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[client]
showErrorDetails = true
toolbarMode = "auto"
EOF
```

**Nota:** Si no creas este archivo, Streamlit usará configuración por defecto (funciona perfectamente).

---

### 4. `README.md` ✅ (YA EXISTE)

**Estado:** ✅ Ya existe y está bien documentado

**Recomendación:** Agregar badge de Streamlit al README:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://TU-APP.streamlit.app)
```

---

## 🚀 Pasos de Despliegue

### Paso 1: Preparar el Repositorio

#### 1.1 Verificar que todo está en GitHub

```bash
# Ver estado actual
git status

# Ver rama actual
git branch --show-current

# Ver archivos rastreados
git ls-files
```

**Verificación:**
- ✅ `app.py` está en la raíz
- ✅ `requirements.txt` está en la raíz
- ✅ Todos los cambios están commiteados
- ✅ Todo está pusheado a GitHub

#### 1.2 Si hay cambios pendientes

```bash
# Agregar cambios
git add .

# Commit
git commit -m "chore: Prepare for Streamlit Cloud deployment"

# Push
git push origin cursor/convertir-excel-a-base-de-datos-para-analisis-f2c8
```

---

### Paso 2: Acceder a Streamlit Cloud

1. **Ir a:** https://share.streamlit.io
2. **Hacer login** con tu cuenta de GitHub
3. **Autorizar** acceso a repositorios (si es la primera vez)

---

### Paso 3: Crear Nueva App

#### 3.1 Click en "New app"

![New App Button](https://docs.streamlit.io/images/streamlit-community-cloud/deploy-empty-new-app.png)

#### 3.2 Configurar la App

Llenar el formulario:

```
Repository: Sinsapiar1/inventory-analyzer-web
Branch: cursor/convertir-excel-a-base-de-datos-para-analisis-f2c8
Main file path: app.py
App URL: inventory-analyzer-v6-3  (o el nombre que quieras)
```

**Opciones importantes:**

| Campo | Valor Recomendado |
|-------|-------------------|
| **Repository** | `Sinsapiar1/inventory-analyzer-web` |
| **Branch** | `cursor/convertir-excel-a-base-de-datos-para-analisis-f2c8` |
| **Main file path** | `app.py` |
| **Python version** | `3.11` (automático) |
| **App URL** | `inventory-analyzer-v6-3` o similar |

#### 3.3 Click en "Deploy!"

Streamlit Cloud hará automáticamente:

1. ✅ Clonar el repositorio
2. ✅ Instalar Python 3.11
3. ✅ Instalar dependencias de `requirements.txt`
4. ✅ Ejecutar `streamlit run app.py`
5. ✅ Asignar URL pública

**Tiempo estimado:** 2-5 minutos

---

### Paso 4: Monitorear el Despliegue

Durante el despliegue verás logs en tiempo real:

```
Cloning repository...
✅ Repository cloned

Installing Python 3.11...
✅ Python 3.11 installed

Installing dependencies from requirements.txt...
Collecting streamlit>=1.32.0
Collecting pandas>=2.0.0
...
✅ Dependencies installed

Starting Streamlit app...
✅ App is running!
```

**Estados posibles:**

| Estado | Significado |
|--------|-------------|
| 🟡 **Building** | Instalando dependencias |
| 🟢 **Running** | App funcionando correctamente |
| 🔴 **Error** | Hubo un problema (ver logs) |
| ⚪ **Sleeping** | App en sleep mode (plan gratuito) |

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

**¿Necesitas variables de entorno?** (API keys, passwords, etc.)

Esta app **NO necesita** variables de entorno, pero si en el futuro las necesitas:

1. En Streamlit Cloud, ve a: **App settings → Secrets**
2. Agregar en formato TOML:

```toml
# Example secrets
[database]
host = "localhost"
port = 5432

[api]
key = "tu_api_key_secreta"
```

3. En `app.py`, acceder con:

```python
import streamlit as st

# Acceder a secrets
db_host = st.secrets["database"]["host"]
api_key = st.secrets["api"]["key"]
```

---

### Configuración de Python

**Versión de Python:** Se detecta automáticamente

Si necesitas especificar una versión exacta:

**Crear:** `.python-version`

```bash
echo "3.11.5" > .python-version
```

**O usar:** `runtime.txt`

```bash
echo "python-3.11.5" > runtime.txt
```

**Nota:** No es necesario para esta app, Streamlit usará Python 3.11 por defecto.

---

### Configuración de Recursos

**Plan Gratuito (Community Cloud):**

| Recurso | Límite |
|---------|--------|
| **RAM** | 1 GB |
| **CPU** | Compartido |
| **Storage** | 1 GB |
| **Uptime** | Apps duermen tras inactividad |
| **Apps públicas** | Ilimitadas |
| **Apps privadas** | 1 app |

**¿Es suficiente para esta app?**

✅ **SÍ**, siempre que:
- No proceses más de 100 archivos Excel a la vez
- Archivos .db sean < 100 MB
- No tengas más de 10 usuarios concurrentes

---

## 📊 Límites y Consideraciones

### Límites de Tamaño de Archivo

#### Upload Limits (default)

```python
# En app.py ya configurado:
st.file_uploader(
    "Subir archivos Excel",
    accept_multiple_files=True,
    type=['xlsx', 'xls', 'db', 'sqlite', 'sqlite3']
)
```

**Límite por defecto:** 200 MB por archivo

**Configurar límite mayor (si es necesario):**

En `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 500  # En MB (máximo 500 MB en plan gratuito)
```

#### Database Limits

| Tipo de archivo | Tamaño recomendado | Tamaño máximo |
|-----------------|--------------------|-----------------|
| **Excel individual** | < 10 MB | 200 MB |
| **Base de datos .db** | < 50 MB | 200 MB |
| **Total en memoria** | < 500 MB | 1 GB |

**Recomendaciones:**

- ✅ Si tu .db consolidado es < 50 MB: **Perfecto para plan gratuito**
- ⚠️ Si tu .db es 50-100 MB: **Funciona pero puede ser lento**
- ❌ Si tu .db es > 100 MB: **Considera plan de pago o VPS**

### Límites de Procesamiento

**Datos en memoria:**

```python
# Tu app procesa datos en RAM
df_total = pd.concat([df1, df2, df3, ...])  # Máx ~500 MB en RAM
```

**Estimación de uso de RAM:**

| Escenario | RAM Estimada |
|-----------|--------------|
| 10 archivos Excel (~5 MB cada) | ~100 MB |
| 50 archivos Excel (~5 MB cada) | ~400 MB |
| 100 archivos Excel (~5 MB cada) | ~800 MB ⚠️ |
| 1 archivo .db (50 MB) | ~150 MB |
| 1 archivo .db (100 MB) | ~300 MB |

**Nota:** Si tu app usa > 1 GB RAM, Streamlit Cloud la reiniciará.

---

### Sleep Mode (Plan Gratuito)

**Comportamiento:**

```
Usuario no usa app por 7 días
    ↓
App entra en "sleep mode"
    ↓
Próximo usuario que acceda
    ↓
App se "despierta" (toma 10-30 segundos)
```

**¿Cómo evitar sleep mode?**

- 💰 **Opción 1:** Upgrade a plan de pago ($20/mes por usuario)
- 🤖 **Opción 2:** Ping automático (no recomendado, viola ToS)
- ✅ **Opción 3:** Aceptar 10-30 segundos de carga inicial

---

## ✅ Verificación Post-Despliegue

### Checklist de Pruebas

Una vez desplegada, probar:

#### 1. ✅ Modo: Analizar Inventarios

```
1. Subir 3-5 archivos Excel
2. Seleccionar hoja 2
3. Click "Procesar archivos"
4. Verificar que muestra gráficos sin errores
```

**Resultado esperado:** ✅ Gráficos y análisis se muestran correctamente

---

#### 2. ✅ Modo: Consolidar Excel → Base de Datos

```
1. Subir 10-20 archivos Excel
2. Seleccionar hoja 2
3. Click "Consolidar a Base de Datos"
4. Descargar archivo .db
5. Verificar que el archivo .db se descarga
```

**Resultado esperado:** ✅ Archivo `inventarios_consolidados_YYYYMMDD.db` se descarga

---

#### 3. ✅ Modo: Analizar desde Base de Datos

```
1. Subir archivo .db consolidado
2. Verificar que muestra KPIs
3. Ir a tab "Súper Análisis"
4. Verificar que muestra todos los gráficos dinámicos
```

**Resultado esperado:** ✅ Todos los gráficos y tabs funcionan

---

#### 4. ✅ Prueba con Pocos Datos

```
1. Subir solo 2-3 archivos Excel
2. Procesar
3. Verificar que NO aparece error de "Bin edges"
```

**Resultado esperado:** ✅ Análisis funciona sin errores (fix aplicado)

---

### Logs y Monitoring

**Ver logs en tiempo real:**

1. En Streamlit Cloud, click en tu app
2. Click en **"Manage app"**
3. Click en **"Logs"**

**Logs útiles:**

```
[INFO] Streamlit is running at: http://0.0.0.0:8501
[INFO] 2025-10-21 18:30:45 - 📊 Datos normalizados: 571 registros
[INFO] 2025-10-21 18:30:46 - 🔍 Analizando pallets...
```

**Errores comunes:**

```
❌ ModuleNotFoundError: No module named 'openpyxl'
→ Solución: Verificar requirements.txt

❌ MemoryError: Unable to allocate array
→ Solución: Reducir tamaño de archivos o upgrade plan

❌ StreamlitAPIException: File uploader too large
→ Solución: Reducir maxUploadSize en config.toml
```

---

## 🔧 Troubleshooting

### Problema 1: App no despliega

**Síntomas:**

```
🔴 Error during startup
```

**Soluciones:**

1. **Verificar requirements.txt:**

```bash
# En local, probar instalación
python -m pip install -r requirements.txt
```

2. **Verificar app.py:**

```bash
# En local, probar ejecución
streamlit run app.py
```

3. **Revisar logs** en Streamlit Cloud

---

### Problema 2: ImportError / ModuleNotFoundError

**Síntomas:**

```
ModuleNotFoundError: No module named 'openpyxl'
```

**Solución:**

```bash
# Asegurar que requirements.txt tiene:
openpyxl>=3.1.0

# Y está en la raíz del repo
git add requirements.txt
git commit -m "fix: Add missing dependency"
git push
```

Streamlit Cloud **auto-redeploy** en 1-2 minutos.

---

### Problema 3: MemoryError

**Síntomas:**

```
MemoryError: Unable to allocate 800 MB for array
```

**Soluciones:**

1. **Reducir datos procesados:**

```python
# Limitar archivos
if len(uploaded_files) > 50:
    st.warning("⚠️ Máximo 50 archivos a la vez")
```

2. **Upgrade a plan de pago** ($20/mes = 4 GB RAM)

3. **Usar VPS** (Railway, Render, DigitalOcean)

---

### Problema 4: App muy lenta

**Síntomas:**

```
Procesando... (tarda 1-2 minutos)
```

**Soluciones:**

1. **Optimizar caching:**

```python
# Asegurar que usas @st.cache_data
@st.cache_data
def analyze_pallets_data(df_total):
    # ...
```

2. **Reducir datos visualizados:**

```python
# Limitar filas en tablas
df_display = df.head(1000)  # Mostrar solo 1000 filas
```

3. **Upgrade a plan de pago** (CPU dedicado)

---

### Problema 5: App se reinicia frecuentemente

**Síntomas:**

```
App perdió la sesión
Los datos subidos desaparecieron
```

**Causa:** Exceso de RAM (> 1 GB)

**Soluciones:**

1. **Revisar uso de memoria:**

```python
import sys

# Ver tamaño de DataFrame
df_size_mb = sys.getsizeof(df) / 1024 / 1024
st.write(f"RAM usada: {df_size_mb:.2f} MB")
```

2. **Limpiar cache frecuentemente:**

```python
# Botón para limpiar cache
if st.button("Limpiar caché"):
    st.cache_data.clear()
    st.rerun()
```

---

## 🔄 Actualización de la App

### Auto-Deploy (Recomendado)

**Por defecto:** Streamlit Cloud hace auto-deploy cuando haces push a la rama desplegada.

```bash
# Hacer cambios en app.py
vim app.py

# Commit y push
git add app.py
git commit -m "feat: Nueva funcionalidad"
git push origin cursor/convertir-excel-a-base-de-datos-para-analisis-f2c8
```

**Resultado:**

```
1-2 minutos después:
✅ Streamlit Cloud detecta cambios
✅ Re-despliega automáticamente
✅ App actualizada disponible
```

---

### Manual Redeploy

Si necesitas forzar re-deploy:

1. Ve a **Streamlit Cloud → Manage app**
2. Click en **"Reboot app"**
3. Espera 1-2 minutos

---

### Rollback (Deshacer Cambios)

Si el nuevo deploy tiene errores:

```bash
# Ver commits recientes
git log --oneline -5

# Revertir al commit anterior
git revert HEAD

# O resetear a commit específico
git reset --hard abc123

# Forzar push
git push origin cursor/convertir-excel-a-base-de-datos-para-analisis-f2c8 --force
```

Streamlit Cloud re-desplegará automáticamente la versión anterior.

---

## 📱 URLs y Acceso

### URL de tu App

**Formato:**

```
https://[nombre-app]-[hash].streamlit.app
```

**Ejemplo:**

```
https://inventory-analyzer-v6-3-abc123def.streamlit.app
```

### Custom Domain (Opcional)

**Plan de pago:** Puedes configurar dominio personalizado

```
https://inventarios.tuempresa.com
```

**Configuración:**

1. Upgrade a plan de pago
2. En Streamlit Cloud: **Settings → Custom domain**
3. Agregar CNAME en tu DNS:

```
CNAME: inventarios
Value: abc123def.streamlit.app
```

---

## 📊 Plan Gratuito vs Plan de Pago

### Comparación

| Característica | Gratuito | Pro ($20/mes) |
|----------------|----------|---------------|
| **Apps públicas** | ✅ Ilimitadas | ✅ Ilimitadas |
| **Apps privadas** | 1 | 10 |
| **RAM** | 1 GB | 4 GB |
| **CPU** | Compartido | Dedicado |
| **Sleep mode** | Sí (7 días) | No |
| **Custom domain** | ❌ | ✅ |
| **Support** | Community | Email |

### ¿Necesitas Plan de Pago?

**Plan gratuito es suficiente si:**

- ✅ Procesarás < 50 archivos Excel a la vez
- ✅ Archivos .db < 50 MB
- ✅ < 10 usuarios concurrentes
- ✅ Puedes tolerar 10-30 seg de carga inicial tras inactividad

**Plan de pago es necesario si:**

- ❌ Procesarás > 100 archivos Excel a la vez
- ❌ Archivos .db > 100 MB
- ❌ > 50 usuarios concurrentes
- ❌ Necesitas uptime 24/7 garantizado

---

## 🎯 Checklist Final de Despliegue

### Pre-Deploy

- [ ] ✅ `app.py` está en la raíz del repositorio
- [ ] ✅ `requirements.txt` está actualizado
- [ ] ✅ Todos los cambios están pusheados a GitHub
- [ ] ✅ App funciona en local (`streamlit run app.py`)
- [ ] ✅ Cuenta de Streamlit Cloud creada y conectada a GitHub

### Durante Deploy

- [ ] ✅ Repositorio correcto seleccionado
- [ ] ✅ Rama correcta seleccionada (`cursor/convertir-excel-a-base-de-datos-para-analisis-f2c8`)
- [ ] ✅ Main file es `app.py`
- [ ] ✅ URL personalizada elegida

### Post-Deploy

- [ ] ✅ App en estado "Running" (verde)
- [ ] ✅ Probado modo "Analizar Inventarios"
- [ ] ✅ Probado modo "Consolidar Excel → DB"
- [ ] ✅ Probado modo "Analizar desde Base de Datos"
- [ ] ✅ Probado con pocos datos (sin error de bins)
- [ ] ✅ Logs sin errores críticos
- [ ] ✅ URL compartida con usuarios

---

## 🔗 Links Útiles

### Documentación

- **Streamlit Cloud Docs:** https://docs.streamlit.io/streamlit-community-cloud
- **Deploy Tutorial:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- **Troubleshooting:** https://docs.streamlit.io/knowledge-base/deploy

### Soporte

- **Community Forum:** https://discuss.streamlit.io
- **GitHub Issues:** https://github.com/streamlit/streamlit/issues
- **Stack Overflow:** https://stackoverflow.com/questions/tagged/streamlit

### Alternativas de Deploy

Si Streamlit Cloud no te funciona:

| Plataforma | RAM Gratuita | Precio Básico | Mejor para |
|------------|--------------|---------------|------------|
| **Streamlit Cloud** | 1 GB | $20/mes | Apps simples |
| **Railway** | 512 MB | $5/mes | Apps medianas |
| **Render** | 512 MB | $7/mes | Apps medianas |
| **Heroku** | 512 MB | $7/mes | Apps legacy |
| **DigitalOcean** | - | $6/mes | Control total |
| **AWS EC2** | 1 GB (1 año) | $10/mes | Empresas |

Ver `LIMITES_DESPLIEGUE.md` para detalles completos.

---

## 🎉 ¡Listo para Desplegar!

Tu aplicación tiene **todo lo necesario** para ser desplegada en Streamlit Cloud:

✅ Código funcionando  
✅ Dependencias especificadas  
✅ Fix de severidad aplicado  
✅ Documentación completa  

**Siguiente paso:**

```
1. Ir a https://share.streamlit.io
2. Click en "New app"
3. Seleccionar repositorio y rama
4. Click en "Deploy!"
5. ¡Esperar 2-5 minutos y listo! 🚀
```

---

**¿Preguntas?** Revisa la sección de [Troubleshooting](#troubleshooting) o consulta la [documentación oficial](https://docs.streamlit.io).

**¡Éxito con el despliegue! 🎊**