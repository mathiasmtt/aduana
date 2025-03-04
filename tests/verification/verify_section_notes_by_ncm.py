#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar las notas de sección mostradas para un NCM específico.
"""

import os
import sqlite3
import sys

def get_ncm_details(ncm_code):
    """Obtiene los detalles del NCM incluyendo sección y capítulo."""
    db_path = os.path.join('data', 'database.sqlite3')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM arancel_nacional WHERE NCM LIKE ?",
        (ncm_code + '%',)
    )
    
    results = cursor.fetchall()
    
    if not results:
        print(f"No se encontraron resultados para el NCM {ncm_code}")
        conn.close()
        return None
    
    for row in results:
        print(f"NCM: {row['NCM']}")
        print(f"DESCRIPCION: {row['DESCRIPCION']}")
        print(f"SECTION: {row['SECTION']}")
        print(f"CHAPTER: {row['CHAPTER']}")
        print("")
    
    # Obtener el primer resultado para verificar las notas
    first_result = results[0]
    section = first_result['SECTION'].split(' - ')[0] if ' - ' in first_result['SECTION'] else first_result['SECTION']
    
    # Convertir sección a formato numérico (01, 02, etc.)
    if section.isdigit():
        section_number = f"{int(section):02d}"
    else:
        # Intentar extraer número romano
        import re
        roman_match = re.search(r'(I{1,3}|IV|VI{0,3}|I?X|XI{1,3}|XI?V|XVI{1,3}|XI?X|XXI?)', section)
        
        # Mapear números romanos a decimales
        roman_to_decimal = {
            'I': '01', 'II': '02', 'III': '03', 'IV': '04', 'V': '05',
            'VI': '06', 'VII': '07', 'VIII': '08', 'IX': '09', 'X': '10',
            'XI': '11', 'XII': '12', 'XIII': '13', 'XIV': '14', 'XV': '15',
            'XVI': '16', 'XVII': '17', 'XVIII': '18', 'XIX': '19', 'XX': '20',
            'XXI': '21'
        }
        
        if roman_match and roman_match.group(1) in roman_to_decimal:
            section_number = roman_to_decimal[roman_match.group(1)]
        else:
            print(f"No se pudo determinar el número de sección para: {section}")
            conn.close()
            return None
    
    # Verificar la nota de sección
    print(f"\nVerificando nota de sección para sección {section_number}...")
    
    cursor.execute(
        "SELECT * FROM section_notes WHERE section_number = ?",
        (section_number,)
    )
    
    section_note = cursor.fetchone()
    
    if section_note:
        print(f"La sección {section_number} tiene una nota con {len(section_note['note_text'])} caracteres")
        print("\nPrimeras 200 caracteres de la nota:")
        print(section_note['note_text'][:200])
    else:
        print(f"No se encontró nota para la sección {section_number}")
    
    conn.close()
    return first_result

def verify_section_notes_by_ncm(ncm_code):
    """Verifica las notas de sección para un NCM específico."""
    print(f"Verificando notas de sección para el NCM {ncm_code}...\n")
    
    # Obtener detalles del NCM
    ncm_details = get_ncm_details(ncm_code)
    
    if not ncm_details:
        return
    
    # Simular el proceso de recuperación de notas
    print("\nSimulando la recuperación de notas en la aplicación...")
    
    # Obtener la sección desde el valor de SECTION
    section = ncm_details['SECTION'].split(' - ')[0] if ' - ' in ncm_details['SECTION'] else ncm_details['SECTION']
    
    print(f"La aplicación buscaría las notas de sección para: {section}")
    
    # Verificar si la API de notas de sección funcionaría correctamente
    print("\nSugerencias de mejora:")
    
    if section.isdigit():
        print("✅ La sección está en formato numérico, asegúrese de convertirla a formato con ceros a la izquierda (01, 02, etc.).")
    elif any(c.isalpha() for c in section):
        print("⚠️ La sección contiene caracteres alfabéticos (números romanos). Debe ser convertida a formato numérico con ceros a la izquierda.")
        print("   Ejemplo: Si SECTION='IV - Productos alimenticios', se debe extraer 'IV' y convertirlo a '04'.")

if __name__ == "__main__":
    # Usar el NCM proporcionado como argumento o el valor predeterminado '2004'
    ncm_code = sys.argv[1] if len(sys.argv) > 1 else '2004'
    verify_section_notes_by_ncm(ncm_code)
