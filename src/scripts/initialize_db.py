#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para inicializar la base de datos con todas las tablas definidas en los modelos.
"""

import os
import sys
import logging

# Configurar el path para importar módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('initialize_db')

def create_tables():
    """Crea todas las tablas definidas en los modelos."""
    from src.app import create_app, db
    from src.app.models import Arancel, ChapterNote, SectionNote, User
    
    app = create_app()
    
    with app.app_context():
        logger.info("Creando tablas en la base de datos...")
        
        # Crear todas las tablas
        db.create_all()
        
        logger.info("Tablas creadas exitosamente.")

if __name__ == '__main__':
    create_tables()
