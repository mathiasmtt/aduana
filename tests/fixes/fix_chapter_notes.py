#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corregir las notas de capítulo en la base de datos.
Este script específicamente busca y corrige las notas de capítulos con problemas,
principalmente del capítulo 95 (que actualmente tiene contenido del capítulo 39) y
el capítulo 39 (que actualmente tiene contenido del capítulo 27).
"""

import os
import re
import pandas as pd
from app import db, create_app
from app.models.chapter_note import ChapterNote

def extract_chapter_note(file_path, chapter_number):
    """
    Extrae la nota para un capítulo específico del archivo Excel.
    
    Args:
        file_path (str): Ruta al archivo Excel.
        chapter_number (str): Número de capítulo en formato '01', '02', etc.
        
    Returns:
        str: Contenido del capítulo, o None si no se encuentra.
    """
    print(f"Extrayendo nota para capítulo {chapter_number} desde {file_path}...")
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Primero buscar el encabezado del capítulo
    found_row = -1
    chapter_pattern = f"Capítulo {int(chapter_number)}"  # Buscar sin cero a la izquierda
    
    # Manejar capítulos específicos con posiciones conocidas
    if chapter_number == "95":
        # Capítulo 95 está alrededor de la fila 20100
        search_range = range(20090, 20110)
    elif chapter_number == "39":
        # Capítulo 39 está alrededor de la fila 8306
        search_range = range(8300, 8315)
        # Buscar exactamente "Capítulo 39" para evitar coincidencias parciales
        chapter_pattern = "Capítulo 39"
    else:
        # Para otros capítulos, buscar en todo el archivo
        search_range = range(len(df))
    
    # Buscar el inicio del capítulo
    for i in search_range:
        if i >= len(df):
            break
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        # Para el capítulo 39, verificar que sea exactamente "Capítulo 39"
        if chapter_number == "39" and cell_value.strip() == chapter_pattern:
            found_row = i
            print(f"Encontrado capítulo {chapter_number} en fila {i}: {cell_value}")
            break
        # Para otros capítulos
        elif chapter_number != "39" and chapter_pattern in cell_value:
            found_row = i
            print(f"Encontrado capítulo {chapter_number} en fila {i}: {cell_value}")
            break
    
    if found_row == -1:
        print(f"No se encontró el capítulo {chapter_number}")
        return None
    
    # Extraer la nota del capítulo
    # El encabezado debe empezar con "Capítulo" y no ser una referencia a otro capítulo
    chapter_header = None
    chapter_title = None
    notes_content = []
    
    # Buscar nuevamente para obtener el encabezado completo y el título
    for i in range(found_row, min(found_row + 3, len(df))):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if i == found_row:
            chapter_header = cell_value
        elif chapter_title is None and cell_value.strip():
            chapter_title = cell_value
            break
    
    # Agregar el encabezado y título a las notas
    notes_content.append(chapter_header)
    if chapter_title:
        notes_content.append(chapter_title)
    
    # Buscar la sección de notas
    notes_started = False
    in_notes_section = False
    
    # El número máximo de filas a buscar después del inicio del capítulo
    max_rows = 200
    
    for i in range(found_row + 2, min(found_row + max_rows, len(df))):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        
        # Detectar inicio de notas
        if not notes_started and ("Nota" in cell_value or "NOTA" in cell_value):
            notes_started = True
            in_notes_section = True
            notes_content.append(cell_value)
            continue
        
        # Capturar contenido de notas
        if in_notes_section:
            # Terminar si encontramos códigos NCM o siguiente capítulo
            if (re.match(r'^\d{2}\.\d{2}', cell_value) or 
                re.match(r'^Capítulo\s+\d+', cell_value) or 
                cell_value.strip() == "NCM"):
                in_notes_section = False
                break
            
            if cell_value.strip():
                notes_content.append(cell_value)
    
    # Unir todo el contenido
    if notes_content:
        return "\n".join(notes_content)
    else:
        print(f"No se encontraron notas para el capítulo {chapter_number}")
        return None

def fix_chapter_note(chapter_number, auto_update=False):
    """
    Corrige la nota para un capítulo específico en la base de datos.
    
    Args:
        chapter_number (str): Número de capítulo a corregir.
        auto_update (bool): Si es True, actualiza automáticamente sin preguntar.
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    
    # Extraer la nota correcta del capítulo
    correct_note = extract_chapter_note(file_path, chapter_number)
    
    if not correct_note:
        print(f"No se pudo extraer nota correcta para el capítulo {chapter_number}")
        return
    
    # Verificar si la nota extraída contiene el texto correcto para el capítulo 39
    if chapter_number == "39" and "plástico" not in correct_note.lower():
        print(" La nota extraída para el capítulo 39 no contiene la palabra 'plástico'")
        print(" Esto indica que probablemente se extrajo una nota incorrecta")
        return
    
    # Actualizar la nota en la base de datos
    app = create_app()
    with app.app_context():
        # Buscar la nota en la base de datos
        chapter_note = ChapterNote.query.filter_by(chapter_number=chapter_number).first()
        
        if chapter_note:
            # Mostrar la nota actual
            print(f"\nNota actual del capítulo {chapter_number}:")
            print("-" * 40)
            print(chapter_note.note_text[:500] + "..." if len(chapter_note.note_text) > 500 else chapter_note.note_text)
            print("-" * 40)
            
            # Mostrar la nota corregida
            print(f"\nNota corregida del capítulo {chapter_number}:")
            print("-" * 40)
            print(correct_note[:500] + "..." if len(correct_note) > 500 else correct_note)
            print("-" * 40)
            
            # Verificar si actualizar
            if auto_update:
                update = 's'
            else:
                update = input(f"¿Actualizar la nota del capítulo {chapter_number}? (s/n): ")
            
            if update.lower() == 's':
                # Actualizar la nota
                chapter_note.note_text = correct_note
                db.session.commit()
                print(f"Nota del capítulo {chapter_number} actualizada correctamente")
            else:
                print("Operación cancelada")
        else:
            print(f"No se encontró nota para el capítulo {chapter_number} en la base de datos")
            
            # Verificar si crear
            if auto_update:
                create = 's'
            else:
                create = input(f"¿Crear nueva nota para el capítulo {chapter_number}? (s/n): ")
            
            if create.lower() == 's':
                # Crear nueva nota
                new_note = ChapterNote(chapter_number=chapter_number, note_text=correct_note)
                db.session.add(new_note)
                db.session.commit()
                print(f"Nota del capítulo {chapter_number} creada correctamente")
            else:
                print("Operación cancelada")

def view_chapter_rows(chapter_number, start_row=0, num_rows=20):
    """
    Muestra filas específicas del archivo Excel para ayudar a encontrar el contenido correcto.
    
    Args:
        chapter_number (str): Número de capítulo a buscar.
        start_row (int): Fila desde donde empezar la búsqueda.
        num_rows (int): Número de filas a mostrar.
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    print(f"Mostrando filas {start_row} a {start_row + num_rows - 1} del archivo Excel:")
    print("-" * 80)
    
    for i in range(start_row, min(start_row + num_rows, len(df))):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        print(f"Fila {i}: {cell_value}")
    
    print("-" * 80)

def main():
    """Función principal."""
    # Verificar filas específicas del archivo para el capítulo 39
    view_chapter_rows(8300, 8300, 20)
    
    # Corregir la nota del capítulo 95
    fix_chapter_note("95", auto_update=True)
    
    # Corregir la nota del capítulo 39
    fix_chapter_note("39", auto_update=True)

if __name__ == "__main__":
    main()
