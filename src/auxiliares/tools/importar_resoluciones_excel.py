#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar resoluciones de clasificación arancelaria desde un archivo Excel.
Este script borra el contenido existente en la tabla y carga los nuevos datos.
"""

import os
import sys
import sqlite3
import pandas as pd
import datetime
from pathlib import Path

# Añadir la ruta del proyecto al path de Python para poder importar los módulos
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.aduana.db_init import obtener_ruta_db

def importar_resoluciones_excel(excel_path, db_path=None):
    """
    Importa resoluciones de clasificación arancelaria desde un archivo Excel.
    
    Args:
        excel_path (str): Ruta al archivo Excel con los datos
        db_path (str, optional): Ruta a la base de datos. Por defecto, usa la configuración estándar.
    
    Returns:
        int: Número de resoluciones importadas
    """
    if db_path is None:
        db_path = obtener_ruta_db()
    
    # Verificar que el archivo Excel existe
    if not os.path.exists(excel_path):
        print(f"Error: El archivo {excel_path} no existe.")
        return 0
    
    try:
        # Leer el archivo Excel
        print(f"Leyendo el archivo Excel: {excel_path}")
        df = pd.read_excel(excel_path)
        
        # Verificar que el DataFrame tiene las columnas necesarias
        required_columns = ['YEAR', 'NUMBER ', 'NCM', 'CONCEPTO', 'FECHA']
        for col in required_columns:
            if col not in df.columns:
                print(f"Error: El archivo no contiene la columna '{col}'")
                return 0
        
        # Conectar a la base de datos
        print(f"Conectando a la base de datos: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Borrar todos los registros de la tabla
        print("Borrando registros existentes...")
        cursor.execute("DELETE FROM resoluciones_clasificacion_arancelaria")
        
        # Preparar los datos para inserción
        count = 0
        for _, row in df.iterrows():
            try:
                year = int(row['YEAR'])
                numero = int(row['NUMBER '])  # Nota el espacio en 'NUMBER '
                ncm = row['NCM']
                concepto = row['CONCEPTO']
                
                # Procesar la fecha
                fecha = row['FECHA']
                if isinstance(fecha, str):
                    try:
                        fecha = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
                    except ValueError:
                        print(f"Error en formato de fecha: {fecha}. Usando fecha actual.")
                        fecha = datetime.date.today()
                elif isinstance(fecha, datetime.datetime):
                    fecha = fecha.date()
                else:
                    fecha = datetime.date.today()
                
                # Insertar en la base de datos
                cursor.execute('''
                INSERT INTO resoluciones_clasificacion_arancelaria 
                (year, numero, fecha, referencia, dictamen, resolucion) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (year, numero, fecha, ncm, concepto, ''))
                
                count += 1
            except Exception as e:
                print(f"Error al procesar fila {count+1}: {str(e)}")
        
        # Guardar los cambios
        conn.commit()
        conn.close()
        
        print(f"Se importaron {count} resoluciones exitosamente")
        return count
    
    except Exception as e:
        print(f"Error al importar resoluciones: {str(e)}")
        return 0

def main():
    """Función principal para ejecutar el script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Importar resoluciones de clasificación arancelaria desde un archivo Excel')
    
    parser.add_argument(
        '--excel', 
        type=str, 
        default=str(project_root / 'data' / 'excel' / 'RESOLUCIONES_CLASIF_ARANCELARIA.xlsx'),
        help='Ruta al archivo Excel con las resoluciones'
    )
    
    parser.add_argument(
        '--db', 
        type=str,
        help='Ruta a la base de datos (opcional)'
    )
    
    args = parser.parse_args()
    
    # Ejecutar la importación
    importar_resoluciones_excel(args.excel, args.db)

if __name__ == "__main__":
    main() 