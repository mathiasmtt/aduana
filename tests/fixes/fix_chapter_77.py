#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corregir específicamente la nota del capítulo 77, que muestra una diferencia
menor en la verificación.
"""

import os
import pandas as pd
import re
from app import db, create_app
from app.models.chapter_note import ChapterNote

def find_chapter_77_in_excel(df):
    """
    Encuentra la posición del capítulo 77 en el Excel.
    """
    exact_pattern = "Capítulo 77"
    
    for i in range(len(df)):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if exact_pattern in cell_value:
            return i
    
    return -1

def extract_chapter_77_content(df, start_row):
    """
    Extrae el contenido del capítulo 77 del Excel.
    """
    if start_row == -1:
        return None
    
    return str(df.iloc[start_row, 0]) if pd.notna(df.iloc[start_row, 0]) else ""

def fix_chapter_77():
    """
    Corrige la nota del capítulo 77.
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    print(f"Leyendo archivo Excel: {file_path}")
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Crear la aplicación y contexto
    app = create_app()
    
    with app.app_context():
        # Buscar el capítulo 77 en el Excel
        chapter_row = find_chapter_77_in_excel(df)
        
        if chapter_row == -1:
            print("❌ No se pudo encontrar el capítulo 77 en el Excel")
            return
        
        # Extraer el contenido del capítulo 77
        excel_content = extract_chapter_77_content(df, chapter_row)
        
        if not excel_content:
            print("❌ No se pudo extraer el contenido del capítulo 77")
            return
        
        print(f"Contenido del capítulo 77 en el Excel:\n{excel_content}")
        
        # Obtener la nota actual del capítulo 77
        chapter_note = ChapterNote.query.filter_by(chapter_number="77").first()
        
        if not chapter_note:
            print("❌ No se encontró la nota del capítulo 77 en la base de datos")
            return
        
        print(f"Nota actual del capítulo 77 en la base de datos:\n{chapter_note.note_text}")
        
        # Actualizar la nota del capítulo 77
        chapter_note.note_text = excel_content
        
        # Guardar los cambios
        db.session.commit()
        
        print(f"✅ Nota del capítulo 77 actualizada correctamente")

if __name__ == "__main__":
    fix_chapter_77()
