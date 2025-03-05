#!/usr/bin/env python
"""
Script para consultar las resoluciones de clasificación arancelaria.
"""

import os
import sys
import sqlite3
from pathlib import Path
from tabulate import tabulate
import argparse

def consultar_resoluciones(db_path, year=None, numero=None, limit=10):
    """
    Consulta las resoluciones de clasificación arancelaria.
    
    Args:
        db_path (str): Ruta de la base de datos.
        year (int, opcional): Filtrar por año.
        numero (int, opcional): Filtrar por número.
        limit (int, opcional): Límite de resultados a mostrar.
        
    Returns:
        list: Lista de resoluciones encontradas.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM resoluciones_clasificacion_arancelaria"
        params = []
        
        # Construir la consulta según los filtros
        where_clauses = []
        
        if year is not None:
            where_clauses.append("year = ?")
            params.append(year)
            
        if numero is not None:
            where_clauses.append("numero = ?")
            params.append(numero)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY year DESC, numero DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error al consultar la base de datos: {str(e)}")
        return []

def main():
    """Función principal para consultar resoluciones de clasificación arancelaria."""
    parser = argparse.ArgumentParser(description='Consultar resoluciones de clasificación arancelaria')
    parser.add_argument('--year', type=int, help='Filtrar por año')
    parser.add_argument('--numero', type=int, help='Filtrar por número')
    parser.add_argument('--limit', type=int, default=10, help='Límite de resultados a mostrar')
    
    args = parser.parse_args()
    
    # Obtener la ruta absoluta del proyecto
    base_dir = Path(__file__).resolve().parent.parent
    
    # Definir la ruta de la base de datos
    db_path = os.path.join(base_dir, 'data', 'aduana', 'aduana.db')
    
    # Verificar si la base de datos existe
    if not os.path.exists(db_path):
        print(f"❌ La base de datos no existe en la ruta: {db_path}")
        print("Por favor, ejecute primero el script 'crear_db_aduana.py'")
        return 1
    
    # Consultar las resoluciones
    print("Consultando resoluciones de clasificación arancelaria...")
    resoluciones = consultar_resoluciones(
        db_path=db_path,
        year=args.year,
        numero=args.numero,
        limit=args.limit
    )
    
    if not resoluciones:
        print("No se encontraron resoluciones con los criterios especificados.")
        return 0
    
    # Mostrar los resultados en formato tabular
    headers = ["ID", "Año", "Número", "Fecha", "Referencia", "Dictamen", "Resolución"]
    rows = []
    
    for res in resoluciones:
        # Acortar los textos largos para mejor visualización
        dictamen = res['dictamen'][:50] + '...' if len(res['dictamen']) > 50 else res['dictamen']
        resolucion = res['resolucion'][:50] + '...' if len(res['resolucion']) > 50 else res['resolucion']
        
        rows.append([
            res['id'],
            res['year'],
            res['numero'],
            res['fecha'],
            res['referencia'],
            dictamen,
            resolucion
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(f"\nTotal de resoluciones encontradas: {len(resoluciones)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 