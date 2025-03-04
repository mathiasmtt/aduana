import pandas as pd
import re
import os
import sys
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app, db
from app.models import SectionNote

# Ruta al archivo Excel
EXCEL_FILE = 'data/Arancel Nacional_Abril 2024.xlsx'

# Mapeo de notas por sección (basado en el ejemplo que has proporcionado)
SECTION_NOTES = {
    "01": """1. En esta Sección, cualquier referencia a un género o a una especie determinada de un animal se aplica también, salvo disposición en contrario, a los animales jóvenes de ese género o de esa especie.
2. Salvo disposición en contrario, cualquier referencia en la Nomenclatura a productos secos o desecados alcanza también a los productos deshidratados, evaporados o liofilizados.""",
    
    "02": """1. En esta Sección, el término «pellets» designa los productos en forma de cilindro, bolita, etc., aglomerados por simple presión o con adición de un aglutinante en proporción inferior o igual al 3% en peso.""",
    
    "03": """Notas.
1. Esta Sección no comprende:
   a) los estearatos o jabones cosméticos de la partida 34.01;
   b) las ceras artificiales de la partida 34.04.""",
    
    # Puedes añadir más notas de sección aquí
}

def extract_section_notes():
    """Extrae las notas de sección del archivo Excel o utiliza las predefinidas."""
    
    print(f"Procesando notas de sección...")
    
    # Verificamos si ya tenemos notas predefinidas
    if SECTION_NOTES:
        print(f"Utilizando {len(SECTION_NOTES)} notas de sección predefinidas")
        for section, notes in sorted(SECTION_NOTES.items()):
            print(f"Sección {section}: {len(notes.split('\\n'))} líneas de notas")
        return SECTION_NOTES
    
    # Si no tenemos notas predefinidas, intentamos extraerlas del Excel
    # Aquí podrías implementar la lógica para extraer las notas de sección
    # similar a lo que hicimos con las notas de capítulo
    
    return SECTION_NOTES

def save_notes_to_db(section_notes):
    """Guarda las notas de sección en la base de datos."""
    app = create_app()
    with app.app_context():
        # Crear tabla si no existe
        db.create_all()
        
        # Contador para nuevas entradas y actualizaciones
        new_count = 0
        update_count = 0
        
        # Guardar cada nota en la base de datos
        for section_number, note_text in section_notes.items():
            # Buscar si ya existe la nota
            note = SectionNote.query.filter_by(section_number=section_number).first()
            
            if note:
                # Actualizar nota existente
                note.note_text = note_text
                update_count += 1
            else:
                # Crear nueva nota
                note = SectionNote(section_number=section_number, note_text=note_text)
                db.session.add(note)
                new_count += 1
        
        # Guardar cambios
        db.session.commit()
        print(f"Se crearon {new_count} nuevas notas de sección y se actualizaron {update_count} notas existentes.")

def main():
    """Función principal."""
    section_notes = extract_section_notes()
    if section_notes:
        save_notes_to_db(section_notes)
    else:
        print("No se encontraron notas de sección para guardar.")

if __name__ == "__main__":
    main()
