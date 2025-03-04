#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer y mostrar las notas de la sección 2 del archivo Excel.
"""
import pandas as pd
import re
import os
import numpy as np

# Ruta al archivo Excel
excel_path = os.path.join('data', 'Arancel Nacional_Abril 2024.xlsx')

# Variable para almacenar las notas de la sección 2
section_2_notes = []
in_section_2 = False
capturing_notes = False
section_title = ""

# Función para limpiar una fila de texto (eliminar 'nan' y espacios extra)
def clean_row_text(row_values):
    # Convertir a string y filtrar valores nulos o 'nan'
    clean_values = []
    for val in row_values:
        if val is not None and val != '' and not (isinstance(val, float) and np.isnan(val)):
            clean_values.append(str(val).strip())
    return " ".join(clean_values).strip()

# Abrir el archivo Excel y buscar la Sección 2
if os.path.exists(excel_path):
    # Leer el archivo Excel
    print(f"Leyendo archivo Excel: {excel_path}")
    # Primero obtenemos los nombres de las hojas
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names
    
    print(f"Hojas disponibles: {sheet_names}")
    
    # Por lo general, la primera hoja contiene los datos
    if sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet_names[0], header=None)
        print(f"Examinando la hoja: {sheet_names[0]}")
        
        # Iteramos por las filas para encontrar la sección 2
        for i, row in df.iterrows():
            # Limpiamos la fila
            row_text = clean_row_text(row)
            
            if not row_text:  # Saltamos filas vacías
                continue
                
            # Verificamos si encontramos la sección 2
            section_match = re.search(r'Sección\s+II\b|SECCION\s+II\b|SECCIÓN\s+II\b', row_text, re.IGNORECASE)
            if section_match:
                print(f"Encontrada Sección II en fila {i+1}: {row_text}")
                in_section_2 = True
                section_title = row_text
                
                # Buscamos la siguiente fila para obtener el título completo
                if i + 1 < len(df):
                    next_row_text = clean_row_text(df.iloc[i+1])
                    if next_row_text and not re.search(r'Notas\.?|NOTAS\.?', next_row_text, re.IGNORECASE):
                        section_title += "\n" + next_row_text
                continue
            
            # Si estamos en la sección 2, verificamos si son notas
            if in_section_2:
                # Verificamos si encontramos las notas
                if re.search(r'Notas\.?|NOTAS\.?', row_text, re.IGNORECASE):
                    print(f"Encontradas notas en fila {i+1}: {row_text}")
                    capturing_notes = True
                    section_2_notes.append(row_text)
                    continue
                
                # Si estamos capturando notas, las agregamos
                if capturing_notes:
                    # Verificamos si hemos llegado al final de las notas (inicio de Capítulo)
                    if re.search(r'Capítulo|CAPITULO|CAPÍTULO', row_text, re.IGNORECASE):
                        print(f"Final de las notas en fila {i+1}: {row_text}")
                        capturing_notes = False
                        in_section_2 = False
                        # También incluimos la línea del capítulo para comparación
                        section_2_notes.append(row_text)
                        break
                    else:
                        # Agregar la línea a las notas
                        section_2_notes.append(row_text)
else:
    print(f"¡Error! No se encontró el archivo Excel: {excel_path}")

# Combinamos el título con las notas
complete_notes = section_title + "\n" + "\n".join(section_2_notes)

# Mostrar las notas obtenidas
print("\nNotas de la Sección 2 obtenidas del Excel:")
print("-" * 80)
print(complete_notes)
print("-" * 80)

# Mostrar las notas almacenadas en la base de datos para comparación
print("\nComparando con las notas de la base de datos:")
from app import create_app, db
from app.models.section_note import SectionNote

app = create_app()
with app.app_context():
    # Obtenemos la nota de la sección 2
    section_note = SectionNote.query.filter_by(section_number='02').first()
    if section_note:
        print("-" * 80)
        print(section_note.note_text)
        print("-" * 80)
        
        # Hacer una comparación línea por línea
        print("\nComparación línea por línea:")
        print("-" * 80)
        
        excel_lines = complete_notes.strip().split('\n')
        db_lines = section_note.note_text.strip().split('\n')
        
        # Normalizar ambos textos eliminando espacios extras
        excel_lines = [line.strip() for line in excel_lines if line.strip()]
        db_lines = [line.strip() for line in db_lines if line.strip()]
        
        min_lines = min(len(excel_lines), len(db_lines))
        
        for i in range(min_lines):
            excel_line = excel_lines[i]
            db_line = db_lines[i]
            
            if excel_line == db_line:
                print(f"[IGUAL] {excel_line}")
            else:
                print(f"[DIFERENTE]")
                print(f"  Excel: {excel_line}")
                print(f"  BD:    {db_line}")
        
        # Mostrar líneas adicionales en cualquiera de los dos lados
        if len(excel_lines) > min_lines:
            print("\nLíneas adicionales en Excel:")
            for i in range(min_lines, len(excel_lines)):
                print(f"  {excel_lines[i]}")
                
        if len(db_lines) > min_lines:
            print("\nLíneas adicionales en la base de datos:")
            for i in range(min_lines, len(db_lines)):
                print(f"  {db_lines[i]}")
    else:
        print("No se encontraron notas para la sección 2 en la base de datos.")
