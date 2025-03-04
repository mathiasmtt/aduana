#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar la sección 01 en el archivo Excel.
"""

import sys
import pandas as pd
import re
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app, db
from app.models import SectionNote

def check_section_01():
    """
    Verifica si la sección 01 existe en el archivo Excel y la agrega a la base de datos.
    """
    excel_file = 'data/Arancel Nacional_Abril 2024.xlsx'
    
    try:
        # Intentamos leer todo el archivo Excel para buscar la sección I
        df = pd.read_excel(excel_file, sheet_name=0, header=None)
        print(f"Se leyó el archivo Excel: {excel_file}")
        
        # Buscar texto que indique la sección I
        section_pattern = re.compile(r'^Sección I', re.IGNORECASE)
        found = False
        section_text = ""
        
        for i, row in df.iterrows():
            for col in df.columns:
                if isinstance(row[col], str) and section_pattern.search(row[col]):
                    print(f"¡Encontrada la sección I en la fila {i}, columna {col}!")
                    found = True
                    
                    # Intentar reconstruir la nota
                    start_row = i
                    section_text = row[col] + "\n"
                    
                    # Recopilar texto hasta encontrar otra sección o un código NCM
                    next_section_pattern = re.compile(r'^Sección II', re.IGNORECASE)
                    ncm_pattern = re.compile(r'^\d{4}\.\d{2}\.\d{2}\.\d{2}$')
                    
                    for j in range(start_row + 1, len(df)):
                        stop_collection = False
                        
                        for c in df.columns:
                            cell_value = df.iloc[j, c]
                            if isinstance(cell_value, str):
                                if next_section_pattern.search(cell_value) or ncm_pattern.search(cell_value):
                                    stop_collection = True
                                    break
                                
                                if cell_value.strip():
                                    section_text += cell_value + "\n"
                        
                        if stop_collection:
                            break
                    
                    break
            
            if found:
                break
        
        if not found:
            print("No se encontró la sección I en el archivo Excel.")
            return
        
        # Mostrar el texto recopilado de la sección I
        print("\nTexto de la sección I encontrado:")
        print("=" * 80)
        print(section_text[:500] + "..." if len(section_text) > 500 else section_text)
        print("=" * 80)
        
        # Verificar si ya existe en la base de datos
        app = create_app()
        with app.app_context():
            existing_note = SectionNote.query.filter_by(section_number='01').first()
            
            if existing_note:
                print(f"La sección 01 ya existe en la base de datos con ID {existing_note.id}")
                return
            
            # Preguntar si se desea agregar la nota a la base de datos
            add_to_db = input("¿Desea agregar esta nota a la base de datos? (s/n): ")
            
            if add_to_db.lower() == 's':
                # Agregar la nota a la base de datos
                new_note = SectionNote(section_number='01', note_text=section_text)
                db.session.add(new_note)
                db.session.commit()
                print("Nota para la sección 01 agregada a la base de datos.")
            else:
                print("No se agregó la nota a la base de datos.")
    
    except Exception as e:
        print(f"Error al procesar el archivo Excel: {e}")

if __name__ == "__main__":
    check_section_01()
