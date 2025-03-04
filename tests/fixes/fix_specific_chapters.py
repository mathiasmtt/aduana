#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corregir específicamente las notas de los capítulos con problemas
que siguen mostrando contenido incorrecto a pesar de las correcciones anteriores.
Este script utiliza una búsqueda más precisa en el archivo Excel y garantiza
que el contenido correcto se almacene en la base de datos.
"""

import os
import re
import sys
import pandas as pd
from app import db, create_app
from app.models.chapter_note import ChapterNote

def find_chapter_in_excel(df, chapter_number):
    """
    Busca la posición exacta de un capítulo en el Excel utilizando una búsqueda
    más precisa para evitar falsos positivos.
    
    Args:
        df (DataFrame): DataFrame de pandas con el contenido del Excel
        chapter_number (str): Número de capítulo (con o sin ceros iniciales)
        
    Returns:
        int: Índice de la fila donde comienza el capítulo, o -1 si no se encuentra
    """
    # Convertir a entero para eliminar ceros iniciales en la búsqueda
    chapter_int = int(chapter_number)
    
    # Patrón exacto para el encabezado del capítulo
    exact_pattern = f"Capítulo {chapter_int}"
    
    # Primero, búsqueda general para encontrar todas las menciones al capítulo
    potential_matches = []
    for i in range(len(df)):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if exact_pattern in cell_value:
            # Verificar que sea un encabezado de capítulo y no una referencia
            if cell_value.strip() == exact_pattern or cell_value.strip().startswith(exact_pattern + "\n"):
                potential_matches.append(i)
            # También considerar los casos donde hay un número de capítulo y luego texto
            elif re.match(rf'^{exact_pattern}\s', cell_value):
                potential_matches.append(i)
    
    if not potential_matches:
        return -1
    
    # Si hay múltiples coincidencias, usar heurísticas para encontrar la correcta
    if len(potential_matches) > 1:
        # Para el capítulo 39, sabemos que debe estar cerca de la fila 8300
        if chapter_int == 39:
            for idx in potential_matches:
                if 8250 <= idx <= 8350:
                    return idx
        # Para el capítulo 95, sabemos que debe estar cerca de la fila 20100
        elif chapter_int == 95:
            for idx in potential_matches:
                if 20050 <= idx <= 20150:
                    return idx
        # Para el capítulo 90, sabemos que debe estar cerca de la fila 19500
        elif chapter_int == 90:
            for idx in potential_matches:
                if 19450 <= idx <= 19550:
                    return idx
    
    # Si no hay coincidencias especiales, usar la primera coincidencia
    return potential_matches[0] if potential_matches else -1

def extract_chapter_content(df, start_row):
    """
    Extrae todo el contenido de un capítulo a partir de su fila inicial.
    
    Args:
        df (DataFrame): DataFrame de pandas con el contenido del Excel
        start_row (int): Fila donde comienza el capítulo
        
    Returns:
        str: Contenido completo del capítulo
    """
    content_lines = []
    
    # Obtener el encabezado del capítulo
    header = str(df.iloc[start_row, 0]) if pd.notna(df.iloc[start_row, 0]) else ""
    content_lines.append(header)
    
    # Extraer todas las líneas hasta encontrar el siguiente capítulo o NCM
    for i in range(start_row + 1, min(start_row + 500, len(df))):
        cell_value = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        
        # Detener la extracción si encontramos el siguiente capítulo
        if re.match(r'^Capítulo\s+\d+', cell_value) and i > start_row + 2:
            break
        
        # Detener la extracción si encontramos códigos NCM
        if re.match(r'^\d{2}\.\d{2}', cell_value) or cell_value.strip() == "NCM":
            break
        
        # Agregar la línea si tiene contenido
        if cell_value.strip():
            content_lines.append(cell_value)
    
    return '\n'.join(content_lines)

def fix_specific_chapters(chapters=None):
    """
    Corrige específicamente las notas de los capítulos con problemas
    
    Args:
        chapters (list): Lista de capítulos a corregir. Si es None, se corrigen los capítulos 39 y 95.
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    print(f"Leyendo archivo Excel: {file_path}")
    
    # Leer el archivo Excel
    df = pd.read_excel(file_path, header=None)
    
    # Si no se especifican capítulos, usar los predeterminados
    if not chapters:
        chapters_to_fix = ["39", "95"]
    else:
        chapters_to_fix = chapters
    
    app = create_app()
    with app.app_context():
        for chapter in chapters_to_fix:
            print(f"\n{'=' * 80}")
            print(f"Procesando capítulo {chapter}...")
            
            # Encontrar la posición del capítulo en el Excel
            chapter_row = find_chapter_in_excel(df, chapter)
            
            if chapter_row == -1:
                print(f"  ❌ ERROR: No se pudo encontrar el capítulo {chapter} en el Excel")
                continue
            
            print(f"  ✅ Capítulo {chapter} encontrado en la fila {chapter_row}")
            
            # Extraer el contenido completo del capítulo
            chapter_content = extract_chapter_content(df, chapter_row)
            
            # Verificar que el contenido sea apropiado para el capítulo
            content_valid = True
            if chapter == "39" and "plástico" not in chapter_content.lower():
                content_valid = False
            elif chapter == "95" and "juguetes" not in chapter_content.lower():
                content_valid = False
            elif chapter == "90" and "instrumentos" not in chapter_content.lower() and "óptica" not in chapter_content.lower():
                content_valid = False
            
            if not content_valid:
                print(f"  ❌ ADVERTENCIA: El contenido extraído no parece ser apropiado para el capítulo {chapter}")
                print(f"  Primeros 100 caracteres: {chapter_content[:100]}...")
                continue
            
            # Buscar la nota en la base de datos
            chapter_note = ChapterNote.query.filter_by(chapter_number=chapter).first()
            
            if not chapter_note:
                print(f"  ⚠️ No se encontró nota para el capítulo {chapter} en la base de datos")
                print(f"  Creando nueva entrada...")
                chapter_note = ChapterNote(chapter_number=chapter, note_text=chapter_content)
                db.session.add(chapter_note)
            else:
                print(f"  Actualizando nota existente del capítulo {chapter}...")
                chapter_note.note_text = chapter_content
            
            db.session.commit()
            print(f"  ✅ Nota del capítulo {chapter} actualizada correctamente")
            
            # Mostrar primeros caracteres de la nota
            print(f"  Primeros 200 caracteres de la nota actualizada:")
            print(f"  {chapter_content[:200]}...")
    
    print(f"\n{'=' * 80}")
    print("Proceso completado. Verificando resultados:")
    
    # Verificar resultados
    with app.app_context():
        for chapter in chapters_to_fix:
            note = ChapterNote.query.filter_by(chapter_number=chapter).first()
            if note:
                print(f"\nCapítulo {chapter}:")
                print(f"  {note.note_text[:100]}...")
                
                # Verificar contenido
                if chapter == "39" and "plástico" in note.note_text.lower():
                    print(f"  ✅ CORRECTO: La nota contiene la palabra 'plástico'")
                elif chapter == "95" and "juguetes" in note.note_text.lower():
                    print(f"  ✅ CORRECTO: La nota contiene la palabra 'juguetes'")
                elif chapter == "90" and ("instrumentos" in note.note_text.lower() or "óptica" in note.note_text.lower()):
                    print(f"  ✅ CORRECTO: La nota contiene palabras clave para el capítulo 90")
                else:
                    print(f"  ❌ ERROR: La nota NO contiene las palabras clave esperadas")

if __name__ == "__main__":
    # Si se proporcionan argumentos, usarlos como capítulos a corregir
    if len(sys.argv) > 1:
        chapters_to_fix = sys.argv[1:]
        fix_specific_chapters(chapters_to_fix)
    else:
        fix_specific_chapters()
