#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar rápidamente algunas notas de sección.
"""

import sys
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app
from app.models import SectionNote, Arancel

def test_section_notes():
    """
    Verifica el contenido de algunas notas de sección.
    """
    app = create_app()
    
    with app.app_context():
        # Obtener todas las secciones disponibles
        sections = [note.section_number for note in SectionNote.query.all()]
        sections.sort()
        
        print(f"Hay {len(sections)} secciones en la base de datos: {', '.join(sections)}\n")
        
        # Verificar algunas secciones específicas
        test_sections = ['02', '07', '15', '21']
        
        for section in test_sections:
            note = SectionNote.get_note_by_section(section)
            if note:
                print(f"=== Sección {section} ===")
                print(f"Primeros 200 caracteres:\n{note[:200]}...")
                print(f"Longitud total: {len(note)} caracteres\n")
            else:
                print(f"❌ No se encontró nota para la sección {section}\n")
        
        # Probar la obtención de notas por NCM
        test_ncms = ['3901.90.90.00', '8471.30.12.00', '6402.19.00.00', '9031.80.99.00']
        
        print("\nVerificando notas de sección por NCM:")
        for ncm in test_ncms:
            # Obtener el número de sección para este NCM
            arancel = Arancel.query.filter_by(NCM=ncm).first()
            if not arancel:
                print(f"❌ No se encontró el NCM {ncm} en la base de datos")
                continue
            
            section_number = arancel.SECTION
            if not section_number:
                print(f"❌ El NCM {ncm} no tiene asignada una sección")
                continue
            
            # Formatear el número de sección correctamente
            section_number = section_number.zfill(2)
            
            # Obtener la nota de sección
            note = SectionNote.get_note_by_ncm(ncm)
            
            print(f"NCM: {ncm} -> Sección: {section_number}")
            if note:
                print(f"✅ Nota disponible (primeros 100 caracteres):\n{note[:100]}...")
            else:
                print(f"❌ Nota NO disponible")
            print()

if __name__ == "__main__":
    test_section_notes()
