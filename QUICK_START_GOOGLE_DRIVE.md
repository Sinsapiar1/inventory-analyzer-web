# 🚀 Quick Start - Google Drive Integration

## 📋 Inicio Rápido (5 minutos)

### Opción 1: Prueba Local Rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar Google Drive (ver instrucciones abajo)
# 3. Ejecutar app
streamlit run app.py

# 4. Seleccionar modo: 🤖 Historial Automático Google Drive
# 5. Click: 🔄 Conectar y Cargar Archivos
# 6. Autorizar acceso cuando se abra el navegador
# 7. ¡Listo! Tus datos se cargarán automáticamente
```

---

## 🔧 Configuración Mínima (Primera Vez)

### Paso 1: Google Cloud Console (5 min)

1. Ve a: https://console.cloud.google.com
2. Crea nuevo proyecto: "Inventory-Analyzer"
3. Habilita: **Google Drive API**
4. Crea credenciales: **OAuth 2.0** (Desktop app)
5. Descarga JSON como `credentials.json`
6. Pon `credentials.json` en la carpeta raíz del proyecto

### Paso 2: Ejecutar App

```bash
streamlit run app.py
```

### Paso 3: Primera Autorización

1. Selecciona modo: **🤖 Historial Automático Google Drive**
2. Click **🔄 Conectar y Cargar Archivos**
3. Se abrirá navegador → Inicia sesión con tu Google
4. Autoriza permisos (solo lectura)
5. ¡Listo! Token guardado automáticamente

---

## 📁 Verificar que Funcione

Tu carpeta de Google Drive debe tener:

```
📁 https://drive.google.com/drive/folders/1eSbNu-PbBC5ikiJsMetM58GdUsR1eRz1
├── 10-21-2025.xlsx  ← Formato: MM-DD-YYYY
├── 10-22-2025.xlsx
└── 10-23-2025.xlsx
```

Cada archivo debe tener:
- **Hoja:** `PBI4. Gestión Negativos, Tabl`
- **Columnas:** CompanyId, InventLocationId, ProductId, ProductName_es, LabelId, Stock, CostStock

---

## ✅ Checklist Rápido

- [ ] Python 3.8+ instalado
- [ ] `pip install -r requirements.txt` ejecutado
- [ ] Proyecto creado en Google Cloud
- [ ] Google Drive API habilitada
- [ ] `credentials.json` descargado y en carpeta raíz
- [ ] App corriendo: `streamlit run app.py`
- [ ] Modo seleccionado: 🤖 Historial Automático
- [ ] Primera autorización completada
- [ ] Archivos cargándose correctamente ✨

---

## ❓ Problemas Comunes

### "Google Drive API no está disponible"
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### "No se pudo autenticar"
1. Verifica que `credentials.json` existe en raíz
2. Verifica que Google Drive API está habilitada
3. Intenta borrar `token.json` y vuelve a autorizar

### "No se encontraron archivos"
1. Verifica que el FOLDER_ID es correcto (en `app.py` línea 39)
2. Verifica que tu cuenta tiene acceso a la carpeta
3. Verifica que hay archivos .xlsx en la carpeta

---

## 📚 Más Información

- **Guía Completa:** Ver `GOOGLE_DRIVE_SETUP.md`
- **Documentación Técnica:** Ver `NUEVO_TAB_GOOGLE_DRIVE.md`
- **Uso General:** Ver `README.md`

---

## 🎉 ¡Todo Listo!

Si seguiste estos pasos, deberías ver:

```
✅ Conectado con Google Drive
✅ Se encontraron X archivos
🔄 Procesando archivos...
✅ Análisis completado

📊 Dashboard Automático
[Tus datos visualizados aquí]
```

**¡Disfruta tu análisis automático!** 🚀
