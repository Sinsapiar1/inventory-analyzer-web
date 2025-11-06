# 🚀 SOLUCIÓN: Leer Archivos desde Google Drive

## 📋 Situación Actual

✅ **Ya tienes:**
- Carpeta en Google Drive con archivos Excel
- Sincronización automática desde SharePoint
- URL de la carpeta: https://drive.google.com/drive/folders/1eSbNu-PbBC5ikiJsMetM58GdUsR1eRz1

⚠️ **Necesitas:**
- Que tu app Streamlit lea esos archivos automáticamente
- Sin descargar manualmente cada vez

---

## 🎯 OPCIÓN 1: Descarga Manual Facilitada (MÁS SIMPLE) ⭐⭐⭐⭐⭐

### **Cómo funciona:**

1. Usuario abre Google Drive en su navegador
2. Selecciona los archivos que quiere analizar
3. Los descarga (ZIP si son varios)
4. Los sube a tu app Streamlit

### **Ventajas:**
- ✅ **MUY simple de implementar** (0 configuración)
- ✅ **No requiere permisos especiales** de Google
- ✅ **Funciona inmediatamente**
- ✅ **Control total** sobre qué archivos analizar
- ✅ **Sin costos** de APIs

### **Desventajas:**
- ❌ Requiere 2 clicks extra (descargar + subir)
- ❌ No es "automático al 100%"

### **Implementación:**

```python
# En tu nuevo tab
st.markdown("""
### 📁 Archivos desde Google Drive

1. Abre tu carpeta: [Google Drive](https://drive.google.com/drive/folders/1eSbNu-PbBC5ikiJsMetM58GdUsR1eRz1)
2. Selecciona los archivos que quieres analizar
3. Descárgalos (clic derecho → Descargar)
4. Súbelos aquí abajo ⬇️
""")

uploaded_files = st.file_uploader(
    "📤 Subir archivos Excel desde Google Drive",
    type=['xlsx', 'xls'],
    accept_multiple_files=True,
    help="Archivos sincronizados automáticamente desde SharePoint"
)

if uploaded_files:
    process_google_drive_files(uploaded_files)
```

**Tiempo de implementación: 30 minutos**

---

## 🎯 OPCIÓN 2: Google Drive API con OAuth (SEMI-AUTOMÁTICO) ⭐⭐⭐

### **Cómo funciona:**

1. Usuario autoriza la app una sola vez (OAuth)
2. App lista los archivos de la carpeta automáticamente
3. Usuario selecciona cuáles analizar
4. App los descarga y procesa en memoria

### **Ventajas:**
- ✅ **Más automático**: No descargar manualmente
- ✅ **Lista archivos** directamente en la app
- ✅ **Una sola autorización** (persiste)
- ✅ **Profesional**: Experiencia de usuario superior

### **Desventajas:**
- ❌ Requiere configurar proyecto en Google Cloud
- ❌ OAuth es complejo de implementar
- ❌ Requiere almacenar credenciales
- ❌ Si usas Streamlit Cloud, necesitas configurar secrets

### **Implementación:**

#### Paso 1: Configurar Google Cloud Project

```bash
1. Ir a https://console.cloud.google.com
2. Crear nuevo proyecto: "Streamlit-Inventory-Analyzer"
3. Habilitar "Google Drive API"
4. Crear credenciales OAuth 2.0:
   - Tipo: Desktop app
   - Descargar JSON
```

#### Paso 2: Instalar dependencias

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### Paso 3: Código de autenticación

```python
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1eSbNu-PbBC5ikiJsMetM58GdUsR1eRz1'

def authenticate_google_drive():
    """Autenticar con Google Drive"""
    creds = None
    
    # Token guardado
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no hay credenciales válidas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar token
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def list_files_from_folder(service, folder_id):
    """Listar archivos de la carpeta"""
    query = f"'{folder_id}' in parents and (mimeType='application/vnd.ms-excel' or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')"
    
    results = service.files().list(
        q=query,
        pageSize=100,
        fields="files(id, name, createdTime, modifiedTime, size)",
        orderBy='modifiedTime desc'
    ).execute()
    
    return results.get('files', [])

def download_file(service, file_id):
    """Descargar archivo en memoria"""
    request = service.files().get_media(fileId=file_id)
    
    import io
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    
    fh.seek(0)
    return fh
```

#### Paso 4: Integrar en Streamlit

