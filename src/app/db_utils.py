import os
import sqlite3
import logging
from pathlib import Path
from flask import g, current_app, request, has_app_context
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from . import db

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constantes
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_VERSIONS_DIR = BASE_DIR / 'data' / 'db_versions'
# Ya no usamos database.sqlite3 como base de datos predeterminada
# ORIGINAL_DB_PATH = BASE_DIR / 'data' / 'database.sqlite3'
LATEST_SYMLINK = DB_VERSIONS_DIR / 'arancel_latest.sqlite3'

# Registrar las rutas de base de datos para depuración
logging.info(f"BASE_DIR: {BASE_DIR}")
logging.info(f"DB_VERSIONS_DIR: {DB_VERSIONS_DIR}")
# Ya no mostramos la ruta a database.sqlite3
logging.info(f"LATEST_SYMLINK: {LATEST_SYMLINK}")

def init_app(app):
    """Inicializa las funciones de utilidad de base de datos en la aplicación Flask."""
    check_versions(app)
    check_and_create_notes_tables(app)
    
    @app.template_filter('format_version')
    def format_version(version_str):
        """Formatea una cadena de versión para mostrarla en la interfaz."""
        if not version_str:
            return "Última versión"
        
        # Formato esperado: YYYYMM
        if len(version_str) == 6:
            año = version_str[:4]
            mes = version_str[4:6]
            return f"{meses_map.get(mes, mes)}/{año}"
        
        return version_str

def close_db(e=None):
    """Cerrar la conexión a la base de datos al final de cada solicitud."""
    try:
        db.session.remove()
        logging.debug("Cerrada sesión de base de datos")
    except Exception as e:
        logging.error(f"Error al cerrar sesión de base de datos: {str(e)}")

def get_available_versions():
    """Obtener todas las versiones disponibles de la base de datos."""
    versions = []
    
    try:
        # Verificar que el directorio existe
        if not DB_VERSIONS_DIR.exists():
            logging.warning(f"El directorio {DB_VERSIONS_DIR} no existe")
            return versions
        
        # Buscar archivos .sqlite3 en el directorio de versiones
        for file in DB_VERSIONS_DIR.glob('arancel_*.sqlite3'):
            filename = file.name
            
            # No incluir el enlace simbólico "latest"
            if filename == 'arancel_latest.sqlite3' and file.is_symlink():
                continue
                
            # Extraer la versión del nombre del archivo (arancel_20XX.sqlite3 -> 20XX)
            if '_' in filename:
                version = filename.split('_')[1].split('.')[0]
                versions.append(version)
        
        # Ordenar las versiones de manera descendente
        versions.sort(reverse=True)
    except Exception as e:
        logging.error(f"Error al obtener versiones disponibles: {str(e)}")
        # Devolver lista vacía en caso de error
        versions = []
    
    logging.debug(f"Versiones disponibles: {versions}")
    return versions

def get_db_path_for_version(version=None):
    """
    Obtener la ruta al archivo de base de datos para una versión específica.
    
    Args:
        version: Versión del arancel (ej: "2017", "2022")
        
    Returns:
        Path al archivo de base de datos
    """
    # Si no se especifica versión, usar la más reciente
    if not version:
        if LATEST_SYMLINK.exists():
            db_path = LATEST_SYMLINK
            logging.info(f"Solicitada base de datos más reciente, devolviendo: {db_path}")
        else:
            # Ya no usamos database.sqlite3 como base de datos predeterminada
            # db_path = ORIGINAL_DB_PATH
            error_msg = "No se encontró el enlace simbólico a la versión más reciente y no hay una base de datos predeterminada."
            logging.warning(error_msg)
            raise FileNotFoundError(error_msg)
    else:
        # Buscar una versión específica
        db_path = DB_VERSIONS_DIR / f"arancel_{version}.sqlite3"
        
        # Si no existe, usar la más reciente
        if not db_path.exists():
            logging.warning(f"No se encontró la versión {version}, usando la más reciente en su lugar")
            if LATEST_SYMLINK.exists():
                db_path = LATEST_SYMLINK
            else:
                # Ya no usamos database.sqlite3 como base de datos predeterminada
                error_msg = "No se encontró la versión especificada ni una versión predeterminada."
                logging.warning(error_msg)
                raise FileNotFoundError(error_msg)
    
    return db_path

