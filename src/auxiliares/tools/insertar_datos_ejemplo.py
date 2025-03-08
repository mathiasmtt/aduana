import os
import sys
from pathlib import Path
import sqlite3

# Agregar el directorio src al path para poder importar app
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent.parent
sys.path.append(str(src_dir))

# Datos de ejemplo de países
DATOS_EJEMPLO = [
    {"codigo_num": "032", "nombre": "Argentina", "codigo_letras": "ARG"},
    {"codigo_num": "076", "nombre": "Brasil", "codigo_letras": "BRA"},
    {"codigo_num": "152", "nombre": "Chile", "codigo_letras": "CHL"},
    {"codigo_num": "218", "nombre": "Ecuador", "codigo_letras": "ECU"},
    {"codigo_num": "600", "nombre": "Paraguay", "codigo_letras": "PRY"},
    {"codigo_num": "604", "nombre": "Perú", "codigo_letras": "PER"},
    {"codigo_num": "858", "nombre": "Uruguay", "codigo_letras": "URY"},
    {"codigo_num": "862", "nombre": "Venezuela", "codigo_letras": "VEN"},
    {"codigo_num": "484", "nombre": "México", "codigo_letras": "MEX"},
    {"codigo_num": "068", "nombre": "Bolivia", "codigo_letras": "BOL"},
    {"codigo_num": "170", "nombre": "Colombia", "codigo_letras": "COL"},
    {"codigo_num": "188", "nombre": "Costa Rica", "codigo_letras": "CRI"},
    {"codigo_num": "214", "nombre": "República Dominicana", "codigo_letras": "DOM"},
    {"codigo_num": "222", "nombre": "El Salvador", "codigo_letras": "SLV"},
    {"codigo_num": "320", "nombre": "Guatemala", "codigo_letras": "GTM"},
    {"codigo_num": "340", "nombre": "Honduras", "codigo_letras": "HND"},
    {"codigo_num": "558", "nombre": "Nicaragua", "codigo_letras": "NIC"},
    {"codigo_num": "591", "nombre": "Panamá", "codigo_letras": "PAN"},
    {"codigo_num": "840", "nombre": "Estados Unidos", "codigo_letras": "USA"},
    {"codigo_num": "124", "nombre": "Canadá", "codigo_letras": "CAN"}
]

def insertar_datos_ejemplo():
    """
    Inserta datos de ejemplo en la tabla CODIGO_PAISES usando SQLite directamente
    """
    print("Insertando datos de ejemplo en la tabla CODIGO_PAISES...")
    
    # Obtener la ruta de la base de datos
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    db_path = base_dir / 'data' / 'auxiliares.sqlite3'
    
    if not db_path.exists():
        print(f"ERROR: La base de datos {db_path} no existe.")
        return
    
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Eliminar registros existentes
        cursor.execute("DELETE FROM CODIGO_PAISES")
        
        # Insertar nuevos registros
        for pais in DATOS_EJEMPLO:
            # Asegurar que codigo_num siempre tenga 3 dígitos
            codigo_num = pais['codigo_num'].zfill(3)
            
            # Verificar que no exceda los 3 dígitos
            if len(codigo_num) > 3:
                print(f"Advertencia: El código numérico '{codigo_num}' excede los 3 dígitos. Se usarán los últimos 3.")
                codigo_num = codigo_num[-3:]
            
            cursor.execute(
                "INSERT INTO CODIGO_PAISES (codigo_num, nombre, codigo_letras) VALUES (?, ?, ?)",
                (codigo_num, pais['nombre'], pais['codigo_letras'])
            )
        
        # Guardar cambios
        conn.commit()
        
        # Verificar cuántos registros se insertaron
        cursor.execute("SELECT COUNT(*) FROM CODIGO_PAISES")
        count = cursor.fetchone()[0]
        print(f"Se han insertado {count} códigos de países.")
        
        conn.close()
    
    except Exception as e:
        print(f"Error al insertar datos: {e}")

if __name__ == "__main__":
    insertar_datos_ejemplo() 