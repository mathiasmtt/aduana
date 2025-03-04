#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar que las notas de sección en la base de datos
coincidan con las que se encuentran en el archivo Excel.
"""

import pandas as pd
import os
import sys
import re
from difflib import SequenceMatcher

sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app, db
from app.models import SectionNote

# Ruta al archivo Excel
EXCEL_FILE = 'data/Arancel Nacional_Abril 2024.xlsx'

def similar(a, b):
    """Calcula la similitud entre dos cadenas de texto."""
    return SequenceMatcher(None, a, b).ratio() * 100

def extract_section_info_from_excel():
    """
    Extrae información de las secciones del archivo Excel.
    Retorna un diccionario con las secciones y sus notas.
    """
    print(f"Leyendo archivo Excel: {EXCEL_FILE}")
    
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: El archivo {EXCEL_FILE} no existe")
        return {}

    # Leer la hoja de secciones del Excel
    try:
        # Intentamos leer la primera hoja (índice 0)
        excel_data = pd.read_excel(EXCEL_FILE, sheet_name=0)
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return {}
    
    section_notes = {}
    current_section = None
    note_text = []
    section_pattern = re.compile(r'^Sección\s+([IVX]+)')
    
    for index, row in excel_data.iterrows():
        for col in excel_data.columns:
            cell_value = str(row[col])
            if pd.isna(row[col]) or cell_value == 'nan' or not cell_value.strip():
                continue
            
            # Buscar encabezados de sección
            section_match = section_pattern.search(cell_value)
            if section_match:
                # Si encontramos una nueva sección y ya teníamos una anterior
                if current_section and note_text:
                    section_notes[current_section] = '\n'.join(note_text)
                    note_text = []
                
                # Obtener el número de sección en romano
                section_roman = section_match.group(1)
                current_section = convert_roman_to_decimal(section_roman)
                note_text.append(f"Sección {section_roman}")
                continue
            
            # Si estamos en una sección y encontramos texto de nota
            if current_section and "Nota" in cell_value:
                note_text.append(cell_value)
                
                # Seguir leyendo líneas hasta encontrar otra sección o capítulo
                for i in range(index + 1, len(excel_data)):
                    next_row = excel_data.iloc[i]
                    for next_col in excel_data.columns:
                        next_value = str(next_row[next_col])
                        if pd.isna(next_row[next_col]) or next_value == 'nan' or not next_value.strip():
                            continue
                        
                        # Si encontramos una nueva sección o un capítulo, terminamos
                        if "Sección" in next_value or "Capítulo" in next_value:
                            break
                        
                        note_text.append(next_value)
                    
                    # Si terminamos, salir del bucle
                    if "Sección" in next_value or "Capítulo" in next_value:
                        break
    
    # Guardar la última sección si existe
    if current_section and note_text:
        section_notes[current_section] = '\n'.join(note_text)
    
    return section_notes

def convert_roman_to_decimal(roman):
    """Convierte un número romano a decimal y lo devuelve con formato de dos dígitos."""
    roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    decimal = 0
    prev_value = 0
    
    for char in reversed(roman):
        current_value = roman_values[char]
        if current_value >= prev_value:
            decimal += current_value
        else:
            decimal -= current_value
        prev_value = current_value
    
    # Devolver el número con formato de dos dígitos
    return f"{decimal:02d}"

def verify_section_notes():
    """
    Verifica que las notas de sección en la base de datos coincidan con
    las que se encuentran en el archivo Excel.
    """
    # Extraer notas de sección del Excel
    excel_section_notes = extract_section_info_from_excel()
    
    if not excel_section_notes:
        print("No se encontraron notas de sección en el Excel.")
        return
    
    # Obtener notas de la base de datos
    app = create_app()
    with app.app_context():
        db_section_notes = {note.section_number: note.note_text 
                          for note in SectionNote.query.all()}
    
    # Comparar notas
    sections_match = []
    sections_mismatch = []
    sections_not_in_db = []
    sections_not_in_excel = []
    
    # Verificar coincidencias
    for section_number in sorted(set(list(excel_section_notes.keys()) + list(db_section_notes.keys()))):
        print(f"\nVerificando sección {section_number}...")
        
        excel_note = excel_section_notes.get(section_number)
        db_note = db_section_notes.get(section_number)
        
        if excel_note and db_note:
            # Limpiar los textos para comparación
            excel_note_clean = re.sub(r'\s+', ' ', excel_note).strip()
            db_note_clean = re.sub(r'\s+', ' ', db_note).strip()
            
            # Comparar los primeros 100 caracteres
            excel_sample = excel_note_clean[:100]
            db_sample = db_note_clean[:100]
            
            similarity = similar(excel_sample, db_sample)
            
            if similarity >= 75:  # Umbral de similitud
                print(f"✅ Los primeros 100 caracteres coinciden (similitud: {similarity:.2f}%)")
                sections_match.append(section_number)
            else:
                print(f"❌ Los primeros 100 caracteres NO coinciden (similitud: {similarity:.2f}%)")
                print(f"  Excel: {excel_sample}")
                print(f"  Base de datos: {db_sample}")
                sections_mismatch.append(section_number)
        elif excel_note and not db_note:
            print(f"⚠️ La sección existe en Excel pero NO en la base de datos")
            sections_not_in_db.append(section_number)
        elif not excel_note and db_note:
            print(f"⚠️ La sección existe en la base de datos pero NO en Excel")
            sections_not_in_excel.append(section_number)
    
    # Mostrar resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE VERIFICACIÓN:")
    print(f"  ✅ Secciones que coinciden ({len(sections_match)}): {', '.join(sections_match)}")
    print(f"  ❌ Secciones que NO coinciden ({len(sections_mismatch)}): {', '.join(sections_mismatch)}")
    print(f"  ⚠️ Secciones sin nota en BD ({len(sections_not_in_db)}): {', '.join(sections_not_in_db)}")
    print(f"  ⚠️ Secciones sin nota en Excel ({len(sections_not_in_excel)}): {', '.join(sections_not_in_excel)}")

if __name__ == "__main__":
    verify_section_notes()
