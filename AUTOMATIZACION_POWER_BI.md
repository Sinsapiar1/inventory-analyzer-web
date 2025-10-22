# 🤖 Automatización de Power BI

## 🎯 Opciones de Automatización

---

## 1️⃣ Power BI REST API ⭐⭐⭐

### ¿Qué puede hacer?

- ✅ Publicar reportes automáticamente
- ✅ Actualizar datasets (refrescar datos)
- ✅ Exportar reportes a PDF/PNG/PPTX
- ✅ Gestionar workspaces
- ✅ Configurar permisos
- ✅ Programar actualizaciones

### Ejemplo: Actualizar Dataset Automáticamente

```python
import requests
import json

# 1. Obtener Access Token (Azure AD)
def get_access_token(tenant_id, client_id, client_secret):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://analysis.windows.net/powerbi/api/.default'
    }
    
    response = requests.post(url, data=data)
    return response.json()['access_token']

# 2. Actualizar Dataset
def refresh_dataset(workspace_id, dataset_id, access_token):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 202:
        print("✅ Actualización iniciada")
    else:
        print(f"❌ Error: {response.text}")

# 3. Verificar Estado de Actualización
def get_refresh_status(workspace_id, dataset_id, access_token):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)
    refreshes = response.json()['value']
    
    if refreshes:
        latest = refreshes[0]
        print(f"Estado: {latest['status']}")
        print(f"Inicio: {latest['startTime']}")
        if 'endTime' in latest:
            print(f"Fin: {latest['endTime']}")

# Uso
token = get_access_token(
    tenant_id="tu-tenant-id",
    client_id="tu-client-id",
    client_secret="tu-client-secret"
)

refresh_dataset(
    workspace_id="workspace-id",
    dataset_id="dataset-id",
    access_token=token
)
```

---

### Ejemplo: Exportar Reporte a PDF Automáticamente

```python
def export_report_to_pdf(workspace_id, report_id, access_token, output_path):
    # 1. Iniciar exportación
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/ExportTo"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    body = {
        'format': 'PDF'
    }
    
    response = requests.post(url, headers=headers, json=body)
    export_id = response.json()['id']
    
    # 2. Esperar a que termine
    import time
    while True:
        status_url = f"{url}/{export_id}"
        status = requests.get(status_url, headers=headers).json()
        
        if status['status'] == 'Succeeded':
            break
        elif status['status'] == 'Failed':
            print("❌ Exportación falló")
            return
        
        time.sleep(5)  # Esperar 5 segundos
    
    # 3. Descargar archivo
    file_url = f"{status_url}/file"
    file_response = requests.get(file_url, headers=headers)
    
    with open(output_path, 'wb') as f:
        f.write(file_response.content)
    
    print(f"✅ Reporte exportado a: {output_path}")

# Uso
export_report_to_pdf(
    workspace_id="workspace-id",
    report_id="report-id",
    access_token=token,
    output_path="reporte_inventarios.pdf"
)
```

---

## 2️⃣ Power BI PowerShell ⭐⭐

### Instalación

```powershell
# Instalar módulo
Install-Module -Name MicrosoftPowerBIMgmt

# Importar
Import-Module MicrosoftPowerBIMgmt

# Login
Connect-PowerBIServiceAccount
```

---

### Ejemplo: Actualizar Dataset

```powershell
# Actualizar dataset
Invoke-PowerBIRestMethod -Url "groups/$workspaceId/datasets/$datasetId/refreshes" -Method Post

# Ver estado
$refreshes = Invoke-PowerBIRestMethod -Url "groups/$workspaceId/datasets/$datasetId/refreshes" -Method Get | ConvertFrom-Json
$refreshes.value[0]
```

---

### Ejemplo: Publicar Reporte desde Archivo

```powershell
# Publicar archivo .pbix
New-PowerBIReport -Path "C:\reportes\inventarios.pbix" -WorkspaceId $workspaceId -Name "Inventarios Negativos"
```

---

### Ejemplo: Listar Todos los Reportes

```powershell
# Obtener workspace
$workspace = Get-PowerBIWorkspace -Name "Mi Workspace"

# Listar reportes
Get-PowerBIReport -WorkspaceId $workspace.Id | Format-Table Name, Id, WebUrl
```

