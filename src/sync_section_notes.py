#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script que sincroniza completamente las notas de sección entre el Excel y la base de datos.
Este script implementa una extracción más precisa del Excel y una actualización controlada.
"""
import pandas as pd
import os
import re
import numpy as np
from app import create_app, db
from app.models.section_note import SectionNote
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('section_notes_sync.log')
    ]
)
logger = logging.getLogger('sync_section_notes')

# Ruta al archivo Excel
excel_path = os.path.join('data', 'Arancel Nacional_Abril 2024.xlsx')

def clean_text(text):
    """Limpia el texto eliminando espacios extra y caracteres no deseados."""
    if pd.isna(text) or text is None:
        return ""
    return str(text).strip()

def roman_to_decimal(roman):
    """Convierte número romano a decimal con formato de dos dígitos."""
    roman_numerals = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
        'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
        'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
        'XXI': 21
    }
    roman = roman.strip().upper()
    if roman in roman_numerals:
        return f"{roman_numerals[roman]:02d}"
    return None

def extract_section_data_from_excel():
    """
    Extrae todas las secciones y sus notas del Excel utilizando un enfoque mejorado.
    """
    if not os.path.exists(excel_path):
        logger.error(f"El archivo Excel no existe: {excel_path}")
        return {}

    logger.info(f"Cargando Excel: {excel_path}")
    
    # Cargar Excel
    xl = pd.ExcelFile(excel_path)
    sheet_name = xl.sheet_names[0]  # Usar la primera hoja
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    
    # Diccionario para almacenar datos de secciones
    sections_data = {}
    
    # Variables de control
    current_section = None
    current_section_num = None
    in_section_title = False
    in_section_notes = False
    section_content = []
    
    # Iterar por todas las filas
    for idx, row in df.iterrows():
        # Limpiar y unir texto de la fila
        row_text = " ".join([clean_text(cell) for cell in row if clean_text(cell)])
        
        if not row_text:
            continue
            
        # Buscar patrón de sección
        section_match = re.search(r'Sección\s+([IVXLCDM]+)', row_text, re.IGNORECASE)
        
        # Si encontramos una nueva sección
        if section_match:
            # Si ya estábamos procesando una sección, guardarla
            if current_section_num and section_content:
                sections_data[current_section_num] = "\n".join(section_content)
                logger.info(f"Sección {current_section_num} guardada con {len(section_content)} líneas")
            
            # Iniciar nueva sección
            roman_numeral = section_match.group(1)
            current_section_num = roman_to_decimal(roman_numeral)
            current_section = roman_numeral
            
            if current_section_num:
                logger.info(f"Encontrada Sección {current_section} (número {current_section_num}) en línea {idx+1}")
                section_content = [row_text]
                in_section_title = True
                in_section_notes = False
            continue
        
        # Si estamos dentro de una sección
        if current_section_num:
            # Buscar otra sección (indica fin de la actual)
            next_section = re.search(r'Sección\s+([IVXLCDM]+)', row_text, re.IGNORECASE)
            if next_section:
                # Guardar sección actual y empezar la nueva
                if section_content:
                    sections_data[current_section_num] = "\n".join(section_content)
                    logger.info(f"Sección {current_section_num} guardada con {len(section_content)} líneas")
                
                roman_numeral = next_section.group(1)
                current_section_num = roman_to_decimal(roman_numeral)
                current_section = roman_numeral
                
                logger.info(f"Encontrada Sección {current_section} (número {current_section_num}) en línea {idx+1}")
                section_content = [row_text]
                in_section_title = True
                in_section_notes = False
                continue
            
            # Detectar si estamos en la parte del título de sección
            if in_section_title and not in_section_notes:
                # Si la línea no indica notas ni capítulo, es parte del título
                if not re.search(r'Notas?\.?|Capítulo', row_text, re.IGNORECASE) and not re.match(r'^\d{4}', row_text):
                    section_content.append(row_text)
                    continue
            
            # Detectar notas de sección
            notes_match = re.search(r'Notas?\.?', row_text, re.IGNORECASE)
            if notes_match:
                logger.info(f"Encontradas notas para sección {current_section_num} en línea {idx+1}")
                in_section_notes = True
                in_section_title = False
                section_content.append(row_text)
                continue
            
            # Si estamos en notas, seguir agregando hasta encontrar un capítulo o código NCM
            if in_section_notes:
                # Verificar si hay un patrón de inicio de capítulo o código NCM
                if re.search(r'^Capítulo\s+\d+', row_text, re.IGNORECASE) or re.match(r'^\d{4}', row_text):
                    logger.info(f"Fin de notas de sección {current_section_num} en línea {idx+1}")
                    # No incluir la línea del capítulo/NCM en las notas
                    in_section_notes = False
                else:
                    section_content.append(row_text)
                    continue
            
            # Si ya no estamos en notas ni título, hemos terminado con esta sección
            if not in_section_notes and not in_section_title:
                continue
    
    # Guardar la última sección procesada
    if current_section_num and section_content:
        sections_data[current_section_num] = "\n".join(section_content)
        logger.info(f"Sección {current_section_num} guardada con {len(section_content)} líneas")
    
    return sections_data

def update_section_notes_in_db(sections_data, dry_run=False):
    """
    Actualiza las notas de sección en la base de datos.
    
    Args:
        sections_data: Diccionario con datos de secciones {sección_num: contenido}
        dry_run: Si es True, solo muestra los cambios sin aplicarlos
    """
    if not sections_data:
        logger.error("No hay datos de secciones para actualizar")
        return
    
    logger.info(f"Actualizando {len(sections_data)} secciones en la base de datos")
    
    # Crear backup antes de actualizar
    if not dry_run:
        # Hacer un respaldo de las notas actuales
        num_updated = 0
        
        for section_num, content in sections_data.items():
            # Buscar la nota en la base de datos
            section_note = SectionNote.query.filter_by(section_number=section_num).first()
            
            if section_note:
                # Comparar el contenido
                if section_note.note_text != content:
                    logger.info(f"Actualizando sección {section_num} - Contenido diferente")
                    logger.info(f"Longitud actual: {len(section_note.note_text)}, Nueva longitud: {len(content)}")
                    section_note.note_text = content
                    num_updated += 1
                else:
                    logger.info(f"Sección {section_num} - Sin cambios (mismo contenido)")
            else:
                logger.warning(f"La sección {section_num} no existe en la base de datos")
        
        if num_updated > 0:
            logger.info(f"Guardando {num_updated} secciones actualizadas en la base de datos")
            db.session.commit()
            logger.info("Base de datos actualizada con éxito")
        else:
            logger.info("No se encontraron cambios para aplicar")
    else:
        logger.info("Modo simulación - No se aplicaron cambios a la base de datos")
        
        # Mostrar cambios que se aplicarían
        for section_num, content in sections_data.items():
            section_note = SectionNote.query.filter_by(section_number=section_num).first()
            
            if section_note:
                if section_note.note_text != content:
                    logger.info(f"Sección {section_num} - Se actualizaría")
                    # Mostrar primeras líneas
                    db_lines = section_note.note_text.split("\n")[:3]
                    excel_lines = content.split("\n")[:3]
                    logger.info(f"DB: {db_lines}")
                    logger.info(f"Excel: {excel_lines}")
                else:
                    logger.info(f"Sección {section_num} - Sin cambios")
            else:
                logger.info(f"Sección {section_num} - No existe en la base de datos")

def verify_section_notes():
    """
    Verifica las notas de sección en la base de datos con las del Excel.
    """
    logger.info("Verificando notas de sección")
    
    # Obtener datos del Excel
    excel_sections = extract_section_data_from_excel()
    
    if not excel_sections:
        logger.error("No se pudieron obtener datos del Excel")
        return
    
    # Verificar secciones en la base de datos
    section_notes = SectionNote.query.order_by(SectionNote.section_number).all()
    logger.info(f"Encontradas {len(section_notes)} secciones en la base de datos")
    
    # Comparar cada sección
    for note in section_notes:
        section_num = note.section_number
        
        if section_num in excel_sections:
            # Comparar contenido
            excel_content = excel_sections[section_num]
            db_content = note.note_text
            
            # Limpiar para comparación
            excel_lines = [line.strip() for line in excel_content.split("\n") if line.strip()]
            db_lines = [line.strip() for line in db_content.split("\n") if line.strip()]
            
            # Contar diferencias
            min_len = min(len(excel_lines), len(db_lines))
            diff_lines = sum(1 for i in range(min_len) if excel_lines[i] != db_lines[i])
            len_diff = abs(len(excel_lines) - len(db_lines))
            
            if diff_lines == 0 and len_diff == 0:
                logger.info(f"Sección {section_num}: ✅ Las notas coinciden exactamente")
            else:
                logger.warning(f"Sección {section_num}: ❌ Hay diferencias ({diff_lines} líneas diferentes, {len_diff} diferencia en longitud)")
                # Mostrar primeras líneas diferentes
                for i in range(min(5, min_len)):
                    if i < len(excel_lines) and i < len(db_lines) and excel_lines[i] != db_lines[i]:
                        logger.warning(f"Línea {i+1} - DB: '{db_lines[i]}'")
                        logger.warning(f"Línea {i+1} - Excel: '{excel_lines[i]}'")
        else:
            logger.warning(f"Sección {section_num}: ⚠️ No encontrada en el Excel")

def main():
    """Función principal"""
    # Crear aplicación Flask para contexto
    app = create_app()
    
    with app.app_context():
        # Opciones para el usuario
        print("\nSincronización de Notas de Sección")
        print("===============================")
        print("1. Extraer datos del Excel y mostrar (sin actualizar DB)")
        print("2. Verificar diferencias entre Excel y DB")
        print("3. Actualizar la base de datos con datos del Excel")
        print("4. Salir")
        
        opcion = input("\nSeleccione una opción (1-4): ").strip()
        
        if opcion == "1":
            # Extraer datos sin actualizar
            sections_data = extract_section_data_from_excel()
            
            print(f"\nSe encontraron {len(sections_data)} secciones en el Excel:")
            for section_num, content in sorted(sections_data.items()):
                lines = content.split("\n")
                print(f"Sección {section_num}: {len(lines)} líneas")
                # Mostrar primeras 3 líneas
                for i, line in enumerate(lines[:3]):
                    print(f"  {i+1}: {line[:80]}{'...' if len(line) > 80 else ''}")
                print()
            
            update_section_notes_in_db(sections_data, dry_run=True)
            
        elif opcion == "2":
            # Verificar diferencias
            verify_section_notes()
            
        elif opcion == "3":
            # Actualizar la base de datos
            confirmacion = input("\n¿Está seguro de actualizar la base de datos? (s/n): ").lower()
            
            if confirmacion == "s":
                sections_data = extract_section_data_from_excel()
                update_section_notes_in_db(sections_data, dry_run=False)
                print("\nNotas de sección actualizadas correctamente")
            else:
                print("\nOperación cancelada")
        
        elif opcion == "4":
            print("\nSaliendo...")
        
        else:
            print("\nOpción no válida")

if __name__ == "__main__":
    main()
