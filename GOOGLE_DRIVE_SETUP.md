# 🔧 Configuración de Google Drive - Guía Completa

## 📋 Resumen

Este documento explica cómo configurar la integración con Google Drive para que tu aplicación pueda leer automáticamente los archivos Excel sincronizados desde SharePoint.

---

## 🎯 Objetivo

Conectar tu app Streamlit con tu carpeta de Google Drive para:
- ✅ Leer automáticamente archivos Excel
- ✅ Procesar múltiples archivos (hasta 100)
- ✅ Análisis temporal automático
- ✅ Sin descargas manuales

---

## 🚀 OPCIÓN 1: Configuración Local (Recomendada para Desarrollo)

### Paso 1: Crear Proyecto en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Haz clic en **"Select a project" → "New Project"**
3. Nombre del proyecto: `Inventory-Analyzer`
4. Haz clic en **"Create"**

### Paso 2: Habilitar Google Drive API

1. En el menú lateral, ve a **"APIs & Services" → "Library"**
2. Busca **"Google Drive API"**
3. Haz clic en **"Google Drive API"**
4. Haz clic en **"Enable"**

### Paso 3: Crear Credenciales OAuth 2.0

1. Ve a **"APIs & Services" → "Credentials"**
2. Haz clic en **"+ Create Credentials" → "OAuth client ID"**
3. Si te pide configurar la pantalla de consentimiento:
   - Haz clic en **"Configure Consent Screen"**
   - Selecciona **"External"** (o Internal si es workspace empresarial)
   - Completa el formulario:
     - **App name**: Inventory Analyzer
     - **User support email**: Tu email
     - **Developer contact**: Tu email
   - Haz clic en **"Save and Continue"**
   - En **Scopes**, haz clic en **"Add or Remove Scopes"**
   - Busca y selecciona: `../auth/drive.readonly`
   - Haz clic en **"Save and Continue"**
   - En **Test users**, agrega tu email
   - Haz clic en **"Save and Continue"**

4. Ahora crea las credenciales:
   - **Application type**: Desktop app
   - **Name**: Inventory Analyzer Desktop
   - Haz clic en **"Create"**

5. **Descarga el JSON**:
   - Haz clic en el botón de descarga (icono de flecha)
   - Guarda el archivo como `credentials.json`
   - **Coloca el archivo en la carpeta raíz de tu proyecto** (donde está `app.py`)

### Paso 4: Ejecutar la App

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar app
streamlit run app.py
```

### Paso 5: Autorizar Acceso

1. Selecciona el modo: **🤖 Historial Automático Google Drive**
2. Haz clic en **🔄 Conectar y Cargar Archivos**
3. Se abrirá una ventana del navegador
4. Inicia sesión con tu cuenta de Google (la que tiene acceso al Drive)
5. Autoriza los permisos solicitados
6. ¡Listo! La app ahora puede leer tu carpeta

**Nota:** El token se guarda automáticamente y no necesitarás autorizar nuevamente.

---

## ☁️ OPCIÓN 2: Configuración en Streamlit Cloud

### Paso 1: Crear Service Account

Para Streamlit Cloud, necesitas usar una **Service Account** en lugar de OAuth.

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Selecciona tu proyecto (o crea uno nuevo)
3. Ve a **"IAM & Admin" → "Service Accounts"**
4. Haz clic en **"+ Create Service Account"**
5. Completa el formulario:
   - **Service account name**: `inventory-analyzer-sa`
   - **Service account ID**: Se genera automáticamente
   - Haz clic en **"Create and Continue"**
6. **Grant this service account access to project**:
   - No necesitas agregar roles aquí
   - Haz clic en **"Continue"**
7. Haz clic en **"Done"**

### Paso 2: Crear Clave JSON

1. Encuentra tu service account en la lista
2. Haz clic en los **tres puntos** → **"Manage keys"**
3. Haz clic en **"Add Key" → "Create new key"**
4. Selecciona **JSON**
5. Haz clic en **"Create"**
6. Se descargará un archivo JSON automáticamente

### Paso 3: Compartir Carpeta de Drive con Service Account

**IMPORTANTE:** La service account necesita acceso a tu carpeta de Drive.

1. Abre el archivo JSON descargado
2. Copia el valor de `client_email` (algo como: `inventory-analyzer-sa@...iam.gserviceaccount.com`)
3. Ve a tu carpeta de Google Drive: https://drive.google.com/drive/folders/1eSbNu-PbBC5ikiJsMetM58GdUsR1eRz1
4. Haz clic derecho en la carpeta → **"Share"**
5. Pega el email de la service account
6. Dale permiso de **"Viewer"** (solo lectura)
7. **Desactiva** "Notify people" (no necesitas notificar)
8. Haz clic en **"Share"**

### Paso 4: Configurar Secrets en Streamlit Cloud

1. Ve a tu app en Streamlit Cloud
2. Haz clic en **"Settings" → "Secrets"**
3. Copia el contenido COMPLETO del archivo JSON
4. Pégalo en el editor de secrets con el siguiente formato:

```toml
[google]
type = "service_account"
project_id = "tu-proyecto-12345"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQ...\n-----END PRIVATE KEY-----\n"
client_email = "inventory-analyzer-sa@tu-proyecto.iam.gserviceaccount.com"
client_id = "123456789..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

