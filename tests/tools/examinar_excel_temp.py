#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para examinar la estructura de un archivo Excel
"""

import pandas as pd
import sys

def examinar_excel(file_path):
    """
    Examina la estructura de un archivo Excel y muestra información relevante
    
    Args:
        file_path: Ruta al archivo Excel
    """
    print(f"Examinando archivo: {file_path}")
    
    try:
        # Leer información del archivo
        excel_file = pd.ExcelFile(file_path)
        
        # Mostrar hojas disponibles
        print(f"\nHojas disponibles: {excel_file.sheet_names}")
        
        # Examinar cada hoja
        for sheet_name in excel_file.sheet_names:
            print(f"\n{'=' * 50}")
            print(f"Hoja: {sheet_name}")
            print(f"{'=' * 50}")
            
            # Leer las primeras filas para obtener información
            df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=5)
            
            # Mostrar columnas
            print(f"Columnas ({len(df.columns)}):")
            for col in df.columns:
                print(f"  - {col}")
            
            # Mostrar tamaño
            full_df = pd.read_excel(excel_file, sheet_name=sheet_name)
            print(f"\nDimensiones: {full_df.shape[0]} filas × {full_df.shape[1]} columnas")
            
            # Mostrar primeras filas
            print("\nPrimeras 3 filas:")
            print(df.head(3))
            
    except Exception as e:
        print(f"Error al examinar el archivo: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        examinar_excel(sys.argv[1])
    else:
        print("Uso: python examinar_excel.py <ruta_al_archivo_excel>")
