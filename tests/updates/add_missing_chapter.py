#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para añadir el capítulo 77 (reservado) a la base de datos.
"""

import sqlite3
import os
import glob
from pathlib import Path

# Directorio de bases de datos
DB_VERSIONS_DIR = '/Users/mat/Code/aduana/data/db_versions'
MAIN_DB = '/Users/mat/Code/aduana/data/database.sqlite3'

def add_chapter_77(db_path):
    """
    Añade un registro para el capítulo 77 (reservado) a la base de datos.
    
    Args:
        db_path: Ruta a la base de datos
    
    Returns:
        True si se añadió correctamente, False en caso de error
    """
    try:
        # Verificar si la base de datos existe
        if not os.path.exists(db_path):
            print(f"La base de datos {db_path} no existe")
            return False
        
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si el capítulo 77 ya existe
        cursor.execute("SELECT COUNT(*) FROM arancel_nacional WHERE CHAPTER = '77 - Reservado para uso futuro'")
        if cursor.fetchone()[0] > 0:
            print(f"El capítulo 77 ya existe en {db_path}")
            conn.close()
            return True
            
        # Añadir el registro para el capítulo 77
        cursor.execute("""
            INSERT INTO arancel_nacional (NCM, DESCRIPCION, CHAPTER, SECTION)
            VALUES ('7700.00.00.00', 'Capítulo reservado para uso futuro', '77 - Reservado para uso futuro', 'XV - Metales comunes y sus manufacturas')
        """)
        
        # Guardar los cambios
        conn.commit()
        
        # Verificar que se haya añadido correctamente
        cursor.execute("SELECT COUNT(*) FROM arancel_nacional WHERE CHAPTER = '77 - Reservado para uso futuro'")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        if count > 0:
            print(f"Capítulo 77 añadido correctamente a {db_path}")
            return True
        else:
            print(f"No se pudo añadir el capítulo 77 a {db_path}")
            return False
            
    except Exception as e:
        print(f"Error al añadir el capítulo 77 a {db_path}: {str(e)}")
        return False

def main():
    # Añadir el capítulo 77 a la base de datos principal
    add_chapter_77(MAIN_DB)
    
    # Añadir el capítulo 77 a todas las bases de datos versionadas
    for db_file in glob.glob(os.path.join(DB_VERSIONS_DIR, "*.sqlite3")):
        if os.path.basename(db_file) not in ['latest.sqlite3', 'arancel_latest.sqlite3']:
            add_chapter_77(db_file)

if __name__ == "__main__":
    main()