---

## 3️⃣ Tabular Object Model (TOM) ⭐⭐⭐

### ¿Qué puede hacer?

- ✅ Crear/modificar medidas DAX programáticamente
- ✅ Crear/modificar tablas calculadas
- ✅ Gestionar relaciones
- ✅ Modificar modelo de datos sin abrir Power BI Desktop

### Instalación

```powershell
Install-Package Microsoft.AnalysisServices.retail.amd64
```

---

### Ejemplo: Agregar Medidas DAX Automáticamente

```csharp
using Microsoft.AnalysisServices.Tabular;

// Conectar a dataset publicado
var server = new Server();
server.Connect("powerbi://api.powerbi.com/v1.0/myorg/Mi%20Workspace");

// Obtener database
var database = server.Databases.FindByName("Inventarios Negativos");
var model = database.Model;

// Agregar medida
var table = model.Tables.Find("InventariosNegativos");
var measure = new Measure
{
    Name = "Total Pallets",
    Expression = "DISTINCTCOUNT(InventariosNegativos[id_pallet])",
    FormatString = "#,##0"
};
table.Measures.Add(measure);

// Guardar cambios
model.SaveChanges();
```

---

### Ejemplo Python: Agregar Múltiples Medidas

```python
import subprocess
import json

# Script para ejecutar en .NET
def add_dax_measures(workspace, dataset, measures_json):
    script = f"""
    using Microsoft.AnalysisServices.Tabular;
    
    var server = new Server();
    server.Connect("powerbi://api.powerbi.com/v1.0/myorg/{workspace}");
    
    var db = server.Databases.FindByName("{dataset}");
    var model = db.Model;
    var table = model.Tables.Find("InventariosNegativos");
    
    var measures = {measures_json};
    
    foreach (var m in measures)
    {{
        var measure = new Measure
        {{
            Name = m.Name,
            Expression = m.Expression,
            FormatString = m.FormatString
        }};
        table.Measures.Add(measure);
    }}
    
    model.SaveChanges();
    """
    
    # Guardar y ejecutar
    with open("add_measures.cs", "w") as f:
        f.write(script)
    
    subprocess.run(["csc", "/r:Microsoft.AnalysisServices.Tabular.dll", "add_measures.cs"])
    subprocess.run(["add_measures.exe"])

# Definir medidas
measures = [
    {
        "Name": "Total Pallets",
        "Expression": "DISTINCTCOUNT(InventariosNegativos[id_pallet])",
        "FormatString": "#,##0"
    },
    {
        "Name": "Total Negativo",
        "Expression": "SUM(InventariosNegativos[cantidad_negativa])",
        "FormatString": "#,##0.00"
    }
]

add_dax_measures("Mi Workspace", "Inventarios Negativos", json.dumps(measures))
```

---

## 4️⃣ Power Automate (Low-Code) ⭐⭐⭐⭐⭐

### ¿Qué puede hacer?

- ✅ Actualizar datasets en horarios específicos
- ✅ Enviar reportes por email automáticamente
- ✅ Notificar cuando actualización falla
- ✅ Exportar y compartir reportes
- ✅ Integrar con SharePoint, Teams, Email

---

### Ejemplo: Actualizar Dataset Diariamente

```
Trigger: Recurrence
  - Frecuencia: Diaria
  - Hora: 7:00 AM
    ↓
Action: Refresh a dataset (Power BI)
  - Workspace: Mi Workspace
  - Dataset: Inventarios Negativos
    ↓
Condition: Si actualización falla
  ↓
Action: Send an email (Office 365)
  - To: admin@empresa.com
  - Subject: ❌ Error en actualización Power BI
  - Body: El dataset de inventarios no se pudo actualizar
```

**Crear en Power Automate:**

1. Ir a: https://make.powerautomate.com
2. Crear flujo → Programado
3. Agregar acción "Refresh a dataset" (conector Power BI)
4. Configurar horario
5. Guardar

---

### Ejemplo: Enviar Reporte PDF por Email

