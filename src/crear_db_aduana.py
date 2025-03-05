#!/usr/bin/env python
"""
Script para crear la base de datos aduana.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path para poder importar el módulo aduana
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aduana import crear_base_datos

def main():
    """Función principal para crear la base de datos aduana."""
    # Obtener la ruta absoluta del proyecto
    base_dir = Path(__file__).resolve().parent.parent
    
    # Definir la ruta donde se guardará la base de datos
    db_path = os.path.join(base_dir, 'data', 'aduana', 'aduana.db')
    
    # Crear la base de datos
    exito = crear_base_datos(db_path)
    
    if exito:
        print(f"✅ Base de datos 'aduana' creada exitosamente en: {db_path}")
        print("La tabla 'resoluciones_clasificacion_arancelaria' ha sido creada con las siguientes columnas:")
        print("  - id (clave primaria)")
        print("  - year")
        print("  - numero")
        print("  - fecha")
        print("  - referencia")
        print("  - dictamen")
        print("  - resolucion")
        print("  - created_at")
        print("  - updated_at")
    else:
        print("❌ Error al crear la base de datos. Revise los logs para más información.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 