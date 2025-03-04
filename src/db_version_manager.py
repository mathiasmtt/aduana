#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para gestionar múltiples bases de datos por versión temporal.
Permite crear, actualizar y consultar bases de datos específicas para
diferentes versiones del arancel.
"""

import os
import re
import datetime
import sqlite3
import shutil
from pathlib import Path
import logging
from contextlib import closing

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db_version_manager')

# Rutas base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_VERSIONS_DIR = os.path.join(BASE_DIR, 'data', 'db_versions')
ORIGINAL_DB_PATH = os.path.join(BASE_DIR, 'data', 'database.sqlite3')
LATEST_SYMLINK = os.path.join(DB_VERSIONS_DIR, 'arancel_latest.sqlite3')

# Para diagnóstico
logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"DB_VERSIONS_DIR: {DB_VERSIONS_DIR}")
logger.info(f"ORIGINAL_DB_PATH: {ORIGINAL_DB_PATH}")
logger.info(f"LATEST_SYMLINK: {LATEST_SYMLINK}")

# Asegurar que el directorio de versiones exista
os.makedirs(DB_VERSIONS_DIR, exist_ok=True)

def get_db_path_for_date(date):
    """
    Obtiene la ruta a la base de datos correspondiente a una fecha específica.
    Si date es None, devuelve la base de datos más reciente.
    
    Args:
        date: Fecha en formato YYYY-MM-DD o YYYYMM o None para la más reciente
        
    Returns:
        Ruta absoluta a la base de datos
    """
    if date is None:
        logger.info(f"Solicitada base de datos más reciente, devolviendo: {LATEST_SYMLINK}")
        
        # Verificar si existe el enlace simbólico
        if not os.path.exists(LATEST_SYMLINK):
            logger.warning(f"El enlace simbólico {LATEST_SYMLINK} no existe, intentando usar latest.sqlite3")
            alt_symlink = os.path.join(DB_VERSIONS_DIR, 'latest.sqlite3')
            if os.path.exists(alt_symlink):
                return alt_symlink
            else:
                logger.warning(f"No se encontró ningún enlace simbólico, usando la base de datos original")
                return ORIGINAL_DB_PATH
        
        return LATEST_SYMLINK
    
    # Convertir la fecha a YYYYMM y YYYYMMDD
    date_prefix = None
    
    # Si es una cadena, intentar convertirla
    if isinstance(date, str):
        # Si es formato YYYYMM (6 dígitos)
        if re.match(r'^\d{6}$', date):
            year = date[:4]
            month = date[4:6]
            date_prefix = f"{year}{month}"
            logger.info(f"Buscando base de datos para YYYYMM: {date_prefix}")
        # Si es formato YYYY-MM-DD
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            try:
                date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
                date_prefix = f"{date_obj.year}{date_obj.month:02d}"
                logger.info(f"Buscando base de datos para fecha: {date} (YYYYMM: {date_prefix})")
            except ValueError:
                logger.warning(f"Formato de fecha inválido: {date}")
                return ORIGINAL_DB_PATH
        else:
            logger.warning(f"Formato de fecha no reconocido: {date}")
            return ORIGINAL_DB_PATH
    elif isinstance(date, datetime.datetime):
        date_prefix = f"{date.year}{date.month:02d}"
        logger.info(f"Buscando base de datos para fecha datetime: (YYYYMM: {date_prefix})")
    else:
        logger.warning(f"Tipo de fecha no soportado: {type(date)}")
        return ORIGINAL_DB_PATH
    
    # Buscar todas las bases de datos que empiecen con ese prefijo
    db_files = []
    for filename in os.listdir(DB_VERSIONS_DIR):
        if filename.endswith('.sqlite3') and filename.startswith(date_prefix) and filename != 'latest.sqlite3' and filename != 'arancel_latest.sqlite3':
            db_files.append(filename)
    
    if not db_files:
        logger.warning(f"No existe base de datos para la fecha {date}")
        
        # Intentamos buscar todas las bases de datos disponibles
        all_dbs = []
        for filename in os.listdir(DB_VERSIONS_DIR):
            if filename.endswith('.sqlite3') and filename not in ['latest.sqlite3', 'arancel_latest.sqlite3']:
                all_dbs.append(filename)
        
        if all_dbs:
            # Ordenar por nombre (que debe ser YYYYMMDD)
            all_dbs.sort(reverse=True)
            
            # Si la fecha buscada es menor que la más antigua, usar la más antigua
            # Si es mayor que la más reciente, usar la más reciente
            first_db_date = all_dbs[-1][:8]  # El más antiguo
            last_db_date = all_dbs[0][:8]    # El más reciente
            
            if date_prefix < first_db_date[:6]:
                logger.info(f"La fecha {date_prefix} es anterior a la base de datos más antigua ({first_db_date}). Usando la más antigua.")
                return os.path.join(DB_VERSIONS_DIR, all_dbs[-1])
            elif date_prefix > last_db_date[:6]:
                logger.info(f"La fecha {date_prefix} es posterior a la base de datos más reciente ({last_db_date}). Usando la más reciente.")
                return os.path.join(DB_VERSIONS_DIR, all_dbs[0])
            else:
                # Buscar la base de datos más cercana anterior a la fecha solicitada
                for db_file in sorted(all_dbs, reverse=True):
                    if db_file[:6] <= date_prefix:
                        logger.info(f"Usando base de datos más cercana anterior: {db_file}")
                        return os.path.join(DB_VERSIONS_DIR, db_file)
        
        logger.warning("No hay bases de datos disponibles, usando la original")
        return ORIGINAL_DB_PATH
    
    # Ordenar para tomar la versión más reciente dentro del mes
    db_files.sort(reverse=True)
    db_path = os.path.join(DB_VERSIONS_DIR, db_files[0])
    logger.info(f"Base de datos encontrada: {db_path}")
    
    return db_path

def get_available_versions():
    """
    Obtiene la lista de versiones disponibles en formato YYYYMM
    
    Returns:
        Lista de versiones disponibles ordenadas de más reciente a más antigua
    """
    versions = []
    pattern = re.compile(r'arancel_(\d{6})\.sqlite3$')
    
    for file in os.listdir(DB_VERSIONS_DIR):
        match = pattern.match(file)
        if match:
            versions.append(match.group(1))
    
    return sorted(versions, reverse=True)  # Ordenar de más reciente a más antigua

def get_db_connection(version=None):
    """
    Obtiene una conexión a la base de datos para una versión específica
    
    Args:
        version: Versión en formato YYYYMM o None para la más reciente
        
    Returns:
        Conexión a la base de datos
    """
    if version is None:
        db_path = LATEST_SYMLINK
    else:
        db_path = os.path.join(DB_VERSIONS_DIR, f'arancel_{version}.sqlite3')
    
    if not os.path.exists(db_path):
        logger.warning(f"No existe la base de datos {db_path}")
        if version:
            logger.info(f"Buscando versión más cercana a {version}")
            db_path = get_db_path_for_date(f"{version[:4]}-{version[4:6]}-01")
        else:
            logger.warning("Usando base de datos original")
            db_path = ORIGINAL_DB_PATH
    
    return sqlite3.connect(db_path)

def create_new_version_db(version_date, source_name):
    """
    Crea una nueva base de datos para una versión específica
    
    Args:
        version_date: Fecha en formato YYYY-MM-DD
        source_name: Nombre del archivo fuente (para registro)
        
    Returns:
        Ruta a la nueva base de datos
    """
    # Convertir la fecha a YYYYMM
    if isinstance(version_date, str):
        try:
            date_obj = datetime.datetime.strptime(version_date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Fecha inválida: {version_date}. Debe estar en formato YYYY-MM-DD")
            return None
    else:
        date_obj = version_date
    
    version_str = date_obj.strftime('%Y%m')
    new_db_path = os.path.join(DB_VERSIONS_DIR, f'arancel_{version_str}.sqlite3')
    
    # Verificar si ya existe esta versión
    if os.path.exists(new_db_path):
        logger.warning(f"La versión {version_str} ya existe. Se usará la existente.")
        return new_db_path
    
    # Crear una nueva base de datos con el esquema correcto
    logger.info(f"Creando nueva base de datos para la versión {version_str}")
    
    # Copiar el esquema desde la base de datos original
    with closing(sqlite3.connect(ORIGINAL_DB_PATH)) as conn:
        schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        indexes = conn.execute("SELECT sql FROM sqlite_master WHERE type='index'").fetchall()
        
        with closing(sqlite3.connect(new_db_path)) as new_conn:
            # Crear las tablas
            for table_sql in schema:
                if table_sql[0]:  # Evitar None
                    new_conn.execute(table_sql[0])
            
            # Crear los índices
            for index_sql in indexes:
                if index_sql[0]:  # Evitar None
                    new_conn.execute(index_sql[0])
            
            # Registrar meta-información
            new_conn.execute(
                "CREATE TABLE IF NOT EXISTS db_metadata (key TEXT PRIMARY KEY, value TEXT)"
            )
            new_conn.execute(
                "INSERT INTO db_metadata VALUES (?, ?), (?, ?), (?, ?)",
                ('version', version_str, 'created_at', datetime.datetime.now().isoformat(), 'source', source_name)
            )
            
            new_conn.commit()
    
    # Actualizar el enlace simbólico a la versión más reciente
    update_latest_symlink()
    
    logger.info(f"Base de datos para la versión {version_str} creada correctamente")
    return new_db_path

def update_latest_symlink():
    """
    Actualiza el enlace simbólico a la base de datos más reciente
    """
    versions = get_available_versions()
    if not versions:
        logger.warning("No hay versiones disponibles para enlazar como latest")
        return False
    
    latest_version = versions[-1]  # La última en la lista ordenada
    latest_db_path = os.path.join(DB_VERSIONS_DIR, f'arancel_{latest_version}.sqlite3')
    
    # Eliminar enlace simbólico existente si existe
    if os.path.exists(LATEST_SYMLINK):
        try:
            os.remove(LATEST_SYMLINK)
        except OSError as e:
            logger.error(f"No se pudo eliminar el enlace simbólico existente: {e}")
            return False
    
    # Crear nuevo enlace simbólico
    try:
        # En sistemas Unix
        os.symlink(latest_db_path, LATEST_SYMLINK)
        logger.info(f"Enlace simbólico actualizado a la versión {latest_version}")
        return True
    except OSError as e:
        # En Windows o si ocurre un error
        logger.error(f"No se pudo crear el enlace simbólico: {e}")
        logger.info("Intentando crear una copia en lugar de un enlace simbólico")
        try:
            shutil.copy2(latest_db_path, LATEST_SYMLINK)
            logger.info(f"Copia creada correctamente para la versión {latest_version}")
            return True
        except OSError as e2:
            logger.error(f"No se pudo crear la copia: {e2}")
            return False

def migrate_data_to_new_version(source_version, target_version, tables=None):
    """
    Migra datos selectivos desde una versión a otra
    
    Args:
        source_version: Versión fuente en formato YYYYMM
        target_version: Versión destino en formato YYYYMM
        tables: Lista de tablas a migrar, None para todas
        
    Returns:
        True si la migración fue exitosa
    """
    source_db = os.path.join(DB_VERSIONS_DIR, f'arancel_{source_version}.sqlite3')
    target_db = os.path.join(DB_VERSIONS_DIR, f'arancel_{target_version}.sqlite3')
    
    if not os.path.exists(source_db):
        logger.error(f"La base de datos fuente {source_version} no existe")
        return False
    
    if not os.path.exists(target_db):
        logger.error(f"La base de datos destino {target_version} no existe")
        return False
    
    logger.info(f"Migrando datos de {source_version} a {target_version}")
    
    with closing(sqlite3.connect(source_db)) as source_conn, \
         closing(sqlite3.connect(target_db)) as target_conn:
        
        # Determinar qué tablas migrar
        if tables is None:
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'db_metadata'"
            tables = [row[0] for row in source_conn.execute(tables_query).fetchall()]
        
        for table in tables:
            try:
                # Verificar si la tabla existe en ambas bases de datos
                if source_conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'").fetchone() and \
                   target_conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'").fetchone():
                    
                    # Obtener datos de la tabla fuente
                    data = source_conn.execute(f"SELECT * FROM {table}").fetchall()
                    if not data:
                        logger.info(f"La tabla {table} está vacía en la fuente")
                        continue
                    
                    # Obtener columnas de la tabla
                    columns = [col[1] for col in source_conn.execute(f"PRAGMA table_info({table})").fetchall()]
                    
                    # Borrar datos existentes en la tabla destino
                    target_conn.execute(f"DELETE FROM {table}")
                    
                    # Preparar consulta de inserción
                    placeholders = ", ".join(["?" for _ in columns])
                    columns_str = ", ".join(columns)
                    insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                    
                    # Insertar datos en lotes
                    batch_size = 1000
                    for i in range(0, len(data), batch_size):
                        batch = data[i:i+batch_size]
                        target_conn.executemany(insert_query, batch)
                    
                    logger.info(f"Migrados {len(data)} registros de la tabla {table}")
            except sqlite3.Error as e:
                logger.error(f"Error al migrar la tabla {table}: {e}")
        
        # Actualizar metadata
        target_conn.execute("UPDATE db_metadata SET value = ? WHERE key = 'updated_at'", 
                          (datetime.datetime.now().isoformat(),))
        
        target_conn.commit()
    
    logger.info(f"Migración de {source_version} a {target_version} completada")
    return True

if __name__ == "__main__":
    # Ejemplo de uso
    print("Gestor de Versiones de Base de Datos")
    print("====================================")
    print("1. Listar versiones disponibles")
    print("2. Crear nueva versión")
    print("3. Migrar datos entre versiones")
    print("4. Actualizar enlace 'latest'")
    
    choice = input("\nSeleccione una opción: ")
    
    if choice == "1":
        versions = get_available_versions()
        if versions:
            print("Versiones disponibles:")
            for v in versions:
                year, month = v[:4], v[4:6]
                print(f"- {year}-{month}")
        else:
            print("No hay versiones disponibles")
    
    elif choice == "2":
        date_str = input("Ingrese fecha (YYYY-MM-DD): ")
        source = input("Ingrese nombre del archivo fuente: ")
        db_path = create_new_version_db(date_str, source)
        if db_path:
            print(f"Base de datos creada en: {db_path}")
    
    elif choice == "3":
        source = input("Ingrese versión fuente (YYYYMM): ")
        target = input("Ingrese versión destino (YYYYMM): ")
        tables_input = input("Ingrese tablas a migrar (separadas por coma, vacío para todas): ")
        
        tables = None
        if tables_input.strip():
            tables = [t.strip() for t in tables_input.split(",")]
        
        success = migrate_data_to_new_version(source, target, tables)
        if success:
            print("Migración completada con éxito")
        else:
            print("La migración falló")
    
    elif choice == "4":
        if update_latest_symlink():
            print("Enlace 'latest' actualizado correctamente")
        else:
            print("Error al actualizar el enlace 'latest'")
    
    else:
        print("Opción no válida")