```
Trigger: Recurrence
  - Frecuencia: Semanal
  - Día: Lunes
  - Hora: 8:00 AM
    ↓
Action: Export to file for reports (Power BI)
  - Workspace: Mi Workspace
  - Report: Dashboard Inventarios
  - File Format: PDF
    ↓
Action: Send an email (Office 365)
  - To: gerencia@empresa.com
  - Subject: 📊 Reporte Semanal de Inventarios
  - Attachments: [Output del paso anterior]
```

---

### Ejemplo: Notificar Cuando Hay Pallets Críticos

```
Trigger: Recurrence
  - Frecuencia: Diaria
  - Hora: 9:00 AM
    ↓
Action: Run a query against a dataset (Power BI)
  - Workspace: Mi Workspace
  - Dataset: Inventarios Negativos
  - DAX Query:
    EVALUATE
    FILTER(
      InventariosNegativos,
      InventariosNegativos[Severidad] = "Crítico"
    )
    ↓
Condition: Si hay filas
  ↓
Action: Post message in a chat or channel (Teams)
  - Team: Operaciones
  - Channel: General
  - Message: ⚠️ Hay {count} pallets críticos hoy
```

---

## 5️⃣ Python + Power BI (pypowerbi / powerbiclient) ⭐⭐

### Instalación

```bash
pip install powerbiclient
pip install requests
```

---

### Ejemplo: Biblioteca pypowerbi

```python
from powerbiclient import PowerBIClient
from powerbiclient.authentication import DeviceCodeLoginAuthentication

# Autenticación
auth = DeviceCodeLoginAuthentication()

# Crear cliente
client = PowerBIClient(auth)

# Listar workspaces
workspaces = client.get_workspaces()
for ws in workspaces:
    print(f"Workspace: {ws.name} (ID: {ws.id})")

# Obtener datasets de un workspace
datasets = client.get_datasets(workspace_id="workspace-id")
for ds in datasets:
    print(f"Dataset: {ds.name} (ID: {ds.id})")

# Actualizar dataset
client.refresh_dataset(
    workspace_id="workspace-id",
    dataset_id="dataset-id"
)
```

---

### Ejemplo: Script Completo de Actualización Programada

```python
import requests
import time
import logging
from datetime import datetime

# Configuración de logs
logging.basicConfig(
    filename='powerbi_refresh.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PowerBIAutomation:
    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
    
    def get_token(self):
        """Obtener token de acceso"""
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://analysis.windows.net/powerbi/api/.default'
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            self.token = response.json()['access_token']
            logging.info("✅ Token obtenido exitosamente")
            return True
        else:
            logging.error(f"❌ Error obteniendo token: {response.text}")
            return False
    
    def refresh_dataset(self, workspace_id, dataset_id):
        """Actualizar dataset"""
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers)
        
        if response.status_code == 202:
            logging.info(f"✅ Actualización iniciada para dataset {dataset_id}")
            return True
        else:
            logging.error(f"❌ Error iniciando actualización: {response.text}")
            return False
    
    def wait_for_refresh(self, workspace_id, dataset_id, timeout=3600):
        """Esperar a que termine la actualización"""
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                logging.error("❌ Timeout esperando actualización")
                return False
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                refreshes = response.json()['value']
                if refreshes:
                    latest = refreshes[0]
                    status = latest['status']
                    
                    if status == 'Completed':
                        logging.info("✅ Actualización completada exitosamente")
                        return True
                    elif status == 'Failed':
                        error = latest.get('serviceExceptionJson', 'Error desconocido')
                        logging.error(f"❌ Actualización falló: {error}")
                        return False
                    else:
                        logging.info(f"⏳ Estado: {status}")
            
            time.sleep(30)  # Esperar 30 segundos antes de verificar nuevamente
    
    def export_to_pdf(self, workspace_id, report_id, output_path):
        """Exportar reporte a PDF"""
        # 1. Iniciar exportación
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/ExportTo"
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        body = {'format': 'PDF'}
        
        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 202:
            logging.error(f"❌ Error iniciando exportación: {response.text}")
            return False
        
        export_id = response.json()['id']
        logging.info(f"✅ Exportación iniciada (ID: {export_id})")
        
        # 2. Esperar a que termine
        status_url = f"{url}/{export_id}"
        
        while True:
            status_response = requests.get(status_url, headers=headers)
            status = status_response.json()['status']
            
            if status == 'Succeeded':
                break
            elif status == 'Failed':
                logging.error("❌ Exportación falló")
                return False
            
            time.sleep(5)
        
        # 3. Descargar archivo
        file_url = f"{status_url}/file"
        file_response = requests.get(file_url, headers=headers)
        
        with open(output_path, 'wb') as f:
            f.write(file_response.content)
        
        logging.info(f"✅ Reporte exportado a: {output_path}")
        return True
    
    def send_email_notification(self, to_email, subject, body):
        """Enviar notificación por email (requiere configuración SMTP)"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Configurar según tu servidor SMTP
        smtp_server = "smtp.office365.com"
        smtp_port = 587
        sender_email = "bot@tuempresa.com"
        sender_password = "password"
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            logging.info(f"✅ Email enviado a {to_email}")
            return True
        except Exception as e:
            logging.error(f"❌ Error enviando email: {str(e)}")
            return False

# USO
if __name__ == "__main__":
    # Configuración
    pbi = PowerBIAutomation(
        tenant_id="tu-tenant-id",
        client_id="tu-client-id",
        client_secret="tu-client-secret"
    )
    
    # Autenticar
    if not pbi.get_token():
        exit(1)
    
    # Actualizar dataset
    workspace_id = "workspace-id"
    dataset_id = "dataset-id"
    
    if pbi.refresh_dataset(workspace_id, dataset_id):
        # Esperar a que termine
        if pbi.wait_for_refresh(workspace_id, dataset_id):
            # Exportar reporte
            report_id = "report-id"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reporte_inventarios_{timestamp}.pdf"
            
            if pbi.export_to_pdf(workspace_id, report_id, output_path):
                # Enviar notificación
                pbi.send_email_notification(
                    to_email="gerencia@empresa.com",
                    subject=f"📊 Reporte de Inventarios - {datetime.now().strftime('%d/%m/%Y')}",
                    body=f"""
                    <h2>Reporte de Inventarios Negativos</h2>
                    <p>El reporte ha sido generado exitosamente.</p>
                    <p>Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                    <p>Ver dashboard: <a href="https://app.powerbi.com/...">Abrir Power BI</a></p>
                    """
                )
```

