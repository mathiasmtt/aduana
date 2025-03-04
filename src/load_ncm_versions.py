#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para cargar diferentes versiones de los NCM desde archivos Excel.
Lee los archivos Excel de diferentes fechas y carga los datos en la tabla ncm_versions.
"""
import os
import pandas as pd
import re
from datetime import datetime
import logging
from app import create_app, db
from app.models.ncm_version import NCMVersion

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ncm_versions_load.log')
    ]
)
logger = logging.getLogger('load_ncm_versions')

# Directorio donde se encuentran los archivos Excel
data_dir = os.path.join('data')

def extract_date_from_filename(filename):
    """
    Extrae la fecha del nombre del archivo Excel.
    
    Args:
        filename: Nombre del archivo Excel (ej: 'Arancel Nacional_Abril 2024.xlsx')
        
    Returns:
        Objeto datetime con la fecha extraída o None si no se pudo extraer
    """
    # Patrones para meses en español
    month_patterns = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    # Buscar patrón de mes y año
    for month_name, month_num in month_patterns.items():
        pattern = rf'{month_name}\s+(\d{{4}})'.lower()
        match = re.search(pattern, filename.lower())
        if match:
            year = int(match.group(1))
            # Usar el día 1 como predeterminado
            return datetime(year, month_num, 1)
    
    # Si no se encuentra, intentar otro formato
    match = re.search(r'(\d{2})[-_\s](\d{2})[-_\s](\d{4})', filename)
    if match:
        day, month, year = map(int, match.groups())
        return datetime(year, month, day)
    
    return None

def get_excel_files():
    """
    Obtiene todos los archivos Excel en el directorio de datos.
    
    Returns:
        Lista de tuplas (ruta_completa, fecha) de archivos Excel ordenados por fecha
    """
    excel_files = []
    
    for file in os.listdir(data_dir):
        if file.endswith('.xlsx') and 'Arancel Nacional' in file:
            full_path = os.path.join(data_dir, file)
            date = extract_date_from_filename(file)
            
            if date:
                excel_files.append((full_path, file, date))
            else:
                logger.warning(f"No se pudo extraer la fecha del archivo: {file}")
    
    # Ordenar por fecha
    return sorted(excel_files, key=lambda x: x[2])

def clean_value(value):
    """Limpia y formatea un valor"""
    if pd.isna(value) or value is None:
        return None
    
    # Si es una cadena, limpiar espacios
    if isinstance(value, str):
        return value.strip()
    
    return value

def extract_ncm_from_excel(filepath, source_filename, version_date):
    """
    Extrae información de NCM desde un archivo Excel.
    
    Args:
        filepath: Ruta al archivo Excel
        source_filename: Nombre del archivo fuente
        version_date: Fecha de la versión
        
    Returns:
        Lista de diccionarios con la información de cada NCM
    """
    logger.info(f"Procesando archivo: {filepath}")
    
    try:
        # Cargar Excel
        xl = pd.ExcelFile(filepath)
        sheet_name = xl.sheet_names[0]  # Usar la primera hoja
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        
        # Inicializar lista para almacenar datos
        data = []
        
        # Variable para rastreo de códigos específicos para diagnóstico
        codigos_importantes = ['2004.10.00.00']
        codigos_encontrados = {codigo: False for codigo in codigos_importantes}
        
        # Iterar por todas las filas buscando patrones de NCM
        for idx, row in df.iterrows():
            ncm_value = row.iloc[0]  # La primera columna contiene el código NCM
            
            # Verificar si es un código NCM válido
            if isinstance(ncm_value, str) and any(c.isdigit() for c in ncm_value) and '.' in ncm_value:
                # Validación adicional: verificar que es un patrón NCM completo
                if all(c.isdigit() or c == '.' for c in ncm_value.strip()):
                    # Extraer valores de las columnas relevantes
                    description = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else None
                    aec = clean_value(row.iloc[2]) if len(row) > 2 else None
                    cl = clean_value(row.iloc[3]) if len(row) > 3 else None
                    ez = clean_value(row.iloc[4]) if len(row) > 4 else None
                    iz = clean_value(row.iloc[5]) if len(row) > 5 else None
                    uvf = clean_value(row.iloc[6]) if len(row) > 6 else None
                    
                    # Crear registro
                    ncm_data = {
                        'ncm_code': ncm_value,
                        'source_file': source_filename,
                        'version_date': version_date.date(),
                        'description': description
                    }
                    
                    # Agregar campos numéricos solo si tienen valores
                    if aec is not None:
                        ncm_data['aec'] = aec
                    if cl is not None:
                        ncm_data['cl'] = cl
                    if ez is not None:
                        ncm_data['ez'] = ez
                    if iz is not None:
                        ncm_data['iz'] = iz
                    if uvf is not None:
                        ncm_data['uvf'] = uvf
                    
                    # Verificar códigos importantes (para diagnóstico)
                    if ncm_value in codigos_importantes:
                        codigos_encontrados[ncm_value] = True
                        logger.info(f"¡ENCONTRADO CÓDIGO IMPORTANTE!: {ncm_value} en fila {idx}")
                        logger.info(f"Datos: {ncm_data}")
                    
                    data.append(ncm_data)
        
        # Diagnóstico final de códigos importantes
        for codigo, encontrado in codigos_encontrados.items():
            if encontrado:
                logger.info(f"Código importante {codigo} fue encontrado y procesado correctamente")
            else:
                logger.warning(f"⚠️ Código importante {codigo} NO fue encontrado en {source_filename}")
        
        return data
    
    except Exception as e:
        logger.error(f"Error al procesar el archivo {filepath}: {str(e)}")
        return []

def load_versions_to_db(versions_data):
    """
    Carga los datos de versiones en la base de datos.
    
    Args:
        versions_data: Lista de diccionarios con datos de NCM
        
    Returns:
        Número de registros agregados
    """
    count = 0
    
    # Búsqueda específica para diagnóstico
    codigos_importantes = ['2004.10.00.00']
    codigos_encontrados = {codigo: False for codigo in codigos_importantes}
    
    # Verificar si los datos contienen los códigos importantes
    for data in versions_data:
        if data.get('ncm_code') in codigos_importantes:
            logger.info(f"🔍 Código importante {data.get('ncm_code')} encontrado en los datos a cargar")
            logger.info(f"Detalles: {data}")
            codigos_encontrados[data.get('ncm_code')] = True
    
    # Mensaje si no se encontraron
    for codigo, encontrado in codigos_encontrados.items():
        if not encontrado:
            logger.warning(f"⚠️ Código importante {codigo} NO se encontró en los datos a cargar")
    
    try:
        # Procesar los datos en lotes pequeños para evitar problemas de memoria
        batch_size = 100
        total_batches = len(versions_data) // batch_size + (1 if len(versions_data) % batch_size > 0 else 0)
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(versions_data))
            batch = versions_data[start_idx:end_idx]
            
            logger.info(f"Procesando lote {batch_idx + 1}/{total_batches} ({start_idx}-{end_idx})")
            
            for data in batch:
                try:
                    # Verificar si esta versión ya existe
                    existing = NCMVersion.query.filter_by(
                        ncm_code=data['ncm_code'],
                        version_date=data['version_date']
                    ).first()
                    
                    if existing:
                        # Actualizar versión existente
                        for key, value in data.items():
                            setattr(existing, key, value)
                        logger.info(f"Actualizada versión: {data['ncm_code']} {data['version_date']}")
                    else:
                        # Crear nueva versión
                        new_version = NCMVersion(**data)
                        db.session.add(new_version)
                        count += 1
                        logger.info(f"Agregada nueva versión: {data['ncm_code']} {data['version_date']}")
                    
                    # Diagnóstico especial para códigos importantes
                    if data.get('ncm_code') in codigos_importantes:
                        logger.info(f"✅ Procesado código importante: {data['ncm_code']}")
                
                except Exception as e:
                    logger.error(f"Error al guardar versión {data.get('ncm_code')}: {str(e)}")
                    # Registrar todos los detalles para diagnóstico
                    logger.error(f"Detalles completos del registro con error: {data}")
                    db.session.rollback()
            
            # Commit después de cada lote
            try:
                db.session.commit()
                logger.info(f"Commit exitoso del lote {batch_idx + 1}")
            except Exception as e:
                logger.error(f"Error en commit del lote {batch_idx + 1}: {str(e)}")
                db.session.rollback()
    
    except Exception as e:
        logger.error(f"Error general en load_versions_to_db: {str(e)}")
        db.session.rollback()
    
    # Verificar si los códigos importantes se guardaron correctamente
    for codigo in codigos_importantes:
        verificacion = NCMVersion.query.filter_by(ncm_code=codigo).all()
        if verificacion:
            logger.info(f"✓ Código {codigo} guardado correctamente en la base de datos. Versiones: {len(verificacion)}")
            for v in verificacion:
                logger.info(f"  - {v.version_date} desde {v.source_file}")
        else:
            logger.error(f"✗ Código {codigo} NO se encontró en la base de datos después de cargarlo")
    
    return count

def main():
    """Función principal que ejecuta la carga de versiones NCM."""
    # Crear contexto de aplicación Flask
    app = create_app()
    
    with app.app_context():
        print("\nCarga de Versiones NCM")
        print("======================")
        
        # Verificar si la tabla existe y crearla si no existe
        from sqlalchemy import inspect
        if not inspect(db.engine).has_table('ncm_versions'):
            print("Creando tabla para versiones NCM...")
            db.create_all()
            print("Tabla creada exitosamente.")
        
        # Obtener archivos Excel
        excel_files = get_excel_files()
        
        if not excel_files:
            print("No se encontraron archivos Excel en el directorio de datos.")
            return
        
        print(f"Se encontraron {len(excel_files)} archivos Excel:")
        for filepath, filename, date in excel_files:
            print(f"- {filename} ({date.strftime('%d/%m/%Y')})")
        
        print("\nOpciones:")
        print("1. Cargar todas las versiones")
        print("2. Cargar versiones específicas")
        print("3. Ver estadísticas de versiones")
        print("4. Salir")
        
        opcion = input("\nSeleccione una opción (1-4): ").strip()
        
        if opcion == "1":
            # Cargar todas las versiones
            total_added = 0
            
            for filepath, filename, date in excel_files:
                print(f"\nProcesando {filename}...")
                versions_data = extract_ncm_from_excel(filepath, filename, date)
                added = load_versions_to_db(versions_data)
                total_added += added
                print(f"Se agregaron {added} registros de {filename}")
            
            print(f"\nSe agregaron un total de {total_added} versiones a la base de datos.")
        
        elif opcion == "2":
            # Cargar versiones específicas
            for i, (filepath, filename, date) in enumerate(excel_files, 1):
                print(f"{i}. {filename} ({date.strftime('%d/%m/%Y')})")
            
            seleccion = input("\nSeleccione el número del archivo a cargar (separados por coma): ")
            indices = [int(idx.strip()) - 1 for idx in seleccion.split(",") if idx.strip().isdigit()]
            
            total_added = 0
            for idx in indices:
                if 0 <= idx < len(excel_files):
                    filepath, filename, date = excel_files[idx]
                    print(f"\nProcesando {filename}...")
                    versions_data = extract_ncm_from_excel(filepath, filename, date)
                    added = load_versions_to_db(versions_data)
                    total_added += added
                    print(f"Se agregaron {added} registros de {filename}")
            
            print(f"\nSe agregaron un total de {total_added} versiones a la base de datos.")
        
        elif opcion == "3":
            # Ver estadísticas
            total_versions = NCMVersion.query.count()
            distinct_ncm = db.session.query(NCMVersion.ncm_code).distinct().count()
            versions_by_date = db.session.query(
                NCMVersion.version_date,
                db.func.count(NCMVersion.id)
            ).group_by(NCMVersion.version_date).all()
            
            print(f"\nEstadísticas de versiones NCM:")
            print(f"- Total de registros: {total_versions}")
            print(f"- Códigos NCM distintos: {distinct_ncm}")
            print("\nRegistros por fecha:")
            
            for date, count in versions_by_date:
                print(f"- {date.strftime('%d/%m/%Y')}: {count} registros")
        
        elif opcion == "4":
            print("\nSaliendo...")
        
        else:
            print("\nOpción no válida")

if __name__ == "__main__":
    main()
