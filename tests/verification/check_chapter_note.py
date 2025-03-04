import sys
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app, db
from app.models import ChapterNote

def check_chapter_note(chapter_number):
    """Verifica el contenido de una nota de capítulo específica."""
    app = create_app()
    with app.app_context():
        note_text = ChapterNote.get_note_by_chapter(chapter_number.zfill(2))
        if note_text:
            print(f"Nota del capítulo {chapter_number}:")
            print("-" * 40)
            print(note_text)
            print("-" * 40)
        else:
            print(f"No se encontró ninguna nota para el capítulo {chapter_number}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_chapter_note(sys.argv[1])
    else:
        print("Por favor especifica un número de capítulo, por ejemplo: python check_chapter_note.py 23")
