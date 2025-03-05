#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar metadatos de versiones de bases de datos.

Este script permite registrar información de metadatos en las bases de datos
para que el sistema reconozca las diferentes versiones disponibles.
"""

import os
import sys
import sqlite3
from datetime import datetime
import argparse
from contextlib import closing
from pathlib import Path

def register_version_metadata(db_path, version_date, source_file):
    """
    Registra metadatos de versión en una base de datos
    
    Args:
        db_path: Ruta a la base de datos
        version_date: Fecha de la versión (YYYY-MM-DD)
        source_file: Nombre del archivo fuente
    """
    if not os.path.exists(db_path):
        print(f"Error: La base de datos {db_path} no existe")
        return False
        
    # Verificar si el formato de fecha es correcto (YYYYMMDD)
    try:
        date_obj = datetime.strptime(version_date, '%Y%m%d')
        formatted_date = date_obj.strftime('%Y-%m-%d')
    except ValueError:
        try:
            # Intentar con formato YYYY-MM-DD
            date_obj = datetime.strptime(version_date, '%Y-%m-%d')
            formatted_date = version_date
        except ValueError:
            print(f"Error: Formato de fecha inválido. Debe ser YYYYMMDD o YYYY-MM-DD")
            return False
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Verificar si existe la tabla de metadatos
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='version_metadata'")
            if not cursor.fetchone():
                # Crear la tabla si no existe
                cursor.execute("""
                    CREATE TABLE version_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version_date DATE NOT NULL,
                        source_file TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
            # Insertar o actualizar los metadatos
            cursor.execute("""
                INSERT OR REPLACE INTO version_metadata (version_date, source_file)
                VALUES (?, ?)
            """, (formatted_date, source_file))
            
            conn.commit()
            print(f"Metadatos registrados correctamente en {db_path}")
            return True
            
    except Exception as e:
        print(f"Error al registrar metadatos: {str(e)}")
        return False

def create_latest_symlink(versions_dir):
    """
    Crea o actualiza el enlace simbólico 'latest.sqlite3' apuntando
    a la versión más reciente de la base de datos.
    
    Args:
        versions_dir: Directorio donde se almacenan las versiones de bases de datos
    """
    if not os.path.isdir(versions_dir):
        print(f"Error: El directorio {versions_dir} no existe")
        return False
        
    # Buscar todas las bases de datos de versión
    db_files = [f for f in os.listdir(versions_dir) if f.endswith('.sqlite3') and f != 'latest.sqlite3']
    if not db_files:
        print("No se encontraron bases de datos versionadas")
        return False
        
    # Ordenar por nombre (que contiene la fecha en formato YYYYMMDD)
    db_files.sort(reverse=True)
    latest_db = db_files[0]
    
    # Ruta completa al archivo más reciente
    latest_path = os.path.join(versions_dir, latest_db)
    symlink_path = os.path.join(versions_dir, 'latest.sqlite3')
    
    # Eliminar el enlace simbólico si ya existe
    if os.path.exists(symlink_path):
        if os.path.islink(symlink_path):
            os.unlink(symlink_path)
        else:
            print(f"Error: {symlink_path} existe pero no es un enlace simbólico")
            return False
            
    # Crear el enlace simbólico
    try:
        os.symlink(latest_db, symlink_path)
        print(f"Enlace simbólico 'latest.sqlite3' ahora apunta a {latest_db}")
        return True
    except Exception as e:
        print(f"Error al crear enlace simbólico: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Actualiza metadatos de versiones de bases de datos')
    parser.add_argument('--db', help='Ruta a la base de datos')
    parser.add_argument('--date', help='Fecha de la versión (YYYYMMDD o YYYY-MM-DD)')
    parser.add_argument('--source', help='Nombre del archivo fuente')
    parser.add_argument('--update-symlink', action='store_true', help='Actualizar el enlace simbólico latest.sqlite3')
    
    args = parser.parse_args()
    
    # Directorio de versiones de bases de datos
    versions_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'db_versions')
    
    if args.update_symlink:
        create_latest_symlink(versions_dir)
        return 0
        
    if not args.db or not args.date or not args.source:
        parser.print_help()
        return 1
        
    # Registrar metadatos
    success = register_version_metadata(args.db, args.date, args.source)
    
    # Si se registraron los metadatos correctamente, actualizar el enlace simbólico
    if success:
        create_latest_symlink(versions_dir)
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
