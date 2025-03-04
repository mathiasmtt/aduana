#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corregir todos los capítulos restantes que muestran problemas en la 
verificación con verify_random_ncm_notes.py. Este script aplica una corrección 
más agresiva, asegurándose de que todos los capítulos tengan el texto correcto
extraído del archivo Excel.
"""

import os
import re
import pandas as pd
from difflib import SequenceMatcher
from app import db, create_app
from app.models.chapter_note import ChapterNote

def similarity(a, b):
    """
    Calcula la similitud entre dos cadenas de texto.
    """
    if not a or not b:
        return 0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

def clean_text(text):
    """
    Limpia el texto para una mejor comparación.
    """
    if not text:
        return ""
    # Reemplazar múltiples espacios, tabulaciones y saltos de línea por un solo espacio
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    return text.strip()

def find_chapter_in_excel(df, chapter_number):
    """
    Encuentra de forma exacta un capítulo en el Excel.
    
    Args:
        df (DataFrame): DataFrame del Excel
        chapter_number (str or int): Número de capítulo a buscar
        
    Returns:
        int: Índice donde comienza el capítulo, o -1 si no se encuentra
    """
    chapter_int = int(chapter_number)
    
    # Patrón para buscar el encabezado exacto del capítulo
    exact_pattern = f"Capítulo {chapter_int}"
    
    # Buscar el encabezado del capítulo
    for i in range(len(df)):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if exact_pattern in cell_value and (
            cell_value.strip() == exact_pattern or
            cell_value.strip().startswith(exact_pattern + "\n") or
            re.match(rf'^{exact_pattern}\s', cell_value)
        ):
            return i
    
    # Si no encontramos el encabezado exacto, buscar una aproximación
    for i in range(len(df)):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if exact_pattern in cell_value:
            return i
    
    return -1

def extract_chapter_content(df, start_row):
    """
    Extrae todo el contenido de un capítulo a partir de su fila inicial.
    
    Args:
        df (DataFrame): DataFrame del Excel
        start_row (int): Fila donde comienza el capítulo
        
    Returns:
        str: Contenido completo del capítulo
    """
    content_lines = []
    
    # Obtener el encabezado del capítulo
    header = str(df.iloc[start_row, 0]) if pd.notna(df.iloc[start_row, 0]) else ""
    content_lines.append(header)
    
    # Extraer todas las líneas hasta encontrar el siguiente capítulo o códigos NCM
    for i in range(start_row + 1, min(start_row + 500, len(df))):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        
        # Detener la extracción si encontramos el siguiente capítulo
        if (re.match(r'^Capítulo\s+\d+', cell_value) and i > start_row + 2) or \
           re.match(r'^\d{2}\.\d{2}', cell_value) or \
           cell_value.strip() == "NCM":
            break
        
        # Agregar la línea si tiene contenido
        if cell_value.strip():
            content_lines.append(cell_value)
    
    return '\n'.join(content_lines)

def fix_all_chapters():
    """
    Corrige todos los capítulos, actualizando sus notas con el contenido del Excel.
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    print(f"Leyendo archivo Excel: {file_path}")
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Crear la aplicación y contexto
    app = create_app()
    
    problematic_chapters = []
    corrected_chapters = []
    skipped_chapters = []
    
    with app.app_context():
        # Obtener todos los capítulos del 01 al 97
        for chapter_num in range(1, 98):
            chapter = f"{chapter_num:02d}"  # Formato con ceros a la izquierda
            
            print(f"\n{'=' * 80}")
            print(f"Procesando capítulo {chapter}...")
            
            # Buscar la posición del capítulo en el Excel
            chapter_row = find_chapter_in_excel(df, chapter_num)
            
            if chapter_row == -1:
                print(f"⚠️ No se pudo encontrar el capítulo {chapter} en el Excel")
                problematic_chapters.append(chapter)
                continue
            
            # Extraer el contenido del capítulo
            excel_content = extract_chapter_content(df, chapter_row)
            
            if not excel_content:
                print(f"⚠️ No se pudo extraer contenido para el capítulo {chapter}")
                problematic_chapters.append(chapter)
                continue
            
            # Obtener la nota actual de la base de datos
            chapter_note = ChapterNote.query.filter_by(chapter_number=chapter).first()
            
            if not chapter_note:
                print(f"  🆕 Creando nueva nota para el capítulo {chapter}")
                chapter_note = ChapterNote(chapter_number=chapter, note_text=excel_content)
                db.session.add(chapter_note)
                corrected_chapters.append(chapter)
            else:
                # Verificar si la nota actual es diferente
                db_excerpt = chapter_note.note_text[:100] if chapter_note.note_text else ""
                excel_excerpt = excel_content[:100] if excel_content else ""
                
                sim = similarity(clean_text(db_excerpt), clean_text(excel_excerpt))
                
                if sim < 85:  # Si la similitud es baja, actualizar
                    print(f"  🔄 Actualizando nota para el capítulo {chapter} (similitud: {sim:.2f}%)")
                    print(f"    DB: {db_excerpt}")
                    print(f"  Excel: {excel_excerpt}")
                    chapter_note.note_text = excel_content
                    corrected_chapters.append(chapter)
                else:
                    print(f"  ✅ La nota para el capítulo {chapter} está correcta (similitud: {sim:.2f}%)")
                    skipped_chapters.append(chapter)
            
            # Guardar los cambios en la base de datos
            db.session.commit()
    
    # Mostrar resumen
    print(f"\n{'=' * 80}")
    print("RESUMEN DE CORRECCIÓN:")
    print(f"  ✅ Capítulos corregidos ({len(corrected_chapters)}): {', '.join(corrected_chapters)}")
    print(f"  ⏩ Capítulos sin cambios ({len(skipped_chapters)}): {', '.join(skipped_chapters)}")
    print(f"  ❌ Capítulos problemáticos ({len(problematic_chapters)}): {', '.join(problematic_chapters)}")

if __name__ == "__main__":
    fix_all_chapters()
