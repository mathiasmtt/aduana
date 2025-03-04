#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script mejorado para corregir el contenido del capítulo 77, con más detalles sobre
el contenido tanto en el Excel como en la base de datos.
"""

import os
import pandas as pd
import re
from app import db, create_app
from app.models.chapter_note import ChapterNote

def fix_chapter_77():
    """
    Corrige la nota del capítulo 77 con un enfoque más detallado.
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    print(f"Leyendo archivo Excel: {file_path}")
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Crear la aplicación y contexto
    app = create_app()
    
    with app.app_context():
        # Buscar manualmente el capítulo 77 en el Excel
        print("Buscando 'Capítulo 77' en el Excel...")
        for i in range(len(df)):
            cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
            if "Capítulo 77" in cell_value:
                print(f"Encontrado en la fila {i}: '{cell_value}'")
                
                # Extraer el texto completo del Excel para el capítulo 77
                excel_content = cell_value.strip()
                print(f"Contenido completo del Excel: '{excel_content}'")
                
                # Verificar las filas siguientes por si hay más contenido
                next_row = i + 1
                if next_row < len(df):
                    next_cell = str(df.iloc[next_row, 0]) if pd.notna(df.iloc[next_row, 0]) else ""
                    print(f"Siguiente fila ({next_row}): '{next_cell}'")
                    
                    # Si la siguiente fila contiene texto relacionado con el capítulo 77
                    if "Reservado" in next_cell:
                        excel_content += "\n" + next_cell.strip()
                        print(f"Contenido actualizado con fila siguiente: '{excel_content}'")
                
                # Buscar el registro en la base de datos
                chapter_note = ChapterNote.query.filter_by(chapter_number="77").first()
                
                if not chapter_note:
                    print("No se encontró la nota del capítulo 77 en la base de datos. Creando nuevo registro...")
                    chapter_note = ChapterNote(chapter_number="77", note_text=excel_content)
                    db.session.add(chapter_note)
                else:
                    print(f"Nota actual en BD: '{chapter_note.note_text}'")
                    print(f"Actualizando a: '{excel_content}'")
                    chapter_note.note_text = excel_content
                
                db.session.commit()
                print("✅ Nota del capítulo 77 actualizada correctamente")
                return
        
        print("⚠️ No se encontró 'Capítulo 77' en el Excel")

if __name__ == "__main__":
    fix_chapter_77()
