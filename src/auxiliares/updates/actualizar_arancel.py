#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para automatizar el proceso de carga de un nuevo archivo Excel del Arancel Nacional.
Este script ejecuta todos los pasos necesarios para actualizar el sistema con una nueva versión.

Uso:
    python actualizar_arancel.py --file ruta/al/excel.xlsx --version YYYYMMDD --descripcion "Descripción"

Ejemplo:
    python actualizar_arancel.py --file data/excel/Arancel_Mayo_2025.xlsx --version 20250501 --descripcion "Arancel Mayo 2025"
"""

import os
import sys
import argparse
import subprocess
import logging
import datetime
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('actualizar_arancel')

# Rutas base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, 'src')
PYTHON_PATH = BASE_DIR

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando y registra su salida."""
    logger.info(f"Ejecutando: {descripcion}")
    logger.debug(f"Comando: {comando}")
    
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Éxito: {descripcion}")
        return True, resultado.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error: {descripcion}")
        logger.error(f"Salida de error: {e.stderr}")
        return False, e.stderr

def main():
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Actualizar el Arancel Nacional con un nuevo archivo Excel')
    parser.add_argument('--file', required=True, help='Ruta al archivo Excel con el nuevo Arancel')
    parser.add_argument('--version', required=True, help='Versión en formato YYYYMMDD')
    parser.add_argument('--descripcion', required=True, help='Descripción de la versión')
    
    args = parser.parse_args()
    
    # Verificar que el archivo Excel existe
    excel_path = os.path.abspath(args.file)
    if not os.path.exists(excel_path):
        logger.error(f"El archivo Excel no existe: {excel_path}")
        sys.exit(1)
        
    # Verificar formato de versión
    try:
        version_date = datetime.datetime.strptime(args.version, '%Y%m%d')
        logger.info(f"Versión: {version_date.strftime('%Y-%m-%d')}")
    except ValueError:
        logger.error(f"Formato de versión inválido: {args.version}. Debe ser YYYYMMDD.")
        sys.exit(1)
    
    # 1. Cargar los datos a una nueva base de datos versionada
    comando_1 = f"PYTHONPATH={PYTHON_PATH} python {os.path.join(SRC_DIR, 'load_version_db.py')} --file {excel_path} --version {args.version}"
    exito_1, _ = ejecutar_comando(comando_1, "Cargar datos del Excel a nueva base de datos")
    
    if not exito_1:
        logger.error("No se pudo cargar el archivo Excel. Abortando.")
        sys.exit(1)
    
    # 2. Actualizar los metadatos de la versión
    comando_2 = f"PYTHONPATH={PYTHON_PATH} python {os.path.join(SRC_DIR, 'update_version_metadata.py')} --version {args.version} --descripcion \"{args.descripcion}\""
    exito_2, _ = ejecutar_comando(comando_2, "Actualizar metadatos de versión")
    
    if not exito_2:
        logger.error("No se pudieron actualizar los metadatos. Continuando de todas formas...")
    
    # 3. Sincronizar las notas de sección
    comando_3 = f"PYTHONPATH={PYTHON_PATH} python {os.path.join(SRC_DIR, 'sync_section_notes.py')} --version {args.version} --file {excel_path}"
    exito_3, _ = ejecutar_comando(comando_3, "Sincronizar notas de sección")
    
    if not exito_3:
        logger.error("No se pudieron sincronizar las notas de sección. Continuando de todas formas...")
    
    # 4. Sincronizar las notas de capítulo
    comando_4 = f"PYTHONPATH={PYTHON_PATH} python {os.path.join(SRC_DIR, 'sync_chapter_notes.py')} --version {args.version} --file {excel_path}"
    exito_4, _ = ejecutar_comando(comando_4, "Sincronizar notas de capítulo")
    
    if not exito_4:
        logger.error("No se pudieron sincronizar las notas de capítulo. Continuando de todas formas...")
    
    # Resumen final
    logger.info("\n=== RESUMEN DE LA ACTUALIZACIÓN ===")
    logger.info(f"Archivo Excel: {excel_path}")
    logger.info(f"Versión: {args.version} ({version_date.strftime('%Y-%m-%d')})")
    logger.info(f"Descripción: {args.descripcion}")
    logger.info(f"Cargar datos: {'✓' if exito_1 else '✗'}")
    logger.info(f"Actualizar metadatos: {'✓' if exito_2 else '✗'}")
    logger.info(f"Sincronizar notas de sección: {'✓' if exito_3 else '✗'}")
    logger.info(f"Sincronizar notas de capítulo: {'✓' if exito_4 else '✗'}")
    
    if exito_1 and exito_2 and exito_3 and exito_4:
        logger.info("\n✓ ACTUALIZACIÓN COMPLETADA CON ÉXITO")
        logger.info("Para ver los cambios, reinicia el servidor y accede a la aplicación.")
    else:
        logger.warning("\n⚠ ACTUALIZACIÓN COMPLETADA CON ADVERTENCIAS")
        logger.warning("Revisa los mensajes anteriores para solucionar los problemas encontrados.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
