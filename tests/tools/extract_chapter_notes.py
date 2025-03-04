#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extrae las notas de capítulo del archivo Excel del Arancel Nacional
y las guarda en la base de datos.
"""

import os
import re
import pandas as pd
from app import db, create_app
from app.models.chapter_note import ChapterNote

def extract_chapter_notes(file_path):
    """
    Extrae las notas de capítulo del archivo Excel del Arancel Nacional.
    
    Args:
        file_path (str): Ruta al archivo Excel.
        
    Returns:
        dict: Diccionario con las notas de capítulo.
    """
    print(f"Extrayendo notas de capítulo de {file_path}...")
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Diccionario para almacenar las notas por capítulo
    chapter_notes = {}
    
    # Función auxiliar para buscar el capítulo específico y extraer su contenido completo
    def extract_chapter_content(chapter_num):
        """Extrae el contenido completo de un capítulo específico."""
        pattern = f"Capítulo {int(chapter_num)}"
        start_row = -1
        
        # Buscar el inicio del capítulo
        for i, row in df.iterrows():
            cell_value = str(row[0]) if pd.notna(row[0]) else ""
            if pattern in cell_value:
                start_row = i
                break
        
        if start_row == -1:
            return None
        
        # Buscar el final del capítulo (inicio del próximo capítulo o fin del archivo)
        end_row = len(df)
        for i in range(start_row + 1, len(df)):
            cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
            if re.match(r'^Capítulo\s+\d+', cell_value) and not pattern in cell_value:
                end_row = i
                break
        
        # Extraer todo el contenido entre el inicio y el final del capítulo
        content = []
        capturing_notes = False
        reached_ncm_codes = False
        
        for i in range(start_row, end_row):
            cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
            
            # Si llegamos a los códigos NCM, detenemos la captura (fin de las notas)
            if re.match(r'^\d{2}\.\d{2}', cell_value):
                reached_ncm_codes = True
            
            # Si aún no llegamos a los códigos NCM, seguimos capturando
            if not reached_ncm_codes:
                # Si es una línea no vacía, la capturamos
                if cell_value.strip():
                    content.append(cell_value)
                # Si encontramos "Notas" o "Nota", marcamos que estamos capturando notas
                if "Nota" in cell_value:
                    capturing_notes = True
        
        return "\n".join(content) if content else None
    
    # Extraer notas para cada capítulo del 1 al 97
    for chapter in range(1, 98):
        chapter_num = f"{chapter:02d}"
        content = extract_chapter_content(chapter_num)
        if content:
            chapter_notes[chapter_num] = content
            print(f"Procesado capítulo {chapter_num}: {len(content.split('\n'))} líneas")
    
    # Mostrar estadísticas
    print(f"Se encontraron notas para {len(chapter_notes)} capítulos")
    for chapter_num, note_text in sorted(chapter_notes.items()):
        print(f"Capítulo {chapter_num}: {len(note_text.split('\n'))} líneas de contenido")
    
    return chapter_notes

def save_notes_to_db(chapter_notes):
    """
    Guarda las notas de capítulo en la base de datos.
    
    Args:
        chapter_notes (dict): Diccionario con las notas de capítulo.
    """
    try:
        created_count = 0
        updated_count = 0
        
        app = create_app()
        with app.app_context():
            # Crear tabla si no existe
            db.create_all()
            
            # Recorrer cada capítulo encontrado
            for chapter_num, note_content in chapter_notes.items():
                # Actualizar o crear la nota del capítulo
                chapter_note = ChapterNote.query.filter_by(chapter_number=chapter_num).first()
                
                if chapter_note:
                    chapter_note.note_text = note_content
                    updated_count += 1
                else:
                    new_note = ChapterNote(chapter_number=chapter_num, note_text=note_content)
                    db.session.add(new_note)
                    created_count += 1
            
            # Guardar cambios
            db.session.commit()
            print(f"Se crearon {created_count} nuevas notas y se actualizaron {updated_count} notas existentes.")
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar las notas: {e}")
        raise

def main():
    """Función principal."""
    # Ruta al archivo Excel
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    
    # Extraer notas de capítulo
    chapter_notes = extract_chapter_notes(file_path)
    
    # Guardar notas en la base de datos
    save_notes_to_db(chapter_notes)

if __name__ == "__main__":
    main()
