#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script que sincroniza las notas de capítulo entre el Excel y la base de datos versionada.
Este script extrae las notas de capítulo del archivo Excel del Arancel Nacional y las guarda
en la base de datos especificada por la versión.

Uso:
    python sync_chapter_notes.py --version YYYYMMDD --file ruta/al/excel.xlsx
    
Ejemplo:
    python sync_chapter_notes.py --version 202502 --file data/excel/arancel_202502.xlsx
"""

import os
import sys
import re
import argparse
import pandas as pd
import sqlite3
from pathlib import Path
import logging

# Importar el gestor de versiones de BD
from db_version_manager import get_db_path_for_date

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('chapter_notes_sync.log')
    ]
)
logger = logging.getLogger('sync_chapter_notes')

def extract_chapter_notes(file_path):
    """
    Extrae las notas de capítulo del archivo Excel del Arancel Nacional.
    
    Args:
        file_path (str): Ruta al archivo Excel.
        
    Returns:
        dict: Diccionario con las notas de capítulo (clave: número de capítulo, valor: texto).
    """
    if not os.path.exists(file_path):
        logger.error(f"El archivo Excel no existe: {file_path}")
        return {}
        
    logger.info(f"Extrayendo notas de capítulo de {file_path}...")
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path, header=None)
        
        # Diccionario para almacenar las notas por capítulo
        chapter_notes = {}
        
        # Función auxiliar para extraer el contenido completo de un capítulo
        def extract_chapter_content(chapter_num):
            """Extrae el contenido completo de un capítulo específico."""
            pattern = f"Capítulo {int(chapter_num)}"
            start_row = -1
            
            # Buscar el inicio del capítulo
            for i, row in df.iterrows():
                row_text = ""
                for cell in row:
                    if pd.notna(cell):
                        row_text += str(cell) + " "
                row_text = row_text.strip()
                
                if pattern in row_text:
                    start_row = i
                    break
            
            if start_row == -1:
                logger.warning(f"No se encontró el capítulo {chapter_num}")
                return None
            
            # Buscar el final del capítulo (inicio del próximo capítulo o fin del archivo)
            end_row = len(df)
            for i in range(start_row + 1, len(df)):
                cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
                if re.match(r'^Capítulo\s+\d+', cell_value) and pattern not in cell_value:
                    end_row = i
                    break
            
            # Extraer todo el contenido entre el inicio y el final del capítulo
            content = []
            capturing_notes = False
            reached_ncm_codes = False
            
            for i in range(start_row, end_row):
                row_text = ""
                for cell in df.iloc[i]:
                    if pd.notna(cell):
                        row_text += str(cell) + " "
                row_text = row_text.strip()
                
                # Si llegamos a los códigos NCM, detenemos la captura (fin de las notas)
                if re.match(r'^\d{2}\.\d{2}', row_text) or re.match(r'^\d{4}', row_text):
                    reached_ncm_codes = True
                
                # Si aún no llegamos a los códigos NCM, seguimos capturando
                if not reached_ncm_codes:
                    # Si es una línea no vacía, la capturamos
                    if row_text.strip():
                        content.append(row_text)
                    # Si encontramos "Notas" o "Nota", marcamos que estamos capturando notas
                    if "Nota" in row_text:
                        capturing_notes = True
            
            # Verificar que capturamos notas válidas
            if not capturing_notes or not content:
                logger.warning(f"No se encontraron notas válidas para el capítulo {chapter_num}")
                return None
                
            return "\n".join(content) if content else None
        
        # Extraer notas para cada capítulo del 1 al 97
        for chapter in range(1, 98):
            chapter_num = f"{chapter:02d}"
            content = extract_chapter_content(chapter_num)
            if content:
                chapter_notes[chapter_num] = content
                logger.info(f"Procesado capítulo {chapter_num}: {len(content.split('\n'))} líneas")
        
        # Mostrar estadísticas
        logger.info(f"Se encontraron notas para {len(chapter_notes)} capítulos")
        
        return chapter_notes
        
    except Exception as e:
        logger.error(f"Error al extraer notas de capítulo: {e}")
        return {}

def update_chapter_notes_in_db(chapter_notes, db_path, dry_run=False):
    """
    Actualiza las notas de capítulo en la base de datos.
    
    Args:
        chapter_notes (dict): Diccionario con las notas de capítulo.
        db_path (str): Ruta a la base de datos.
        dry_run (bool): Si es True, solo muestra los cambios sin aplicarlos.
    """
    if not chapter_notes:
        logger.error("No hay datos de capítulos para actualizar")
        return
    
    logger.info(f"Actualizando {len(chapter_notes)} capítulos en la base de datos {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chapter_notes'")
        if not cursor.fetchone():
            # Crear la tabla si no existe
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapter_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_number VARCHAR(2) NOT NULL UNIQUE,
                note_text TEXT NOT NULL
            )
            """)
            logger.info(f"Tabla chapter_notes creada en {db_path}")
        
        # Contadores para estadísticas
        created = 0
        updated = 0
        unchanged = 0
        
        if not dry_run:
            # Actualizar cada capítulo
            for chapter_num, note_text in chapter_notes.items():
                # Verificar si ya existe
                cursor.execute("SELECT id, note_text FROM chapter_notes WHERE chapter_number = ?", (chapter_num,))
                result = cursor.fetchone()
                
                if result:
                    # Ya existe, verificar si hay cambios
                    if result[1] != note_text:
                        cursor.execute("UPDATE chapter_notes SET note_text = ? WHERE chapter_number = ?", 
                                      (note_text, chapter_num))
                        updated += 1
                        logger.info(f"Actualizado capítulo {chapter_num}")
                    else:
                        unchanged += 1
                        logger.info(f"Sin cambios en capítulo {chapter_num}")
                else:
                    # Crear nuevo
                    cursor.execute("INSERT INTO chapter_notes (chapter_number, note_text) VALUES (?, ?)", 
                                  (chapter_num, note_text))
                    created += 1
                    logger.info(f"Creado capítulo {chapter_num}")
            
            # Guardar cambios
            conn.commit()
            
        else:
            # Modo simulación
            logger.info("Modo simulación (dry run) - No se aplicarán cambios")
            
            # Verificar cada capítulo
            for chapter_num, note_text in chapter_notes.items():
                cursor.execute("SELECT id, note_text FROM chapter_notes WHERE chapter_number = ?", (chapter_num,))
                result = cursor.fetchone()
                
                if result:
                    if result[1] != note_text:
                        logger.info(f"[SIMULACIÓN] Se actualizaría el capítulo {chapter_num}")
                        updated += 1
                    else:
                        logger.info(f"[SIMULACIÓN] Sin cambios en capítulo {chapter_num}")
                        unchanged += 1
                else:
                    logger.info(f"[SIMULACIÓN] Se crearía el capítulo {chapter_num}")
                    created += 1
        
        # Estadísticas finales
        logger.info(f"Resumen: {created} capítulos nuevos, {updated} actualizados, {unchanged} sin cambios")
        
        # Cerrar conexión
        conn.close()
        
    except Exception as e:
        logger.error(f"Error al actualizar la base de datos: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Sincronizar notas de capítulo entre Excel y base de datos')
    parser.add_argument('--version', required=True, help='Versión de la base de datos (formato YYYYMMDD)')
    parser.add_argument('--file', required=True, help='Ruta al archivo Excel del Arancel')
    parser.add_argument('--dry-run', action='store_true', help='Ejecutar en modo simulación sin aplicar cambios')
    
    args = parser.parse_args()
    
    # Verificar que el archivo Excel existe
    excel_path = os.path.abspath(args.file)
    if not os.path.exists(excel_path):
        logger.error(f"El archivo Excel no existe: {excel_path}")
        return 1
    
    # Construir la ruta a la base de datos para la versión especificada
    try:
        # Construir directamente la ruta a la base de datos
        base_dir = Path(__file__).resolve().parent.parent
        db_path = str(base_dir / 'data' / 'db_versions' / f'arancel_{args.version}.sqlite3')
        
        if not os.path.exists(db_path):
            logger.error(f"No se encontró la base de datos: {db_path}")
            return 1
            
        logger.info(f"Base de datos encontrada: {db_path}")
    except Exception as e:
        logger.error(f"Error al obtener la ruta de la base de datos: {e}")
        return 1
    
    # Extraer notas de capítulo del Excel
    chapter_notes = extract_chapter_notes(excel_path)
    
    if not chapter_notes:
        logger.error("No se pudieron extraer notas de capítulo del Excel")
        return 1
    
    # Actualizar las notas en la base de datos
    update_chapter_notes_in_db(chapter_notes, db_path, args.dry_run)
    
    logger.info("Proceso completado")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 