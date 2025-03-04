#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar específicamente las notas de los capítulos 39 y 95
en diferentes códigos NCM y confirmar que están correctas.
"""

import os
import sys
from app import create_app
from app.models.chapter_note import ChapterNote

def verify_specific_chapters():
    """
    Verifica las notas de los capítulos 39 y 95 en diferentes códigos NCM.
    """
    # Lista de NCM a verificar para cada capítulo
    ncm_capitulo_39 = [
        "3901.10.10", "3904.10.00", "3907.20.31", 
        "3912.20.29", "3919.90.20", "3923.50.00"
    ]
    
    ncm_capitulo_95 = [
        "9503.00.10", "9504.50.00", "9506.91.00",
        "9508.10.00", "9505.10.00", "9507.30.00"
    ]
    
    app = create_app()
    with app.app_context():
        print("\n" + "=" * 80)
        print("VERIFICACIÓN DE NOTAS DE CAPÍTULO 39")
        print("=" * 80)
        
        for ncm in ncm_capitulo_39:
            note = ChapterNote.get_note_by_ncm(ncm.replace(".", ""))
            if note:
                print(f"\nNCM: {ncm}")
                print(f"Las primeras 100 caracteres de la nota:")
                print("-" * 50)
                print(note[:100] + "..." if len(note) > 100 else note)
                print("-" * 50)
                
                # Verificar que la nota es correcta
                if "plástico" in note.lower():
                    print("✅ CORRECTO: La nota contiene la palabra 'plástico'")
                else:
                    print("❌ ERROR: La nota NO contiene la palabra 'plástico'")
            else:
                print(f"\nNCM: {ncm}")
                print("❌ ERROR: No se encontró nota para este NCM")
        
        print("\n" + "=" * 80)
        print("VERIFICACIÓN DE NOTAS DE CAPÍTULO 95")
        print("=" * 80)
        
        for ncm in ncm_capitulo_95:
            note = ChapterNote.get_note_by_ncm(ncm.replace(".", ""))
            if note:
                print(f"\nNCM: {ncm}")
                print(f"Las primeras 100 caracteres de la nota:")
                print("-" * 50)
                print(note[:100] + "..." if len(note) > 100 else note)
                print("-" * 50)
                
                # Verificar que la nota es correcta
                if "juguetes" in note.lower():
                    print("✅ CORRECTO: La nota contiene la palabra 'juguetes'")
                else:
                    print("❌ ERROR: La nota NO contiene la palabra 'juguetes'")
            else:
                print(f"\nNCM: {ncm}")
                print("❌ ERROR: No se encontró nota para este NCM")

if __name__ == "__main__":
    verify_specific_chapters()
