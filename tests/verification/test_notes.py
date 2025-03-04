#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar rápidamente si las notas de capítulo específicas
están disponibles en la base de datos.
"""

from app import create_app
from app.models.chapter_note import ChapterNote

def test_specific_chapters():
    """
    Verifica si las notas de capítulo específicas están disponibles.
    """
    app = create_app()
    
    with app.app_context():
        # Capítulos a verificar
        chapters = ['39', '64', '90', '95']
        
        for chapter in chapters:
            note = ChapterNote.get_note_by_chapter(chapter)
            if note:
                print(f"✅ Capítulo {chapter}: Nota disponible")
                print(f"Primeros 100 caracteres: {note[:100]}")
            else:
                print(f"❌ Capítulo {chapter}: Nota NO disponible")
        
        # Verificar capítulo 77 que fue un caso especial
        note_77 = ChapterNote.get_note_by_chapter('77')
        if note_77:
            print(f"\n✅ Capítulo 77: Nota disponible")
            print(f"Contenido completo: {note_77}")
        else:
            print(f"\n❌ Capítulo 77: Nota NO disponible")

if __name__ == "__main__":
    test_specific_chapters()