---

### Programar con Cron (Linux) o Task Scheduler (Windows)

**Linux (crontab):**

```bash
# Ejecutar todos los días a las 7:00 AM
0 7 * * * /usr/bin/python3 /path/to/powerbi_automation.py
```

**Windows (Task Scheduler):**

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\scripts\powerbi_automation.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 7:00AM
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Power BI Refresh"
```

---

## 6️⃣ DAX Studio (Gestión de Medidas) ⭐⭐

### ¿Qué puede hacer?

- ✅ Exportar todas las medidas DAX a archivo
- ✅ Importar medidas desde archivo
- ✅ Útil para migrar medidas entre reportes

### Ejemplo: Exportar Medidas

```
1. Abrir DAX Studio
2. Conectar a dataset de Power BI
3. Advanced → Export Metrics
4. Guardar archivo .json o .txt
```

### Ejemplo: Importar Medidas

```
1. Crear archivo de medidas
2. DAX Studio → Advanced → Define Measure
3. Pegar DAX desde archivo
4. Aplicar a todas las medidas
```

---

## 7️⃣ Power BI CLI (Command Line) ⭐

### Instalación

```bash
npm install -g powerbi-cli
```

### Ejemplo: Login

```bash
powerbi login
```

### Ejemplo: Listar Workspaces

```bash
powerbi workspace list
```

### Ejemplo: Actualizar Dataset

```bash
powerbi dataset refresh --workspace "Mi Workspace" --dataset "Inventarios Negativos"
```

---

## 8️⃣ Deployment Pipelines (CI/CD) ⭐⭐⭐

### Power BI con Azure DevOps

```yaml
# azure-pipelines.yml

trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'windows-latest'

