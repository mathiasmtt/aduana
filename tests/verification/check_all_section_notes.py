#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar las notas de todas las secciones, comparando lo que hay en la base de datos
con lo que hay en el Excel.
"""
import pandas as pd
import re
import os
import numpy as np
from app import create_app, db
from app.models.section_note import SectionNote

# Ruta al archivo Excel
excel_path = os.path.join('data', 'Arancel Nacional_Abril 2024.xlsx')

def clean_row_text(row_values):
    """Limpia una fila de texto eliminando valores nulos y espacios extra."""
    clean_values = []
    for val in row_values:
        if val is not None and val != '' and not (isinstance(val, float) and np.isnan(val)):
            clean_values.append(str(val).strip())
    return " ".join(clean_values).strip()

def extract_section_notes_from_excel(section_number_roman):
    """Extrae las notas de una sección específica del Excel."""
    
    if not os.path.exists(excel_path):
        print(f"¡Error! No se encontró el archivo Excel: {excel_path}")
        return ""
    
    # Convertir número de sección decimal a número romano
    roman_numerals = {
        1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V',
        6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X',
        11: 'XI', 12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV',
        16: 'XVI', 17: 'XVII', 18: 'XVIII', 19: 'XIX', 20: 'XX',
        21: 'XXI'
    }
    
    # Convertir el número de sección a entero e intentar conseguir su representación romana
    section_number = int(section_number_roman)
    section_roman = roman_numerals.get(section_number, "")
    
    if not section_roman:
        print(f"¡Error! No se pudo convertir el número de sección {section_number} a romano.")
        return ""
    
    # Variables para almacenar las notas de la sección
    section_notes = []
    in_target_section = False
    capturing_notes = False
    
    # Leer el archivo Excel
    print(f"Buscando sección {section_roman} en el Excel...")
    # Primero obtenemos los nombres de las hojas
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names
    
    if not sheet_names:
        print("No se encontraron hojas en el Excel.")
        return ""
    
    # Por lo general, la primera hoja contiene los datos
    df = pd.read_excel(excel_path, sheet_name=sheet_names[0], header=None)
    
    # Iteramos por las filas para encontrar la sección objetivo
    for i, row in df.iterrows():
        # Limpiamos la fila
        row_text = clean_row_text(row)
        
        if not row_text:  # Saltamos filas vacías
            continue
            
        # Verificamos si encontramos la sección objetivo
        section_pattern = fr'Sección\s+{section_roman}\b|SECCION\s+{section_roman}\b|SECCIÓN\s+{section_roman}\b'
        section_match = re.search(section_pattern, row_text, re.IGNORECASE)
        if section_match:
            print(f"Encontrada Sección {section_roman} en fila {i+1}: {row_text}")
            in_target_section = True
            section_notes.append(row_text)
            continue
        
        # Verificamos si encontramos otra sección o un capítulo (lo que indicaría el final de la sección actual)
        next_section_match = re.search(r'Sección\s+[IVXLCDM]+\b|SECCION\s+[IVXLCDM]+\b|SECCIÓN\s+[IVXLCDM]+\b', row_text, re.IGNORECASE)
        chapter_match = re.search(r'^\s*Capítulo\s+\d+\b|^\s*CAPITULO\s+\d+\b|^\s*CAPÍTULO\s+\d+\b', row_text, re.IGNORECASE)
        ncm_match = re.match(r'^\s*\d{4}', row_text)
        
        if in_target_section and (next_section_match or (chapter_match and not capturing_notes) or (ncm_match and not capturing_notes)):
            if next_section_match:
                print(f"Encontrada siguiente sección en fila {i+1}, finalizando captura.")
            else:
                print(f"Encontrado inicio de capítulo o NCM en fila {i+1}, finalizando captura.")
            break
        
        # Si estamos en la sección objetivo, verificamos si son notas
        if in_target_section:
            # Verificamos si encontramos las notas
            note_match = re.search(r'Notas\.?|NOTAS\.?', row_text, re.IGNORECASE)
            if note_match:
                print(f"Encontradas notas en fila {i+1}: {row_text}")
                capturing_notes = True
                section_notes.append(row_text)
                continue
            
            # Si estamos capturando notas o título de sección, las agregamos
            if capturing_notes or len(section_notes) <= 2:  # Permitimos capturar el título completo (hasta 2 líneas)
                # Verificamos si hemos llegado al final de las notas (inicio de Capítulo)
                if chapter_match or ncm_match:
                    print(f"Final de las notas en fila {i+1}: {row_text}")
                    break
                
                # Agregar la línea a las notas
                section_notes.append(row_text)
    
    # Combinamos todas las notas en un solo texto
    return "\n".join(section_notes)

def compare_notes(db_notes, excel_notes):
    """Compara las notas de la base de datos con las del Excel."""
    db_lines = [line.strip() for line in db_notes.strip().split('\n') if line.strip()]
    excel_lines = [line.strip() for line in excel_notes.strip().split('\n') if line.strip()]
    
    # Calcular el número de líneas diferentes
    min_lines = min(len(db_lines), len(excel_lines))
    
    different_lines = 0
    for i in range(min_lines):
        if db_lines[i] != excel_lines[i]:
            different_lines += 1
    
    # Calcular la diferencia de longitud
    length_diff = abs(len(db_lines) - len(excel_lines))
    
    if different_lines == 0 and length_diff == 0:
        print("✅ Las notas coinciden exactamente.")
        return True
    else:
        print(f"❌ Hay diferencias significativas ({different_lines} líneas diferentes, {length_diff} líneas de diferencia en longitud).")
        return False

def main():
    # Crear una aplicación Flask para el contexto de SQLAlchemy
    app = create_app()
    
    with app.app_context():
        # Obtener todas las notas de sección de la base de datos
        section_notes = SectionNote.query.order_by(SectionNote.section_number).all()
        
        print(f"Encontradas {len(section_notes)} notas de sección en la base de datos.\n")
        
        # Procesar cada sección
        for section_note in section_notes:
            section_number = section_note.section_number
            section_int = int(section_number)
            
            print(f"\n{'='*80}")
            print(f"Revisando Sección {section_number}:")
            print(f"{'='*80}\n")
            
            # Mostrar las primeras líneas de la nota en la base de datos
            db_note_text = section_note.note_text
            db_lines = db_note_text.split('\n')
            
            print("En la base de datos:")
            print(f"{'-'*80}")
            
            # Mostrar las primeras 5 líneas y luego un resumen si hay más
            for i, line in enumerate(db_lines):
                if i < 5:
                    print(line)
                else:
                    remaining = len(db_lines) - 5
                    print(f"... (y {remaining} líneas más)")
                    break
            
            print(f"{'-'*80}")
            
            # Extraer las notas de la sección del Excel
            excel_note_text = extract_section_notes_from_excel(section_int)
            
            if excel_note_text:
                excel_lines = excel_note_text.split('\n')
                
                print("\nEn el Excel:")
                print(f"{'-'*80}")
                
                # Mostrar las primeras 5 líneas del Excel y luego un resumen si hay más
                for i, line in enumerate(excel_lines):
                    if i < 5:
                        print(line)
                    else:
                        remaining = len(excel_lines) - 5
                        print(f"... (y {remaining} líneas más)")
                        break
                
                print(f"{'-'*80}\n")
                
                # Comparar las notas
                compare_notes(db_note_text, excel_note_text)
            else:
                print("\n⚠️ No se pudieron extraer las notas de esta sección del Excel.\n")

if __name__ == "__main__":
    main()
