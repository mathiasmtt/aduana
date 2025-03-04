#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar las notas de capítulo almacenadas en la base de datos.
"""

import sys
from app import create_app
from app.models.chapter_note import ChapterNote

def check_chapter_note_by_ncm(ncm_code):
    """
    Verifica la nota de capítulo para un código NCM específico.
    
    Args:
        ncm_code (str): Código NCM a verificar.
    """
    print(f"Verificando nota para NCM: {ncm_code}")
    
    app = create_app()
    with app.app_context():
        # Usar el método get_note_by_ncm
        note_text = ChapterNote.get_note_by_ncm(ncm_code)
        
        if note_text:
            chapter_number = ncm_code[:2]
            print(f"Nota para capítulo {chapter_number} (NCM {ncm_code}):")
            print("-" * 80)
            print(note_text[:500] + "..." if len(note_text) > 500 else note_text)
            print("-" * 80)
        else:
            print(f"No se encontró nota para NCM {ncm_code}")

def list_all_chapter_notes():
    """
    Lista todas las notas de capítulo disponibles en la base de datos.
    """
    print("Listando todas las notas de capítulo:")
    
    app = create_app()
    with app.app_context():
        notes = ChapterNote.query.order_by(ChapterNote.chapter_number).all()
        
        if notes:
            for note in notes:
                preview = note.note_text[:100] + "..." if len(note.note_text) > 100 else note.note_text
                print(f"Capítulo {note.chapter_number}: {preview}")
        else:
            print("No hay notas de capítulo en la base de datos")

def main():
    """Función principal."""
    if len(sys.argv) == 1:
        # Mostrar todas las notas
        list_all_chapter_notes()
    else:
        # Verificar nota por NCM
        ncm_code = sys.argv[1]
        check_chapter_note_by_ncm(ncm_code)

if __name__ == "__main__":
    main()
