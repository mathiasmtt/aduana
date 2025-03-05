#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar la correcta configuración y funcionamiento de las notas de sección.
Verifica que todas las secciones (01-21) existen y pueden ser accedidas en diferentes formatos.
"""

import sys
import os
import sqlite3

# Importar el diccionario de mapeo de números romanos
from roman_mapping import ROMAN_MAPPING

# Conectarse a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'database.sqlite3')
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def print_header(title):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def get_note_by_section(section_number):
    """
    Obtiene la nota de una sección por su número.
    
    Args:
        section_number: Número de sección (puede ser '01', '7', 'VII', etc.)
    
    Returns:
        str: Texto de la nota o None si no existe
    """
    # Normalizar el número de sección
    section = section_number.strip().upper()
    decimal_section = None
    
    # Si es número romano, convertir a decimal
    if section in ROMAN_MAPPING:
        decimal_section = f"{ROMAN_MAPPING[section]:02d}"
    # Si es número decimal, asegurar formato de 2 dígitos
    elif section.isdigit():
        decimal_section = section.zfill(2)
    # Si tiene formato "XXI - Descripción", extraer la parte romana
    elif " - " in section:
        roman_part = section.split(" - ")[0].strip()
        if roman_part in ROMAN_MAPPING:
            decimal_section = f"{ROMAN_MAPPING[roman_part]:02d}"
    
    # Si no pudimos determinar el número decimal, retornar None
    if not decimal_section:
        return None
    
    # Buscar en la base de datos
    cursor.execute("SELECT note_text FROM section_notes WHERE section_number = ?", (decimal_section,))
    result = cursor.fetchone()
    
    return result['note_text'] if result else None

def test_all_section_notes():
    """Verifica que todas las secciones existen y pueden ser accedidas."""
    print_header("VERIFICACIÓN DE TODAS LAS NOTAS DE SECCIÓN")
    
    # Obtener todas las notas de sección de la base de datos
    cursor.execute("SELECT section_number, note_text FROM section_notes ORDER BY section_number")
    all_notes = {row['section_number']: row['note_text'] for row in cursor.fetchall()}
    
    print(f"Total de notas de sección en base de datos: {len(all_notes)}")
    
    # Verificar cada sección del 1 al 21
    for i in range(1, 22):
        section_number = f"{i:02d}"
        
        # Verificar si existe en la base de datos
        exists_in_db = section_number in all_notes
        
        # Buscar por número de sección
        note_by_section = get_note_by_section(section_number)
        
        # Buscar por número romano
        roman_number = [k for k, v in ROMAN_MAPPING.items() if v == i][0]
        note_by_roman = get_note_by_section(roman_number)
        
        # Buscar por formato "XXI - Descripción"
        # Primero necesitamos obtener la descripción de la sección
        cursor.execute("""
            SELECT DISTINCT SECTION FROM arancel_nacional 
            WHERE SECTION LIKE ? OR SECTION LIKE ?
            LIMIT 1
        """, (f"{i}%", f"{i:02d}%"))
        section_row = cursor.fetchone()
        section_with_desc = section_row['SECTION'] if section_row else f"{roman_number} - Sección {i}"
        
        note_by_section_desc = get_note_by_section(section_with_desc)
        
        # Verificar coincidencias
        formats_match = (note_by_section == note_by_roman == note_by_section_desc)
        
        print(f"Sección {section_number} (Romano: {roman_number}, Formato completo: {section_with_desc}):")
        print(f"  - ¿Existe en la base de datos?: {'SÍ' if exists_in_db else 'NO'}")
        print(f"  - ¿Se puede recuperar por número?: {'SÍ' if note_by_section else 'NO'}")
        print(f"  - ¿Se puede recuperar por número romano?: {'SÍ' if note_by_roman else 'NO'}")
        print(f"  - ¿Se puede recuperar por formato completo?: {'SÍ' if note_by_section_desc else 'NO'}")
        print(f"  - ¿Coinciden todos los formatos?: {'SÍ' if formats_match else 'NO'}")
        
        # Mostrar inicio de la nota si existe
        if note_by_section:
            print(f"  - Inicio de la nota: {note_by_section[:50]}...")
        
        print("")

if __name__ == "__main__":
    test_all_section_notes()
    conn.close()
