#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para examinar la estructura de una base de datos SQLite y
mostrar información sobre sus tablas y columnas.
"""

import os
import sys
import sqlite3
from contextlib import closing

def examinar_db(db_path):
    """
    Examina la estructura de una base de datos SQLite
    
    Args:
        db_path: Ruta a la base de datos SQLite
    """
    if not os.path.exists(db_path):
        print(f"Error: La base de datos {db_path} no existe.")
        return
    
    try:
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Obtener lista de tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = cursor.fetchall()
            
            print(f"\nExaminando base de datos: {db_path}")
            print(f"\nTablas encontradas ({len(tablas)}):")
            for i, (tabla,) in enumerate(tablas, 1):
                print(f"{i}. {tabla}")
            
            # Examinar cada tabla
            for (tabla,) in tablas:
                print(f"\n{'='*40}")
                print(f"Tabla: {tabla}")
                print(f"{'='*40}")
                
                # Obtener estructura de la tabla
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas = cursor.fetchall()
                
                print("\nEstructura de la tabla:")
                print("ID | Nombre | Tipo | NotNull | Default | PK")
                print("-" * 60)
                for col in columnas:
                    print(" | ".join(str(c) for c in col))
                
                # Mostrar primeras filas
                try:
                    cursor.execute(f"SELECT * FROM {tabla} LIMIT 5")
                    filas = cursor.fetchall()
                    
                    if filas:
                        print("\nPrimeras 5 filas:")
                        # Obtener nombres de columnas
                        nombres_columnas = [col[1] for col in columnas]
                        print(" | ".join(nombres_columnas))
                        print("-" * 80)
                        
                        for fila in filas:
                            print(" | ".join(str(c) if c is not None else "NULL" for c in fila))
                    else:
                        print("\nLa tabla está vacía.")
                except Exception as e:
                    print(f"\nError al consultar datos: {e}")
                
                # Contar registros
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    count = cursor.fetchone()[0]
                    print(f"\nTotal de registros: {count}")
                except Exception as e:
                    print(f"\nError al contar registros: {e}")
                
                # Buscar columnas relevantes para AEC
                print("\nBuscando columnas relevantes:")
                for col in columnas:
                    col_name = col[1].lower()
                    if "ncm" in col_name or "codigo" in col_name:
                        print(f"  - Posible columna NCM: {col[1]}")
                    elif "aec" in col_name or "arancel" in col_name:
                        print(f"  - Posible columna AEC: {col[1]}")
    
    except Exception as e:
        print(f"Error al examinar la base de datos: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python examinar_db.py ruta_a_la_base_de_datos.sqlite3")
        return 1
    
    db_path = sys.argv[1]
    examinar_db(db_path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
