#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar el formato de las secciones en la base de datos.
"""

import sys
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app
from app.models import SectionNote, Arancel

def check_sections_format():
    """
    Verifica el formato de las secciones en la base de datos.
    """
    app = create_app()
    
    with app.app_context():
        print("Secciones en la tabla section_notes:")
        for note in SectionNote.query.all():
            print(f"- {note.section_number}")
        
        print("\nFormato de SECTION en la tabla arancel:")
        sections = Arancel.query.with_entities(Arancel.SECTION).distinct().all()
        for section in sections:
            if section[0]:  # Evitar None
                print(f"- '{section[0]}'")
        
        print("\nPrimeros 5 registros del Arancel:")
        for a in Arancel.query.limit(5).all():
            print(f"NCM: {a.NCM}, Sección: '{a.SECTION}'")
        
        # Realizar una prueba: buscar un NCM y verificar su sección
        print("\nPrueba con un NCM específico:")
        test_ncm = "3901.90.90.00"
        arancel = Arancel.query.filter_by(NCM=test_ncm).first()
        if arancel:
            print(f"NCM: {arancel.NCM}, Sección (sin formato): '{arancel.SECTION}'")
            print(f"Sección (con formato): '{arancel.SECTION.zfill(2)}' si es numérico")
            
            # Verificar si existe la nota para esta sección
            section_number = arancel.SECTION.zfill(2) if arancel.SECTION.isdigit() else arancel.SECTION
            note = SectionNote.query.filter_by(section_number=section_number).first()
            if note:
                print(f"✅ Nota encontrada para sección {section_number}")
            else:
                print(f"❌ No se encontró nota para sección {section_number}")

if __name__ == "__main__":
    check_sections_format()
