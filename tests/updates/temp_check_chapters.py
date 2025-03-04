#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar los capítulos en la base de datos.
"""

import sqlite3
import os

# Ruta a la base de datos
DB_PATH = '/Users/mat/Code/aduana/data/db_versions/20250201.sqlite3'

def check_chapters():
    """Verifica los capítulos presentes en la base de datos."""
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Consultar los capítulos distintos
        cursor.execute('SELECT DISTINCT CHAPTER FROM arancel_nacional ORDER BY CHAPTER')
        chapters = cursor.fetchall()
        
        # Mostrar estadísticas
        print(f'Total de capítulos distintos: {len(chapters)}')
        
        # Mostrar los primeros capítulos
        print('\nPrimeros 10 capítulos:')
        for i in range(min(10, len(chapters))):
            print(chapters[i])
        
        # Mostrar los últimos capítulos
        print('\nÚltimos 10 capítulos:')
        for i in range(max(0, len(chapters)-10), len(chapters)):
            print(chapters[i])
            
        # Verificar si hay capítulos faltantes
        all_chapters = set(range(1, 98))  # Capítulos del 1 al 97
        existing_chapters = set()
        
        for chapter_tuple in chapters:
            chapter_str = chapter_tuple[0]
            # Intentar extraer el número de capítulo
            try:
                # Si el formato es "XX - Descripción"
                if ' - ' in chapter_str:
                    chapter_num = int(chapter_str.split(' - ')[0])
                # Si es solo el número
                else:
                    chapter_num = int(chapter_str)
                existing_chapters.add(chapter_num)
            except (ValueError, TypeError, IndexError):
                print(f"No se pudo extraer el número de capítulo de: {chapter_str}")
        
        # Encontrar capítulos faltantes
        missing_chapters = all_chapters - existing_chapters
        if missing_chapters:
            print("\nCapítulos faltantes:")
            for chapter in sorted(missing_chapters):
                print(f"Capítulo {chapter}")
        else:
            print("\nNo faltan capítulos (1-97)")
            
        # Cerrar la conexión
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_chapters()
