"""
Script para generar archivos Excel de prueba para Power BI
Simula reportes diarios de inventarios negativos con fechas diferentes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path

def generar_datos_inventario(fecha, num_registros=50):
    """
    Genera datos simulados de inventario negativo para una fecha específica
    
    Args:
        fecha: datetime object de la fecha del reporte
        num_registros: cantidad de registros a generar
    """
    
    # Códigos de productos (algunos se repiten entre fechas para simular reincidencias)
    codigos_base = [
        "PROD001", "PROD002", "PROD003", "PROD004", "PROD005",
        "PROD006", "PROD007", "PROD008", "PROD009", "PROD010",
        "PROD011", "PROD012", "PROD013", "PROD014", "PROD015"
    ]
    
    nombres_productos = {
        "PROD001": "Tornillo M8 x 25mm",
        "PROD002": "Cable RJ45 Cat6",
        "PROD003": "Conector BNC",
        "PROD004": "Resistencia 1K Ohm",
        "PROD005": "Capacitor 100uF",
        "PROD006": "LED Rojo 5mm",
        "PROD007": "Switch Push Button",
        "PROD008": "Relay 12V DC",
        "PROD009": "Fusible 10A",
        "PROD010": "Terminal Block 2P",
        "PROD011": "Cable AWG 18",
        "PROD012": "Sensor PIR",
        "PROD013": "Módulo WiFi ESP32",
        "PROD014": "Display LCD 16x2",
        "PROD015": "Motor DC 12V"
    }
    
    almacenes = ["ALM01", "ALM02", "ALM03", "BODEGA_CENTRAL", "BODEGA_SUR"]
    
    # Generar datos
    datos = []
    
    for i in range(num_registros):
        # Seleccionar código (algunos se repiten más para simular productos problemáticos)
        if np.random.random() < 0.3:  # 30% de probabilidad de ser código recurrente
            codigo = np.random.choice(codigos_base[:5])  # Primeros 5 códigos son más problemáticos
        else:
            codigo = np.random.choice(codigos_base)
        
        # Generar pallet único para esta fecha
        id_pallet = f"PAL{fecha.strftime('%Y%m%d')}{i+1:03d}"
        
        # Cantidad negativa (más variedad)
        if np.random.random() < 0.2:  # 20% críticos
            cantidad_negativa = np.random.uniform(-100, -50)
        elif np.random.random() < 0.5:  # 50% medios
            cantidad_negativa = np.random.uniform(-50, -20)
        else:  # 30% bajos
            cantidad_negativa = np.random.uniform(-20, -1)
        
        # Redondear a 2 decimales
        cantidad_negativa = round(cantidad_negativa, 2)
        
        datos.append({
            'codigo': codigo,
            'nombre': nombres_productos.get(codigo, f"Producto {codigo}"),
            'almacen': np.random.choice(almacenes),
            'id_pallet': id_pallet,
            'cantidad_negativa': cantidad_negativa,
            'disponible': cantidad_negativa,  # Mismo valor que cantidad_negativa
            'fecha_reporte': fecha.strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(datos)


def generar_archivos_simulados(carpeta_destino, dias_historicos=30, registros_por_dia=50):
    """
    Genera múltiples archivos Excel simulando reportes diarios
    
    Args:
        carpeta_destino: ruta donde se guardarán los archivos
        dias_historicos: cantidad de días hacia atrás a generar
        registros_por_dia: cantidad de registros por archivo
    """
    
    # Crear carpeta si no existe
    Path(carpeta_destino).mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Generando archivos en: {carpeta_destino}")
    print(f"📅 Días a generar: {dias_historicos}")
    print(f"📊 Registros por día: {registros_por_dia}")
    print("-" * 60)
    
    fecha_fin = datetime.now()
    archivos_generados = []
    
    for i in range(dias_historicos):
        # Calcular fecha (hacia atrás desde hoy)
        fecha = fecha_fin - timedelta(days=i)
        
        # Generar datos para esta fecha
        df = generar_datos_inventario(fecha, registros_por_dia)
        
        # Nombre del archivo (formato que Power BI puede leer fácilmente)
        nombre_archivo = f"inventario_negativo_{fecha.strftime('%Y%m%d')}.xlsx"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
        
        # Guardar Excel
        df.to_excel(ruta_completa, index=False, sheet_name='Inventario')
        
        archivos_generados.append(nombre_archivo)
        print(f"✅ Generado: {nombre_archivo} ({len(df)} registros)")
    
    print("-" * 60)
    print(f"🎉 ¡Completado! {len(archivos_generados)} archivos generados")
    print(f"📂 Ubicación: {os.path.abspath(carpeta_destino)}")
    
    # Crear un resumen
    resumen = {
        'Total archivos': len(archivos_generados),
        'Fecha más antigua': (fecha_fin - timedelta(days=dias_historicos-1)).strftime('%Y-%m-%d'),
        'Fecha más reciente': fecha_fin.strftime('%Y-%m-%d'),
        'Registros por archivo': registros_por_dia,
        'Total registros': len(archivos_generados) * registros_por_dia
    }
    
    print("\n📊 RESUMEN:")
    for key, value in resumen.items():
        print(f"   {key}: {value}")
    
    return archivos_generados


def generar_variaciones_especificas(carpeta_destino):
    """
    Genera archivos con variaciones específicas para probar escenarios
    """
    
    print("\n🔬 Generando archivos de prueba específicos...")
    
    # Escenario 1: Pocos registros (probar fix de severidad)
    fecha1 = datetime.now() - timedelta(days=2)
    df1 = generar_datos_inventario(fecha1, num_registros=3)
    archivo1 = os.path.join(carpeta_destino, f"inventario_negativo_{fecha1.strftime('%Y%m%d')}_pocos.xlsx")
    df1.to_excel(archivo1, index=False, sheet_name='Inventario')
    print(f"   ✅ Archivo con pocos registros (3): {os.path.basename(archivo1)}")
    
    # Escenario 2: Muchos registros
    fecha2 = datetime.now() - timedelta(days=1)
    df2 = generar_datos_inventario(fecha2, num_registros=200)
    archivo2 = os.path.join(carpeta_destino, f"inventario_negativo_{fecha2.strftime('%Y%m%d')}_muchos.xlsx")
    df2.to_excel(archivo2, index=False, sheet_name='Inventario')
    print(f"   ✅ Archivo con muchos registros (200): {os.path.basename(archivo2)}")
    
    # Escenario 3: Valores muy similares
    fecha3 = datetime.now()
    df3 = generar_datos_inventario(fecha3, num_registros=20)
    df3['cantidad_negativa'] = -15.5  # Todos iguales
    df3['disponible'] = -15.5
    archivo3 = os.path.join(carpeta_destino, f"inventario_negativo_{fecha3.strftime('%Y%m%d')}_similares.xlsx")
    df3.to_excel(archivo3, index=False, sheet_name='Inventario')
    print(f"   ✅ Archivo con valores similares (todos -15.5): {os.path.basename(archivo3)}")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 GENERADOR DE ARCHIVOS DE PRUEBA PARA POWER BI")
    print("=" * 60)
    print()
    
    # CONFIGURACIÓN
    CARPETA_DESTINO = "./datos_prueba_powerbi"  # Cambia esta ruta si quieres
    DIAS_HISTORICOS = 30  # Generar últimos 30 días
    REGISTROS_POR_DIA = 50  # 50 registros por día
    
    # Opción 1: Generar archivos estándar
    print("📌 Opción 1: Archivos diarios estándar")
    archivos = generar_archivos_simulados(
        carpeta_destino=CARPETA_DESTINO,
        dias_historicos=DIAS_HISTORICOS,
        registros_por_dia=REGISTROS_POR_DIA
    )
    
    # Opción 2: Generar archivos con casos especiales
    print("\n📌 Opción 2: Archivos de casos especiales")
    generar_variaciones_especificas(CARPETA_DESTINO)
    
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
    print()
    print("🎯 PRÓXIMOS PASOS:")
    print()
    print("1. Abre Power BI Desktop")
    print("2. Obtener datos → Carpeta")
    print(f"3. Selecciona la carpeta: {os.path.abspath(CARPETA_DESTINO)}")
    print("4. Combinar archivos")
    print("5. ¡Listo para analizar!")
    print()
    print("💡 TIP: La fecha está en el nombre del archivo Y dentro de los datos")
    print("        Power BI puede usar cualquiera de las dos fuentes")
    print()
