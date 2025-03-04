#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para cambiar manualmente entre versiones de bases de datos de aranceles.
Permite al administrador seleccionar qué versión de la base de datos usar como activa.
"""

import os
import sys
import logging
from pathlib import Path
import argparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constantes
BASE_DIR = Path(__file__).resolve().parent.parent
DB_VERSIONS_DIR = BASE_DIR / 'data' / 'db_versions'
LATEST_SYMLINK = DB_VERSIONS_DIR / 'arancel_latest.sqlite3'

def listar_versiones():
    """Lista todas las versiones disponibles de la base de datos."""
    versiones = []
    
    # Verificar que el directorio exista
    if not DB_VERSIONS_DIR.exists():
        logging.error(f"El directorio {DB_VERSIONS_DIR} no existe")
        return versiones
    
    # Buscar archivos .sqlite3 en el directorio de versiones
    for file in DB_VERSIONS_DIR.glob('arancel_*.sqlite3'):
        if file.is_symlink():
            continue
            
        # Extraer la versión del nombre del archivo (arancel_20XX.sqlite3 -> 20XX)
        filename = file.name
        if '_' in filename:
            version = filename.split('_')[1].split('.')[0]
            versiones.append((version, file))
    
    # Ordenar las versiones de manera descendente
    versiones.sort(reverse=True)
    
    return versiones

def get_current_version():
    """Obtiene la versión actual activa."""
    if not LATEST_SYMLINK.exists() or not LATEST_SYMLINK.is_symlink():
        return None
        
    try:
        target = os.readlink(LATEST_SYMLINK)
        target_path = Path(target)
        filename = target_path.name
        if '_' in filename:
            return filename.split('_')[1].split('.')[0]
    except:
        return None
        
    return None

def cambiar_version(version=None):
    """Cambia la versión activa de la base de datos."""
    versiones = listar_versiones()
    
    if not versiones:
        logging.error("No se encontraron versiones disponibles")
        return False
    
    # Si no se especifica versión, mostrar las disponibles
    if version is None:
        print("\nVersiones disponibles:")
        for idx, (ver, path) in enumerate(versiones, 1):
            is_current = get_current_version() == ver
            current_mark = " (ACTUAL)" if is_current else ""
            print(f"{idx}. {ver}{current_mark} - {path}")
        
        # Solicitar selección al usuario
        try:
            seleccion = int(input("\nSeleccione una versión (número): "))
            if seleccion < 1 or seleccion > len(versiones):
                logging.error(f"Selección inválida. Debe ser entre 1 y {len(versiones)}")
                return False
                
            version, path = versiones[seleccion - 1]
        except ValueError:
            logging.error("Entrada inválida. Debe ingresar un número.")
            return False
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
            return False
    else:
        # Buscar la versión especificada
        found = False
        for ver, path in versiones:
            if ver == version:
                found = True
                break
                
        if not found:
            logging.error(f"Versión {version} no encontrada")
            return False
    
    # Actualizar el enlace simbólico
    try:
        if LATEST_SYMLINK.exists():
            LATEST_SYMLINK.unlink()
            
        os.symlink(path, LATEST_SYMLINK)
        logging.info(f"Versión cambiada exitosamente a {version}")
        logging.info(f"Enlace simbólico actualizado: {LATEST_SYMLINK} -> {path}")
        return True
    except Exception as e:
        logging.error(f"Error al cambiar la versión: {str(e)}")
        return False

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Cambiar entre versiones de la base de datos de aranceles')
    parser.add_argument('--version', '-v', help='Versión a activar (ej: 202404)')
    parser.add_argument('--list', '-l', action='store_true', help='Listar versiones disponibles')
    
    args = parser.parse_args()
    
    # Verificar que el directorio de versiones exista
    if not DB_VERSIONS_DIR.exists():
        logging.error(f"El directorio {DB_VERSIONS_DIR} no existe")
        return 1
    
    if args.list:
        versiones = listar_versiones()
        if not versiones:
            logging.info("No hay versiones disponibles")
            return 0
            
        current = get_current_version()
        print("\nVersiones disponibles:")
        for ver, path in versiones:
            is_current = current == ver
            current_mark = " (ACTUAL)" if is_current else ""
            print(f"- {ver}{current_mark} - {path}")
        return 0
    
    # Cambiar versión
    if args.version:
        success = cambiar_version(args.version)
    else:
        success = cambiar_version()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 