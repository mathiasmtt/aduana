#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para comparar los Aranceles Externos Comunes (AEC) entre dos bases de datos
y encontrar diferencias.

Este script consulta directamente las bases de datos SQLite para encontrar
NCMs donde el AEC ha cambiado entre versiones.
"""

import os
import sys
import sqlite3
import pandas as pd
from contextlib import closing

def consultar_aec(db_path):
    """
    Consulta la base de datos para obtener los NCM y sus AEC
    
    Args:
        db_path: Ruta a la base de datos SQLite
        
    Returns:
        DataFrame con código NCM y AEC
    """
    if not os.path.exists(db_path):
        print(f"Error: La base de datos {db_path} no existe.")
        return None
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            # Primero verificamos si existe la tabla ncm
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ncm'")
            if not cursor.fetchone():
                print(f"Error: La tabla 'ncm' no existe en la base de datos {db_path}")
                return None
            
            # Verificamos qué columnas tiene la tabla ncm
            cursor.execute("PRAGMA table_info(ncm)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            # Buscamos las columnas que contienen el AEC
            col_aec = None
            for col in columnas:
                if "aec" in col.lower() or "arancel_externo" in col.lower():
                    col_aec = col
                    break
            
            if not col_aec:
                print(f"Error: No se encontró una columna AEC en la tabla ncm de {db_path}")
                return None
            
            # Consultamos los NCM con sus AEC
            query = f"SELECT code, {col_aec} FROM ncm"
            df = pd.read_sql_query(query, conn)
            
            # Renombramos las columnas para estandarizar
            df.columns = ['NCM', 'AEC']
            
            return df
    
    except Exception as e:
        print(f"Error al consultar la base de datos {db_path}: {e}")
        return None

def comparar_aec(df1, df2):
    """
    Compara los AEC entre dos DataFrames y encuentra las diferencias
    
    Args:
        df1: DataFrame con los AEC de la primera base de datos
        df2: DataFrame con los AEC de la segunda base de datos
        
    Returns:
        DataFrame con las diferencias encontradas
    """
    if df1 is None or df2 is None:
        return None
    
    # Preparamos los DataFrames para la comparación
    df1 = df1.set_index('NCM')
    df2 = df2.set_index('NCM')
    
    # Encontramos los NCM comunes
    ncm_comunes = set(df1.index) & set(df2.index)
    
    # Creamos una lista para almacenar las diferencias
    diferencias = []
    
    # Comparamos los AEC para cada NCM común
    for ncm in ncm_comunes:
        aec1 = df1.loc[ncm, 'AEC']
        aec2 = df2.loc[ncm, 'AEC']
        
        # Si hay diferencia, lo agregamos a la lista
        if aec1 != aec2:
            diferencias.append({
                'NCM': ncm,
                'AEC_anterior': aec1,
                'AEC_nuevo': aec2,
                'Diferencia': aec2 - aec1
            })
    
    # Convertimos a DataFrame
    df_diferencias = pd.DataFrame(diferencias)
    
    # Ordenamos por la magnitud de la diferencia (de mayor a menor)
    if not df_diferencias.empty:
        df_diferencias = df_diferencias.sort_values(by='Diferencia', ascending=False)
    
    return df_diferencias

def main():
    # Rutas a las bases de datos
    db_original = "/Users/mat/Code/aduana/data/database.sqlite3"
    db_version = "/Users/mat/Code/aduana/data/db_versions/arancel_202404.sqlite3"
    
    # Verificar existencia de las bases de datos
    if not os.path.exists(db_original):
        print(f"Error: La base de datos original {db_original} no existe.")
        return 1
    
    if not os.path.exists(db_version):
        print(f"Error: La base de datos de versión {db_version} no existe.")
        return 1
    
    # Consultar AEC de ambas bases de datos
    print(f"Consultando AEC de la base de datos original: {db_original}")
    df_original = consultar_aec(db_original)
    if df_original is not None:
        print(f"  - {len(df_original)} registros encontrados")
    
    print(f"Consultando AEC de la base de datos de versión: {db_version}")
    df_version = consultar_aec(db_version)
    if df_version is not None:
        print(f"  - {len(df_version)} registros encontrados")
    
    # Comparar los AEC
    print("Comparando AEC entre las bases de datos...")
    diferencias = comparar_aec(df_original, df_version)
    
    if diferencias is not None and not diferencias.empty:
        print(f"\nSe encontraron {len(diferencias)} NCMs con cambios en el AEC:")
        
        # Mostrar los primeros 3 ejemplos
        ejemplos = min(3, len(diferencias))
        print(f"\nEjemplos de NCMs con cambios en el AEC:")
        
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 120)
        pd.set_option('display.precision', 2)
        
        print(diferencias.head(ejemplos).to_string(index=False))
        
        return 0
    else:
        print("No se encontraron diferencias en el AEC entre las bases de datos.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
