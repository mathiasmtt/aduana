#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para comparar todas las notas de capítulo almacenadas en la base de datos
con las notas extraídas directamente del archivo Excel original.
"""

import os
import re
import pandas as pd
from difflib import SequenceMatcher
from app import create_app
from app.models.chapter_note import ChapterNote
from sqlalchemy import text

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

def get_all_chapter_numbers_from_db():
    """
    Obtiene todos los números de capítulo almacenados en la base de datos.
    
    Returns:
        list: Lista de números de capítulo en formato string (01, 02, etc.)
    """
    app = create_app()
    with app.app_context():
        # Obtener todos los capítulos de la base de datos
        chapters = ChapterNote.query.all()
        return [chapter.chapter_number for chapter in chapters]

def check_all_chapters():
    """
    Compara todas las notas de capítulo en la base de datos con las del Excel.
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    
    # Obtener todos los números de capítulo
    chapter_numbers = get_all_chapter_numbers_from_db()
    
    if not chapter_numbers:
        print("No se encontraron capítulos en la base de datos.")
        return
    
    # Ordenar capítulos numéricamente
    chapter_numbers.sort(key=lambda x: int(x))
    
    print(f"Comparando {len(chapter_numbers)} capítulos entre la base de datos y el Excel...")
    print(f"{'=' * 80}")
    
    # Resultados de la comparación
    matches = []
    mismatches = []
    errors = []
    
    app = create_app()
    with app.app_context():
        for chapter_number in chapter_numbers:
            print(f"\nVerificando Capítulo {chapter_number}...")
            
            # Obtener nota de la base de datos
            chapter_note = ChapterNote.query.filter_by(chapter_number=chapter_number).first()
            if not chapter_note:
                print(f"❌ ERROR: Capítulo {chapter_number} no encontrado en la base de datos")
                errors.append(chapter_number)
                continue
            
            db_note_text = chapter_note.note_text
            
            # Obtener nota del Excel
            excel_note_text = extract_chapter_note_from_excel(file_path, chapter_number)
            
            if not excel_note_text:
                print(f"⚠️ ADVERTENCIA: No se pudo extraer nota para capítulo {chapter_number} del Excel")
                mismatches.append((chapter_number, 0))
                continue
            
            # Calcular similitud
            sim_percentage = similarity(db_note_text, excel_note_text)
            print(f"Similitud: {sim_percentage:.2f}%")
            
            # Determinar si coinciden
            if sim_percentage > 90:
                matches.append(chapter_number)
                print(f"✅ COINCIDE: Las notas del capítulo {chapter_number} son similares (> 90%)")
            else:
                mismatches.append((chapter_number, sim_percentage))
                print(f"❌ NO COINCIDE: Las notas del capítulo {chapter_number} tienen una similitud de {sim_percentage:.2f}%")
                
                # Mostrar inicio de ambas notas para comparación manual
                print("\nPrimeros 200 caracteres en BD:")
                print(f"  {db_note_text[:200]}...")
                print("\nPrimeros 200 caracteres en Excel:")
                print(f"  {excel_note_text[:200]}...")
    
    # Mostrar resumen
    print(f"\n{'=' * 80}")
    print("RESUMEN DE LA COMPARACIÓN:")
    print(f"✅ Capítulos con notas coincidentes: {len(matches)} de {len(chapter_numbers)}")
    if matches:
        print(f"   {', '.join(matches)}")
    
    print(f"\n❌ Capítulos con notas diferentes: {len(mismatches)}")
    if mismatches:
        for chapter, sim in sorted(mismatches, key=lambda x: x[1]):
            print(f"   Capítulo {chapter}: Similitud {sim:.2f}%")
    
    print(f"\n⚠️ Capítulos con errores: {len(errors)}")
    if errors:
        print(f"   {', '.join(errors)}")
    
    # Sugerencias
    if mismatches:
        print(f"\n{'=' * 80}")
        print("SUGERENCIAS:")
        print("Para corregir las notas de capítulos con baja similitud, ejecuta:")
        print("python src/fix_chapter_notes.py <número_capítulo>")

if __name__ == "__main__":
    check_all_chapters()