steps:
  - task: PowerShell@2
    displayName: 'Publicar Reporte Power BI'
    inputs:
      targetType: 'inline'
      script: |
        Install-Module -Name MicrosoftPowerBIMgmt -Force
        
        $password = ConvertTo-SecureString "$(ServiceAccountPassword)" -AsPlainText -Force
        $credential = New-Object System.Management.Automation.PSCredential ("$(ServiceAccountUser)", $password)
        Connect-PowerBIServiceAccount -Credential $credential
        
        New-PowerBIReport -Path "$(Build.SourcesDirectory)/inventarios.pbix" -WorkspaceId "$(WorkspaceId)" -Name "Inventarios Negativos"
```

---

## 9️⃣ Monitoring y Alertas ⭐⭐

### Ejemplo: Monitor de Actualización con Python

```python
import requests
import time
from datetime import datetime, timedelta

def monitor_refresh_failures(workspace_id, dataset_id, token):
    """Monitorear fallos en actualizaciones"""
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
    headers = {'Authorization': f'Bearer {token}'}
    
    while True:
        response = requests.get(url, headers=headers)
        refreshes = response.json()['value']
        
        if refreshes:
            latest = refreshes[0]
            if latest['status'] == 'Failed':
                # Enviar alerta
                send_alert(
                    f"❌ Actualización falló en dataset {dataset_id}",
                    latest.get('serviceExceptionJson', 'Error desconocido')
                )
        
        # Verificar cada 5 minutos
        time.sleep(300)
```

---

## 🎯 ¿Cuál Usar Para Tu Caso?

### Para Actualizar Datos Automáticamente

**Opción 1: Power Automate** ⭐⭐⭐⭐⭐
- ✅ Más fácil (sin código)
- ✅ Integración nativa
- ✅ Notificaciones automáticas
- **RECOMENDADO**

**Opción 2: Python Script + Cron/Task Scheduler** ⭐⭐⭐⭐
- ✅ Más control
- ✅ Logs detallados
- ✅ Integraciones personalizadas

---

### Para Exportar Reportes Automáticamente

**Opción 1: Power Automate** ⭐⭐⭐⭐⭐
- ✅ Fácil
- ✅ Envío por email directo
- **RECOMENDADO**

**Opción 2: Python + REST API** ⭐⭐⭐
- ✅ Personalización total
- ✅ Multiple formatos

---

### Para Gestionar Medidas DAX

**Opción 1: Tabular Object Model (TOM)** ⭐⭐⭐⭐
- ✅ Crear medidas programáticamente
- ✅ Migrar entre ambientes

**Opción 2: DAX Studio** ⭐⭐⭐
- ✅ Export/Import manual
- ✅ Más simple

---

### Para Deployment CI/CD

**Opción 1: Azure DevOps Pipelines** ⭐⭐⭐⭐⭐
- ✅ Control de versiones
- ✅ Deployment automático
- ✅ Testing

---

## 📋 Scripts Listos Para Usar

### Script 1: Actualización Diaria Completa

```python
# refresh_daily.py
from powerbi_automation import PowerBIAutomation
from datetime import datetime
import sys

def main():
    # Configuración
    config = {
        'tenant_id': 'your-tenant-id',
        'client_id': 'your-client-id',
        'client_secret': 'your-client-secret',
        'workspace_id': 'your-workspace-id',
        'dataset_id': 'your-dataset-id'
    }
    
    print(f"🚀 Iniciando actualización: {datetime.now()}")
    
    # Crear cliente
    pbi = PowerBIAutomation(
        config['tenant_id'],
        config['client_id'],
        config['client_secret']
    )
    
    # Autenticar
    if not pbi.get_token():
        print("❌ Error en autenticación")
        sys.exit(1)
    
    # Actualizar
    if not pbi.refresh_dataset(config['workspace_id'], config['dataset_id']):
        print("❌ Error iniciando actualización")
        sys.exit(1)
    
    # Esperar
    if not pbi.wait_for_refresh(config['workspace_id'], config['dataset_id']):
        print("❌ Actualización falló")
        sys.exit(1)
    
    print(f"✅ Actualización completada: {datetime.now()}")

if __name__ == "__main__":
    main()
```

**Programar en Linux:**

```bash
# Agregar a crontab
crontab -e

# Ejecutar diario a las 7:00 AM
0 7 * * * /usr/bin/python3 /path/to/refresh_daily.py >> /var/log/powerbi_refresh.log 2>&1
```

---

### Script 2: Exportar Reporte Semanal

```python
# export_weekly_report.py
from powerbi_automation import PowerBIAutomation
from datetime import datetime

