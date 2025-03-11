"""
Módulo para inicializar la base de datos de aduana.
"""

import os
import sqlite3
import logging
from pathlib import Path

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def obtener_ruta_db():
    """
    Obtiene la ruta estándar de la base de datos.
    
    Returns:
        str: Ruta a la base de datos.
    """
    # Ruta estándar de la base de datos
    project_root = Path(__file__).resolve().parent.parent.parent
    return str(project_root / 'data' / 'aduana' / 'aduana.db')

def crear_base_datos(db_path='/data/aduana/aduana.db'):
    """
    Crea la base de datos aduana con sus tablas correspondientes.
    
    Args:
        db_path (str): Ruta donde se creará la base de datos.
        
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    try:
        # Asegurar que el directorio exista
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Crear conexión a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla de resoluciones de clasificación arancelaria
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resoluciones_clasificacion_arancelaria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            numero INTEGER NOT NULL,
            fecha DATE NOT NULL,
            referencia TEXT,
            dictamen TEXT,
            resolucion TEXT,
            url_dictamen TEXT,
            url_resolucion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Crear índice para búsqueda rápida por año y número
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_year_numero 
        ON resoluciones_clasificacion_arancelaria (year, numero)
        ''')
        
        # Guardar cambios y cerrar conexión
        conn.commit()
        conn.close()
        
        logger.info(f"Base de datos aduana creada exitosamente en {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error al crear la base de datos: {str(e)}")
        return False

def agregar_resolucion(db_path, year, numero, fecha, referencia='', dictamen='', resolucion='', url_dictamen='', url_resolucion=''):
    """
    Agrega una nueva resolución de clasificación arancelaria a la base de datos.
    
    Args:
        db_path (str): Ruta de la base de datos.
        year (int): Año de la resolución.
        numero (int): Número de la resolución.
        fecha (str): Fecha de la resolución en formato YYYY-MM-DD.
        referencia (str): Referencia de la resolución.
        dictamen (str): Texto del dictamen.
        resolucion (str): Texto de la resolución.
        url_dictamen (str): URL del dictamen.
        url_resolucion (str): URL de la resolución.
        
    Returns:
        int: ID de la resolución creada o -1 en caso de error.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO resoluciones_clasificacion_arancelaria
        (year, numero, fecha, referencia, dictamen, resolucion, url_dictamen, url_resolucion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (year, numero, fecha, referencia, dictamen, resolucion, url_dictamen, url_resolucion))
        
        last_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        logger.info(f"Resolución {year}/{numero} agregada exitosamente (ID: {last_id})")
        return last_id
        
    except Exception as e:
        logger.error(f"Error al agregar resolución: {str(e)}")
        return -1

if __name__ == "__main__":
    # Ejemplo de uso
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                          'data', 'aduana', 'aduana.db')
    
    if crear_base_datos(db_path):
        print(f"Base de datos creada exitosamente en {db_path}")
        
        # Ejemplo de inserción
        agregar_resolucion(
            db_path=db_path,
            year=2023,
            numero=1,
            fecha='2023-01-15',
            referencia='Ejemplo de referencia',
            dictamen='Dictamen de prueba',
            resolucion='Resolución de prueba',
            url_dictamen='http://example.com/dictamen',
            url_resolucion='http://example.com/resolucion'
        ) 