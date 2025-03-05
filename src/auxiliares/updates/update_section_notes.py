#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar las notas de sección en la base de datos con las encontradas en el Excel.
"""
import pandas as pd
import re
import os
import numpy as np
import sys
from app import create_app, db
from app.models.section_note import SectionNote
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('section_notes_update.log')
    ]
)
logger = logging.getLogger('update_section_notes')

# Ruta al archivo Excel
excel_path = os.path.join('data', 'Arancel Nacional_Abril 2024.xlsx')

def clean_row_text(row_values):
    """Limpia una fila de texto eliminando valores nulos y espacios extra."""
    clean_values = []
    for val in row_values:
        if val is not None and val != '' and not (isinstance(val, float) and np.isnan(val)):
            clean_values.append(str(val).strip())
    return " ".join(clean_values).strip()

def extract_section_notes_from_excel(section_number_roman):
    """Extrae las notas de una sección específica del Excel."""
    
    if not os.path.exists(excel_path):
        logger.error(f"¡Error! No se encontró el archivo Excel: {excel_path}")
        return "", []
    
    # Convertir número de sección decimal a número romano
    roman_numerals = {
        1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V',
        6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X',
        11: 'XI', 12: 'XII', 13: 'XIII', 14: 'XIV', 15: 'XV',
        16: 'XVI', 17: 'XVII', 18: 'XVIII', 19: 'XIX', 20: 'XX',
        21: 'XXI'
    }
    
    # Convertir el número de sección a entero e intentar conseguir su representación romana
    section_number = int(section_number_roman)
    section_roman = roman_numerals.get(section_number, "")
    
    if not section_roman:
        logger.error(f"¡Error! No se pudo convertir el número de sección {section_number} a romano.")
        return "", []
    
    # Variables para almacenar las notas de la sección
    section_notes = []
    in_target_section = False
    capturing_notes = False
    section_title = ""
    
    # Leer el archivo Excel
    logger.info(f"Buscando sección {section_roman} en el Excel...")
    # Primero obtenemos los nombres de las hojas
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names
    
    if not sheet_names:
        logger.error("No se encontraron hojas en el Excel.")
        return "", []
    
    # Por lo general, la primera hoja contiene los datos
    df = pd.read_excel(excel_path, sheet_name=sheet_names[0], header=None)
    
    chapter_notes = []  # Para almacenar las notas de capítulo que también pertenecen a esta sección
    current_chapter = None
    current_chapter_notes = []
    
    # Iteramos por las filas para encontrar la sección objetivo
    for i, row in df.iterrows():
        # Limpiamos la fila
        row_text = clean_row_text(row)
        
        if not row_text:  # Saltamos filas vacías
            continue
            
        # Verificamos si encontramos la sección objetivo
        section_pattern = fr'Sección\s+{section_roman}\b|SECCION\s+{section_roman}\b|SECCIÓN\s+{section_roman}\b'
        section_match = re.search(section_pattern, row_text, re.IGNORECASE)
        if section_match:
            logger.info(f"Encontrada Sección {section_roman} en fila {i+1}: {row_text}")
            in_target_section = True
            section_title = row_text
            
            # Buscamos la siguiente fila para obtener el título completo
            if i + 1 < len(df):
                next_row_text = clean_row_text(df.iloc[i+1])
                if next_row_text and not re.search(r'Notas\.?|NOTAS\.?', next_row_text, re.IGNORECASE):
                    section_title += "\n" + next_row_text
            continue
        
        # Verificamos si encontramos otra sección (lo que indicaría el final de la sección actual)
        next_section_match = re.search(r'Sección\s+[IVXLCDM]+\b|SECCION\s+[IVXLCDM]+\b|SECCIÓN\s+[IVXLCDM]+\b', row_text, re.IGNORECASE)
        if in_target_section and next_section_match:
            logger.info(f"Encontrada siguiente sección en fila {i+1}, finalizando captura.")
            in_target_section = False
            capturing_notes = False
            break
        
        # Si estamos en la sección objetivo, verificamos si son notas
        if in_target_section:
            # Verificamos si encontramos las notas
            if re.search(r'Notas\.?|NOTAS\.?', row_text, re.IGNORECASE):
                logger.info(f"Encontradas notas en fila {i+1}: {row_text}")
                capturing_notes = True
                section_notes.append(row_text)
                continue
            
            # Si estamos capturando notas, las agregamos
            if capturing_notes:
                # Verificamos si hemos llegado al final de las notas (inicio de Capítulo)
                chapter_match = re.search(r'Capítulo\s+(\d+)|CAPITULO\s+(\d+)|CAPÍTULO\s+(\d+)', row_text, re.IGNORECASE)
                if chapter_match:
                    logger.info(f"Encontrado Capítulo en fila {i+1}: {row_text}")
                    
                    # Añadimos la línea del capítulo a las notas de la sección
                    section_notes.append(row_text)
                    
                    # Inicializamos las variables para capturar las notas del capítulo
                    current_chapter = row_text
                    current_chapter_notes = []
                    
                    # Continuamos para buscar las notas del capítulo
                    continue
                
                # Si ya estamos en un capítulo de esta sección, capturamos también sus notas
                if current_chapter:
                    # Verificamos si encontramos la nota del capítulo
                    if re.search(r'Nota\.?|NOTA\.?', row_text, re.IGNORECASE):
                        current_chapter_notes.append(row_text)
                        continue
                    
                    # Si ya estamos capturando notas del capítulo
                    if current_chapter_notes:
                        # Verificamos si hemos llegado al final de las notas del capítulo (NCM o siguiente capítulo)
                        if re.match(r'^\d{4}', row_text) or re.search(r'Capítulo\s+\d+|CAPITULO\s+\d+|CAPÍTULO\s+\d+', row_text, re.IGNORECASE):
                            # Añadimos las notas del capítulo a las notas de la sección
                            section_notes.extend(current_chapter_notes)
                            # Reiniciamos para el siguiente capítulo
                            if re.search(r'Capítulo\s+\d+|CAPITULO\s+\d+|CAPÍTULO\s+\d+', row_text, re.IGNORECASE):
                                current_chapter = row_text
                                current_chapter_notes = []
                            else:
                                # Si es un NCM, hemos terminado con este capítulo
                                section_notes.append(row_text)  # Añadimos la línea del NCM
                                break
                        else:
                            # Seguir capturando las notas del capítulo
                            current_chapter_notes.append(row_text)
                else:
                    # Agregar la línea a las notas
                    section_notes.append(row_text)
    
    # Combinamos el título con las notas
    if section_title and section_notes:
        return section_title, section_notes
    else:
        return "", []

def update_section_note(section_number, note_text):
    """Actualiza la nota de sección en la base de datos."""
    section_note = SectionNote.query.filter_by(section_number=section_number.zfill(2)).first()
    
    if section_note:
        logger.info(f"Actualizando nota para sección {section_number}...")
        section_note.note_text = note_text
        db.session.commit()
        return True
    else:
        logger.error(f"No se encontró la nota para la sección {section_number} en la base de datos.")
        return False

def main():
    # Crear una aplicación Flask para el contexto de SQLAlchemy
    app = create_app()
    
    with app.app_context():
        # Obtener todas las notas de sección de la base de datos
        section_notes = SectionNote.query.order_by(SectionNote.section_number).all()
        
        logger.info(f"Encontradas {len(section_notes)} notas de sección en la base de datos.")
        
        # Preguntar al usuario si desea actualizar todas las notas
        update_all = input("¿Desea actualizar todas las notas de sección? (s/n): ").lower() == 's'
        
        # Si no se actualizan todas, preguntar cuáles
        sections_to_update = []
        if not update_all:
            sections_input = input("Ingrese los números de sección que desea actualizar (separados por comas, ej: 1,2,5): ")
            sections_to_update = [s.strip() for s in sections_input.split(',') if s.strip()]
        
        # Procesar cada sección
        updated_sections = 0
        for section_note in section_notes:
            section_number = section_note.section_number
            section_int = int(section_number)
            
            # Verificar si se debe actualizar esta sección
            if not update_all and str(section_int) not in sections_to_update:
                logger.info(f"Saltando Sección {section_number}...")
                continue
            
            logger.info(f"Procesando Sección {section_number}...")
            
            # Extraer las notas de la sección del Excel
            excel_title, excel_notes = extract_section_notes_from_excel(section_int)
            
            if excel_title and excel_notes:
                # Combinar las notas extraídas
                excel_notes_text = excel_title + "\n" + "\n".join(excel_notes)
                
                # Mostrar un resumen de las diferencias
                excel_lines = excel_notes_text.strip().split('\n')
                db_lines = section_note.note_text.strip().split('\n')
                
                # Contar líneas diferentes
                excel_lines_clean = [line.strip() for line in excel_lines if line.strip()]
                db_lines_clean = [line.strip() for line in db_lines if line.strip()]
                
                min_lines = min(len(excel_lines_clean), len(db_lines_clean))
                differences = 0
                
                for i in range(min_lines):
                    if excel_lines_clean[i] != db_lines_clean[i]:
                        differences += 1
                
                # Calcular diferencia en longitud
                length_diff = abs(len(excel_lines_clean) - len(db_lines_clean))
                
                if differences == 0 and length_diff == 0:
                    logger.info(f"Las notas de la Sección {section_number} no tienen diferencias, no es necesario actualizar.")
                    continue
                
                # Mostrar un preview de las diferencias
                logger.info(f"La Sección {section_number} tiene {differences} líneas diferentes y {length_diff} líneas de diferencia en longitud.")
                
                # Confirmar la actualización
                confirm_update = True
                if not update_all:
                    confirm_update = input(f"¿Confirma la actualización de la Sección {section_number}? (s/n): ").lower() == 's'
                
                if confirm_update:
                    if update_section_note(section_number, excel_notes_text):
                        updated_sections += 1
                        logger.info(f"Sección {section_number} actualizada correctamente.")
                    else:
                        logger.error(f"No se pudo actualizar la Sección {section_number}.")
                else:
                    logger.info(f"Actualización de la Sección {section_number} cancelada por el usuario.")
            else:
                logger.warning(f"No se encontraron notas para la Sección {section_number} en el Excel.")
        
        logger.info(f"Proceso completado. Se actualizaron {updated_sections} secciones.")

if __name__ == "__main__":
    main()
