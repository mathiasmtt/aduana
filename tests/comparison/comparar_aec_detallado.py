#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script detallado para comparar los AEC entre las dos bases de datos.
Este script proporciona un análisis completo de los cambios en el AEC
con información contextual adicional.
"""

import os
import sqlite3
import datetime
from contextlib import closing

def obtener_info_ncm(db_path, ncm_code):
    """
    Obtiene información detallada de un NCM
    
    Args:
        db_path: Ruta a la base de datos
        ncm_code: Código NCM a consultar
        
    Returns:
        Diccionario con la información del NCM
    """
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Consultar en ncm_versions
            cursor.execute("""
                SELECT ncm_code, description, aec, ez, iz, uvf, 
                       version_date, source_file, cl
                FROM ncm_versions 
                WHERE ncm_code = ?
            """, (ncm_code,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'ncm_code': row[0],
                    'descripcion': row[1] or 'Sin descripción',
                    'aec': row[2],
                    'ez': row[3],
                    'iz': row[4],
                    'uvf': row[5],
                    'version_date': row[6],
                    'source_file': row[7],
                    'cl': row[8]
                }
            
            # Si no está en ncm_versions, buscar en arancel_nacional
            cursor.execute("""
                SELECT NCM, DESCRIPCION, AEC, CL, "E/Z", "I/Z", UVF, SECTION, CHAPTER
                FROM arancel_nacional
                WHERE NCM = ?
            """, (ncm_code,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'ncm_code': row[0],
                    'descripcion': row[1] or 'Sin descripción',
                    'aec': float(row[2]) if row[2] and row[2].strip() else None,
                    'ez': float(row[4]) if row[4] and row[4].strip() else None,
                    'iz': float(row[5]) if row[5] and row[5].strip() else None,
                    'uvf': float(row[6]) if row[6] and row[6].strip() else None,
                    'cl': row[3],
                    'section': row[7],
                    'chapter': row[8]
                }
            
            return None
    except Exception as e:
        print(f"Error al obtener información de NCM {ncm_code}: {e}")
        return None

def obtener_cambios_aec():
    """
    Compara los AEC entre las dos bases de datos y encuentra los cambios
    
    Returns:
        Lista de diccionarios con los cambios
    """
    # Rutas a las bases de datos
    db_original = "/Users/mat/Code/aduana/data/database.sqlite3"
    db_version = "/Users/mat/Code/aduana/data/db_versions/arancel_202404.sqlite3"
    
    # Lista para almacenar los cambios
    cambios = []
    
    # Set para evitar duplicados
    procesados = set()
    
    try:
        # Conectar a ambas bases de datos
        with closing(sqlite3.connect(db_original)) as conn_original, \
             closing(sqlite3.connect(db_version)) as conn_version:
            
            # Crear cursores
            cursor_original = conn_original.cursor()
            cursor_version = conn_version.cursor()
            
            # Consultar todos los NCM de la base original
            cursor_original.execute("""
                SELECT ncm_code FROM ncm_versions
            """)
            
            for (ncm_code,) in cursor_original.fetchall():
                # Evitar procesar el mismo NCM más de una vez
                if ncm_code in procesados:
                    continue
                
                procesados.add(ncm_code)
                
                # Obtener información completa del NCM en ambas bases
                info_original = obtener_info_ncm(db_original, ncm_code)
                info_version = obtener_info_ncm(db_version, ncm_code)
                
                # Verificar si ambos existen y si hay cambio en AEC
                if info_original and info_version and \
                   info_original['aec'] is not None and info_version['aec'] is not None and \
                   info_original['aec'] != info_version['aec']:
                    
                    # Calcular diferencia
                    diferencia = info_version['aec'] - info_original['aec']
                    
                    # Crear un registro con toda la información relevante
                    cambio = {
                        'ncm_code': ncm_code,
                        'descripcion': info_version['descripcion'],
                        'aec_original': info_original['aec'],
                        'aec_version': info_version['aec'],
                        'diferencia': diferencia,
                        'ez_original': info_original.get('ez'),
                        'ez_version': info_version.get('ez'),
                        'iz_original': info_original.get('iz'),
                        'iz_version': info_version.get('iz'),
                        'uvf_original': info_original.get('uvf'),
                        'uvf_version': info_version.get('uvf'),
                        'chapter': info_version.get('chapter', info_original.get('chapter')),
                        'section': info_version.get('section', info_original.get('section'))
                    }
                    
                    cambios.append(cambio)
        
        # Ordenar por magnitud de la diferencia (de mayor a menor)
        cambios.sort(key=lambda x: abs(x['diferencia']), reverse=True)
        
        return cambios
    
    except Exception as e:
        print(f"Error al comparar bases de datos: {e}")
        return []

def mostrar_cambio_detallado(cambio, num):
    """
    Muestra información detallada de un cambio de AEC
    
    Args:
        cambio: Diccionario con la información del cambio
        num: Número de cambio para mostrar
    """
    ncm = cambio['ncm_code']
    desc = cambio['descripcion']
    aec_orig = cambio['aec_original']
    aec_new = cambio['aec_version']
    dif = cambio['diferencia']
    
    # Truncar descripción si es muy larga
    if len(desc) > 70:
        desc = desc[:67] + "..."
    
    # Calcular cambio porcentual relativo
    if aec_orig > 0:
        cambio_porcentual = (dif / aec_orig) * 100
        texto_porcentual = f"({cambio_porcentual:+.1f}%)"
    else:
        texto_porcentual = "(nuevo valor)"
    
    # Formatear texto
    signo = "+" if dif > 0 else ""
    
    print(f"\n{'='*100}")
    print(f"CAMBIO #{num}: NCM {ncm}")
    print(f"{'='*100}")
    print(f"Descripción: {desc}")
    print(f"Sección/Capítulo: {cambio.get('section', 'N/A')} / {cambio.get('chapter', 'N/A')}")
    print(f"\nAEC ORIGINAL: {aec_orig:.1f}%  →  AEC NUEVO: {aec_new:.1f}%  →  DIFERENCIA: {signo}{dif:.1f}% {texto_porcentual}")
    
    # Mostrar otros valores si han cambiado
    if cambio.get('ez_original') != cambio.get('ez_version') and cambio.get('ez_original') is not None and cambio.get('ez_version') is not None:
        print(f"E/Z ORIGINAL: {cambio['ez_original']:.1f}%  →  E/Z NUEVO: {cambio['ez_version']:.1f}%")
    
    if cambio.get('iz_original') != cambio.get('iz_version') and cambio.get('iz_original') is not None and cambio.get('iz_version') is not None:
        print(f"I/Z ORIGINAL: {cambio['iz_original']:.1f}%  →  I/Z NUEVO: {cambio['iz_version']:.1f}%")

def main():
    print("\n" + "="*50)
    print(" COMPARACIÓN DE ARANCELES EXTERNOS COMUNES (AEC)")
    print("="*50)
    print("\nBuscando cambios en los valores AEC entre las bases de datos...")
    
    # Obtener los cambios
    cambios = obtener_cambios_aec()
    
    if cambios:
        print(f"\n[OK] Se encontraron {len(cambios)} NCMs con cambios en el valor AEC.")
        
        # Mostrar resumen
        print("\nRESUMEN DE CAMBIOS:")
        print(f"{'NCM':<15} {'AEC ORIG':<10} {'AEC NUEVO':<10} {'DIFERENCIA':<12} {'DESCRIPCIÓN':<40}")
        print("-" * 90)
        
        for i, cambio in enumerate(cambios[:10], 1):
            signo = "+" if cambio['diferencia'] > 0 else ""
            desc_corta = cambio['descripcion'][:37] + "..." if len(cambio['descripcion']) > 40 else cambio['descripcion']
            print(f"{cambio['ncm_code']:<15} {cambio['aec_original']:<10.1f} {cambio['aec_version']:<10.1f} {signo}{cambio['diferencia']:<10.1f} {desc_corta:<40}")
        
        # Mostrar los 3 primeros cambios en detalle
        print("\nDETALLE DE LOS 3 CAMBIOS MÁS SIGNIFICATIVOS:")
        for i, cambio in enumerate(cambios[:3], 1):
            mostrar_cambio_detallado(cambio, i)
    else:
        print("\n[INFO] No se encontraron cambios en los valores AEC entre las bases de datos.")
    
    print("\n" + "="*50)
    return 0

if __name__ == "__main__":
    main()
