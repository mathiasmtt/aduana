#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar todas las notas de sección.
"""

import sys
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app
from app.models import SectionNote, Arancel
import re

def roman_to_decimal(roman):
    """Convierte un número romano a decimal."""
    roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    decimal = 0
    prev_value = 0
    
    for char in reversed(roman):
        current_value = roman_values[char]
        if current_value >= prev_value:
            decimal += current_value
        else:
            decimal -= current_value
        prev_value = current_value
    
    return decimal

def verify_all_section_notes():
    """
    Verifica todas las notas de sección, su existencia y accesibilidad.
    """
    app = create_app()
    
    with app.app_context():
        # 1. Verificar las secciones disponibles en la base de datos
        db_sections = SectionNote.query.all()
        db_section_numbers = [note.section_number for note in db_sections]
        db_section_numbers.sort()
        
        print(f"Hay {len(db_section_numbers)} secciones en la base de datos:")
        for section in db_section_numbers:
            print(f"- {section}")
        
        # 2. Verificar las secciones en el arancel
        arancel_sections = Arancel.query.with_entities(Arancel.SECTION).distinct().all()
        arancel_section_dict = {}
        
        for section_text in arancel_sections:
            if not section_text[0]:
                continue
            
            section_match = re.match(r'^([IVX]+)\s*-\s*(.*)$', section_text[0])
            if section_match:
                roman = section_match.group(1)
                desc = section_match.group(2)
                decimal = roman_to_decimal(roman)
                decimal_str = f"{decimal:02d}"
                
                arancel_section_dict[decimal_str] = {
                    'roman': roman,
                    'description': desc,
                    'full_text': section_text[0]
                }
        
        print(f"\nHay {len(arancel_section_dict)} secciones en el arancel:")
        for decimal, data in sorted(arancel_section_dict.items()):
            print(f"- {decimal}: {data['roman']} - {data['description']}")
        
        # 3. Verificar la correspondencia entre ambas fuentes
        print("\nVerificando correspondencia entre secciones de BD y arancel:")
        for decimal in sorted(arancel_section_dict.keys()):
            if decimal in db_section_numbers:
                print(f"✅ Sección {decimal} ({arancel_section_dict[decimal]['roman']}): Presente en ambos")
            else:
                print(f"❌ Sección {decimal} ({arancel_section_dict[decimal]['roman']}): Falta en la BD")
        
        for section in db_section_numbers:
            if section not in arancel_section_dict:
                print(f"⚠️ Sección {section}: Presente en BD pero no en arancel")
        
        # 4. Probar la recuperación de notas con diferentes formatos
        print("\nPrueba de recuperación de notas con diferentes formatos:")
        test_sections = [
            ('01', 'Numérico con ceros'),
            ('1', 'Numérico sin ceros'),
            ('I', 'Romano'),
            ('I - Animales vivos y productos del reino animal', 'Romano con descripción')
        ]
        
        for section, desc in test_sections:
            note = SectionNote.get_note_by_section(section)
            print(f"\nFormato: {desc} ('{section}')")
            if note:
                print(f"✅ Nota recuperada (primeros 50 caracteres): {note[:50]}...")
            else:
                print(f"❌ No se pudo recuperar la nota")
        
        # 5. Verificar que todas las notas sean accesibles por NCM
        print("\nVerificando acceso a notas por NCM:")
        
        # Tomar un NCM por cada sección
        test_ncms = []
        for section in sorted(arancel_section_dict.keys()):
            roman = arancel_section_dict[section]['roman']
            # Buscar un NCM para esta sección
            arancel = Arancel.query.filter(Arancel.SECTION == arancel_section_dict[section]['full_text']).first()
            if arancel:
                test_ncms.append((arancel.NCM, roman, section))
        
        for ncm, roman, section in test_ncms:
            note = SectionNote.get_note_by_ncm(ncm)
            if note:
                print(f"✅ NCM: {ncm} -> Sección {roman} ({section}): Nota accesible")
            else:
                print(f"❌ NCM: {ncm} -> Sección {roman} ({section}): Nota NO accesible")

if __name__ == "__main__":
    verify_all_section_notes()
