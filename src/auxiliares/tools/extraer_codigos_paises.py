import os
import re
import argparse
import PyPDF2
import json
import sys
import sqlite3
from pathlib import Path

def extraer_codigos_paises_de_pdf(pdf_path):
    """
    Extrae códigos de países de un archivo PDF.
    
    Args:
        pdf_path (str): Ruta al archivo PDF con los códigos de países.
        
    Returns:
        list: Lista de diccionarios con los códigos de países.
    """
    print(f"Extrayendo datos del PDF: {pdf_path}")
    codigos_paises = []
    
    try:
        # Abrir el PDF
        with open(pdf_path, 'rb') as file:
            # Crear un objeto PDF reader
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extraer texto de todas las páginas
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Eliminar encabezados y pies de página que puedan interferir
            text = re.sub(r'CLASIFICADOR DE PAÍSES.*', '', text, flags=re.IGNORECASE)
            
            # Patrón para capturar códigos de países: código numérico, nombre y código de letras
            pattern = r'(\d{3})\s+([\w\s\.,\-\'\(\)]+?)\s+([A-Z]{3})'
            
            # Buscar todas las coincidencias en el texto completo
            matches = re.findall(pattern, text)
            
            # Procesar cada coincidencia
            for match in matches:
                codigo_num = match[0].strip()
                nombre = match[1].strip()
                codigo_letras = match[2].strip()
                
                # Validar que los datos no estén vacíos
                if codigo_num and nombre and codigo_letras:
                    # Asegurar que codigo_num siempre tenga 3 dígitos
                    codigo_num = codigo_num.zfill(3)
                    
                    # Verificar que no exceda los 3 dígitos
                    if len(codigo_num) > 3:
                        print(f"Advertencia: El código numérico '{codigo_num}' excede los 3 dígitos. Se usarán los últimos 3.")
                        codigo_num = codigo_num[-3:]
                    
                    # Limpiar el nombre para eliminar posibles caracteres especiales o espacios extras
                    nombre = re.sub(r'\s+', ' ', nombre).strip()
                    # Eliminar cualquier texto "CLASIFICADOR DE" al final del nombre
                    nombre = re.sub(r'CLASIFICADOR DE.*$', '', nombre).strip()
                    
                    # Verificar si es una zona franca (código entre 898 y 997)
                    codigo_num_int = int(codigo_num)
                    if 898 <= codigo_num_int <= 997:
                        codigo_letras = "ZFF"  # Código específico para zonas francas
                    
                    # Verificar si el nombre contiene otro código numérico (caso de zonas francas concatenadas)
                    if re.search(r'\d{3}\s+', nombre):
                        # Extraer el primer nombre antes del siguiente código
                        nombre_limpio = re.sub(r'\d{3}.*', '', nombre).strip()
                        
                        # Verificar si es una zona franca (código entre 898 y 997)
                        if 898 <= codigo_num_int <= 997:
                            codigos_paises.append({
                                'codigo_num': codigo_num,
                                'nombre': nombre_limpio,
                                'codigo_letras': "ZFF"
                            })
                        else:
                            codigos_paises.append({
                                'codigo_num': codigo_num,
                                'nombre': nombre_limpio,
                                'codigo_letras': codigo_letras
                            })
                        
                        # Extraer las zonas francas adicionales
                        zonas_pattern = r'(\d{3})\s+(Zonas?\s+Francas?\s+[\w\s\.,\-\'\(\)]+?)(?=\d{3}|\s+[A-Z]{3}|$)'
                        zonas_matches = re.findall(zonas_pattern, nombre)
                        for zona_match in zonas_matches:
                            if len(zona_match) == 2:
                                zona_codigo = zona_match[0].strip()
                                zona_nombre = zona_match[1].strip()
                                
                                # Eliminar cualquier texto "CLASIFICADOR DE" al final del nombre
                                zona_nombre = re.sub(r'CLASIFICADOR DE.*$', '', zona_nombre).strip()
                                
                                # Validar que los datos no estén vacíos
                                if zona_codigo and zona_nombre:
                                    # Asegurar que zona_codigo siempre tenga 3 dígitos
                                    zona_codigo = zona_codigo.zfill(3)
                                    
                                    # Verificar si es una zona franca (código entre 898 y 997)
                                    zona_codigo_int = int(zona_codigo)
                                    if 898 <= zona_codigo_int <= 997:
                                        codigos_paises.append({
                                            'codigo_num': zona_codigo,
                                            'nombre': zona_nombre,
                                            'codigo_letras': "ZFF"
                                        })
                                    else:
                                        codigos_paises.append({
                                            'codigo_num': zona_codigo,
                                            'nombre': zona_nombre,
                                            'codigo_letras': "ZON"
                                        })
                    else:
                        codigos_paises.append({
                            'codigo_num': codigo_num,
                            'nombre': nombre,
                            'codigo_letras': codigo_letras
                        })
    
    except Exception as e:
        print(f"Error al procesar el PDF: {e}")
        return []
    
    print(f"Se han encontrado {len(codigos_paises)} códigos de países.")
    return codigos_paises

