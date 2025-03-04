#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para probar diferentes URLs de la aplicación y verificar que las notas de sección
se muestran correctamente.
"""

import sys
import webbrowser
import time

def test_urls():
    """Abre varias URLs para probar la aplicación."""
    base_url = "http://127.0.0.1:5050"
    
    # Lista de URLs a probar
    urls = [
        # Página principal
        f"{base_url}/",
        
        # Búsqueda por NCM
        f"{base_url}/buscar?q=3901.90.90.00&tipo=ncm",
        
        # Búsqueda por sección (formato romano)
        f"{base_url}/buscar?q=VII&tipo=seccion",
        
        # Búsqueda por sección (formato decimal)
        f"{base_url}/buscar?q=7&tipo=seccion",
        
        # Búsqueda por capítulo
        f"{base_url}/buscar?q=39&tipo=capitulo",
        
        # Ver lista de secciones
        f"{base_url}/secciones",
    ]
    
    # Abrir cada URL con un pequeño retraso
    for url in urls:
        print(f"Abriendo: {url}")
        webbrowser.open(url)
        time.sleep(2)  # Esperar 2 segundos entre cada URL

if __name__ == "__main__":
    test_urls()
