import sys
sys.path.append('/Users/mat/Code/aduana/src')

from app import create_app
from app.models import ChapterNote

def main():
    """Revisar las notas de capítulo en la base de datos."""
    app = create_app()
    with app.app_context():
        # Contar el total de notas
        total_notes = ChapterNote.query.count()
        print(f'Total de notas de capítulo en la base de datos: {total_notes}')
        
        # Mostrar todas las notas disponibles
        notes = ChapterNote.query.order_by(ChapterNote.chapter_number).all()
        
        for note in notes:
            # Mostrar resumen de cada nota
            lines = note.note_text.count('\n') + 1
            preview = note.note_text.replace('\n', ' ')
            if len(preview) > 100:
                preview = preview[:97] + '...'
                
            print(f'Capítulo {note.chapter_number}: {lines} líneas - {preview}')
            
        # Verificar capítulos sin notas
        missing_chapters = []
        for i in range(1, 98):  # Del capítulo 01 al 97
            chapter_num = f"{i:02d}"
            if not ChapterNote.query.filter_by(chapter_number=chapter_num).first():
                missing_chapters.append(chapter_num)
        
        if missing_chapters:
            print(f'\nHay {len(missing_chapters)} capítulos sin notas:')
            for chapter in missing_chapters:
                print(f'Capítulo {chapter}')
        else:
            print('\nTodos los capítulos tienen notas!')

if __name__ == "__main__":
    main()
