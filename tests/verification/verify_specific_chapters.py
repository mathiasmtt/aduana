#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar específicamente las notas de los capítulos que anteriormente
presentaban problemas (capítulos 39, 64, 90 y 95), comparando sus notas en la base 
de datos con las del archivo Excel.
"""

import os
import pandas as pd
import re
from difflib import SequenceMatcher
from app import create_app
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
    Encuentra la posición de un capítulo en el archivo Excel.
    """
    chapter_int = int(chapter_number)
    exact_pattern = f"Capítulo {chapter_int}"
    
    for i in range(len(df)):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if exact_pattern in cell_value and (
            cell_value.strip() == exact_pattern or
            cell_value.strip().startswith(exact_pattern + "\n") or
            re.match(rf'^{exact_pattern}\s', cell_value)
        ):
            return i
    
    for i in range(len(df)):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if exact_pattern in cell_value:
            return i
    
    return -1

def extract_chapter_content(df, start_row):
    """
    Extrae el contenido completo de un capítulo.
    """
    content_lines = []
    
    header = str(df.iloc[start_row, 0]) if pd.notna(df.iloc[start_row, 0]) else ""
    content_lines.append(header)
    
    for i in range(start_row + 1, min(start_row + 500, len(df))):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        
        if (re.match(r'^Capítulo\s+\d+', cell_value) and i > start_row + 2) or \
           re.match(r'^\d{2}\.\d{2}', cell_value) or \
           cell_value.strip() == "NCM":
            break
        
        if cell_value.strip():
            content_lines.append(cell_value)
    
    return '\n'.join(content_lines)

def verify_specific_chapters():
    """
    Verifica específicamente las notas de los capítulos 39, 64, 90 y 95.
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    print(f"Leyendo archivo Excel: {file_path}")
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Crear la aplicación y contexto
    app = create_app()
    
    # Capítulos a verificar
    chapters_to_verify = ["39", "64", "90", "95"]
    
    with app.app_context():
        for chapter in chapters_to_verify:
            print(f"\n{'=' * 80}")
            print(f"Verificando capítulo {chapter}...")
            
            # Obtener la nota de la base de datos
            db_note = ChapterNote.get_note_by_chapter(chapter)
            if not db_note:
                print(f"⚠️ No se encontró nota en la base de datos para el capítulo {chapter}")
                continue
            
            # Buscar el capítulo en el Excel
            chapter_row = find_chapter_in_excel(df, int(chapter))
            if chapter_row == -1:
                print(f"⚠️ No se encontró el capítulo {chapter} en el Excel")
                continue
            
            # Extraer el contenido del capítulo
            excel_note = extract_chapter_content(df, chapter_row)
            if not excel_note:
                print(f"⚠️ No se pudo extraer contenido para el capítulo {chapter}")
                continue
            
            # Calcular similitud completa y de las primeras 100 caracteres
            full_sim = similarity(clean_text(db_note), clean_text(excel_note))
            start_sim = similarity(clean_text(db_note[:100]), clean_text(excel_note[:100]))
            
            print(f"Similitud de los primeros 100 caracteres: {start_sim:.2f}%")
            print(f"Similitud completa: {full_sim:.2f}%")
            
            if start_sim >= 85:
                print(f"✅ Los primeros 100 caracteres coinciden")
            else:
                print(f"❌ Los primeros 100 caracteres NO coinciden")
                print(f"DB (primeros 100): {db_note[:100]}")
                print(f"Excel (primeros 100): {excel_note[:100]}")
            
            if full_sim >= 75:
                print(f"✅ Las notas completas tienen buena similitud")
            else:
                print(f"⚠️ Las notas completas tienen baja similitud ({full_sim:.2f}%)")
                print("Esto puede deberse a diferencias en formato o espacios.")
            
            # Mostrar las longitudes de las notas
            print(f"Longitud de la nota en BD: {len(db_note)} caracteres")
            print(f"Longitud de la nota en Excel: {len(excel_note)} caracteres")

if __name__ == "__main__":
    verify_specific_chapters()
