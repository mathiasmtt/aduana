from app import create_app, db
from app.models import Arancel

def main():
    app = create_app()
    with app.app_context():
        # Contar registros totales
        total_registros = Arancel.query.count()
        print(f'Total registros: {total_registros}')
        
        # Contar capítulos distintos
        capitulos_count = db.session.query(Arancel.CHAPTER).distinct().filter(Arancel.CHAPTER != "").count()
        print(f'Capítulos distintos: {capitulos_count}')
        
        # Mostrar todos los capítulos
        if capitulos_count > 0:
            capitulos = db.session.query(Arancel.CHAPTER).distinct().filter(
                Arancel.CHAPTER != ''
            ).order_by(Arancel.CHAPTER).all()
            
            print("\nListado completo de capítulos:")
            for i, capitulo in enumerate(capitulos, 1):
                print(f"{i}. {capitulo[0]}")
        
        # Contar secciones distintas
        secciones_count = db.session.query(Arancel.SECTION).distinct().filter(Arancel.SECTION != "").count()
        print(f'\nSecciones distintas: {secciones_count}')
        
        # Mostrar primeras 5 secciones
        if secciones_count > 0:
            secciones = db.session.query(Arancel.SECTION).distinct().filter(
                Arancel.SECTION != ''
            ).order_by(Arancel.SECTION).limit(5).all()
            
            print("\nPrimeras 5 secciones:")
            for i, seccion in enumerate(secciones, 1):
                print(f"{i}. {seccion[0]}")

if __name__ == "__main__":
    main()
