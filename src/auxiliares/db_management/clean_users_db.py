#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import get_app
import os
import sqlite3
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def clean_users_db():
    """Elimina todas las tablas no deseadas en la base de datos de usuarios."""
    app = get_app()
    
    # Obtener la ruta de la base de datos de usuarios
    with app.app_context():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        db_path = db_uri.replace('sqlite:///', '')
        
        # Verificar si existe la base de datos
        if not os.path.exists(db_path):
            logging.error(f"La base de datos no existe: {db_path}")
            return
        
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener lista de todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Mostrar las tablas actuales
        logging.info("Tablas actuales en la base de datos:")
        for table in tables:
            logging.info(f"- {table[0]}")
        
        # Eliminar todas las tablas excepto 'users'
        tables_to_drop = [table[0] for table in tables if table[0] != 'users' and table[0] != 'sqlite_sequence']
        
        if tables_to_drop:
            logging.info("Eliminando las siguientes tablas:")
            for table in tables_to_drop:
                logging.info(f"- {table}")
                cursor.execute(f"DROP TABLE IF EXISTS {table};")
            
            # Guardar cambios
            conn.commit()
            logging.info("Tablas eliminadas correctamente.")
        else:
            logging.info("No hay tablas adicionales para eliminar.")
        
        # Verificar las tablas restantes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        remaining_tables = cursor.fetchall()
        
        logging.info("Tablas restantes en la base de datos:")
        for table in remaining_tables:
            logging.info(f"- {table[0]}")
        
        # Cerrar conexión
        conn.close()

def main():
    """Punto de entrada principal para el script."""
    clean_users_db()

if __name__ == '__main__':
    main() 