**⚠️ IMPORTANTE:**
- Cada campo debe estar entre comillas
- La `private_key` debe mantener los `\n` (saltos de línea)
- NO agregues comas al final de cada línea

5. Haz clic en **"Save"**

### Paso 5: Actualizar Código para Service Account

El código actual ya soporta service accounts. Solo necesitas modificar la función de autenticación:

```python
def authenticate_google_drive():
    """Autenticar con Google Drive usando Service Account"""
    try:
        if 'google' in st.secrets:
            from google.oauth2 import service_account
            
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["google"],
                scopes=SCOPES
            )
            
            return build('drive', 'v3', credentials=credentials)
        else:
            st.error("No se encontraron credenciales en secrets")
            return None
    except Exception as e:
        st.error(f"Error de autenticación: {e}")
        return None
```

---

## 📁 Estructura de Archivos Esperada

Tu carpeta de Google Drive debe tener archivos con este formato:

```
📁 SharePoint-Sync (Google Drive)
├── 10-21-2025.xlsx
├── 10-22-2025.xlsx
├── 10-23-2025.xlsx
├── 10-24-2025.xlsx
└── ...
```

### Formato de Nombre de Archivo:
- **Patrón:** `MM-DD-YYYY.xlsx`
- **Ejemplos válidos:**
  - `10-21-2025.xlsx` ✅
  - `1-5-2025.xlsx` ✅ (sin ceros a la izquierda)
  - `12-31-2024.xlsx` ✅

### Estructura Interna del Excel:
- **Hoja requerida:** `PBI4. Gestión Negativos, Tabl`
- **Columnas requeridas:**
  - `CompanyId`
  - `InventLocationId`
  - `ProductId`
  - `ProductName_es`
  - `LabelId` (puede estar vacío)
  - `Stock` (solo se procesan negativos)
  - `CostStock`

---

## 🔒 Seguridad

### Mejores Prácticas:

✅ **DO:**
- Usa service accounts para Streamlit Cloud
- Guarda credenciales en `.gitignore`
- Da solo permisos de **"Viewer"** (lectura)
- Limita el acceso solo a la carpeta necesaria

❌ **DON'T:**
- Nunca subas `credentials.json` a GitHub
- No compartas tu `private_key`
- No des permisos de **"Editor"** (escritura)

### Archivo `.gitignore`:

```gitignore
# Google Drive credentials
credentials.json
token.json
token.pickle

# Streamlit secrets (local)
.streamlit/secrets.toml
```

---

## 🧪 Probar la Conexión

### Test Rápido:

```python
# test_drive.py
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1eSbNu-PbBC5ikiJsMetM58GdUsR1eRz1'

creds = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('drive', 'v3', credentials=creds)

# Listar archivos
results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    pageSize=10,
    fields="files(id, name)"
).execute()

files = results.get('files', [])
print(f"Archivos encontrados: {len(files)}")
for f in files:
    print(f" - {f['name']}")
```

Ejecutar:
```bash
python test_drive.py
```

---

## ❓ Troubleshooting

### Error: "Access denied"
**Causa:** La service account no tiene acceso a la carpeta.
**Solución:** Comparte la carpeta con el email de la service account (paso 3).

### Error: "Invalid credentials"
**Causa:** El formato del JSON en secrets es incorrecto.
**Solución:** Verifica que todos los campos estén entre comillas y la `private_key` tenga `\n`.

### Error: "No files found"
**Causa:** El FOLDER_ID es incorrecto.
**Solución:** Verifica que el ID de la carpeta sea correcto. Lo puedes obtener de la URL:
```
https://drive.google.com/drive/folders/1eSbNu-PbBC5ikiJsMetM58GdUsR1eRz1
                                          ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                          Este es el FOLDER_ID
```

### Error: "Quota exceeded"
**Causa:** Demasiadas peticiones a la API.
**Solución:** La app usa caché (5 minutos). Si necesitas refrescar, usa el botón "Limpiar Caché".

---

## 📊 Límites de la API

- **Consultas por día:** 1,000,000,000 (muy alto, no es problema)
- **Consultas por minuto:** 1,000 (suficiente)
- **Caché de la app:** 5 minutos (reduce llamadas)

---

## 🎯 Flujo Completo

```
SharePoint → Power Automate → Google Drive → Tu App
    ↓             ↓               ↓             ↓
Archivos      Sincroniza      Carpeta       Lee y
originales    automático      compartida    procesa
```

---

## 📚 Referencias

- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- [Service Accounts Explained](https://cloud.google.com/iam/docs/service-accounts)

---

## ✅ Checklist de Configuración

### Local (Desarrollo):
- [ ] Proyecto creado en Google Cloud
- [ ] Google Drive API habilitada
- [ ] Credenciales OAuth 2.0 creadas
- [ ] `credentials.json` descargado y en carpeta raíz
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Primera autorización completada
- [ ] Archivos listándose correctamente

### Cloud (Producción):
- [ ] Service Account creada
- [ ] Clave JSON descargada
- [ ] Carpeta de Drive compartida con service account email
- [ ] Secrets configurados en Streamlit Cloud
- [ ] App desplegada y funcionando
- [ ] Test de carga de archivos exitoso

---

**¿Necesitas ayuda?** Consulta la sección de Troubleshooting o revisa los logs de la app.