```python
# En tu nuevo tab
st.header("🤖 Historial Automático - Google Drive")

# Autenticar (una sola vez)
if 'drive_service' not in st.session_state:
    with st.spinner("Conectando con Google Drive..."):
        try:
            st.session_state.drive_service = authenticate_google_drive()
            st.success("✅ Conectado con Google Drive")
        except Exception as e:
            st.error(f"❌ Error de autenticación: {e}")
            st.stop()

# Listar archivos
service = st.session_state.drive_service
files = list_files_from_folder(service, FOLDER_ID)

if files:
    st.write(f"📁 **{len(files)} archivos encontrados**")
    
    # Mostrar tabla de archivos
    file_data = []
    for f in files:
        file_data.append({
            'Seleccionar': False,
            'Nombre': f['name'],
            'Modificado': f['modifiedTime'][:10],
            'ID': f['id']
        })
    
    df_files = pd.DataFrame(file_data)
    
    # Seleccionar archivos
    selected_indices = st.multiselect(
        "Selecciona archivos para analizar:",
        options=range(len(df_files)),
        format_func=lambda i: df_files.iloc[i]['Nombre']
    )
    
    if st.button("📊 Analizar Archivos Seleccionados"):
        all_data = []
        
        progress = st.progress(0)
        for idx, file_idx in enumerate(selected_indices):
            file_id = df_files.iloc[file_idx]['ID']
            file_name = df_files.iloc[file_idx]['Nombre']
            
            st.info(f"Procesando: {file_name}")
            
            # Descargar y procesar
            file_content = download_file(service, file_id)
            df = pd.read_excel(file_content)
            
            # Tu procesamiento habitual
            df = process_dataverse_file(df, file_name)
            all_data.append(df)
            
            progress.progress((idx + 1) / len(selected_indices))
        
        # Análisis completo
        combined_df = pd.concat(all_data, ignore_index=True)
        display_dashboard(combined_df)
```

**Tiempo de implementación: 3-4 horas**

---

## 🎯 OPCIÓN 3: Google Drive Público + Lectura Directa (EXPERIMENTAL) ⭐⭐

### **Cómo funciona:**

1. Haces la carpeta pública (cualquiera con link puede ver)
2. App usa link directo sin autenticación
3. Procesa archivos directamente

### **Ventajas:**
- ✅ Sin OAuth
- ✅ Sin credenciales

### **Desventajas:**
- ❌ **RIESGO DE SEGURIDAD**: Archivos públicos en internet
- ❌ Google Drive no permite listar carpetas públicas fácilmente
- ❌ Solo funciona con links directos de archivos específicos

**❌ NO RECOMENDADA** para datos empresariales

---

## 🎯 OPCIÓN 4: Google Colab + Streamlit (HÍBRIDA) ⭐⭐⭐⭐

### **Cómo funciona:**

1. Usas Google Colab (tiene acceso nativo a Drive)
2. Montas tu Drive en Colab
3. Corres Streamlit dentro de Colab
4. Acceso instantáneo a archivos

### **Ventajas:**
- ✅ **Acceso nativo** a Google Drive (sin OAuth complejo)
- ✅ **Gratis** (Colab es gratis)
- ✅ **Fácil de compartir** con tu equipo
- ✅ **GPU gratis** si necesitas procesamiento pesado

### **Desventajas:**
- ❌ Colab se apaga después de inactividad
- ❌ No es permanente (no es hosting)
- ❌ Requiere ejecutar notebook cada vez

### **Implementación:**

#### Crear notebook en Colab:

```python
# Celda 1: Montar Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Celda 2: Instalar dependencias
!pip install streamlit pandas plotly openpyxl

# Celda 3: Crear archivo app.py
%%writefile app.py
import streamlit as st
import pandas as pd
import os

# Ruta a tu carpeta
DRIVE_FOLDER = '/content/drive/MyDrive/SharePoint-Sync'

st.title("📊 Analizador de Inventarios - Google Drive")

# Listar archivos
files = [f for f in os.listdir(DRIVE_FOLDER) if f.endswith(('.xlsx', '.xls'))]

if files:
    selected_files = st.multiselect("Selecciona archivos:", files)
    
    if st.button("Analizar"):
        all_data = []
        for file in selected_files:
            file_path = os.path.join(DRIVE_FOLDER, file)
            df = pd.read_excel(file_path)
            # Tu procesamiento aquí
            all_data.append(df)
        
        # Dashboard
        st.success(f"✅ Procesados {len(all_data)} archivos")

# Celda 4: Correr Streamlit
!streamlit run app.py & npx localtunnel --port 8501
```

**Ventaja única:** No necesitas configurar nada de OAuth, Colab ya tiene acceso a tu Drive.

