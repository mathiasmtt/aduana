#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar los códigos NCM 2004 en el archivo Excel y revisar las notas de sección.
"""

import pandas as pd
import os
import re
import sqlite3

def get_section_notes_from_db():
    """Obtiene todas las notas de sección de la base de datos."""
    # Ruta a la base de datos
    db_path = os.path.join('data', 'database.sqlite3')
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Consultar todas las notas de sección
    cursor.execute("SELECT section_number, note_text FROM section_notes ORDER BY section_number")
    section_notes = {row['section_number']: row['note_text'] for row in cursor.fetchall()}
    
    conn.close()
    return section_notes

def extract_section_notes_from_excel(excel_file):
    """Extrae las notas de sección del archivo Excel."""
    try:
        # Cargar el Excel
        df = pd.read_excel(excel_file, engine='openpyxl', sheet_name=None)
        
        print(f"Archivo Excel cargado. Hojas disponibles: {', '.join(df.keys())}")
        
        # Buscar la hoja que contiene las notas de sección
        section_notes = {}
        
        # Normalmente las notas de sección están en la primera hoja o en una hoja específica
        # Vamos a buscar en todas las hojas
        for sheet_name, sheet_df in df.items():
            print(f"\nBuscando notas de sección en la hoja: {sheet_name}")
            
            # Convertir la hoja a una lista para facilitar la búsqueda
            sheet_data = sheet_df.values.tolist()
            
            # Buscar patrones como "Sección I", "SECCIÓN I", etc.
            section_pattern = re.compile(r'secci[oóòn]+\s+(I{1,3}|IV|VI{0,3}|I?X|XI{0,3})', re.IGNORECASE)
            
            # Variables para seguimiento
            current_section = None
            current_note = []
            
            for row_idx, row in enumerate(sheet_data):
                # Convertir todos los elementos de la fila a string
                row_text = " ".join([str(x) for x in row if x is not None and str(x).strip() != ''])
                
                # Buscar encabezado de sección
                match = section_pattern.search(row_text)
                if match:
                    # Si ya estábamos recolectando una nota, guardarla
                    if current_section and current_note:
                        section_notes[current_section] = "\n".join(current_note)
                        current_note = []
                    
                    # Extraer el número romano
                    roman_numeral = match.group(1).upper()
                    
                    # Mapear números romanos a decimales (formato 01, 02, etc.)
                    roman_to_decimal = {
                        'I': '01', 'II': '02', 'III': '03', 'IV': '04', 'V': '05',
                        'VI': '06', 'VII': '07', 'VIII': '08', 'IX': '09', 'X': '10',
                        'XI': '11', 'XII': '12', 'XIII': '13', 'XIV': '14', 'XV': '15',
                        'XVI': '16', 'XVII': '17', 'XVIII': '18', 'XIX': '19', 'XX': '20',
                        'XXI': '21'
                    }
                    
                    if roman_numeral in roman_to_decimal:
                        current_section = roman_to_decimal[roman_numeral]
                        print(f"  Encontrada sección {roman_numeral} (número {current_section})")
                        
                        # Guardar el encabezado como primera línea de la nota
                        current_note.append(row_text)
                else:
                    # Si estamos en una sección, recolectar el texto
                    if current_section and row_text.strip():
                        current_note.append(row_text)
            
            # Guardar la última nota si existe
            if current_section and current_note:
                section_notes[current_section] = "\n".join(current_note)
        
        return section_notes
    
    except Exception as e:
        print(f"Error al procesar el archivo Excel: {e}")
        return {}

def compare_section_notes(db_notes, excel_notes):
    """Compara las notas de sección de la base de datos con las del Excel."""
    print("\n" + "=" * 80)
    print("COMPARACIÓN DE NOTAS DE SECCIÓN")
    print("=" * 80)
    
    # Verificar secciones existentes en ambos
    all_sections = sorted(set(list(db_notes.keys()) + list(excel_notes.keys())))
    
    for section in all_sections:
        in_db = section in db_notes
        in_excel = section in excel_notes
        
        print(f"\nSección {section}:")
        print(f"  - ¿Existe en BD?: {'SÍ' if in_db else 'NO'}")
        print(f"  - ¿Existe en Excel?: {'SÍ' if in_excel else 'NO'}")
        
        if in_db and in_excel:
            # Comparar contenido (primeros 100 caracteres)
            db_content = db_notes[section][:100].replace('\n', ' ')
            excel_content = excel_notes[section][:100].replace('\n', ' ')
            
            match = "SÍ" if db_content == excel_content else "NO"
            print(f"  - ¿Coinciden los primeros 100 caracteres?: {match}")
            
            if match == "NO":
                print(f"  - BD: {db_content}...")
                print(f"  - Excel: {excel_content}...")

def check_ncm_in_excel():
    """Verifica los códigos NCM que comienzan con 2004 en el archivo Excel."""
    # Ruta al archivo Excel
    excel_file = os.path.join('data', 'Arancel Nacional_Abril 2024.xlsx')
    
    print(f"Verificando archivo Excel: {excel_file}")
    
    # Obtener notas de sección de la base de datos
    db_notes = get_section_notes_from_db()
    print(f"Notas de sección en base de datos: {len(db_notes)}")
    
    # Extraer notas de sección del Excel
    excel_notes = extract_section_notes_from_excel(excel_file)
    print(f"Notas de sección extraídas del Excel: {len(excel_notes)}")
    
    # Comparar notas
    compare_section_notes(db_notes, excel_notes)

if __name__ == "__main__":
    check_ncm_in_excel()
