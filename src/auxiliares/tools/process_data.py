import pandas as pd
import sqlite3
import logging
import numpy as np
import re
import os

# Configurar logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_valid_ncm(code):
    """Verifica si un código NCM es válido"""
    if pd.isna(code):
        return False
    code_str = str(code).strip()
    # Verifica si es un código NCM completo (ej: 0101.21.00.00)
    pattern = r'^\d{4}\.\d{2}\.\d{2}\.\d{2}$'
    return bool(re.match(pattern, code_str))

def is_section(text):
    """Verifica si una línea es un título de sección"""
    if pd.isna(text):
        return False
    text = str(text).strip().lower()
    # Buscar patrones como "SECCION I" o "Sección II"
    return bool(re.match(r'^secci[oó]n\s+[ivxlcdm]+\b', text, re.IGNORECASE))

def is_chapter(text):
    """Verifica si una línea es un título de capítulo"""
    if pd.isna(text):
        return False
    text = str(text).strip().lower()
    # Buscar patrones como "Capítulo 1" o "CAPITULO 2"
    return bool(re.match(r'^cap[ií]tulo\s+\d+\b', text, re.IGNORECASE))

def clean_text(text):
    """Limpia y normaliza el texto"""
    if pd.isna(text):
        return ""
    return str(text).strip()