def main():
    config = {
        'tenant_id': 'your-tenant-id',
        'client_id': 'your-client-id',
        'client_secret': 'your-client-secret',
        'workspace_id': 'your-workspace-id',
        'report_id': 'your-report-id'
    }
    
    pbi = PowerBIAutomation(
        config['tenant_id'],
        config['client_id'],
        config['client_secret']
    )
    
    if not pbi.get_token():
        return
    
    # Nombre con fecha
    filename = f"reporte_inventarios_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Exportar
    pbi.export_to_pdf(
        config['workspace_id'],
        config['report_id'],
        filename
    )
    
    # Enviar por email
    pbi.send_email_notification(
        to_email="gerencia@empresa.com",
        subject=f"📊 Reporte Semanal - {datetime.now().strftime('%d/%m/%Y')}",
        body=f"Adjunto reporte de inventarios negativos."
    )

if __name__ == "__main__":
    main()
```

**Programar semanalmente:**

```bash
# Lunes a las 8:00 AM
0 8 * * 1 /usr/bin/python3 /path/to/export_weekly_report.py
```

---

## 🔐 Configuración de Azure AD (para REST API)

### Pasos:

1. **Ir a Azure Portal**
   ```
   https://portal.azure.com → Azure Active Directory
   ```

2. **Registrar App**
   ```
   App registrations → New registration
   Nombre: PowerBI Automation
   Redirect URI: http://localhost
   ```

3. **Obtener IDs**
   ```
   Application (client) ID: xxxx-xxxx-xxxx
   Directory (tenant) ID: yyyy-yyyy-yyyy
   ```

4. **Crear Secret**
   ```
   Certificates & secrets → New client secret
   Copiar valor: zzzz-zzzz-zzzz
   ```

5. **Dar Permisos**
   ```
   API permissions → Add permission
   Power BI Service → Delegated permissions
   Seleccionar: Dataset.ReadWrite.All, Report.Read.All
   Grant admin consent
   ```

---

## ✅ Recomendación Para Ti

### Fase 1: Ahora (Mientras pruebas local)

**No automatizar todavía**
- Diseña el dashboard primero
- Prueba con archivos locales
- Refresca manual (F5)

---

### Fase 2: Cuando SharePoint esté listo

**Power Automate** ⭐⭐⭐⭐⭐

```
Ventajas:
✅ Sin código
✅ Configuración en 5 minutos
✅ Integración nativa con SharePoint
✅ Notificaciones automáticas
✅ Gratis (incluido en licencia Office 365)

Flujo:
Bot → SharePoint (6:00 AM)
  ↓
Power Automate → Refresh dataset (7:00 AM)
  ↓
Power BI actualizado → Usuarios ven datos frescos
```

---

### Fase 3: Si necesitas más control

**Python + REST API**

```python
✅ Logs detallados
✅ Manejo de errores personalizado
✅ Integraciones adicionales
✅ Exportación automática de reportes
✅ Envío de alertas personalizadas
```

---

## 📚 Recursos

### Documentación Oficial

- **Power BI REST API**: https://docs.microsoft.com/en-us/rest/api/power-bi/
- **PowerShell**: https://docs.microsoft.com/en-us/powershell/power-bi/
- **Power Automate**: https://powerautomate.microsoft.com/
- **Tabular Object Model**: https://docs.microsoft.com/en-us/analysis-services/tom/

### Ejemplos de Código

- **GitHub - Power BI Python**: https://github.com/microsoft/powerbi-python
- **GitHub - PowerBI REST API Samples**: https://github.com/microsoft/PowerBI-Developer-Samples

---

## 🎯 Próximos Pasos

¿Qué quieres automatizar primero?

**[ A ]** Actualización diaria de datos (Recomiendo Power Automate)

**[ B ]** Exportar reportes semanales (Recomiendo Power Automate)

**[ C ]** Crear medidas DAX automáticamente (Necesitas TOM)

**[ D ]** Todo lo anterior con Python (Script completo)

**[ E ]** Solo necesito saber que existe, por ahora actualizo manual

---

**¡Hay MUCHAS formas de automatizar Power BI! 🚀**