def cargar_codigos_paises_sqlite(paises_data):
    """
    Carga los códigos de países en la tabla CODIGO_PAISES usando SQLite directamente.
    
    Args:
        paises_data (list): Lista de diccionarios con los datos de los países (codigo_num, nombre, codigo_letras)
    """
    print("Cargando códigos de países en la base de datos...")
    
    # Obtener la ruta de la base de datos
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    db_path = base_dir / 'data' / 'auxiliares.sqlite3'
    
    if not db_path.exists():
        print(f"ERROR: La base de datos {db_path} no existe.")
        return False
    
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Eliminar registros existentes
        cursor.execute("DELETE FROM CODIGO_PAISES")
        
        # Verificar si hay códigos de letras duplicados
        codigos_letras = {}
        for pais in paises_data:
            codigo_letras = pais['codigo_letras']
            if codigo_letras in codigos_letras:
                # Si ya existe, modificar el código de letras para hacerlo único
                print(f"Advertencia: Código de letras duplicado '{codigo_letras}' para '{pais['nombre']}' y '{codigos_letras[codigo_letras]}'. Se modificará para hacerlo único.")
                # Agregar un sufijo numérico para hacerlo único
                i = 1
                while f"{codigo_letras}{i}" in codigos_letras:
                    i += 1
                pais['codigo_letras'] = f"{codigo_letras}{i}"
                codigos_letras[pais['codigo_letras']] = pais['nombre']
            else:
                codigos_letras[codigo_letras] = pais['nombre']
        
        # Insertar nuevos registros
        insertados = 0
        for pais in paises_data:
            try:
                # Asegurar que codigo_num siempre tenga 3 dígitos
                codigo_num = pais['codigo_num'].zfill(3)
                
                # Verificar que no exceda los 3 dígitos
                if len(codigo_num) > 3:
                    print(f"Advertencia: El código numérico '{codigo_num}' excede los 3 dígitos. Se usarán los últimos 3.")
                    codigo_num = codigo_num[-3:]
                
                cursor.execute(
                    "INSERT INTO CODIGO_PAISES (codigo_num, nombre, codigo_letras) VALUES (?, ?, ?)",
                    (codigo_num, pais['nombre'], pais['codigo_letras'])
                )
                insertados += 1
            except sqlite3.IntegrityError as e:
                print(f"Error al insertar {pais['nombre']} ({pais['codigo_num']}): {e}")
        
        # Guardar cambios
        conn.commit()
        
        # Verificar cuántos registros se insertaron
        cursor.execute("SELECT COUNT(*) FROM CODIGO_PAISES")
        count = cursor.fetchone()[0]
        print(f"Se han insertado {count} códigos de países en la base de datos.")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error al insertar datos en la base de datos: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Extraer códigos de países de PDF, guardarlos en un archivo JSON y cargarlos en la base de datos')
    parser.add_argument('pdf_path', help='Ruta al archivo PDF con los códigos de países')
    parser.add_argument('--output', '-o', default='codigos_paises.json', help='Ruta del archivo JSON de salida')
    parser.add_argument('--no-db', action='store_true', help='No cargar los datos en la base de datos')
    args = parser.parse_args()
    
    # Verificar que el archivo exista
    if not os.path.isfile(args.pdf_path):
        print(f"Error: El archivo {args.pdf_path} no existe.")
        return
    
    # Extraer códigos de países del PDF
    paises_data = extraer_codigos_paises_de_pdf(args.pdf_path)
    
    if paises_data:
        # Guardar los datos en un archivo JSON
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(paises_data, f, ensure_ascii=False, indent=2)
        print(f"Se han guardado {len(paises_data)} códigos de países en {args.output}")
        
        # Cargar los datos en la base de datos si no se especificó --no-db
        if not args.no_db:
            cargar_codigos_paises_sqlite(paises_data)
    else:
        print("No se encontraron códigos de países para guardar.")

if __name__ == "__main__":
    main() 