**Tiempo de implementación: 1 hora**

---

## 📊 Comparación de Opciones

| Opción | Complejidad | Tiempo Setup | Automatización | Seguridad | Costo | Recomendación |
|--------|-------------|--------------|----------------|-----------|-------|---------------|
| **1. Manual** | ⭐ Muy Baja | 30 min | ⭐⭐ Baja | ⭐⭐⭐⭐⭐ | Gratis | **MVP inicial** |
| **2. OAuth API** | ⭐⭐⭐⭐ Alta | 3-4 horas | ⭐⭐⭐⭐⭐ Alta | ⭐⭐⭐⭐ | Gratis | **Largo plazo** |
| **3. Público** | ⭐⭐ Baja | 1 hora | ⭐⭐⭐ Media | ⭐ MUY BAJA | Gratis | **NO usar** |
| **4. Colab** | ⭐⭐ Media | 1 hora | ⭐⭐⭐⭐ Alta | ⭐⭐⭐⭐ | Gratis | **Alternativa** |

---

## 🎯 MI RECOMENDACIÓN FINAL

### **PLAN DE IMPLEMENTACIÓN PROGRESIVA**

#### **FASE 1: Empezar Simple (HOY)** ⭐⭐⭐⭐⭐
```
Opción 1: Descarga Manual
├─ Implementación: 30 minutos
├─ Sin configuración compleja
├─ Prueba inmediata del concepto
└─ Si funciona → Pasar a Fase 2
```

**Código para agregar ahora:**

```python
# En app.py, dentro del nuevo modo
elif modo == "🤖 Historial Automático Dataverse":
    st.subheader("🤖 Historial Automático desde Google Drive")
    
    st.info("""
    📁 **Tus archivos están sincronizados automáticamente** desde SharePoint a Google Drive.
    
    **Pasos:**
    1. Abre tu [carpeta de Google Drive](https://drive.google.com/drive/folders/1eSbNu-PbBC5ikiJsMetM58GdUsR1eRz1)
    2. Selecciona los archivos Excel que quieres analizar
    3. Descárgalos (clic derecho → Descargar)
    4. Súbelos aquí abajo
    """)
    
    gdrive_files = st.file_uploader(
        "📤 Subir archivos desde Google Drive",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        help="Archivos sincronizados automáticamente desde SharePoint"
    )
    
    if gdrive_files and st.button("🚀 Procesar Archivos"):
        with st.spinner("Procesando archivos..."):
            result = process_google_drive_files(gdrive_files)
            display_automatic_dashboard(result)
```

#### **FASE 2: Automatizar (DESPUÉS - Si te gusta la Fase 1)**
```
Opción 2: Google Drive API
├─ Si Fase 1 funciona bien
├─ Implementación: 1 fin de semana
├─ Experiencia profesional
└─ 100% automático
```

#### **ALTERNATIVA: Si Fase 2 es muy compleja**
```
Opción 4: Google Colab
├─ Más simple que OAuth
├─ Acceso nativo a Drive
├─ Bueno para equipo técnico
└─ No requiere hosting
```

---

## 🚀 ¿Qué Hacemos AHORA?

### **OPCIÓN A: Implemento Fase 1 inmediatamente** (30 min)
- Agrego el tercer tab
- Función para procesar archivos de Google Drive
- Dashboard básico funcionando
- **Puedes probarlo HOY**

### **OPCIÓN B: Primero verificamos los archivos**
- Me compartes un archivo de ejemplo
- Verifico estructura y columnas
- Luego implemento Fase 1 con mapeo correcto

### **OPCIÓN C: Te explico más sobre OAuth**
- Si quieres ir directo a Opción 2
- Te guío paso a paso para configurar
- Implementación completa en esta sesión

---

## ❓ Preguntas Clave

1. **¿Qué columnas tienen los Excel de tu carpeta?**
   - ¿Son iguales a los que pegaste antes? (CompanyId, ProductId, Stock, etc.)

2. **¿Cuántos archivos sueles tener en la carpeta?**
   - ¿5-10 archivos? ¿30 días de histórico?

3. **¿Qué tan seguido necesitas analizarlos?**
   - ¿Diario? ¿Semanal?
   - Esto determina si vale la pena automatizar

4. **¿Tu app se va a deployar en Streamlit Cloud o local?**
   - Si es Cloud → OAuth es más complejo
   - Si es local → OAuth es más fácil

---

**¿Empiezo con la Fase 1 (Manual) para tener algo funcionando en 30 minutos?** 🚀
