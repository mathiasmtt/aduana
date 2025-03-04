#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Muestra el contenido de un capítulo en el archivo Excel del Arancel Nacional.
"""

import sys
import pandas as pd

def view_chapter_content(chapter_number, num_rows=30):
    """
    Muestra el contenido de un capítulo en el archivo Excel.
    
    Args:
        chapter_number (str): Número de capítulo.
        num_rows (int): Número de filas a mostrar después del inicio del capítulo.
    """
    # Ruta al archivo Excel
    file_path = "data/Arancel Nacional_Abril 2024.xlsx"
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Buscar el capítulo
    target_text = f"Capítulo {chapter_number}"
    target_row = -1
    
    # Buscar el inicio del capítulo
    for i, row in df.iterrows():
        if pd.notna(row[0]) and target_text in str(row[0]):
            target_row = i
            break
    
    if target_row >= 0:
        print(f"Contenido del capítulo {chapter_number}:")
        print("-" * 40)
        
        # Mostrar las filas siguientes
        for j in range(target_row, min(target_row + num_rows, len(df))):
            if pd.notna(df.iloc[j, 0]):
                print(df.iloc[j, 0])
        
        print("-" * 40)
    else:
        print(f"No se encontró el capítulo {chapter_number}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        chapter_number = sys.argv[1]
        view_chapter_content(chapter_number)
    else:
        print("Por favor especifica un número de capítulo, por ejemplo: python view_chapter_content.py 20")
