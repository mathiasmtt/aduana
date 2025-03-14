#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import get_app, db
from app.models.user import User
import os
import shutil
from datetime import datetime
import logging
import sqlite3

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    """Elimina la base de datos de usuarios y la recrea con la nueva estructura."""
    app = get_app()
    
    # Obtener la ruta de la base de datos de usuarios
    with app.app_context():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        db_path = db_uri.replace('sqlite:///', '')
        
        # Verificar si existe el directorio
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Directorio creado: {db_dir}")
        
        # Hacer una copia de seguridad si existe la base de datos
        if os.path.exists(db_path):
            backup_path = f"{db_path}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            shutil.copy2(db_path, backup_path)
            print(f"Copia de seguridad creada: {backup_path}")
            
            # Eliminar la base de datos original
            os.remove(db_path)
            print(f"Base de datos eliminada: {db_path}")
        
        # Crear solo la tabla de usuarios, no todas las tablas
        # En lugar de usar db.create_all() que crearía todas las tablas
        # creamos manualmente la tabla de usuarios
        conn = sqlite3.connect(db_path)
        
        # Crear la tabla users
        conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(64) UNIQUE,
            name VARCHAR(64),
            email VARCHAR(120) UNIQUE,
            password_hash VARCHAR(128),
            role VARCHAR(20),
            import_role VARCHAR(50),
            created_at TIMESTAMP,
            last_login TIMESTAMP,
            session_expires_at TIMESTAMP,
            is_active BOOLEAN,
            verification_token VARCHAR(64)
        )
        ''')
        
        # Crear los índices necesarios
        conn.execute('CREATE INDEX ix_users_email ON users (email)')
        conn.execute('CREATE INDEX ix_users_username ON users (username)')
        
        conn.commit()
        conn.close()
        
        print(f"Base de datos recreada solo con la tabla de usuarios: {db_path}")
        
        print("\nAhora puede ejecutar el script 'create_vip_users.py' para crear los usuarios.")

if __name__ == '__main__':
    main() 