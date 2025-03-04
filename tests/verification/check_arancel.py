from app import create_app, db
from app.models import Arancel

def main():
    app = create_app()
    with app.app_context():
        # Obtener el primer arancel
        arancel = Arancel.query.first()
        
        if arancel:
            # Mostrar todos los atributos
            print("Atributos del primer arancel:")
            for key, value in vars(arancel).items():
                if not key.startswith('_'):
                    print(f"{key}: {value}")
            
            # Mostrar información específica
            print("\nInformación específica:")
            print(f"NCM: {arancel.NCM}")
            print(f"DESCRIPCION: {arancel.DESCRIPCION}")
            print(f"CHAPTER: {arancel.CHAPTER}")
            print(f"SECTION: {arancel.SECTION}")
        else:
            print("No se encontraron registros de aranceles.")

if __name__ == "__main__":
    main()
