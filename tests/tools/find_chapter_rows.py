#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para encontrar y mostrar filas específicas del archivo Excel.
"""

import sys
import pandas as pd

def show_rows(start_row, end_row, file_path):
    """
    Muestra las filas específicas del archivo Excel.
    
    Args:
        start_row (int): Fila inicial.
        end_row (int): Fila final.
        file_path (str): Ruta al archivo Excel.
    """
    print(f"Mostrando filas {start_row} a {end_row} de {file_path}")
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Mostrar las filas
    for i in range(start_row, min(end_row + 1, len(df))):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        print(f"Fila {i}: {cell_value}")

def main():
    """Función principal."""
    if len(sys.argv) < 3:
        print("Uso: python find_chapter_rows.py <fila_inicial> <fila_final>")
        print("Ejemplo: python find_chapter_rows.py 8306 8350")
        return
    
    start_row = int(sys.argv[1])
    end_row = int(sys.argv[2])
    file_path = "data/Arancel Nacional_Abril 2024.xlsx"
    
    show_rows(start_row, end_row, file_path)

if __name__ == "__main__":
    main()
