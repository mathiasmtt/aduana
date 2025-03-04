#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para cargar datos de NCM a una base de datos específica por versión.
Este script crea una nueva base de datos para cada archivo de arancel cargado,
permitiendo tener un registro histórico separado.
"""

import os
import sys
import argparse
import datetime
import pandas as pd
import sqlite3
from pathlib import Path
import logging
from tqdm import tqdm

# Importar el gestor de versiones
from db_version_manager import create_new_version_db, get_db_path_for_date

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('load_version_db')

def extract_ncm_from_excel(file_path, sheet_name=None):
    """
    Extrae datos de NCM desde un archivo Excel
    
    Args:
        file_path: Ruta al archivo Excel
        sheet_name: Nombre de la hoja (opcional)
        
    Returns:
        DataFrame con los datos del NCM
    """
    logger.info(f"Leyendo archivo: {file_path}")
    
    try:
        # Determinar las hojas disponibles
        if sheet_name:
            xls = pd.ExcelFile(file_path)
            if sheet_name not in xls.sheet_names:
                logger.warning(f"La hoja '{sheet_name}' no existe en el archivo. Hojas disponibles: {xls.sheet_names}")
                sheet_name = None  # Resetear para usar la primera hoja
        
        # Leer el archivo Excel
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)
        
        # Detectar y renombrar columnas
        rename_map = {}
        original_columns = df.columns.tolist()
        
        # Mapeo de posibles nombres para cada columna estándar
        column_aliases = {
            'NCM': ['NCM', 'CÓDIGO', 'CODIGO', 'CODE', 'CÓDIGO NCM', 'CODIGO NCM'],
            'DESCRIPCION': ['DESCRIPCION', 'DESCRIPCIÓN', 'DESCRIPTION', 'TEXTO', 'MERCANCIAS', 'MERCANCÍAS'],
            'AEC': ['AEC', 'ARANCEL EXTERNO COMÚN', 'TARIFA', 'DERECHO'],
            'CL': ['CL', 'REGIMEN LEGAL', 'RÉGIMEN LEGAL', 'REGIMEN', 'RÉGIMEN'],
            'E/Z': ['E/Z', 'EXPORTACIÓN', 'EXPORTACION', 'EXP'],
            'I/Z': ['I/Z', 'IMPORTACIÓN', 'IMPORTACION', 'IMP'],
            'UVF': ['UVF', 'VALOR FOB', 'FOB', 'VALOR']
        }
        
        # Intentar encontrar las columnas por sus posibles nombres
        for standard_name, aliases in column_aliases.items():
            for alias in aliases:
                matches = [col for col in original_columns if col.upper().strip() == alias]
                if matches:
                    rename_map[matches[0]] = standard_name
                    break
        
        # Renombrar columnas si encontramos correspondencias
        if rename_map:
            df = df.rename(columns=rename_map)
        
        # Verificar columnas requeridas
        required_columns = ['NCM', 'DESCRIPCION']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Faltan columnas requeridas: {missing_columns}")
            return None
        
        # Limpiar y preparar datos
        # - Eliminar filas sin NCM
        df = df.dropna(subset=['NCM'])
        
        # - Convertir NCM a string asegurando el formato correcto
        df['NCM'] = df['NCM'].astype(str).str.strip()
        
        # - Asegurar que DESCRIPCION sea string
        if 'DESCRIPCION' in df.columns:
            df['DESCRIPCION'] = df['DESCRIPCION'].fillna('').astype(str)
        
        # - Extraer información de sección y capítulo del NCM
        df['SECTION'] = df['NCM'].str[:2].apply(lambda x: str(int(x)) if x.isdigit() else '')
        df['CHAPTER'] = df['NCM'].str[:2].apply(lambda x: x if x.isdigit() else '')
        
        # Verificar NCM importantes para diagnóstico
        test_ncm = '2004.10.00.00'
        test_ncm_clean = test_ncm.replace('.', '')
        if test_ncm in df['NCM'].values:
            logger.info(f"✓ NCM {test_ncm} encontrado directamente")
        elif test_ncm_clean in df['NCM'].values:
            logger.info(f"✓ NCM {test_ncm} encontrado como {test_ncm_clean}")
        else:
            similar_ncms = df[df['NCM'].str.contains('2004', regex=False)]
            if not similar_ncms.empty:
                logger.info(f"NCM similares a {test_ncm}: {similar_ncms['NCM'].tolist()}")
            else:
                logger.warning(f"⚠ NCM {test_ncm} no encontrado en el archivo")
        
        logger.info(f"Se extrajeron {len(df)} registros de NCM")
        return df
    
    except Exception as e:
        logger.error(f"Error al procesar el archivo Excel: {e}")
        return None

def get_version_date_from_filename(file_path):
    """
    Extrae la fecha de versión del nombre del archivo
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        Fecha en formato YYYY-MM-DD o la fecha actual
    """
    file_name = os.path.basename(file_path)
    
    # Patrones comunes de fechas en nombres de archivo
    import re
    
    # Buscar patrón YYYYMM o MM_YYYY
    date_patterns = [
        r'(\d{4})[-_]?(\d{2})',  # YYYY-MM o YYYY_MM
        r'(\d{2})[-_]?(\d{4})',  # MM-YYYY o MM_YYYY
        r'(\w{3,})[-_]?(\d{4})'   # MES-YYYY o MES_YYYY (ej. Abril_2024)
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, file_name)
        if match:
            groups = match.groups()
            
            # Determinar si el primer grupo es año o mes
            if len(groups[0]) == 4:  # YYYY-MM
                year, month = groups
            elif len(groups[0]) == 2:  # MM-YYYY
                month, year = groups
            else:  # MES-YYYY
                # Convertir nombre de mes a número
                month_names = {
                    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
                    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05',
                    'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10',
                    'nov': '11', 'dec': '12'
                }
                month_name = groups[0].lower()
                if month_name in month_names:
                    month = month_names[month_name]
                else:
                    # Si no podemos identificar el mes, usar el mes actual
                    month = datetime.datetime.now().strftime('%m')
                year = groups[1]
            
            # Primer día del mes
            return f"{year}-{month}-01"
    
    # Si no se encontró un patrón de fecha, usar la fecha actual
    logger.warning(f"No se pudo determinar la fecha del archivo {file_name}, usando fecha actual")
    return datetime.datetime.now().strftime('%Y-%m-%d')

def load_excel_to_version_db(file_path, version_date=None, sheet_name=None):
    """
    Carga datos de un archivo Excel a una nueva base de datos versionada
    
    Args:
        file_path: Ruta al archivo Excel
        version_date: Fecha de la versión (opcional, se intenta extraer del nombre del archivo)
        sheet_name: Nombre de la hoja (opcional)
        
    Returns:
        Ruta a la base de datos creada o None si falló
    """
    # Obtener la fecha de versión
    if version_date is None:
        version_date = get_version_date_from_filename(file_path)
    
    logger.info(f"Cargando archivo {os.path.basename(file_path)} como versión {version_date}")
    
    # Extraer datos del Excel
    df = extract_ncm_from_excel(file_path, sheet_name)
    if df is None or df.empty:
        logger.error("No se pudieron extraer datos del archivo Excel")
        return None
    
    # Crear la nueva base de datos para esta versión
    source_name = os.path.basename(file_path)
    db_path = create_new_version_db(version_date, source_name)
    if not db_path:
        logger.error("No se pudo crear la base de datos para la versión")
        return None
    
    # Guardar los datos en la base de datos
    logger.info(f"Guardando {len(df)} registros en la base de datos {db_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Guardar arancel_nacional
            batch_size = 1000
            total_batches = (len(df) + batch_size - 1) // batch_size
            
            with tqdm(total=total_batches, desc="Guardando registros") as pbar:
                for i in range(0, len(df), batch_size):
                    batch = df.iloc[i:i+batch_size]
                    batch.to_sql('arancel_nacional', conn, if_exists='append', index=False)
                    pbar.update(1)
            
            # Guardar información en ncm_versions
            logger.info("Actualizando tabla de versiones de NCM")
            
            # Preparar datos para la tabla ncm_versions
            version_records = []
            for _, row in df.iterrows():
                ncm_code = row['NCM']
                description = row.get('DESCRIPCION', None)
                aec = row.get('AEC', None)
                ez = row.get('E/Z', None)
                iz = row.get('I/Z', None)
                uvf = row.get('UVF', None)
                cl = row.get('CL', None)
                
                # Convertir a tipos adecuados
                try:
                    aec = float(aec) if aec not in (None, '', 'NA', 'N/A') else None
                except (ValueError, TypeError):
                    aec = None
                
                try:
                    ez = float(ez) if ez not in (None, '', 'NA', 'N/A') else None
                except (ValueError, TypeError):
                    ez = None
                
                try:
                    iz = float(iz) if iz not in (None, '', 'NA', 'N/A') else None
                except (ValueError, TypeError):
                    iz = None
                
                try:
                    uvf = float(uvf) if uvf not in (None, '', 'NA', 'N/A') else None
                except (ValueError, TypeError):
                    uvf = None
                
                version_records.append((
                    ncm_code,
                    version_date,
                    source_name,
                    description,
                    aec,
                    ez,
                    iz,
                    uvf,
                    cl,
                    True,  # active
                    datetime.datetime.now().isoformat()  # created_at
                ))
            
            # Insertar en lotes
            total_batches = (len(version_records) + batch_size - 1) // batch_size
            with tqdm(total=total_batches, desc="Actualizando versiones") as pbar:
                for i in range(0, len(version_records), batch_size):
                    batch = version_records[i:i+batch_size]
                    conn.executemany(
                        """INSERT INTO ncm_versions 
                           (ncm_code, version_date, source_file, description, aec, ez, iz, uvf, cl, active, created_at) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                        batch
                    )
                    pbar.update(1)
            
            conn.commit()
            
        logger.info(f"Datos cargados correctamente en la base de datos para la versión {version_date}")
        return db_path
    
    except Exception as e:
        logger.error(f"Error al guardar los datos en la base de datos: {e}")
        return None

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Carga un archivo Excel a una base de datos versionada')
    parser.add_argument('file', help='Ruta al archivo Excel')
    parser.add_argument('--date', help='Fecha de la versión (YYYY-MM-DD)')
    parser.add_argument('--sheet', help='Nombre de la hoja')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        logger.error(f"El archivo {args.file} no existe")
        return 1
    
    db_path = load_excel_to_version_db(args.file, args.date, args.sheet)
    if db_path:
        logger.info(f"Proceso completado. Base de datos creada en {db_path}")
        return 0
    else:
        logger.error("El proceso de carga falló")
        return 1

if __name__ == "__main__":
    sys.exit(main())
