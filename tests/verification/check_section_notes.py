import sys
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app, db
from app.models import SectionNote

def check_section_notes():
    """Verifica las notas de sección en la base de datos."""
    app = create_app()
    with app.app_context():
        # Obtener todas las notas de sección
        section_notes = SectionNote.query.all()
        
        print(f"Total de notas de sección en la base de datos: {len(section_notes)}")
        
        if section_notes:
            print("\nResumen de las notas:")
            for note in section_notes:
                print(f"Sección {note.section_number}: {note.note_text[:50]}...")
        else:
            print("No se encontraron notas de sección en la base de datos.")

if __name__ == "__main__":
    check_section_notes()
