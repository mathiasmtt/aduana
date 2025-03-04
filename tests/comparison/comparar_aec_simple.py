#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simplificado para comparar los AEC entre las dos bases de datos.
"""

import os
import sqlite3
from contextlib import closing

def obtener_cambios_aec():
    """
    Compara los AEC entre las dos bases de datos y encuentra los cambios
    
    Returns:
        Lista de diccionarios con los cambios
    """
    # Rutas a las bases de datos
    db_original = "/Users/mat/Code/aduana/data/database.sqlite3"
    db_version = "/Users/mat/Code/aduana/data/db_versions/arancel_202404.sqlite3"
    
    cambios = []
    
    try:
        # Conectar a ambas bases de datos
        with closing(sqlite3.connect(db_original)) as conn_original, \
             closing(sqlite3.connect(db_version)) as conn_version:
            
            # Crear cursores
            cursor_original = conn_original.cursor()
            cursor_version = conn_version.cursor()
            
            # Consultar todos los NCM y AEC de la base original
            cursor_original.execute("""
                SELECT ncm_code, aec, description 
                FROM ncm_versions 
                WHERE aec IS NOT NULL
            """)
            
            rows_original = cursor_original.fetchall()
            
            # Procesar cada NCM
            for ncm_code, aec_original, desc_original in rows_original:
                # Buscar el mismo NCM en la versión
                cursor_version.execute("""
                    SELECT aec, description 
                    FROM ncm_versions 
                    WHERE ncm_code = ? AND aec IS NOT NULL
                """, (ncm_code,))
                
                row_version = cursor_version.fetchone()
                
                # Si existe en ambas bases y el AEC cambió
                if row_version and row_version[0] != aec_original:
                    aec_version = row_version[0]
                    desc_version = row_version[1] or desc_original
                    
                    cambios.append({
                        'ncm_code': ncm_code,
                        'descripcion': desc_version or 'Sin descripción',
                        'aec_original': aec_original,
                        'aec_version': aec_version,
                        'diferencia': aec_version - aec_original
                    })
        
        # Ordenar por diferencia (de mayor a menor)
        cambios.sort(key=lambda x: abs(x['diferencia']), reverse=True)
        
        return cambios
    
    except Exception as e:
        print(f"Error al comparar bases de datos: {e}")
        return []

def main():
    print("Buscando cambios en los valores AEC entre las bases de datos...")
    
    # Obtener los cambios
    cambios = obtener_cambios_aec()
    
    if cambios:
        print(f"\nSe encontraron {len(cambios)} NCMs con cambios en el valor AEC:\n")
        
        # Mostrar los primeros 3 ejemplos
        print(" NCM\t\t| AEC Original\t| AEC Nuevo\t| Diferencia\t| Descripción")
        print("-" * 100)
        
        for i, cambio in enumerate(cambios[:3], 1):
            signo = '+' if cambio['diferencia'] > 0 else ''
            print(f"{i}. {cambio['ncm_code']}\t| {cambio['aec_original']:.1f}%\t\t| {cambio['aec_version']:.1f}%\t\t| {signo}{cambio['diferencia']:.1f}%\t\t| {cambio['descripcion'][:50]}")
    else:
        print("No se encontraron cambios en los valores AEC entre las bases de datos.")
    
    return 0

if __name__ == "__main__":
    main()
