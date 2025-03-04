#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar las notas de capítulo para una muestra aleatoria de códigos NCM.
Compara las notas que devuelve la base de datos con las que deberían existir según el archivo Excel.
"""

import os
import random
import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
from app import create_app
from app.models.chapter_note import ChapterNote

def similarity(a, b):
    """
    Calcula la similitud entre dos cadenas de texto.
    """
    if not a or not b:
        return 0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

def clean_text(text):
    """
    Limpia el texto para una mejor comparación.
    Elimina espacios, tabulaciones y saltos de línea extras.
    """
    if not text:
        return ""
    # Reemplazar múltiples espacios, tabulaciones y saltos de línea por un solo espacio
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    return text.strip()

def find_chapter_in_excel(df, chapter_number):
    """
    Encuentra las notas para un capítulo específico en el archivo Excel.
    
    Args:
        df (DataFrame): DataFrame de pandas con el contenido del Excel
        chapter_number (str): Número de capítulo a buscar
        
    Returns:
        str: Texto de las notas del capítulo o None si no se encuentra
    """
    # Convertir a entero y luego de vuelta a string para manejar ceros iniciales
    chapter_int = int(chapter_number)
    chapter_pattern = f"Capítulo {chapter_int}"
    
    # Buscar el patrón exacto
    chapter_start = None
    for i in range(len(df)):
        cell = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if chapter_pattern in cell and (cell.strip() == chapter_pattern or 
                                        cell.strip().startswith(chapter_pattern + "\n") or
                                        re.match(rf'^{chapter_pattern}\s', cell)):
            chapter_start = i
            break
    
    if chapter_start is None:
        return None
    
    # Recopilar todo el contenido del capítulo hasta encontrar otro capítulo o códigos NCM
    content = []
    for i in range(chapter_start, min(chapter_start + 500, len(df))):
        cell = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        if i > chapter_start and (re.match(r'^Capítulo\s+\d+', cell) or 
                                 re.match(r'^\d{2}\.\d{2}', cell) or 
                                 cell.strip() == "NCM"):
            break
        if cell.strip():
            content.append(cell)
    
    if not content:
        return None
    
    return "\n".join(content)

def extract_all_ncm_codes(file_path):
    """
    Extrae todos los códigos NCM del archivo Excel.
    
    Args:
        file_path (str): Ruta al archivo Excel
        
    Returns:
        list: Lista de códigos NCM únicos
    """
    print(f"Extrayendo todos los códigos NCM de {file_path}...")
    df = pd.read_excel(file_path, header=None)
    
    ncm_codes = []
    for i in range(len(df)):
        cell = str(df.iloc[i, 0]) if pd.notna(df.iloc[i, 0]) else ""
        # Buscar patrones como "84.21" (código NCM de 4 dígitos)
        if re.match(r'^\d{2}\.\d{2}', cell):
            # Intentar encontrar el código NCM completo en la fila actual o en las siguientes
            for j in range(i, min(i + 20, len(df))):
                row = df.iloc[j]
                for col in range(len(row)):
                    if pd.notna(row[col]):
                        cell_value = str(row[col])
                        # Buscar códigos NCM de 8 dígitos (ej. 8421.29.90)
                        matches = re.findall(r'\d{4}\.\d{2}\.\d{2}', cell_value)
                        if matches:
                            for match in matches:
                                ncm_code = match.replace('.', '')
                                if len(ncm_code) == 8:
                                    ncm_codes.append(ncm_code)
    
    # Eliminar duplicados y ordenar
    unique_ncm_codes = sorted(list(set(ncm_codes)))
    print(f"Se encontraron {len(unique_ncm_codes)} códigos NCM válidos")
    return unique_ncm_codes

def verify_random_ncm_notes(n=20):
    """
    Verifica las notas de capítulo para n códigos NCM aleatorios,
    comparando las notas en la base de datos con las del archivo Excel.
    
    Args:
        n (int): Número de códigos NCM aleatorios a verificar
    """
    file_path = os.path.join("data", "Arancel Nacional_Abril 2024.xlsx")
    
    # Extraer todos los códigos NCM del archivo Excel
    all_ncm_codes = extract_all_ncm_codes(file_path)
    
    # Seleccionar n códigos NCM aleatorios
    if n > len(all_ncm_codes):
        n = len(all_ncm_codes)
    random_ncm_codes = random.sample(all_ncm_codes, n)
    
    # Leer el archivo Excel para buscar las notas
    print(f"\nVerificando {n} NCM aleatorios...\n")
    df = pd.read_excel(file_path, header=None)
    
    app = create_app()
    
    # Contador para estadísticas
    match_count = 0
    mismatch_count = 0
    missing_count = 0
    
    with app.app_context():
        for ncm in random_ncm_codes:
            print(f"{'=' * 80}")
            print(f"Verificando NCM: {ncm}")
            
            # Obtener el capítulo correspondiente al NCM (primeros 2 dígitos)
            chapter = ncm[:2]
            
            # Obtener la nota de la base de datos
            db_note = ChapterNote.get_note_by_ncm(ncm)
            
            # Encontrar la nota en el Excel
            excel_note = find_chapter_in_excel(df, chapter)
            
            # Mostrar extractos de las notas y compararlas
            if db_note:
                db_excerpt = db_note[:100] + "..." if len(db_note) > 100 else db_note
                print(f"Nota en BD para capítulo {chapter} (NCM {ncm}):")
                print(f"  {db_excerpt}")
            else:
                print(f"⚠️ No se encontró nota en la BD para el capítulo {chapter} (NCM {ncm})")
            
            if excel_note:
                excel_excerpt = excel_note[:100] + "..." if len(excel_note) > 100 else excel_note
                print(f"Nota en Excel para capítulo {chapter}:")
                print(f"  {excel_excerpt}")
            else:
                print(f"⚠️ No se encontró nota en el Excel para el capítulo {chapter}")
            
            # Verificar si las notas coinciden o no
            if db_note and excel_note:
                # Limpiar textos para una mejor comparación
                clean_db = clean_text(db_note[:100])
                clean_excel = clean_text(excel_note[:100])
                
                # Calcular similitud
                sim_percent = similarity(clean_db, clean_excel)
                
                if sim_percent >= 75:  # Umbral de similitud
                    print(f"✅ COINCIDE: Las notas coinciden en los primeros 100 caracteres")
                    match_count += 1
                else:
                    print(f"❌ NO COINCIDE: Las notas NO coinciden en los primeros 100 caracteres")
                    print(f"  Similitud: {sim_percent:.2f}%")
                    mismatch_count += 1
            elif not db_note and not excel_note:
                print(f"⚠️ No se encontraron notas ni en la BD ni en el Excel")
                missing_count += 1
            else:
                print(f"⚠️ La nota solo existe en {'la BD' if db_note else 'el Excel'}")
                missing_count += 1
    
    # Mostrar resumen
    print(f"\n{'=' * 80}")
    print(f"Resumen de verificación de {n} NCM aleatorios:")
    print(f"  ✅ Coinciden: {match_count}")
    print(f"  ❌ No coinciden: {mismatch_count}")
    print(f"  ⚠️ Sin notas: {missing_count}")

if __name__ == "__main__":
    verify_random_ncm_notes(20)
