#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corregir el método get_note_by_ncm en el modelo SectionNote.
"""

import re
import sys
import os
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app, db
from app.models import SectionNote, Arancel

def convert_roman_to_decimal(roman):
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

def create_section_mapping():
    """
    Crea un mapeo entre los números de sección en formato romano y decimal.
    """
    section_map = {}
    
    app = create_app()
    with app.app_context():
        sections = Arancel.query.with_entities(Arancel.SECTION).distinct().all()
        
        for section_text in sections:
            if not section_text[0]:
                continue
            
            # Extraer el número romano de la sección
            section_match = re.match(r'^([IVX]+)\s*-\s*.*$', section_text[0])
            if section_match:
                roman = section_match.group(1)
                decimal = convert_roman_to_decimal(roman)
                decimal_str = f"{decimal:02d}"
                
                section_map[section_text[0]] = decimal_str
                print(f"Mapeo: '{section_text[0]}' -> '{decimal_str}'")
        
        # Verificar si existe la nota para cada sección decimal
        print("\nVerificando existencia de notas:")
        for roman_section, decimal_section in section_map.items():
            note = SectionNote.query.filter_by(section_number=decimal_section).first()
            if note:
                print(f"✅ Sección {roman_section} -> {decimal_section}: Nota disponible")
            else:
                print(f"❌ Sección {roman_section} -> {decimal_section}: Nota NO disponible")
    
    return section_map

def update_section_note_model():
    """
    Actualiza el modelo SectionNote para manejar correctamente el formato de sección.
    """
    # Contenido del archivo section_note.py actualizado
    section_note_content = """from app import db
import re

class SectionNote(db.Model):
    \"\"\"Modelo para las notas de sección del Arancel Nacional.\"\"\"
    __tablename__ = 'section_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    section_number = db.Column(db.String(2), nullable=False, unique=True, index=True)
    note_text = db.Column(db.Text, nullable=False)
    
    @classmethod
    def get_note_by_section(cls, section_number):
        \"\"\"
        Obtiene la nota correspondiente a un número de sección.
        
        Args:
            section_number (str): Número de sección en formato '01', '02', etc.
            
        Returns:
            str: Texto de la nota de la sección, o None si no existe.
        \"\"\"
        # Si el section_number es un número romano o tiene formato "X - Descripción"
        if not section_number.isdigit():
            # Verificar si contiene un número romano
            roman_match = re.match(r'^([IVX]+)(?:\\s*-\\s*.*)?$', section_number)
            if roman_match:
                roman = roman_match.group(1)
                section_number = cls.convert_roman_to_decimal(roman)
        
        # Asegurarse de que el formato sea de dos dígitos
        if section_number.isdigit():
            section_number = section_number.zfill(2)
        
        note = cls.query.filter_by(section_number=section_number).first()
        return note.note_text if note else None
    
    @classmethod
    def get_note_by_ncm(cls, ncm, section_number=None):
        \"\"\"
        Obtiene la nota correspondiente a la sección de un código NCM.
        
        Args:
            ncm (str): Código NCM de un producto.
            section_number (str, optional): Número de sección si ya se conoce.
            
        Returns:
            str: Texto de la nota de la sección, o None si no existe.
        \"\"\"
        if section_number:
            return cls.get_note_by_section(section_number)
        
        # Si no tenemos el número de sección, necesitamos buscarlo
        # en la base de datos usando el NCM
        if not ncm or len(ncm) < 2:
            return None
        
        # Consulta para obtener la SECTION desde la tabla arancel_nacional
        from app.models import Arancel
        arancel = Arancel.query.filter(Arancel.NCM == ncm).first()
        
        if not arancel or not arancel.SECTION:
            return None
        
        # La sección en el arancel tiene formato "XXI - Objetos de arte o colección y antigüedades"
        # Necesitamos extraer el número romano y convertirlo a decimal
        return cls.get_note_by_section(arancel.SECTION)
    
    @staticmethod
    def convert_roman_to_decimal(roman):
        \"\"\"
        Convierte un número romano a decimal y lo devuelve con formato de dos dígitos.
        
        Args:
            roman (str): Número romano (I, II, III, IV, etc.)
            
        Returns:
            str: Número decimal con formato de dos dígitos (01, 02, 03, etc.)
        \"\"\"
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
        
        # Devolver el número con formato de dos dígitos
        return f"{decimal:02d}"
"""
    
    # Escribir el nuevo contenido al archivo
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'src', 'app', 'models', 'section_note.py')
    
    with open(file_path, 'w') as f:
        f.write(section_note_content)
    
    print(f"\nArchivo {file_path} actualizado con éxito.")

if __name__ == "__main__":
    section_map = create_section_mapping()
    update_section_note_model()
