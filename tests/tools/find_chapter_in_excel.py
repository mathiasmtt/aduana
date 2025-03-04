#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para buscar un capítulo específico en el archivo Excel del Arancel Nacional.
"""

import os
import sys
import pandas as pd

def find_chapter(excel_path, chapter_number):
    """
    Busca un capítulo específico en el archivo Excel.
    
    Args:
        excel_path (str): Ruta al archivo Excel.
        chapter_number (str): Número del capítulo a buscar (sin ceros a la izquierda).
    """
    print(f"Buscando capítulo {chapter_number} en {excel_path}...")
    
    # Leer el archivo Excel
    df = pd.read_excel(excel_path, header=None)
    
    # Patrones de búsqueda
    patterns = [
        f"Capítulo {chapter_number}",
        f"Capítulo {chapter_number.zfill(2)}"
    ]
    
    # Buscar coincidencias
    found_rows = []
    for i, row in df.iterrows():
        cell_value = str(row[0]) if pd.notna(row[0]) else ""
        for pattern in patterns:
            if pattern in cell_value:
                found_rows.append((i, cell_value))
                # También mostrar algunas filas antes y después para contexto
                print(f"\nCoincidencia en fila {i}: {cell_value}")
                print("\nContexto (5 filas antes):")
                for j in range(max(0, i-5), i):
                    context_value = str(df.iloc[j, 0]) if pd.notna(df.iloc[j, 0]) else ""
                    print(f"  Fila {j}: {context_value}")
                
                print("\nContexto (15 filas después):")
                for j in range(i+1, min(len(df), i+16)):
                    context_value = str(df.iloc[j, 0]) if pd.notna(df.iloc[j, 0]) else ""
                    print(f"  Fila {j}: {context_value}")
                print("\n" + "-"*80 + "\n")
    
    if not found_rows:
        print(f"No se encontró el capítulo {chapter_number} exacto.")
        
        # Buscar coincidencias que comiencen con el número del capítulo
        print("\nBuscando otras coincidencias...")
        for i, row in df.iterrows():
            cell_value = str(row[0]) if pd.notna(row[0]) else ""
            if cell_value.startswith(chapter_number) or cell_value.startswith(chapter_number.zfill(2)):
                print(f"Posible coincidencia en fila {i}: {cell_value}")
    else:
        print(f"Se encontraron {len(found_rows)} coincidencias.")

def main():
    """Función principal."""
    if len(sys.argv) < 2:
        print("Por favor especifica un número de capítulo, por ejemplo: python find_chapter_in_excel.py 95")
        return
    
    chapter_number = sys.argv[1]
    excel_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    
    find_chapter(excel_path, chapter_number)

if __name__ == "__main__":
    main()
