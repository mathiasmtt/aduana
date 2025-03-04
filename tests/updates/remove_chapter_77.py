#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar el registro del capítulo 77 de la base de datos.
"""

import sqlite3
import os
import glob

# Directorio de bases de datos
DB_VERSIONS_DIR = '/Users/mat/Code/aduana/data/db_versions'
MAIN_DB = '/Users/mat/Code/aduana/data/database.sqlite3'

def remove_chapter_77(db_path):
    """Elimina el registro del capítulo 77 de la base de datos."""
    try:
        # Verificar si la base de datos existe
        if not os.path.exists(db_path):
            print(f"La base de datos {db_path} no existe")
            return False
        
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Eliminar el registro del capítulo 77
        cursor.execute("DELETE FROM arancel_nacional WHERE CHAPTER = '77 - Reservado para uso futuro'")
        
        # Guardar los cambios
        conn.commit()
        
        print(f"Registro del capítulo 77 eliminado de {db_path}")
        conn.close()
        return True
            
    except Exception as e:
        print(f"Error al eliminar el capítulo 77 de {db_path}: {str(e)}")
        return False

def main():
    # Eliminar el capítulo 77 de la base de datos principal
    remove_chapter_77(MAIN_DB)
    
    # Eliminar el capítulo 77 de todas las bases de datos versionadas
    for db_file in glob.glob(os.path.join(DB_VERSIONS_DIR, "*.sqlite3")):
        if os.path.basename(db_file) not in ['latest.sqlite3', 'arancel_latest.sqlite3']:
            remove_chapter_77(db_file)

if __name__ == "__main__":
    main()
