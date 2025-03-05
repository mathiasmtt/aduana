#!/usr/bin/env python
"""
Script para agregar ejemplos de resoluciones a la base de datos aduana.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path para poder importar el módulo aduana
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aduana.db_init import agregar_resolucion

def main():
    """Función principal para agregar ejemplos a la base de datos aduana."""
    # Obtener la ruta absoluta del proyecto
    base_dir = Path(__file__).resolve().parent.parent
    
    # Definir la ruta donde se guardará la base de datos
    db_path = os.path.join(base_dir, 'data', 'aduana', 'aduana.db')
    
    # Ejemplos de resoluciones
    ejemplos = [
        {
            'year': 2023,
            'numero': 1,
            'fecha': '2023-01-15',
            'referencia': 'Clasificación de equipos médicos',
            'dictamen': 'Se recomienda clasificar en la posición 9018.90',
            'resolucion': 'Se clasifica en la posición arancelaria 9018.90.99'
        },
        {
            'year': 2023,
            'numero': 2,
            'fecha': '2023-02-22',
            'referencia': 'Clasificación de productos alimenticios',
            'dictamen': 'Se recomienda clasificar en la posición 2106.90',
            'resolucion': 'Se clasifica en la posición arancelaria 2106.90.30'
        },
        {
            'year': 2023,
            'numero': 3,
            'fecha': '2023-03-10',
            'referencia': 'Clasificación de textiles',
            'dictamen': 'Se recomienda clasificar en la posición 6204.43',
            'resolucion': 'Se clasifica en la posición arancelaria 6204.43.00'
        },
        {
            'year': 2024,
            'numero': 1,
            'fecha': '2024-01-05',
            'referencia': 'Clasificación de productos electrónicos',
            'dictamen': 'Se recomienda clasificar en la posición 8517.62',
            'resolucion': 'Se clasifica en la posición arancelaria 8517.62.59'
        },
        {
            'year': 2024,
            'numero': 2,
            'fecha': '2024-02-18',
            'referencia': 'Clasificación de productos químicos',
            'dictamen': 'Se recomienda clasificar en la posición 2933.99',
            'resolucion': 'Se clasifica en la posición arancelaria 2933.99.99'
        }
    ]
    
    # Agregar cada ejemplo a la base de datos
    print(f"Agregando {len(ejemplos)} ejemplos a la base de datos...")
    
    for ejemplo in ejemplos:
        result = agregar_resolucion(
            db_path=db_path,
            year=ejemplo['year'],
            numero=ejemplo['numero'],
            fecha=ejemplo['fecha'],
            referencia=ejemplo['referencia'],
            dictamen=ejemplo['dictamen'],
            resolucion=ejemplo['resolucion']
        )
        
        if result > 0:
            print(f"✅ Resolución {ejemplo['year']}/{ejemplo['numero']} agregada exitosamente (ID: {result})")
        else:
            print(f"❌ Error al agregar resolución {ejemplo['year']}/{ejemplo['numero']}")
    
    print("\n¡Ejemplos agregados exitosamente!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 