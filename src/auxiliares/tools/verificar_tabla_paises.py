import os
import sys
from pathlib import Path

# Agregar el directorio src al path para poder importar app
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent.parent
sys.path.append(str(src_dir))

from app import create_app, db
from app.models.auxiliares import CodigoPaises
import sqlite3

def verificar_estructura_tabla():
    """
    Verifica la estructura de la tabla CODIGO_PAISES
    """
    # Obtener la ruta de la base de datos
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    db_path = base_dir / 'data' / 'auxiliares.sqlite3'
    
    print(f"Verificando estructura de la tabla CODIGO_PAISES en {db_path}")
    
    if not db_path.exists():
        print(f"ERROR: La base de datos {db_path} no existe.")
        return False
    
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener la información de la tabla
        cursor.execute("PRAGMA table_info(CODIGO_PAISES)")
        columnas = cursor.fetchall()
        
        print("\nEstructura de la tabla CODIGO_PAISES:")
        print("--------------------------------------")
        for col in columnas:
            print(f"Columna: {col[1]}, Tipo: {col[2]}, Not Null: {col[3]}, Primary Key: {col[5]}")
        
        # Verificar el número de registros
        cursor.execute("SELECT COUNT(*) FROM CODIGO_PAISES")
        count = cursor.fetchone()[0]
        print(f"\nNúmero de registros en la tabla: {count}")
        
        # Verificar las primeras filas si hay datos
        if count > 0:
            cursor.execute("SELECT * FROM CODIGO_PAISES LIMIT 5")
            rows = cursor.fetchall()
            
            print("\nPrimeros 5 registros:")
            print("--------------------")
            for row in rows:
                print(row)
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error al verificar la tabla: {e}")
        return False

if __name__ == "__main__":
    verificar_estructura_tabla() 