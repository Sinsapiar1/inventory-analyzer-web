#!/usr/bin/env python3
"""
Script de Ejemplo para el Área de Sistemas
===========================================

Este script muestra cómo generar un archivo .db compatible
con el Analizador de Inventarios Negativos v6.3.

Requisitos:
- Python 3.6+
- pandas
- sqlite3 (incluido en Python estándar)

Uso:
    python ejemplo_generacion_db_sistemas.py

Autor: Raúl Pivet
Fecha: Octubre 2025
Versión: 1.0
"""

import sqlite3
import pandas as pd
from datetime import datetime
import sys

def crear_db_ejemplo():
    """
    Crea un archivo .db de ejemplo con la estructura correcta
    """
    
    print("="*60)
    print("GENERADOR DE ARCHIVO .DB PARA ANALIZADOR DE INVENTARIOS")
    print("="*60)
    print()
    
    # Nombre del archivo de salida
    fecha_hoy = datetime.now().strftime('%Y%m%d')
    db_filename = f'inventarios_{fecha_hoy}.db'
    
    print(f"📁 Creando archivo: {db_filename}")
    print()
    
    # Conectar a SQLite (crea el archivo si no existe)
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    
    # 1. CREAR TABLA
    print("🗄️  Paso 1: Creando tabla 'inventarios_negativos'...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventarios_negativos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            nombre TEXT,
            almacen TEXT,
            id_pallet TEXT NOT NULL,
            cantidad_negativa REAL NOT NULL,
            disponible REAL,
            fecha_reporte DATE NOT NULL,
            archivo_origen TEXT,
            fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("   ✅ Tabla creada exitosamente")
    print()
    
    # 2. CREAR ÍNDICES
    print("🔑 Paso 2: Creando índices para optimización...")
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fecha ON inventarios_negativos(fecha_reporte)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_codigo ON inventarios_negativos(codigo)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pallet ON inventarios_negativos(id_pallet)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_almacen ON inventarios_negativos(almacen)')
    
    print("   ✅ Índices creados exitosamente")
    print()
    
    # 3. INSERTAR DATOS DE EJEMPLO
    print("📊 Paso 3: Insertando datos de ejemplo...")
    
    # Datos de ejemplo (simula lo que vendría del ERP)
    datos_ejemplo = [
        # (codigo, nombre, almacen, id_pallet, cantidad_negativa, disponible, fecha_reporte, archivo_origen)
        ('PROD001', 'Tornillo M8 x 20mm', 'ALM01', 'PAL12345', -15.0, -15.0, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
        ('PROD002', 'Tuerca M8', 'ALM01', 'PAL12346', -8.5, -8.5, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
        ('PROD003', 'Arandela Plana M8', 'ALM02', 'PAL12347', -23.0, -23.0, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
        ('PROD004', 'Cable RJ45 Cat6', 'ALM02', 'PAL12348', -5.0, -5.0, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
        ('PROD005', 'Conector RJ45', 'ALM03', 'PAL12349', -12.0, -12.0, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
        ('PROD006', 'Switch 24 puertos', 'ALM03', 'PAL12350', -3.0, -3.0, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
        ('PROD007', 'Rack 19" 42U', 'ALM01', 'PAL12351', -2.0, -2.0, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
        ('PROD008', 'Patch Panel 24p', 'ALM02', 'PAL12352', -7.0, -7.0, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
        ('PROD009', 'Organizador cables', 'ALM01', 'PAL12353', -18.0, -18.0, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
        ('PROD010', 'Bandeja rack', 'ALM03', 'PAL12354', -4.0, -4.0, '2025-10-21', 'ERP_EXPORT_EJEMPLO'),
    ]
    
    cursor.executemany('''
        INSERT INTO inventarios_negativos 
        (codigo, nombre, almacen, id_pallet, cantidad_negativa, disponible, fecha_reporte, archivo_origen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', datos_ejemplo)
    
    print(f"   ✅ {len(datos_ejemplo)} registros insertados")
    print()
    
    # 4. COMMIT Y CERRAR
    conn.commit()
    conn.close()
    
    print("💾 Paso 4: Guardando archivo...")
    print(f"   ✅ Archivo '{db_filename}' creado exitosamente")
    print()
    
    # 5. VALIDAR
    print("🔍 Paso 5: Validando archivo generado...")
    validar_db(db_filename)
    
    return db_filename


def validar_db(db_filename):
    """
    Valida que el archivo .db cumple con los requisitos
    """
    
    try:
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        
        # Verificar tabla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventarios_negativos'")
        if not cursor.fetchone():
            print("   ❌ Error: Tabla 'inventarios_negativos' no existe")
            return False
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM inventarios_negativos")
        count = cursor.fetchone()[0]
        print(f"   ✅ Tabla 'inventarios_negativos' encontrada con {count} registros")
        
        # Verificar que todos son negativos
        cursor.execute("SELECT COUNT(*) FROM inventarios_negativos WHERE cantidad_negativa >= 0")
        no_negativos = cursor.fetchone()[0]
        if no_negativos > 0:
            print(f"   ⚠️  Advertencia: {no_negativos} registros tienen cantidad >= 0")
        else:
            print("   ✅ Todos los registros tienen cantidad negativa")
        
        # Verificar columnas requeridas
        cursor.execute("PRAGMA table_info(inventarios_negativos)")
        columnas = {row[1] for row in cursor.fetchall()}
        
        requeridas = {'codigo', 'id_pallet', 'cantidad_negativa', 'fecha_reporte'}
        if requeridas.issubset(columnas):
            print("   ✅ Todas las columnas requeridas están presentes")
        else:
            faltantes = requeridas - columnas
            print(f"   ❌ Faltan columnas: {faltantes}")
            return False
        
        # Ver ejemplo de datos
        cursor.execute("SELECT codigo, nombre, cantidad_negativa, fecha_reporte FROM inventarios_negativos LIMIT 3")
        ejemplos = cursor.fetchall()
        
        print()
        print("   📋 Ejemplo de datos:")
        for ej in ejemplos:
            print(f"      Código: {ej[0]}, Nombre: {ej[1]}, Cantidad: {ej[2]}, Fecha: {ej[3]}")
        
        conn.close()
        
        print()
        print("   ✅ VALIDACIÓN EXITOSA - El archivo es compatible")
        print()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error al validar: {e}")
        return False


def ejemplo_con_pandas():
    """
    Ejemplo alternativo usando pandas (más fácil si ya tienes un CSV o DataFrame)
    """
    
    print()
    print("="*60)
    print("MÉTODO ALTERNATIVO: Usando Pandas")
    print("="*60)
    print()
    
    # Crear DataFrame de ejemplo (puede venir de un CSV o de una consulta SQL)
    datos = {
        'codigo': ['PROD011', 'PROD012', 'PROD013'],
        'nombre': ['Producto A', 'Producto B', 'Producto C'],
        'almacen': ['ALM01', 'ALM02', 'ALM01'],
        'id_pallet': ['PAL001', 'PAL002', 'PAL003'],
        'cantidad_negativa': [-10.0, -15.5, -7.0],
        'disponible': [-10.0, -15.5, -7.0],
        'fecha_reporte': ['2025-10-21', '2025-10-21', '2025-10-21'],
        'archivo_origen': ['PANDAS_EJEMPLO', 'PANDAS_EJEMPLO', 'PANDAS_EJEMPLO']
    }
    
    df = pd.DataFrame(datos)
    
    print("📊 DataFrame creado:")
    print(df)
    print()
    
    # Guardar a SQLite
    db_filename = 'inventarios_pandas_ejemplo.db'
    conn = sqlite3.connect(db_filename)
    
    # Escribir DataFrame a SQLite
    df.to_sql('inventarios_negativos', conn, if_exists='replace', index=False)
    
    # Crear índices
    cursor = conn.cursor()
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fecha ON inventarios_negativos(fecha_reporte)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_codigo ON inventarios_negativos(codigo)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Archivo '{db_filename}' creado con pandas")
    print()


def ejemplo_consulta_sql_server():
    """
    Muestra un ejemplo de cómo sería la consulta desde SQL Server
    (Este código no se ejecuta, solo es referencia)
    """
    
    query_ejemplo = """
    -- EJEMPLO DE QUERY PARA SQL SERVER
    -- Copiar esta estructura y adaptarla a tus tablas
    
    SELECT 
        codigo_articulo AS codigo,
        nombre_producto AS nombre,
        codigo_almacen AS almacen,
        id_pallet AS id_pallet,
        inventario_fisico AS cantidad_negativa,
        fisica_disponible AS disponible,
        CONVERT(VARCHAR(10), GETDATE(), 120) AS fecha_reporte,  -- Formato YYYY-MM-DD
        'ERP_AUTOMATICO' AS archivo_origen,
        GETDATE() AS fecha_extraccion
    FROM 
        [BaseDatos].[Schema].[TuTablaInventario]  -- ← CAMBIAR POR TU TABLA
    WHERE 
        inventario_fisico < 0                      -- Solo negativos
        AND id_pallet IS NOT NULL                  -- Con pallet válido
        AND id_pallet != ''                        -- Pallet no vacío
    ORDER BY 
        fecha_reporte DESC, codigo_articulo;
    """
    
    print()
    print("="*60)
    print("EJEMPLO DE QUERY PARA SQL SERVER")
    print("="*60)
    print(query_ejemplo)


# PROGRAMA PRINCIPAL
if __name__ == '__main__':
    
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   GENERADOR DE ARCHIVO .DB PARA ÁREA DE SISTEMAS         ║")
    print("║   Analizador de Inventarios Negativos v6.3               ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    # Método 1: Creación manual con SQL
    db_creado = crear_db_ejemplo()
    
    # Método 2: Usando pandas (más fácil)
    ejemplo_con_pandas()
    
    # Mostrar query de ejemplo para SQL Server
    ejemplo_consulta_sql_server()
    
    print()
    print("="*60)
    print("ARCHIVOS GENERADOS:")
    print("="*60)
    print(f"1. {db_creado} (creado con SQL)")
    print("2. inventarios_pandas_ejemplo.db (creado con pandas)")
    print()
    print("✅ ¡Ejemplos completados exitosamente!")
    print()
    print("📚 PRÓXIMOS PASOS:")
    print("   1. Revisar los archivos .db generados")
    print("   2. Probarlos en la aplicación de inventarios")
    print("   3. Adaptar el código a tu sistema ERP")
    print("   4. Leer ESPECIFICACION_TECNICA_DB_SISTEMAS.md para más detalles")
    print()
    print("="*60)