def process_excel_data():
    # Rutas de los archivos
    excel_path = "data/Arancel Nacional_Abril 2024.xlsx"
    db_path = "data/database.sqlite3"
    
    try:
        # Configurar logging más detallado
        logger.setLevel(logging.DEBUG)
        
        # Crear directorio de datos si no existe
        os.makedirs("data", exist_ok=True)
        
        # Leer el archivo Excel de referencia
        logger.info(f"Leyendo archivo Excel de referencia desde {excel_path}...")
        df = pd.read_excel(excel_path, header=None)
        
        # Inicializar variables para extraer datos
        valid_rows = []
        current_section = ""
        current_chapter = ""
        ncm_col = None
        desc_col = None
        aec_col = None
        cl_col = None
        ez_col = None
        iz_col = None
        uvf_col = None
        
        # Procesar el archivo línea por línea
        last_valid_ncm = None
        last_valid_desc = None
        
        for idx, row in df.iterrows():
            # Convertir fila a texto para análisis
            row_str = ' '.join([str(cell) for cell in row if not pd.isna(cell)])
            
            # Buscar encabezados de secciones y capítulos
            if is_section(row_str):
                # Extrae el nombre de la sección
                section_match = re.search(r'(secci[oó]n\s+[ivxlcdm]+)\s+(.*)', row_str, re.IGNORECASE)
                if section_match:
                    section_id = section_match.group(1).upper()
                    section_name = section_match.group(2).strip()
                    current_section = f"{section_id} - {section_name}"
                    logger.info(f"Sección encontrada: {current_section}")
                
            elif is_chapter(row_str):
                # Extrae el nombre del capítulo
                chapter_match = re.search(r'(cap[ií]tulo\s+\d+)\s+(.*)', row_str, re.IGNORECASE)
                if chapter_match:
                    chapter_id = chapter_match.group(1).title()
                    chapter_name = chapter_match.group(2).strip()
                    current_chapter = f"{chapter_id} - {chapter_name}"
                    logger.info(f"Capítulo encontrado: {current_chapter}")
            
            # Intentar identificar código NCM y su descripción
            for col_idx, cell in enumerate(row):
                cell_str = str(cell).strip() if not pd.isna(cell) else ""
                
                # Si encontramos un código NCM
                if is_valid_ncm(cell_str):
                    logger.debug(f"NCM encontrado en fila {idx}, columna {col_idx}: {cell_str}")
                    last_valid_ncm = cell_str
                    
                    # Buscar descripción en la misma fila
                    desc = ""
                    aec = ""
                    cl = ""
                    ez = ""
                    iz = ""
                    uvf = ""
                    
                    # Intentar extraer datos de la fila actual basado en la posición
                    if col_idx + 1 < len(row) and not pd.isna(row[col_idx + 1]):
                        desc = str(row[col_idx + 1]).strip()
                    
                    # Intentar obtener otros datos si están disponibles
                    if col_idx + 2 < len(row) and not pd.isna(row[col_idx + 2]):
                        aec = str(row[col_idx + 2]).strip()
                    
                    if col_idx + 3 < len(row) and not pd.isna(row[col_idx + 3]):
                        cl = str(row[col_idx + 3]).strip()
                    
                    if col_idx + 4 < len(row) and not pd.isna(row[col_idx + 4]):
                        ez = str(row[col_idx + 4]).strip()
                    
                    if col_idx + 5 < len(row) and not pd.isna(row[col_idx + 5]):
                        iz = str(row[col_idx + 5]).strip()
                    
                    if col_idx + 6 < len(row) and not pd.isna(row[col_idx + 6]):
                        uvf = str(row[col_idx + 6]).strip()
                    
                    # Si hay descripción, guardarla como la última válida
                    if desc:
                        last_valid_desc = desc
                    
                    # Agregar a los datos válidos
                    valid_rows.append({
                        'NCM': last_valid_ncm,
                        'DESCRIPCION': desc or last_valid_desc or "",
                        'AEC': aec or "0",
                        'CL': cl or "",
                        'E/Z': ez or "",
                        'I/Z': iz or "",
                        'UVF': uvf or "",
                        'SECTION': current_section,
                        'CHAPTER': current_chapter
                    })
                    
                    logger.debug(f"Datos extraídos: NCM={last_valid_ncm}, DESC={desc}, AEC={aec}, SECTION={current_section}, CHAPTER={current_chapter}")
                    
                    # Salir del bucle para esta fila
                    break
        
        # Crear DataFrame con los datos procesados
        processed_df = pd.DataFrame(valid_rows)
        
        # Verificar que tenemos datos para procesar
        if processed_df.empty:
            logger.error("No se encontraron datos válidos en el archivo Excel.")
            return
        
        logger.info(f"Se procesaron {len(processed_df)} filas con códigos NCM válidos.")
        
        # Conectar a la base de datos SQLite
        logger.info("Conectando a la base de datos SQLite...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        create_table_query = """
        CREATE TABLE IF NOT EXISTS arancel_nacional (
            NCM TEXT NOT NULL,
            DESCRIPCION TEXT,
            AEC TEXT,
            CL TEXT,
            "E/Z" TEXT,
            "I/Z" TEXT,
            UVF TEXT,
            SECTION TEXT,
            CHAPTER TEXT
        )
        """
        cursor.execute(create_table_query)
        
        # Eliminar datos previos
        cursor.execute("DELETE FROM arancel_nacional")
        
        # Insertar datos
        logger.info("Guardando datos procesados en la base de datos...")
        for _, row in processed_df.iterrows():
            cursor.execute(
                'INSERT INTO arancel_nacional (NCM, DESCRIPCION, AEC, CL, "E/Z", "I/Z", UVF, SECTION, CHAPTER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    row['NCM'], 
                    row['DESCRIPCION'], 
                    row['AEC'], 
                    row['CL'], 
                    row['E/Z'], 
                    row['I/Z'], 
                    row['UVF'], 
                    row['SECTION'], 
                    row['CHAPTER']
                )
            )
        
        # Guardar cambios
        conn.commit()
        
        # Verificar cantidad de registros insertados
        cursor.execute("SELECT COUNT(*) FROM arancel_nacional")
        count = cursor.fetchone()[0]
        logger.info(f"Se insertaron {count} registros en la base de datos.")
        
        logger.info("Proceso completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error durante el proceso: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    process_excel_data()

if __name__ == "__main__":
    main()