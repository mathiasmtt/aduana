#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar que las notas de sección se puedan obtener correctamente por NCM
después de las correcciones en el modelo SectionNote.
"""

import sys
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app
from app.models import SectionNote, Arancel

def test_fixed_section_notes_by_ncm():
    """
    Prueba la obtención de notas de sección a partir de códigos NCM
    después de las correcciones en el modelo SectionNote.
    """
    app = create_app()
    
    with app.app_context():
        # Probar específicamente algunos NCM de secciones conocidas
        test_ncms = ['3901.90.90.00', '8471.30.12.00', '6402.19.00.00']
        
        print("Verificando notas de sección por NCM después de las correcciones:\n")
        
        for ncm in test_ncms:
            # Buscar el NCM en la base de datos
            arancel = Arancel.query.filter_by(NCM=ncm).first()
            if not arancel:
                print(f"❌ No se encontró el NCM {ncm} en la base de datos")
                continue
            
            section = arancel.SECTION
            
            if not section:
                print(f"❌ El NCM {ncm} no tiene asignada una sección")
                continue
            
            # Obtener la nota de sección
            note = SectionNote.get_note_by_ncm(ncm)
            
            print(f"NCM: {ncm} -> Sección: {section}")
            if note:
                print(f"✅ Nota disponible")
                print(f"Primeros 100 caracteres:\n{note[:100]}...\n")
                print(f"Longitud total: {len(note)} caracteres\n")
            else:
                print(f"❌ Nota NO disponible\n")
        
        # Probar con diferentes formatos de sección
        test_sections = ['VII', 'VII - Plástico y caucho', '7', '07']
        
        print("\nVerificando notas con diferentes formatos de sección:")
        for section in test_sections:
            note = SectionNote.get_note_by_section(section)
            
            print(f"Sección: '{section}'")
            if note:
                print(f"✅ Nota disponible")
                print(f"Primeros 100 caracteres:\n{note[:100]}...\n")
            else:
                print(f"❌ Nota NO disponible\n")

if __name__ == "__main__":
    test_fixed_section_notes_by_ncm()
