import os
import sys
from pathlib import Path

# Agregar el directorio src al path para poder importar app
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent.parent
sys.path.append(str(src_dir))

from app import create_app, db
from app.models.auxiliares import CodigoPaises

def init_auxiliares_database():
    """
    Inicializa la base de datos auxiliares creando todas las tablas definidas en los modelos
    """
    print("Inicializando la base de datos auxiliares...")
    
    # Crear la aplicación con configuración de desarrollo
    app = create_app('development')
    
    # Establecer el contexto de la aplicación
    with app.app_context():
        # Crear todas las tablas definidas en los modelos de auxiliares
        db.create_all()
        print("Tablas de auxiliares creadas correctamente.")
        
        # Verificar si ya existen registros
        if CodigoPaises.query.first() is None:
            print("La tabla CODIGO_PAISES está vacía. Puedes cargar datos de códigos de países.")
        else:
            print(f"La tabla CODIGO_PAISES ya contiene {CodigoPaises.query.count()} registros.")

def cargar_codigos_paises(paises_data):
    """
    Carga los códigos de países en la tabla CODIGO_PAISES.
    
    Args:
        paises_data: Lista de diccionarios con los datos de los países (codigo_num, nombre, codigo_letras)
    """
    app = create_app('development')
    
    with app.app_context():
        # Verificar si ya existen registros
        if CodigoPaises.query.first() is not None:
            # Eliminar registros existentes para insertar los nuevos
            print("Eliminando registros existentes...")
            CodigoPaises.query.delete()
        
        # Insertar nuevos registros
        print("Insertando códigos de países...")
        for pais in paises_data:
            # Asegurar que codigo_num siempre tenga 3 dígitos
            codigo_num = pais['codigo_num'].zfill(3)
            
            # Verificar que no exceda los 3 dígitos
            if len(codigo_num) > 3:
                print(f"Advertencia: El código numérico '{codigo_num}' excede los 3 dígitos. Se usarán los últimos 3.")
                codigo_num = codigo_num[-3:]
            
            codigo_pais = CodigoPaises(
                codigo_num=codigo_num,
                nombre=pais['nombre'],
                codigo_letras=pais['codigo_letras']
            )
            db.session.add(codigo_pais)
        
        # Guardar cambios
        db.session.commit()
        print(f"Se han insertado {len(paises_data)} códigos de países.")

if __name__ == "__main__":
    init_auxiliares_database() 