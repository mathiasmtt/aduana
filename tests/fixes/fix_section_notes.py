#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corregir las notas de sección en la base de datos.
"""

import pandas as pd
import os
import re
import sqlite3
from roman_mapping import ROMAN_MAPPING

def roman_to_decimal(roman):
    """Convierte un número romano a formato decimal con ceros a la izquierda."""
    if roman in ROMAN_MAPPING:
        decimal = ROMAN_MAPPING[roman]
        # Formatear con ceros a la izquierda (01, 02, etc.)
        return f"{decimal:02d}"
    return None

def get_section_notes_from_db():
    """Obtiene todas las notas de sección de la base de datos."""
    db_path = os.path.join('data', 'database.sqlite3')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT section_number, note_text FROM section_notes ORDER BY section_number")
    section_notes = {row['section_number']: row['note_text'] for row in cursor.fetchall()}
    
    conn.close()
    return section_notes

def extract_section_notes_from_excel(excel_file):
    """Extrae correctamente las notas de sección del archivo Excel."""
    try:
        # Cargar todas las hojas del Excel
        xl = pd.ExcelFile(excel_file)
        print(f"Archivo Excel cargado. Hojas disponibles: {', '.join(xl.sheet_names)}")
        
        section_notes = {}
        section_titles = {}
        
        # Para cada hoja del Excel
        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            print(f"\nBuscando notas de sección en la hoja: {sheet_name}")
            
            # Convertir a texto para facilitar la búsqueda
            df_text = df.astype(str)
            
            # Buscar patrones claros de encabezados de sección
            for i, row in df.iterrows():
                # Convertir toda la fila a texto y unir
                row_text = ' '.join([str(cell) for cell in row if str(cell) != 'nan' and str(cell).strip()])
                
                # Buscar patrones como "Sección I", "SECCIÓN I", etc.
                section_match = re.search(r'SECCI[ÓO]N\s+(I{1,3}|IV|VI{1,3}|I?X|XI{1,3}|XI?V|XVI{1,3}|XI?X|XXI?)($|\s+)', row_text.upper())
                
                if section_match:
                    roman_numeral = section_match.group(1)
                    decimal_section = roman_to_decimal(roman_numeral)
                    
                    if decimal_section:
                        print(f"  Encontrada Sección {roman_numeral} (número {decimal_section})")
                        
                        # Guardar el título completo de la sección
                        section_title = row_text.strip()
                        section_titles[decimal_section] = section_title
                        
                        # Buscar las notas de esta sección
                        note_rows = []
                        start_collecting = False
                        collect_note = False
                        
                        # Recorrer las filas después del encabezado de sección
                        for j in range(i+1, len(df)):
                            next_row_text = ' '.join([str(cell) for cell in df.iloc[j] if str(cell) != 'nan' and str(cell).strip()])
                            
                            # Verificar si encontramos el inicio de las notas
                            if re.search(r'(^|\s+)NOTAS?(\s+|\.|\:)', next_row_text.upper()):
                                start_collecting = True
                                collect_note = True
                                note_rows.append(next_row_text)
                                continue
                            
                            # Si estamos en modo de recolección y encontramos otra sección, paramos
                            next_section_match = re.search(r'SECCI[ÓO]N\s+(I{1,3}|IV|VI{1,3}|I?X|XI{1,3}|XI?V|XVI{1,3}|XI?X|XXI?)($|\s+)', next_row_text.upper())
                            if next_section_match and start_collecting:
                                break
                            
                            # Si estamos recolectando la nota, agregar esta línea
                            if collect_note and next_row_text.strip():
                                note_rows.append(next_row_text)
                                
                                # Verificar si esta línea marca el inicio de una lista de capítulos
                                if re.search(r'CAP[IÍ]TULO', next_row_text.upper()):
                                    break
                        
                        # Si encontramos notas, las guardamos
                        if note_rows:
                            section_notes[decimal_section] = '\n'.join([section_title] + note_rows)
        
        return section_notes, section_titles
    
    except Exception as e:
        print(f"Error al procesar el archivo Excel: {e}")
        return {}, {}

def update_section_notes_in_db(section_notes):
    """Actualiza las notas de sección en la base de datos."""
    db_path = os.path.join('data', 'database.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Primero, hacer un respaldo de las notas actuales
    cursor.execute("CREATE TABLE IF NOT EXISTS section_notes_backup AS SELECT * FROM section_notes")
    print("Respaldo de notas de sección creado en tabla section_notes_backup")
    
    # Actualizar cada nota de sección
    for section_number, note_text in section_notes.items():
        cursor.execute(
            "UPDATE section_notes SET note_text = ? WHERE section_number = ?", 
            (note_text, section_number)
        )
        print(f"Actualizada nota para sección {section_number}")
    
    conn.commit()
    
    # Verificar qué secciones se actualizaron
    cursor.execute("SELECT section_number, LENGTH(note_text) as len FROM section_notes ORDER BY section_number")
    rows = cursor.fetchall()
    print("\nResumen de notas de sección actualizadas:")
    for row in rows:
        print(f"Sección {row[0]}: {row[1]} caracteres")
    
    conn.close()

def fix_section_notes():
    """Corrige las notas de sección en la base de datos."""
    # Ruta al archivo Excel
    excel_file = os.path.join('data', 'Arancel Nacional_Abril 2024.xlsx')
    
    print(f"Procesando archivo Excel: {excel_file}")
    
    # Obtener notas actuales de la base de datos
    db_notes = get_section_notes_from_db()
    print(f"Notas de sección en base de datos: {len(db_notes)}")
    
    # Extraer notas correctas del Excel
    excel_notes, section_titles = extract_section_notes_from_excel(excel_file)
    print(f"Notas de sección extraídas del Excel: {len(excel_notes)}")
    
    # Mostrar las secciones encontradas
    for section, title in section_titles.items():
        print(f"Sección {section}: {title}")
    
    # Pedir confirmación antes de actualizar la base de datos
    if excel_notes:
        print("\n¿Desea actualizar las notas de sección en la base de datos? (s/n): ", end="")
        response = input().strip().lower()
        
        if response == 's':
            update_section_notes_in_db(excel_notes)
            print("¡Notas de sección actualizadas correctamente!")
        else:
            print("Operación cancelada por el usuario.")
    else:
        print("No se encontraron notas de sección en el Excel. No se realizaron cambios.")

if __name__ == "__main__":
    fix_section_notes()