def get_db_for_version(version=None):
    """
    Obtener una sesión de SQLAlchemy para una versión específica de la base de datos.
    SIEMPRE devuelve db.session para mantener consistencia.
    
    Args:
        version: Versión del arancel (ej: "2017", "2022")
        
    Returns:
        Sesión de SQLAlchemy
    """
    # Siempre devolver la sesión principal de SQLAlchemy
    return db.session

def get_db():
    """
    Obtener la conexión a la base de datos para la solicitud actual.
    SIEMPRE devuelve db.session para mantener consistencia.
    
    Returns:
        Sesión de SQLAlchemy
    """
    # Siempre devolver la sesión principal de SQLAlchemy
    return db.session

def check_and_create_notes_tables(app=None):
    """
    Verifica si las tablas de notas existen en todas las versiones de la base de datos
    y las crea si es necesario.
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    import sqlite3
    import os
    import logging
    from pathlib import Path
    
    # Si no se proporciona app, obtenerla del contexto actual
    if app is None:
        from flask import current_app
        app = current_app
    
    # Obtener la ruta base para las bases de datos
    base_dir = Path(app.root_path).parent.parent
    db_dir = base_dir / 'data' / 'db_versions'
    
    # Obtener todas las bases de datos de versiones
    db_files = [f for f in os.listdir(db_dir) if f.endswith('.sqlite3')]
    
    for db_file in db_files:
        db_path = db_dir / db_file
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Verificar si la tabla chapter_notes existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chapter_notes'")
            if not cursor.fetchone():
                # Crear tabla de notas de capítulo
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapter_notes (
                    id INTEGER PRIMARY KEY,
                    chapter_number TEXT NOT NULL UNIQUE,
                    note_text TEXT NOT NULL
                )
                ''')
                logging.info(f"Tabla chapter_notes creada en {db_file}")
            
            # Verificar si la tabla section_notes existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='section_notes'")
            if not cursor.fetchone():
                # Crear tabla de notas de sección
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS section_notes (
                    id INTEGER PRIMARY KEY,
                    section_number TEXT NOT NULL UNIQUE,
                    note_text TEXT NOT NULL
                )
                ''')
                logging.info(f"Tabla section_notes creada en {db_file}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error al verificar/crear tablas de notas en {db_file}: {str(e)}")

def check_versions(app=None):
    """
    Verifica y crea la estructura de directorios necesarios para
    el funcionamiento del sistema de versiones de base de datos.
    Ya no crea automáticamente la base de datos principal.
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    # Crear directorios necesarios si no existen
    if not DB_VERSIONS_DIR.exists():
        DB_VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
        logging.info(f"Creado directorio de versiones: {DB_VERSIONS_DIR}")
    
    # Ya no se crea automáticamente la base de datos principal
    
    # Ya no es necesario verificar el enlace simbólico a la base de datos principal
    # puesto que ya no se crea la base de datos predeterminada

def get_latest_version():
    """
    Obtiene la versión más reciente disponible.
    
    Returns:
        str: La versión más reciente, o None si no hay versiones disponibles.
    """
    versions = get_available_versions()
    return versions[0] if versions else None

def get_all_versions():
    """
    Obtiene todas las versiones disponibles.
    
    Returns:
        list: Lista de todas las versiones disponibles.
    """
    return get_available_versions()

def get_active_db():
    """
    Obtiene la conexión a la base de datos activa para la sesión actual.
    
    Returns:
        Session: La sesión de SQLAlchemy activa.
    """
    return get_db()

def set_arancel_version(version):
    """
    Establece la versión de arancel para la sesión actual.
    
    Args:
        version (str): La versión a establecer.
        
    Returns:
        bool: True si se estableció correctamente, False en caso contrario.
    """
    from flask import session
    
    try:
        session['arancel_version'] = version
        return True
    except Exception as e:
        logging.error(f"Error al establecer la versión del arancel: {str(e)}")
        return False

# Mapa de nombres de meses
meses_map = {
    '01': 'Enero',
    '02': 'Febrero',
    '03': 'Marzo',
    '04': 'Abril',
    '05': 'Mayo',
    '06': 'Junio',
    '07': 'Julio',
    '08': 'Agosto',
    '09': 'Septiembre',
    '10': 'Octubre',
    '11': 'Noviembre',
    '12': 'Diciembre'
}
