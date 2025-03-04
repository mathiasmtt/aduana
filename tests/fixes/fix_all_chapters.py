#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corregir automáticamente todas las notas de capítulo con baja similitud
entre la base de datos y el archivo Excel original.
"""

import os
import sys
import time
import pandas as pd
import re
from difflib import SequenceMatcher
from app import create_app, db
from app.models.chapter_note import ChapterNote
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def similarity(a, b):
    """
    Calcula el porcentaje de similitud entre dos strings.
    
    Args:
        a (str): Primer string
        b (str): Segundo string
        
    Returns:
        float: Porcentaje de similitud (0-100)
    """
    if not a or not b:
        return 0
    
    # Normalizar textos para comparación (quitar espacios y convertir a minúsculas)
    a_norm = ' '.join(a.lower().split())
    b_norm = ' '.join(b.lower().split())
    
    # Calcular similitud
    matcher = SequenceMatcher(None, a_norm, b_norm)
    return matcher.ratio() * 100

def extract_chapter_note_from_excel(file_path, chapter_number):
    """
    Extrae la nota para un capítulo específico del archivo Excel.
    
    Args:
        file_path (str): Ruta al archivo Excel.
        chapter_number (str): Número de capítulo en formato '01', '02', etc.
        
    Returns:
        str: Contenido del capítulo, o None si no se encuentra.
    """
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Buscar el patrón de capítulo
    # Convertir a entero para quitar ceros a la izquierda al buscar
    chapter_int = int(chapter_number)
    chapter_pattern = f"Capítulo {chapter_int}"
    found_row = -1
    
    # Buscar el inicio del capítulo
    for i, row in df.iterrows():
        cell_value = str(row[0]) if pd.notna(row[0]) else ""
        if chapter_pattern in cell_value and not f"Capítulo {chapter_int + 1}" in cell_value:
            found_row = i
            break
    
    if found_row == -1:
        return None
    
    # Extraer la nota del capítulo
    chapter_header = None
    chapter_title = None
    notes_content = []
    
    # Obtener encabezado y título
    for i in range(found_row, min(found_row + 3, len(df))):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if i == found_row:
            chapter_header = cell_value
        elif chapter_title is None and cell_value.strip():
            chapter_title = cell_value
            break
    
    # Agregar encabezado y título
    if chapter_header:
        notes_content.append(chapter_header)
    if chapter_title:
        notes_content.append(chapter_title)
    
    # Buscar la sección de notas
    notes_started = False
    in_notes_section = False
    
    for i in range(found_row + 2, min(found_row + 300, len(df))):
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
                break
            
            if cell_value.strip():
                notes_content.append(cell_value)
    
    # Unir todo el contenido
    if notes_content:
        return "\n".join(notes_content)
    else:
        return None

def update_chapter_note(chapter_number, note_text):
    """
    Actualiza la nota de un capítulo en la base de datos.
    
    Args:
        chapter_number (str): Número de capítulo en formato '01', '02', etc.
        note_text (str): Nuevo texto de la nota.
        
    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario.
    """
    app = create_app()
    with app.app_context():
        try:
            # Buscar la nota existente
            chapter_note = ChapterNote.query.filter_by(chapter_number=chapter_number).first()
            
            if chapter_note:
                # Actualizar nota existente
                chapter_note.note_text = note_text
                db.session.commit()
                return True
            else:
                # Crear nueva nota
                new_note = ChapterNote(chapter_number=chapter_number, note_text=note_text)
                db.session.add(new_note)
                db.session.commit()
                return True
                
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error en la base de datos: {e}")
            return False

def fix_all_chapters(threshold=90):
    """
    Corrige todas las notas de capítulo con similitud por debajo del umbral.
    
    Args:
        threshold (int): Porcentaje de similitud por debajo del cual se corrige una nota.
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    
    app = create_app()
    with app.app_context():
        # Obtener todos los capítulos de la base de datos
        chapters = ChapterNote.query.all()
        chapter_numbers = [chapter.chapter_number for chapter in chapters]
        
        if not chapter_numbers:
            print("No se encontraron capítulos en la base de datos.")
            return
        
        # Ordenar capítulos numéricamente
        chapter_numbers.sort(key=lambda x: int(x))
        
        print(f"Analizando {len(chapter_numbers)} capítulos para posible corrección...")
        print(f"{'=' * 80}")
        
        # Contador de capítulos corregidos
        corrected_count = 0
        
        for chapter_number in chapter_numbers:
            # Obtener nota actual de la base de datos
            chapter_note = ChapterNote.query.filter_by(chapter_number=chapter_number).first()
            db_note_text = chapter_note.note_text if chapter_note else ""
            
            # Obtener nota del Excel
            excel_note_text = extract_chapter_note_from_excel(file_path, chapter_number)
            
            if not excel_note_text:
                print(f"⚠️ ADVERTENCIA: No se pudo extraer nota para capítulo {chapter_number} del Excel")
                continue
            
            # Calcular similitud
            sim_percentage = similarity(db_note_text, excel_note_text)
            
            # Determinar si se debe corregir
            if sim_percentage < threshold:
                print(f"Corrigiendo Capítulo {chapter_number} (similitud: {sim_percentage:.2f}%)...")
                
                if update_chapter_note(chapter_number, excel_note_text):
                    print(f"✅ CORREGIDO: Capítulo {chapter_number}")
                    corrected_count += 1
                else:
                    print(f"❌ ERROR: No se pudo actualizar el Capítulo {chapter_number}")
                
                # Pequeña pausa para evitar sobrecarga de la BD
                time.sleep(0.1)
            
        print(f"\n{'=' * 80}")
        print(f"RESUMEN DE CORRECCIONES:")
        print(f"✅ Capítulos corregidos: {corrected_count} de {len(chapter_numbers)}")
        print(f"⚠️ El umbral de similitud utilizado fue: {threshold}%")
        print(f"\nEjecuta 'python src/compare_db_excel_notes.py' para verificar los resultados.")

if __name__ == "__main__":
    # Si se proporciona un umbral como argumento, usarlo
    threshold = 90
    if len(sys.argv) > 1:
        try:
            threshold = float(sys.argv[1])
        except ValueError:
            print(f"Error: '{sys.argv[1]}' no es un número válido. Usando umbral predeterminado de 90%.")
    
    fix_all_chapters(threshold)
