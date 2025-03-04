#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para encontrar y mostrar los cambios en los valores AEC entre
la base de datos principal y la versión.

Este script compara los valores AEC entre las dos bases de datos y
muestra detalles completos sobre los cambios encontrados.
"""

import os
import sqlite3
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.style import Style

# Configuración de estilo
console = Console()

def obtener_datos_ncm(db_path, ncm_code):
    """
    Obtiene todos los datos de un NCM específico
    
    Args:
        db_path: Ruta a la base de datos
        ncm_code: Código NCM a consultar
        
    Returns:
        Diccionario con los datos del NCM
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Consultar datos de la tabla ncm_versions
    cursor.execute("""
        SELECT ncm_code, description, aec, ez, iz, version_date, source_file
        FROM ncm_versions 
        WHERE ncm_code = ?
    """, (ncm_code,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'ncm_code': row[0],
            'description': row[1],
            'aec': row[2],
            'ez': row[3],
            'iz': row[4],
            'version_date': row[5],
            'source_file': row[6]
        }
    else:
        return None

def encontrar_cambios_aec():
    """
    Encuentra NCMs con cambios en el valor AEC entre las dos bases de datos
    
    Returns:
        Lista de tuplas (ncm_code, aec_original, aec_version)
    """
    # Rutas a las bases de datos
    db_original = "/Users/mat/Code/aduana/data/database.sqlite3"
    db_version = "/Users/mat/Code/aduana/data/db_versions/arancel_202404.sqlite3"
    
    # Consultas SQL
    conn_original = sqlite3.connect(db_original)
    conn_version = sqlite3.connect(db_version)
    
    # Obtener todos los NCMs con sus AECs de ambas bases de datos
    df_original = pd.read_sql_query("""
        SELECT ncm_code, aec 
        FROM ncm_versions 
        WHERE aec IS NOT NULL
    """, conn_original)
    
    df_version = pd.read_sql_query("""
        SELECT ncm_code, aec 
        FROM ncm_versions 
        WHERE aec IS NOT NULL
    """, conn_version)
    
    conn_original.close()
    conn_version.close()
    
    # Preparar DataFrames para la comparación
    df_original.set_index('ncm_code', inplace=True)
    df_version.set_index('ncm_code', inplace=True)
    
    # Encontrar NCMs comunes
    ncm_comunes = list(set(df_original.index) & set(df_version.index))
    
    # Comparar AECs y encontrar diferencias
    cambios = []
    for ncm in ncm_comunes:
        aec_original = df_original.loc[ncm, 'aec']
        aec_version = df_version.loc[ncm, 'aec']
        
        if aec_original != aec_version:
            cambios.append((ncm, aec_original, aec_version))
    
    return cambios

def mostrar_cambios(cambios):
    """
    Muestra los cambios de AEC en una tabla formateada
    
    Args:
        cambios: Lista de tuplas (ncm_code, aec_original, aec_version)
    """
    db_original = "/Users/mat/Code/aduana/data/database.sqlite3"
    db_version = "/Users/mat/Code/aduana/data/db_versions/arancel_202404.sqlite3"
    
    # Crear una tabla para mostrar los cambios
    table = Table(title="Cambios en Aranceles Externos Comunes (AEC)")
    
    table.add_column("NCM", style="cyan", no_wrap=True)
    table.add_column("Descripción", style="green")
    table.add_column("AEC Original", style="blue")
    table.add_column("AEC Nuevo", style="yellow")
    table.add_column("Diferencia", style="red")
    
    # Obtener detalles completos de cada NCM
    for ncm, aec_original, aec_version in cambios:
        # Obtener datos completos
        datos_original = obtener_datos_ncm(db_original, ncm)
        datos_version = obtener_datos_ncm(db_version, ncm)
        
        if datos_original and datos_version:
            # Calcular diferencia
            diferencia = aec_version - aec_original
            signo = '+' if diferencia > 0 else ''
            
            # Descripción (usar la más reciente)
            descripcion = datos_version['description'] or datos_original['description'] or 'Sin descripción'
            
            # Añadir fila a la tabla
            table.add_row(
                ncm,
                descripcion[:80] + ('...' if len(descripcion) > 80 else ''),
                f"{aec_original:.1f}%",
                f"{aec_version:.1f}%",
                f"{signo}{diferencia:.1f}%"
            )
    
    # Mostrar la tabla
    console.print(table)

def main():
    console.print("[bold blue]Buscando cambios en los valores AEC entre las bases de datos...[/bold blue]")
    
    # Encontrar cambios
    cambios = encontrar_cambios_aec()
    
    if cambios:
        console.print(f"[bold green]Se encontraron {len(cambios)} NCMs con cambios en el valor AEC[/bold green]")
        mostrar_cambios(cambios)
    else:
        console.print("[bold yellow]No se encontraron cambios en los valores AEC entre las bases de datos.[/bold yellow]")
    
    return 0

if __name__ == "__main__":
    main()
