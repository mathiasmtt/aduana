import os
import sys
from pathlib import Path

# Agregar el directorio src al path para poder importar app
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from app import create_app, db
from app.models.arancel import Arancel

def init_database():
    """
    Inicializa la base de datos creando todas las tablas definidas en los modelos
    """
    print("Inicializando la base de datos...")
    
    # Crear la aplicación con configuración de desarrollo
    app = create_app('development')
    
    # Establecer el contexto de la aplicación
    with app.app_context():
        # Crear todas las tablas definidas en los modelos
        db.create_all()
        print("Tablas creadas correctamente.")
        
        # Verificar si ya existen registros
        if Arancel.query.first() is None:
            print("La base de datos está vacía. Necesitas cargar datos con process_data.py")
        else:
            print(f"La base de datos ya contiene {Arancel.query.count()} registros.")

if __name__ == "__main__":
    init_database()
