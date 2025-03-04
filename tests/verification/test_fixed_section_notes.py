#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para probar el método corregido de obtención de notas de sección.
"""

import os
import sys
import sqlite3

# Añadir la ruta al directorio raíz para importar los módulos
sys.path.append('/Users/mat/Code/aduana/src')

# Configurar variables de entorno
os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'development'

from app import create_app
from app.models import SectionNote, Arancel

def test_section_notes():
    """Prueba la recuperación de notas de sección utilizando diferentes métodos."""
    app = create_app()
    
    with app.app_context():
        # Prueba 1: Obtener nota de sección utilizando número romano
        print("\n=== Prueba 1: Obtener nota usando número romano ===")
        section_roman = "IV"
        note = SectionNote.get_note_by_section(section_roman)
        print(f"Nota para sección {section_roman}: {'✅ OK' if note else '❌ No encontrada'}")
        if note:
            print(f"Primeros 100 caracteres: {note[:100]}...")
        
        # Prueba 2: Obtener nota de sección utilizando formato "IV - Descripción"
        print("\n=== Prueba 2: Obtener nota usando formato 'IV - Descripción' ===")
        section_with_desc = "IV - Productos de las industrias alimentarias"
        note = SectionNote.get_note_by_section(section_with_desc)
        print(f"Nota para sección {section_with_desc}: {'✅ OK' if note else '❌ No encontrada'}")
        if note:
            print(f"Primeros 100 caracteres: {note[:100]}...")
        
        # Prueba 3: Obtener nota de sección utilizando NCM
        print("\n=== Prueba 3: Obtener nota usando NCM ===")
        ncm_codes = ["2004.10.00.00", "3901.90.90.00", "8471.30.90.00"]
        
        for ncm in ncm_codes:
            # Buscar el arancel para obtener la sección
            arancel = Arancel.query.filter(Arancel.NCM == ncm).first()
            section = arancel.SECTION if arancel else "Desconocida"
            
            # Obtener la nota de sección
            note = SectionNote.get_note_by_ncm(ncm)
            
            print(f"NCM: {ncm}, Sección: {section}")
            print(f"Nota: {'✅ OK' if note else '❌ No encontrada'}")
            if note:
                print(f"Primeros 100 caracteres: {note[:100]}...")
            print("")
        
        # Prueba 4: Obtener nota de sección pasando la sección como parámetro
        print("\n=== Prueba 4: Obtener nota pasando la sección como parámetro ===")
        for ncm in ncm_codes:
            # Buscar el arancel para obtener la sección
            arancel = Arancel.query.filter(Arancel.NCM == ncm).first()
            
            if arancel:
                section = arancel.SECTION
                note = SectionNote.get_note_by_ncm(ncm, section)
                
                print(f"NCM: {ncm}, Sección: {section}")
                print(f"Nota: {'✅ OK' if note else '❌ No encontrada'}")
                if note:
                    print(f"Primeros 100 caracteres: {note[:100]}...")
                print("")

if __name__ == "__main__":
    test_section_notes()
