#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para procesar un archivo Excel del Arancel y cargarlo a una versión de base de datos.
Este script maneja el formato específico del Arancel Nacional y lo convierte al formato 
requerido por el sistema.
"""

import os
import sys
import pandas as pd
import numpy as np
import re
import datetime
import sqlite3
from pathlib import Path
import logging
from tqdm import tqdm
from contextlib import closing

# Añadir rutas para importar módulos del proyecto
sys.path.append('/Users/mat/Code/aduana')
sys.path.append('/Users/mat/Code/aduana/src')

# Importar el gestor de versiones
from src.db_version_manager import create_new_version_db, get_db_path_for_date, update_latest_symlink

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('procesar_excel_y_cargar')

def procesar_excel_arancel(file_path, sheet_name=None):
    """
    Procesa un archivo Excel del Arancel Nacional para extraer los datos de NCM
    
    Args:
        file_path: Ruta al archivo Excel
        sheet_name: Nombre de la hoja (opcional)
        
    Returns:
        DataFrame con los datos procesados y estructurados
    """
    logger.info(f"Procesando archivo: {file_path}")
    
    try:
        # Leer el archivo Excel
        if sheet_name:
            df_raw = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df_raw = pd.read_excel(file_path)
        
        # Verificar si el archivo tiene el formato esperado
        if df_raw.shape[1] < 7:
            logger.warning(f"El archivo parece tener un formato inusual: {df_raw.shape[1]} columnas")
        
        # Convertir todos los datos a texto para facilitar el procesamiento
        df_raw = df_raw.astype(str)
        
        # Extraer NCM y descripciones
        data = []
        current_section = None
        current_chapter = None
        
        # Patrones para detectar estructuras
        ncm_pattern = re.compile(r'^(\d{2,4}\.\d{2}|\d{4}\.\d{2}\.\d{2})(\.\d{2})?$')
        section_pattern = re.compile(r'^Sección ([IVX]+)')
        chapter_pattern = re.compile(r'^Capítulo (\d{1,2})')
        
        # Procesar cada fila
        for idx, row in df_raw.iterrows():
            row_values = row.values
            
            # Obtener el valor de la primera columna (la que generalmente tiene los códigos NCM o títulos)
            first_col = str(row_values[0]).strip() if row_values.size > 0 else ""
            
            # Buscar secciones
            section_match = section_pattern.search(first_col)
            if section_match:
                current_section = section_match.group(1)
                continue
            
            # Buscar capítulos
            chapter_match = chapter_pattern.search(first_col)
            if chapter_match:
                current_chapter = chapter_match.group(1).zfill(2)  # Añadir ceros a la izquierda
                continue
            
            # Buscar códigos NCM
            ncm_match = ncm_pattern.match(first_col)
            if ncm_match:
                ncm_code = first_col.replace('.', '')
                
                # Asegurar que el NCM tenga el formato correcto
                if len(ncm_code) < 8:
                    continue  # Ignorar códigos NCM mal formados
                
                # Obtener la descripción (segunda columna si hay más de una)
                description = str(row_values[1]).strip() if row_values.size > 1 else ""
                
                # Extraer los valores de aranceles de otras columnas si están disponibles
                aec = None
                ez = None
                iz = None
                cl = None
                uvf = None
                
                # Típicamente la tercera columna es AEC, cuarta E/Z, quinta I/Z, etc.
                if row_values.size > 2:
                    try:
                        aec_val = str(row_values[2]).strip()
                        aec = float(aec_val.replace('%', '').strip()) if aec_val and aec_val.lower() != 'nan' else None
                    except:
                        pass
                    
                if row_values.size > 3:
                    try:
                        ez_val = str(row_values[3]).strip()
                        ez = float(ez_val.replace('%', '').strip()) if ez_val and ez_val.lower() != 'nan' else None
                    except:
                        pass
                
                if row_values.size > 4:
                    try:
                        iz_val = str(row_values[4]).strip()
                        iz = float(iz_val.replace('%', '').strip()) if iz_val and iz_val.lower() != 'nan' else None
                    except:
                        pass
                
                if row_values.size > 5:
                    cl = str(row_values[5]).strip() if str(row_values[5]).lower() != 'nan' else None
                
                if row_values.size > 6:
                    try:
                        uvf_val = str(row_values[6]).strip()
                        uvf = float(uvf_val.replace('$', '').strip()) if uvf_val and uvf_val.lower() != 'nan' else None
                    except:
                        pass
                
                # Añadir datos estructurados
                data.append({
                    'NCM': ncm_code,
                    'DESCRIPCION': description,
                    'AEC': aec,
                    'E/Z': ez,
                    'I/Z': iz,
                    'CL': cl,
                    'UVF': uvf,
                    'SECTION': current_section,
                    'CHAPTER': current_chapter
                })
        
        # Crear DataFrame con los datos extraídos
        df_processed = pd.DataFrame(data)
        
        logger.info(f"Se procesaron {len(df_processed)} registros NCM del archivo")
        return df_processed
    
    except Exception as e:
        logger.error(f"Error al procesar el archivo Excel: {e}")
        return None

def cargar_a_base_de_datos(df, version_date):
    """
    Carga los datos procesados a una nueva base de datos versionada
    
    Args:
        df: DataFrame con los datos procesados
        version_date: Fecha de la versión en formato YYYY-MM-DD
        
    Returns:
        Ruta a la base de datos creada o None si falló
    """
    if df is None or df.empty:
        logger.error("No hay datos para cargar a la base de datos")
        return None
    
    try:
        # Crear nueva base de datos para esta versión
        fecha_obj = datetime.datetime.strptime(version_date, '%Y-%m-%d')
        source_name = f"Procesado automáticamente: {datetime.datetime.now()}"
        
        db_path = create_new_version_db(fecha_obj, source_name)
        if not db_path:
            logger.error("No se pudo crear la base de datos para la versión")
            return None
        
        logger.info(f"Base de datos creada: {db_path}")
        
        # Conectar a la base de datos y guardar los datos
        with closing(sqlite3.connect(db_path)) as conn:
            # Crear tabla arancel_nacional si no existe
            conn.execute("""
                CREATE TABLE IF NOT EXISTS arancel_nacional (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    NCM TEXT,
                    DESCRIPCION TEXT,
                    AEC REAL,
                    "E/Z" REAL,
                    "I/Z" REAL,
                    CL TEXT,
                    UVF REAL,
                    SECTION TEXT,
                    CHAPTER TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Crear tabla ncm_versions si no existe
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ncm_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ncm_code TEXT,
                    description TEXT,
                    aec REAL,
                    ez REAL,
                    iz REAL,
                    uvf REAL,
                    cl TEXT,
                    source_file TEXT,
                    version_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insertar datos en la tabla arancel_nacional
            df.to_sql('arancel_nacional', conn, if_exists='append', index=False)
            
            # Insertar datos en la tabla ncm_versions con mapeo de columnas
            df_versions = df.copy()
            df_versions = df_versions.rename(columns={
                'NCM': 'ncm_code',
                'DESCRIPCION': 'description',
                'AEC': 'aec',
                'E/Z': 'ez',
                'I/Z': 'iz',
                'UVF': 'uvf',
                'CL': 'cl'
            })
            df_versions['source_file'] = source_name
            df_versions['version_date'] = version_date
            
            # Seleccionar solo las columnas necesarias
            columns_to_use = ['ncm_code', 'description', 'aec', 'ez', 'iz', 'uvf', 'cl', 'source_file', 'version_date']
            df_versions = df_versions[columns_to_use]
            
            df_versions.to_sql('ncm_versions', conn, if_exists='append', index=False)
            
            conn.commit()
            
        # Actualizar el enlace simbólico a la última versión
        update_latest_symlink()
        
        logger.info(f"Datos cargados exitosamente en la base de datos {db_path}")
        return db_path
    
    except Exception as e:
        logger.error(f"Error al cargar datos a la base de datos: {e}")
        return None

def main():
    """Función principal"""
    if len(sys.argv) < 3:
        print("Uso: python procesar_excel_y_cargar.py <ruta_excel> <fecha_version>")
        print("Ejemplo: python procesar_excel_y_cargar.py data/excel/arancel_202502.xlsx 2025-02-01")
        return 1
    
    file_path = sys.argv[1]
    version_date = sys.argv[2]
    
    if not os.path.exists(file_path):
        logger.error(f"El archivo {file_path} no existe")
        return 1
    
    # Procesar el archivo Excel
    df = procesar_excel_arancel(file_path)
    if df is None:
        return 1
    
    # Cargar a la base de datos
    db_path = cargar_a_base_de_datos(df, version_date)
    if db_path:
        logger.info(f"Proceso completado. Base de datos creada en {db_path}")
        return 0
    else:
        logger.error("El proceso de carga falló")
        return 1

if __name__ == "__main__":
    sys.exit(main())
