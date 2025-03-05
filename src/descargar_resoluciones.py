#!/usr/bin/env python
"""
Script para descargar resoluciones de clasificación arancelaria desde el 
sitio web de la Dirección Nacional de Aduanas de Uruguay.
"""

import os
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime

# Agregar el directorio src al path para poder importar el módulo aduana
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.aduana import descargar_resoluciones, ResolucionDownloader

def main():
    """Función principal para descargar resoluciones de clasificación arancelaria."""
    
    parser = argparse.ArgumentParser(
        description='Descarga resoluciones de clasificación arancelaria desde el sitio web de Aduanas'
    )
    
    # Crear subcomandos
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")
    
    # Subcomando para descargar por año
    parser_year = subparsers.add_parser('year', help='Descargar resoluciones de un año específico')
    parser_year.add_argument(
        'year',
        type=str,
        help='Año para descargar resoluciones (por ejemplo: 2023, 2024, 2025)'
    )
    
    # Subcomando para descargar una resolución específica por URL
    parser_url = subparsers.add_parser('url', help='Descargar una resolución específica por URL')
    parser_url.add_argument(
        'url',
        type=str,
        help='URL de la resolución a descargar'
    )
    parser_url.add_argument(
        'year',
        type=int,
        help='Año de la resolución'
    )
    parser_url.add_argument(
        'numero',
        type=int,
        help='Número de la resolución'
    )
    
    # Subcomando para descargar PDFs directamente
    parser_pdf = subparsers.add_parser('pdf', help='Descargar PDFs directamente')
    parser_pdf.add_argument(
        '--resolucion-url',
        type=str,
        help='URL del PDF de la resolución'
    )
    parser_pdf.add_argument(
        '--dictamen-url',
        type=str,
        help='URL del PDF del dictamen'
    )
    parser_pdf.add_argument(
        'year',
        type=int,
        help='Año de la resolución'
    )
    parser_pdf.add_argument(
        'numero',
        type=int,
        help='Número de la resolución'
    )
    parser_pdf.add_argument(
        '--fecha',
        type=str,
        help='Fecha de la resolución (formato: YYYY-MM-DD)',
        default=None
    )
    parser_pdf.add_argument(
        '--referencia',
        type=str,
        help='Referencia o título de la resolución',
        default=""
    )
    
    # Opciones comunes
    for subparser in [parser_year, parser_url, parser_pdf]:
        subparser.add_argument(
            '--db-path',
            type=str,
            help='Ruta a la base de datos SQLite (por defecto: data/aduana/aduana.db)',
            default=None
        )
    
    args = parser.parse_args()
    
    # Si no se especificó comando, mostrar ayuda
    if not args.command:
        parser.print_help()
        return 1
    
    # Obtener la ruta de la base de datos si no se especificó
    if args.db_path is None:
        base_dir = Path(__file__).resolve().parent.parent
        db_path = os.path.join(base_dir, 'data', 'aduana', 'aduana.db')
    else:
        db_path = args.db_path
    
    # Verificar si la base de datos existe
    if not os.path.exists(db_path):
        print(f"❌ La base de datos no existe en la ruta: {db_path}")
        print("Por favor, ejecute primero el script 'crear_db_aduana.py'")
        return 1
    
    # Procesar comando
    if args.command == 'year':
        # Verificar si el año es válido
        if not args.year.isdigit() or len(args.year) != 4:
            print(f"❌ El año '{args.year}' no es válido. Debe ser un número de 4 dígitos.")
            return 1
        
        print(f"🔄 Descargando resoluciones del año {args.year}...")
        print(f"📊 Base de datos: {db_path}")
        print(f"📁 Los PDFs se guardarán en: data/aduana/{args.year}/")
        print("⏳ Este proceso puede tardar varios minutos dependiendo de la cantidad de resoluciones...")
        
        # Descargar las resoluciones
        count = descargar_resoluciones(args.year, db_path)
        
        if count > 0:
            print(f"✅ Se descargaron y procesaron {count} resoluciones del año {args.year}")
        else:
            print(f"⚠️ No se pudo descargar ninguna resolución del año {args.year}")
            print("   Verifique que el año sea correcto y que existan resoluciones para ese año.")
    
    elif args.command == 'url':
        print(f"🔄 Descargando resolución {args.numero}/{args.year} desde URL: {args.url}")
        print(f"📊 Base de datos: {db_path}")
        
        # Crear directorio para el año si no existe
        base_dir = Path(__file__).resolve().parent.parent
        year_dir = os.path.join(base_dir, 'data', 'aduana', str(args.year))
        os.makedirs(year_dir, exist_ok=True)
        
        # Crear un downloader
        downloader = ResolucionDownloader(db_path=db_path)
        
        # Crear información básica de la resolución
        resolution_info = {
            "year": args.year,
            "numero": args.numero,
            "url": args.url
        }
        
        # Procesar los detalles de la resolución
        print("⏳ Procesando los detalles de la resolución...")
        complete_info = downloader.process_resolution_details(resolution_info)
        
        # Guardar en la base de datos
        resolution_id = downloader.save_to_database(complete_info)
        
        if resolution_id > 0:
            print(f"✅ Resolución {args.numero}/{args.year} guardada exitosamente (ID: {resolution_id})")
            print(f"📁 Los PDFs se guardaron en: {year_dir}/")
        else:
            print(f"❌ Error al guardar la resolución en la base de datos.")
    
    elif args.command == 'pdf':
        if not args.resolucion_url and not args.dictamen_url:
            print("❌ Debe especificar al menos una URL para la resolución o el dictamen")
            return 1
            
        print(f"🔄 Descargando PDFs para la resolución {args.numero}/{args.year}...")
        print(f"📊 Base de datos: {db_path}")
        
        # Crear un downloader
        downloader = ResolucionDownloader(db_path=db_path)
        
        # Procesar PDFs
        dictamen_path = ""
        resolucion_path = ""
        
        if args.dictamen_url:
            print(f"📄 Descargando dictamen desde: {args.dictamen_url}")
            dictamen_path = downloader.process_pdf_url(
                args.dictamen_url, 
                args.year, 
                args.numero, 
                "dictamen"
            )
        
        if args.resolucion_url:
            print(f"📄 Descargando resolución desde: {args.resolucion_url}")
            resolucion_path = downloader.process_pdf_url(
                args.resolucion_url, 
                args.year, 
                args.numero, 
                "resolucion"
            )
        
        # Fecha por defecto basada en el año si no se proporciona
        fecha = args.fecha or f"{args.year}-01-01"
        
        # Crear información de la resolución
        resolution_info = {
            "year": args.year,
            "numero": args.numero,
            "fecha": fecha,
            "referencia": args.referencia,
            "dictamen": dictamen_path,
            "resolucion": resolucion_path
        }
        
        # Guardar en la base de datos
        resolution_id = downloader.save_to_database(resolution_info)
        
        if resolution_id > 0:
            print(f"✅ Resolución {args.numero}/{args.year} guardada exitosamente (ID: {resolution_id})")
            base_dir = Path(__file__).resolve().parent.parent
            year_dir = os.path.join(base_dir, 'data', 'aduana', str(args.year))
            print(f"📁 Los PDFs se guardaron en: {year_dir}/")
        else:
            print(f"❌ Error al guardar la resolución en la base de datos.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 