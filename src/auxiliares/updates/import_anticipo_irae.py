#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para importar datos del Excel ANTICIPO_IRAE.xlsx a la base de datos auxiliares.sqlite3
"""

import os
import sys
import sqlite3
import pandas as pd
from pathlib import Path
from contextlib import closing

def import_anticipo_irae():
    """
    Importa datos del archivo Excel ANTICIPO_IRAE.xlsx a la tabla ANTICIPO_IRAE 
    en la base de datos auxiliares.sqlite3
    """
    # Configurar paths
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    excel_path = base_dir / 'data' / 'excel' / 'ANTICIPO_IRAE.xlsx'
    db_path = base_dir / 'data' / 'auxiliares.sqlite3'
    
    print(f"Importando datos desde {excel_path} a {db_path}")
    
    if not excel_path.exists():
        print(f"ERROR: El archivo Excel {excel_path} no existe.")
        return False
    
    if not db_path.exists():
        print(f"ERROR: La base de datos {db_path} no existe.")
        return False
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(excel_path)
        
        # Mostrar información sobre los datos importados
        print(f"Datos importados: {len(df)} filas y {len(df.columns)} columnas")
        print("Columnas encontradas:")
        for col in df.columns:
            print(f"  - {col}")
        
        # Conectar a la base de datos SQLite
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            
            # Crear tabla ANTICIPO_IRAE si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ANTICIPO_IRAE (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    NCM TEXT NOT NULL,
                    ANTICIPO_PORCENTAJE REAL,
                    DTO_230_009 INTEGER,
                    DTO_110_012 INTEGER,
                    DTO_141_012 INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Eliminar registros existentes
            cursor.execute("DELETE FROM ANTICIPO_IRAE")
            
            # Renombrar columnas si es necesario para que coincidan con la estructura de la tabla
            column_mapping = {
                'NCM': 'NCM',
                'ANTICIPO %': 'ANTICIPO_PORCENTAJE',
                'DTO 230/009': 'DTO_230_009',
                'DTO 110/012': 'DTO_110_012', 
                'DTO 141/012': 'DTO_141_012'
            }
            
            df_renamed = df.rename(columns=column_mapping)
            
            # Convertir las columnas DTO a 1/0 (booleano)
            for dto_col in ['DTO_230_009', 'DTO_110_012', 'DTO_141_012']:
                if dto_col in df_renamed.columns:
                    # Convertir valores no nulos a 1, nulos a 0
                    df_renamed[dto_col] = df_renamed[dto_col].notna().astype(int)
            
            # Insertar datos en la tabla
            for index, row in df_renamed.iterrows():
                cursor.execute("""
                    INSERT INTO ANTICIPO_IRAE (
                        NCM, 
                        ANTICIPO_PORCENTAJE, 
                        DTO_230_009, 
                        DTO_110_012, 
                        DTO_141_012
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    row['NCM'],
                    row['ANTICIPO_PORCENTAJE'],
                    row['DTO_230_009'] if 'DTO_230_009' in row else 0,
                    row['DTO_110_012'] if 'DTO_110_012' in row else 0,
                    row['DTO_141_012'] if 'DTO_141_012' in row else 0
                ))
            
            # Guardar cambios
            conn.commit()
            
            # Verificar cuántos registros se insertaron
            cursor.execute("SELECT COUNT(*) FROM ANTICIPO_IRAE")
            count = cursor.fetchone()[0]
            print(f"Se han insertado {count} registros en la tabla ANTICIPO_IRAE.")
            
            return True
    
    except Exception as e:
        print(f"Error al importar datos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import_anticipo_irae() 