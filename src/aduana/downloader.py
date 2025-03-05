"""
Módulo para descargar y procesar resoluciones de clasificación arancelaria
desde el sitio web de la Dirección Nacional de Aduanas de Uruguay.
"""

import os
import re
import time
import logging
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin
import sqlite3
from bs4 import BeautifulSoup

from .db_init import agregar_resolucion

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL base y constantes
BASE_URL = "https://www.aduanas.gub.uy"
CLASIFICACIONES_URL = "https://www.aduanas.gub.uy/innovaportal/v/14029/6/innova.front/clasificacion-arancelaria.html"

# Headers para simular un navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
}

class ResolucionDownloader:
    """
    Clase para descargar y procesar resoluciones de clasificación arancelaria
    desde el sitio web de la Dirección Nacional de Aduanas de Uruguay.
    """
    
    def __init__(self, db_path, download_dir=None):
        """
        Inicializa el descargador de resoluciones.
        
        Args:
            db_path (str): Ruta a la base de datos SQLite.
            download_dir (str, optional): Directorio para guardar los PDFs.
        """
        self.db_path = db_path
        
        if download_dir is None:
            # Obtener directorio base
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            download_dir = os.path.join(base_dir, 'data', 'aduana')
        
        self.download_dir = download_dir
        logger.info(f"Directorio de descarga configurado: {self.download_dir}")
        
        # Inicializar sesión para las peticiones HTTP
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def get_year_urls(self):
        """
        Obtiene las URLs de las páginas de cada año disponible.
        
        Returns:
            dict: Diccionario con años como claves y URLs como valores.
        """
        logger.info(f"Obteniendo URLs de los años desde {CLASIFICACIONES_URL}")
        
        response = self.session.get(CLASIFICACIONES_URL)
        response.raise_for_status()
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar los enlaces de los años en el menú lateral
        year_urls = {}
        
        # Buscar todos los enlaces en la página
        for link in soup.find_all('a'):
            text = link.text.strip()
            # Buscar si el texto es un año (4 dígitos)
            if re.match(r'^\d{4}$', text):
                # Construir URL completa
                href = link.get('href')
                if href:
                    if href.startswith('/'):
                        url = urljoin(BASE_URL, href)
                    else:
                        url = href
                    year_urls[text] = url
        
        logger.info(f"Se encontraron {len(year_urls)} años disponibles: {', '.join(year_urls.keys())}")
        return year_urls
    
    def extract_resolutions_from_year(self, year, url):
        """
        Extrae las resoluciones de un año específico.
        
        Args:
            year (str): Año a procesar.
            url (str): URL de la página del año.
            
        Returns:
            list: Lista de diccionarios con información de las resoluciones.
        """
        resolutions = []
        resolution_pattern = re.compile(r'(\d+)[/_](\d{4})')
        
        logger.info(f"Extrayendo resoluciones del año {year} desde {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # MÉTODO 1: Buscar en una tabla de resoluciones
            table = soup.find('table')
            if table:
                logger.info("Se encontró una tabla, buscando resoluciones en ella")
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Saltar encabezado
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        link = cells[1].find('a')
                        if link:
                            resolution_url = urljoin(BASE_URL, link.get('href'))
                            numero = cells[0].text.strip()
                            
                            resolutions.append({
                                "year": year,
                                "numero": numero,
                                "url": resolution_url
                            })
            
            # MÉTODO 2: Buscar enlaces con formato "Resolución de Clasificación Arancelaria XX/YYYY"
            if not resolutions:
                logger.info("No se encontraron resoluciones en tabla, buscando enlaces directos")
                
                # Patrón específico para resoluciones de clasificación arancelaria
                clasificacion_pattern = re.compile(r'Resolución de Clasificación Arancelaria (\d+)/(\d{4})', re.IGNORECASE)
                
                for link in soup.find_all('a'):
                    link_text = link.text.strip()
                    href = link.get('href', '')
                    
                    # Buscar coincidencias tanto en el texto como en la URL
                    match = clasificacion_pattern.search(link_text)
                    
                    if match and match.group(2) == year:
                        resolution_url = urljoin(BASE_URL, href)
                        numero = match.group(1)
                        
                        # Verificar si ya existe esta resolución para evitar duplicados
                        duplicate = False
                        for existing_res in resolutions:
                            if existing_res["year"] == year and existing_res["numero"] == numero:
                                duplicate = True
                                break
                        
                        if not duplicate:
                            resolutions.append({
                                "year": year,
                                "numero": numero,
                                "url": resolution_url
                            })
                    # También buscar en la URL si contiene el patrón "resolucion-de-clasificacion-arancelaria-XX_YYYY.html"
                    elif 'resolucion-de-clasificacion-arancelaria' in href.lower() and f'_{year}.html' in href.lower():
                        url_match = re.search(r'resolucion-de-clasificacion-arancelaria-(\d+)_(\d{4})\.html', href.lower())
                        if url_match and url_match.group(2) == year:
                            resolution_url = urljoin(BASE_URL, href)
                            numero = url_match.group(1)
                            
                            # Verificar si ya existe esta resolución para evitar duplicados
                            duplicate = False
                            for existing_res in resolutions:
                                if existing_res["year"] == year and existing_res["numero"] == numero:
                                    duplicate = True
                                    break
                            
                            if not duplicate:
                                resolutions.append({
                                    "year": year,
                                    "numero": numero,
                                    "url": resolution_url
                                })
            
            # MÉTODO 3: Buscar enlaces que contengan el año
            if not resolutions:
                logger.info("No se encontraron resoluciones con patrones específicos, buscando enlaces con el año")
                
                for link in soup.find_all('a'):
                    link_text = link.text.strip()
                    href = link.get('href')
                    
                    if not href:
                        continue
                    
                    # Comprobar si el texto o la URL contienen el año
                    if str(year) in link_text or str(year) in href:
                        # Intentar extraer el número de resolución
                        match = resolution_pattern.search(link_text) or resolution_pattern.search(href)
                        
                        if match and match.group(2) == year:
                            resolution_url = urljoin(BASE_URL, href)
                            numero = match.group(1)
                            
                            # Verificar si ya existe esta resolución para evitar duplicados
                            duplicate = False
                            for existing_res in resolutions:
                                if existing_res["year"] == year and existing_res["numero"] == numero:
                                    duplicate = True
                                    break
                            
                            if not duplicate:
                                resolutions.append({
                                    "year": year,
                                    "numero": numero,
                                    "url": resolution_url
                                })
            
            # MÉTODO 4: Intentar con la URL de resoluciones para el año específico
            try:
                # Probar con la URL específica de resoluciones para el año
                alt_url = f"https://www.aduanas.gub.uy/innovaportal/v/27296/6/innova.front/resoluciones.html"
                logger.info(f"Intentando con URL alternativa: {alt_url}")
                
                alt_response = self.session.get(alt_url)
                alt_response.raise_for_status()
                
                alt_soup = BeautifulSoup(alt_response.text, 'html.parser')
                
                # Buscar enlaces de resoluciones
                for div in alt_soup.find_all(['div', 'li']):
                    link = div.find('a')
                    if link:
                        link_text = link.text.strip()
                        href = link.get('href')
                        
                        # Verificar si es del año deseado
                        if f"/{year}" in link_text or f"_{year}" in href:
                            resolution_url = urljoin(BASE_URL, href)
                            
                            # Intentar extraer número de la resolución
                            match = resolution_pattern.search(link_text)
                            if match:
                                numero = match.group(1)
                            else:
                                # Intentar extraer número de la resolución desde la URL
                                url_match = re.search(r'resolucion-(\d+)_\d{4}', href.lower())
                                if url_match:
                                    numero = url_match.group(1)
                                else:
                                    # Si no se puede extraer, usar un contador
                                    numero = str(len(resolutions) + 1)
                            
                            # Verificar si ya existe esta resolución para evitar duplicados
                            duplicate = False
                            for existing_res in resolutions:
                                if existing_res["year"] == year and existing_res["numero"] == numero:
                                    duplicate = True
                                    break
                            
                            if not duplicate:
                                resolutions.append({
                                    "year": year,
                                    "numero": numero,
                                    "url": resolution_url
                                })
            except Exception as e:
                logger.error(f"Error al intentar con URL alternativa: {str(e)}")

            # MÉTODO 5: Intentar con la URL de clasificación arancelaria
            try:
                # Probar directamente con la URL de clasificación arancelaria
                clasi_url = f"https://www.aduanas.gub.uy/innovaportal/v/14029/6/innova.front/clasificacion-arancelaria.html"
                logger.info(f"Intentando con URL de clasificación arancelaria: {clasi_url}")
                
                clasi_response = self.session.get(clasi_url)
                clasi_response.raise_for_status()
                
                clasi_soup = BeautifulSoup(clasi_response.text, 'html.parser')
                
                # Buscar enlaces específicos de clasificación arancelaria
                clasificacion_pattern = re.compile(r'Resolución de Clasificación Arancelaria (\d+)/(\d{4})', re.IGNORECASE)
                url_pattern = re.compile(r'resolucion-de-clasificacion-arancelaria-(\d+)_(\d{4})\.html', re.IGNORECASE)
                
                for link in clasi_soup.find_all('a'):
                    href = link.get('href', '')
                    link_text = link.text.strip()
                    
                    if f"/{year}" in link_text or f"_{year}" in href:
                        # Buscar en la URL y en el texto del enlace
                        url_match = url_pattern.search(href)
                        text_match = clasificacion_pattern.search(link_text)
                        
                        if (url_match and url_match.group(2) == year) or (text_match and text_match.group(2) == year):
                            resolution_url = urljoin(BASE_URL, href)
                            
                            # Obtener el número de la resolución
                            if url_match:
                                numero = url_match.group(1)
                            elif text_match:
                                numero = text_match.group(1)
                            else:
                                # Usar un contador si no se puede extraer
                                numero = str(len(resolutions) + 1)
                            
                            # Verificar duplicados
                            duplicate = False
                            for existing_res in resolutions:
                                if existing_res["year"] == year and existing_res["numero"] == numero:
                                    duplicate = True
                                    break
                            
                            if not duplicate:
                                resolutions.append({
                                    "year": year,
                                    "numero": numero,
                                    "url": resolution_url
                                })
            except Exception as e:
                logger.error(f"Error al intentar con URL de clasificación arancelaria: {str(e)}")
            
            # MÉTODO 6: Buscar en la estructura específica de la página para el año 2025
            try:
                # URL específica de 2025
                specific_url = f"https://www.aduanas.gub.uy/innovaportal/v/27217/6/innova.front/2025.html"
                logger.info(f"Intentando con URL específica para año {year}: {specific_url}")
                
                specific_response = self.session.get(specific_url)
                specific_response.raise_for_status()
                
                specific_soup = BeautifulSoup(specific_response.text, 'html.parser')
                
                # Buscar en divs con clase específica
                box_titles = specific_soup.find_all('div', class_='box-title box-title-withouticon')
                
                for box in box_titles:
                    link = box.find('a')
                    if link:
                        href = link.get('href', '')
                        link_text = link.text.strip()
                        
                        # Buscar patrones específicos en el texto
                        text_match = re.search(r'Resoluci[oó]n de Clasificaci[oó]n Arancelaria (\d+)[/_](\d{4})', link_text, re.IGNORECASE)
                        url_match = re.search(r'resolucion-de-clasificacion-arancelaria-(\d+)_(\d{4})\.html', href, re.IGNORECASE)
                        
                        # También buscar patrón alternativo en la URL
                        if not url_match:
                            url_match = re.search(r'/v/\d+/\d+/innova\.front/resolucion-de-clasificacion-arancelaria-(\d+)_(\d{4})\.html', href, re.IGNORECASE)
                        
                        match = text_match or url_match
                        
                        if match and match.group(2) == year:
                            resolution_url = urljoin(BASE_URL, href)
                            numero = match.group(1)
                            
                            # Verificar duplicados
                            duplicate = False
                            for existing_res in resolutions:
                                if existing_res["year"] == year and existing_res["numero"] == numero:
                                    duplicate = True
                                    break
                            
                            if not duplicate:
                                logger.info(f"Encontrada resolución {numero}/{year} en URL específica")
                                resolutions.append({
                                    "year": year,
                                    "numero": numero,
                                    "url": resolution_url
                                })
            except Exception as e:
                logger.error(f"Error al intentar con URL específica para año {year}: {str(e)}")
            
            # MÉTODO 7: Buscar en la URL específica de resoluciones del año 2025
            try:
                # URL de resoluciones 2025
                resolutions_url = f"https://www.aduanas.gub.uy/innovaportal/v/27222/6/innova.front/2025.html"
                logger.info(f"Intentando con URL de resoluciones para el año {year}: {resolutions_url}")
                
                res_response = self.session.get(resolutions_url)
                res_response.raise_for_status()
                
                res_soup = BeautifulSoup(res_response.text, 'html.parser')
                
                # Buscar en diferentes estructuras
                candidates = []
                
                # Buscar en divs con clase específica
                candidates.extend(res_soup.find_all('div', class_='box-title box-title-withouticon'))
                
                # También buscar en otros elementos comunes
                candidates.extend(res_soup.find_all(['li', 'div', 'p'], class_=['box-title', 'title-item']))
                
                for candidate in candidates:
                    link = candidate.find('a')
                    if not link:
                        continue
                        
                    href = link.get('href', '')
                    link_text = link.text.strip()
                    
                    # Buscar patrones de resolución en el texto y URL
                    text_match = re.search(r'Resoluci[oó]n de Clasificaci[oó]n Arancelaria (\d+)[/_](\d{4})', link_text, re.IGNORECASE)
                    url_match = re.search(r'resolucion-de-clasificacion-arancelaria-(\d+)_(\d{4})\.html', href, re.IGNORECASE)
                    
                    # Búsqueda más general que pueda capturar otros formatos
                    if not text_match and not url_match:
                        if 'resolucion' in href.lower() and 'arancelaria' in href.lower() and f"_{year}" in href.lower():
                            url_match = re.search(r'(\d+)_(\d{4})\.html', href)
                    
                    match = text_match or url_match
                    
                    if match and match.group(2) == year:
                        resolution_url = urljoin(BASE_URL, href)
                        numero = match.group(1)
                        
                        # Verificar duplicados
                        duplicate = False
                        for existing_res in resolutions:
                            if existing_res["year"] == year and existing_res["numero"] == numero:
                                duplicate = True
                                break
                        
                        if not duplicate:
                            logger.info(f"Encontrada resolución {numero}/{year} en URL de resoluciones")
                            resolutions.append({
                                "year": year,
                                "numero": numero,
                                "url": resolution_url
                            })
            except Exception as e:
                logger.error(f"Error al intentar con URL de resoluciones para año {year}: {str(e)}")
                
            # MÉTODO 8: Buscar en la página especifica para resoluciones 2024
            try:
                if year == "2024":
                    # URLs específicas para 2024
                    specific_url_2024 = "https://www.aduanas.gub.uy/innovaportal/v/26136/6/innova.front/2024.html"
                    logger.info(f"Intentando con URL específica para 2024: {specific_url_2024}")
                    
                    specific_response = self.session.get(specific_url_2024)
                    specific_response.raise_for_status()
                    
                    specific_soup = BeautifulSoup(specific_response.text, 'html.parser')
                    
                    # Buscar en divs con clase específica
                    box_titles = specific_soup.find_all('div', class_='box-title box-title-withouticon')
                    
                    for box in box_titles:
                        link = box.find('a')
                        if link:
                            href = link.get('href', '')
                            link_text = link.text.strip()
                            
                            # Buscar patrones específicos para 2024
                            text_match = re.search(r'Resoluci[oó]n de Clasificaci[oó]n Arancelaria (\d+)[/_](\d{4})', link_text, re.IGNORECASE)
                            url_match = re.search(r'resolucion-de-clasificacion-arancelaria-(\d+)_(\d{4})\.html', href, re.IGNORECASE)
                            
                            match = text_match or url_match
                            
                            if match and match.group(2) == year:
                                resolution_url = urljoin(BASE_URL, href)
                                numero = match.group(1)
                                
                                # Verificar duplicados
                                duplicate = False
                                for existing_res in resolutions:
                                    if existing_res["year"] == year and existing_res["numero"] == numero:
                                        duplicate = True
                                        break
                                
                                if not duplicate:
                                    logger.info(f"Encontrada resolución {numero}/{year} en URL específica de 2024")
                                    resolutions.append({
                                        "year": year,
                                        "numero": numero,
                                        "url": resolution_url
                                    })
            except Exception as e:
                logger.error(f"Error al intentar con URL específica para 2024: {str(e)}")
                
            # MÉTODO 9: Búsqueda secuencial de resoluciones por ID conocido
            try:
                if year == "2024":
                    # Lista de ID conocidos para resoluciones específicas que no aparecen en las páginas principales
                    known_ids = [
                        "27003", # Resolución 53/2024
                        "26866", # Resolución 44/2024
                        "26593", # Resolución 25/2024
                        "26348", # Resolución 15/2024
                        "26139"  # Resolución 5/2024
                    ]
                    
                    logger.info(f"Intentando búsqueda por IDs conocidos para el año {year}")
                    
                    for res_id in known_ids:
                        url_template = f"https://www.aduanas.gub.uy/innovaportal/v/{res_id}/6/innova.front/resolucion-de-clasificacion-arancelaria-"
                        
                        # Intentar diferentes formatos de número de resolución
                        numero_patterns = [
                            # Detectar número desde la URL
                            lambda id: re.search(r'resolucion-de-clasificacion-arancelaria-(\d+)_\d{4}', id),
                            # Patrones comunes basados en IDs conocidos
                            "53_2024.html", "44_2024.html", "25_2024.html", "15_2024.html", "5_2024.html"
                        ]
                        
                        for pattern in numero_patterns:
                            if callable(pattern):
                                # Si es una función, usarla para extraer el número
                                match = pattern(res_id)
                                if match:
                                    numero = match.group(1)
                                    resolution_url = url_template + f"{numero}_{year}.html"
                                    logger.info(f"Intentando URL predecible: {resolution_url}")
                            else:
                                # Si es un patrón directo, usar como sufijo
                                numero = pattern.split('_')[0]
                                resolution_url = url_template + pattern
                                logger.info(f"Intentando URL predecible: {resolution_url}")
                            
                            try:
                                res_response = self.session.get(resolution_url)
                                if res_response.status_code == 200:
                                    # Verificar si realmente es una página de resolución
                                    res_soup = BeautifulSoup(res_response.text, 'html.parser')
                                    title = res_soup.find('title')
                                    if title and 'resolución' in title.text.lower() and 'arancelaria' in title.text.lower():
                                        # Extraer número de resolución del título o URL
                                        title_match = re.search(r'Resoluci[oó]n de Clasificaci[oó]n Arancelaria (\d+)[/_](\d{4})', title.text, re.IGNORECASE)
                                        url_match = re.search(r'resolucion-de-clasificacion-arancelaria-(\d+)_(\d{4})\.html', resolution_url, re.IGNORECASE)
                                        
                                        if title_match and title_match.group(2) == year:
                                            numero = title_match.group(1)
                                        elif url_match and url_match.group(2) == year:
                                            numero = url_match.group(1)
                                        
                                        # Verificar duplicados
                                        duplicate = False
                                        for existing_res in resolutions:
                                            if existing_res["year"] == year and existing_res["numero"] == numero:
                                                duplicate = True
                                                break
                                        
                                        if not duplicate:
                                            logger.info(f"Encontrada resolución {numero}/{year} por ID conocido")
                                            resolutions.append({
                                                "year": year,
                                                "numero": numero,
                                                "url": resolution_url
                                            })
                            except Exception as e:
                                # Ignorar errores en este método, solo estamos probando URLs
                                pass
            except Exception as e:
                logger.error(f"Error al buscar por IDs conocidos para {year}: {str(e)}")
                
            # MÉTODO 10: Búsqueda directa de URL para resoluciones proporcionadas manualmente
            try:
                direct_urls = [
                    "https://www.aduanas.gub.uy/innovaportal/v/27003/6/innova.front/resolucion-de-clasificacion-arancelaria-53_2024.html",
                    "https://www.aduanas.gub.uy/innovaportal/v/26866/6/innova.front/resolucion-de-clasificacion-arancelaria-44_2024.html",
                    "https://www.aduanas.gub.uy/innovaportal/v/26593/6/innova.front/resolucion-de-clasificacion-arancelaria-25_2024.html",
                    "https://www.aduanas.gub.uy/innovaportal/v/26348/6/innova.front/resolucion-de-clasificacion-arancelaria-15_2024.html",
                    "https://www.aduanas.gub.uy/innovaportal/v/26139/6/innova.front/resolucion-de-clasificacion-arancelaria-5_2024.html"
                ]
                
                for direct_url in direct_urls:
                    if year in direct_url:
                        logger.info(f"Intentando URL directa: {direct_url}")
                        
                        # Extraer número de resolución de la URL
                        url_match = re.search(r'resolucion-de-clasificacion-arancelaria-(\d+)_(\d{4})\.html', direct_url, re.IGNORECASE)
                        
                        if url_match and url_match.group(2) == year:
                            numero = url_match.group(1)
                            
                            # Verificar duplicados
                            duplicate = False
                            for existing_res in resolutions:
                                if existing_res["year"] == year and existing_res["numero"] == numero:
                                    duplicate = True
                                    break
                            
                            if not duplicate:
                                # Verificar que la URL existe
                                try:
                                    response = self.session.get(direct_url)
                                    if response.status_code == 200:
                                        logger.info(f"Encontrada resolución {numero}/{year} por URL directa")
                                        resolutions.append({
                                            "year": year,
                                            "numero": numero,
                                            "url": direct_url
                                        })
                                except Exception as e:
                                    logger.error(f"Error al verificar URL directa {direct_url}: {str(e)}")
            except Exception as e:
                logger.error(f"Error al procesar URLs directas: {str(e)}")
                
            logger.info(f"Se encontraron {len(resolutions)} resoluciones para el año {year}")
            
        except Exception as e:
            logger.error(f"Error al procesar las resoluciones del año {year}: {str(e)}")
        
        return resolutions
    
    def process_resolution_details(self, resolution_info):
        """
        Procesa los detalles de una resolución específica.
        
        Args:
            resolution_info (dict): Información básica de la resolución.
            
        Returns:
            dict: Información completa de la resolución.
        """
        year = resolution_info["year"]
        numero = resolution_info["numero"]
        url = resolution_info["url"]
        
        logger.info(f"Procesando detalles de la resolución {numero}/{year} desde {url}")
        
        # Crear directorio para el año si no existe
        year_dir = os.path.join(self.download_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Parsear el HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer fecha - intentar varios patrones
            fecha = None
            
            # Intento 1: Buscar en la estructura jerárquica
            fecha_element = soup.select_one('body > div:nth-child(3) > div:nth-child(1) > div:nth-child(2)')
            if fecha_element:
                fecha_text = fecha_element.text.strip()
                fecha_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', fecha_text)
                if fecha_match:
                    fecha_str = fecha_match.group(1)
                    # Convertir fecha de DD/MM/YYYY a YYYY-MM-DD
                    fecha = datetime.strptime(fecha_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            
            # Intento 2: Buscar cualquier elemento con fecha
            if not fecha:
                for element in soup.find_all(['p', 'div', 'span']):
                    text = element.text.strip()
                    fecha_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
                    if fecha_match:
                        fecha_str = fecha_match.group(1)
                        # Convertir fecha de DD/MM/YYYY a YYYY-MM-DD
                        fecha = datetime.strptime(fecha_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                        break
            
            if not fecha:
                logger.warning(f"No se pudo extraer la fecha de la resolución {numero}/{year}")
                # Usar fecha genérica basada en el año
                fecha = f"{year}-01-01"
            
            # Extraer referencia - intentar varios patrones
            referencia = ""
            
            # Intento 1: Buscar en la estructura jerárquica
            referencia_element = soup.select_one('body > div:nth-child(3) > div:nth-child(1) > div:nth-child(3) > div > p')
            if referencia_element:
                referencia = referencia_element.text.strip()
            
            # Intento 2: Buscar en elementos con clases específicas
            if not referencia:
                ref_candidates = soup.find_all(['p', 'div'], class_=['texto-contenido', 'descripcion'])
                for element in ref_candidates:
                    text = element.text.strip()
                    if len(text) > 10 and not text.startswith('http') and not 'descargar' in text.lower():
                        referencia = text
                        break
            
            # Intento 3: Buscar en headings o párrafos
            if not referencia:
                ref_candidates = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p'])
                for element in ref_candidates:
                    text = element.text.strip()
                    if len(text) > 10 and not text.startswith('http') and not 'descargar' in text.lower():
                        referencia = text
                        break
            
            # Extraer enlaces a PDFs
            dictamen_pdf = None
            resolucion_pdf = None
            pdf_links = []
            
            # Recopilar todos los enlaces a PDFs
            for link in soup.find_all('a'):
                href = link.get('href')
                if not href:
                    continue
                    
                # Verificar si es un enlace a un PDF
                if href.lower().endswith('.pdf'):
                    # Construir URL completa si es relativa
                    if href.startswith('/'):
                        pdf_url = urljoin(BASE_URL, href)
                    else:
                        pdf_url = href
                        
                    link_text = link.text.strip().lower()
                    pdf_links.append((pdf_url, link_text))
            
            # Buscar enlaces específicos por su texto
            for pdf_url, link_text in pdf_links:
                if 'dictamen' in link_text or 'informe' in link_text:
                    dictamen_filename = f"dictamen_{year}_{numero}.pdf"
                    dictamen_path = os.path.join(year_dir, dictamen_filename)
                    
                    # Descargar el PDF del dictamen
                    self.download_pdf(pdf_url, dictamen_path)
                    dictamen_pdf = dictamen_path
                
                elif 'resolucion' in link_text or 'resolución' in link_text:
                    resolucion_filename = f"resolucion_{year}_{numero}.pdf"
                    resolucion_path = os.path.join(year_dir, resolucion_filename)
                    
                    # Descargar el PDF de la resolución
                    self.download_pdf(pdf_url, resolucion_path)
                    resolucion_pdf = resolucion_path
            
            # Si no se identificaron por texto, usar los primeros dos PDFs (si hay)
            if len(pdf_links) >= 1 and not dictamen_pdf:
                pdf_url, _ = pdf_links[0]
                dictamen_filename = f"dictamen_{year}_{numero}.pdf"
                dictamen_path = os.path.join(year_dir, dictamen_filename)
                
                # Descargar el PDF del dictamen
                self.download_pdf(pdf_url, dictamen_path)
                dictamen_pdf = dictamen_path
            
            if len(pdf_links) >= 2 and not resolucion_pdf:
                pdf_url, _ = pdf_links[1]
                resolucion_filename = f"resolucion_{year}_{numero}.pdf"
                resolucion_path = os.path.join(year_dir, resolucion_filename)
                
                # Descargar el PDF de la resolución
                self.download_pdf(pdf_url, resolucion_path)
                resolucion_pdf = resolucion_path
            
            # Completar la información de la resolución
            resolution_info.update({
                "fecha": fecha,
                "referencia": referencia,
                "dictamen": dictamen_pdf or "",
                "resolucion": resolucion_pdf or ""
            })
            
            return resolution_info
            
        except Exception as e:
            logger.error(f"Error al procesar los detalles de la resolución {numero}/{year}: {str(e)}")
            return resolution_info
    
    def download_pdf(self, url, output_path):
        """
        Descarga un PDF desde una URL.
        
        Args:
            url (str): URL del PDF.
            output_path (str): Ruta donde guardar el PDF.
            
        Returns:
            bool: True si la descarga fue exitosa, False en caso contrario.
        """
        try:
            logger.info(f"Descargando PDF desde {url} a {output_path}")
            
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"PDF descargado exitosamente: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al descargar el PDF: {str(e)}")
            return False
    
    def process_pdf_url(self, url, year, numero, tipo):
        """
        Procesa una URL directa a un PDF.
        
        Args:
            url (str): URL del PDF.
            year (int): Año de la resolución.
            numero (int): Número de la resolución.
            tipo (str): Tipo de PDF ('dictamen' o 'resolucion').
            
        Returns:
            str: Ruta al archivo PDF descargado o cadena vacía en caso de error.
        """
        try:
            # Crear directorio para el año si no existe
            year_dir = os.path.join(self.download_dir, str(year))
            os.makedirs(year_dir, exist_ok=True)
            
            # Construir nombre de archivo
            filename = f"{tipo}_{year}_{numero}.pdf"
            output_path = os.path.join(year_dir, filename)
            
            # Descargar el PDF
            if self.download_pdf(url, output_path):
                return output_path
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error al procesar URL de PDF {tipo}: {str(e)}")
            return ""
    
    def save_to_database(self, resolution_info):
        """
        Guarda la información de una resolución en la base de datos.
        
        Args:
            resolution_info (dict): Información de la resolución.
            
        Returns:
            int: ID de la resolución en la base de datos o -1 en caso de error.
        """
        try:
            # Verificar si la resolución ya existe en la base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id FROM resoluciones_clasificacion_arancelaria
            WHERE year = ? AND numero = ?
            ''', (resolution_info["year"], resolution_info["numero"]))
            
            existing_id = cursor.fetchone()
            
            if existing_id:
                logger.info(f"La resolución {resolution_info['year']}/{resolution_info['numero']} ya existe en la base de datos (ID: {existing_id[0]})")
                conn.close()
                return existing_id[0]
            
            conn.close()
            
            # Si no existe, agregar la resolución
            return agregar_resolucion(
                db_path=self.db_path,
                year=resolution_info["year"],
                numero=resolution_info["numero"],
                fecha=resolution_info.get("fecha", ""),
                referencia=resolution_info.get("referencia", ""),
                dictamen=resolution_info.get("dictamen", ""),
                resolucion=resolution_info.get("resolucion", "")
            )
        except Exception as e:
            logger.error(f"Error al guardar la resolución en la base de datos: {str(e)}")
            return -1
    
    def download_year(self, year):
        """
        Descarga todas las resoluciones de un año específico.
        
        Args:
            year (str): Año a descargar.
            
        Returns:
            int: Número de resoluciones descargadas y procesadas.
        """
        year_urls = self.get_year_urls()
        
        if year not in year_urls:
            logger.error(f"No se encontró el año {year} en la página de clasificaciones arancelarias")
            return 0
        
        resolutions = self.extract_resolutions_from_year(year, year_urls[year])
        
        count = 0
        for resolution_info in resolutions:
            # Procesar los detalles de la resolución
            complete_info = self.process_resolution_details(resolution_info)
            
            # Guardar en la base de datos
            resolution_id = self.save_to_database(complete_info)
            
            if resolution_id > 0:
                count += 1
                logger.info(f"Resolución {complete_info['numero']}/{complete_info['year']} guardada en la base de datos (ID: {resolution_id})")
            
            # Pequeña pausa para no sobrecargar el servidor
            time.sleep(1)
        
        logger.info(f"Se procesaron {count} resoluciones del año {year}")
        return count

# Función auxiliar para ejecutar la descarga desde la línea de comandos
def descargar_resoluciones(year, db_path=None):
    """
    Descarga las resoluciones de clasificación arancelaria de un año específico.
    
    Args:
        year (str): Año a descargar.
        db_path (str, opcional): Ruta a la base de datos.
        
    Returns:
        int: Número de resoluciones descargadas.
    """
    # Obtener la ruta de la base de datos
    if db_path is None:
        base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(base_dir, 'data', 'aduana', 'aduana.db')
    
    # Crear el downloader y usarlo
    downloader = ResolucionDownloader(db_path=db_path)
    return downloader.download_year(year) 