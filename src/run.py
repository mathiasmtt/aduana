import os
import sys
from pathlib import Path
import argparse
import logging
from contextlib import contextmanager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Agregar el directorio src al path para poder importar app
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# Importar la aplicación después de configurar el path
from app import get_app, db

# Obtener la aplicación Flask
app = get_app()

@contextmanager
def app_context():
    """Asegura que siempre haya un contexto de aplicación activo."""
    ctx = app.app_context()
    ctx.push()
    try:
        yield
    finally:
        ctx.pop()

if __name__ == '__main__':
    # Verificar que la aplicación esté correctamente configurada
    try:
        # Hacer una consulta de prueba para verificar la conexión
        with app_context():
            # Verificar que se puede acceder a la sesión de SQLAlchemy
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1")).scalar()
            logging.info(f"Verificación de base de datos exitosa: {result}")
    except Exception as e:
        logging.error(f"Error al verificar la configuración: {str(e)}")
        sys.exit(1)
    
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Ejecutar el servidor Flask de Aduana')
    parser.add_argument('--port', type=int, default=5051, help='Puerto para ejecutar el servidor')
    args = parser.parse_args()
    
    # Ejecutar la aplicación
    logging.info("Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=args.port, debug=True)
