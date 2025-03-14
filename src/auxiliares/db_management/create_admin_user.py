#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import get_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    """Crea un usuario administrador en la base de datos."""
    app = get_app()
    with app.app_context():
        # Datos del usuario administrador
        admin_data = {
            'username': 'admin',
            'name': 'Administrador del Sistema',
            'email': 'admin@aduana.com',
            'password': 'adminpass123',
            'role': 'admin'
        }
        
        # Verificar si el usuario ya existe
        user = User.query.filter_by(email=admin_data['email']).first()
        
        if user:
            print(f"Actualizando usuario administrador existente: {admin_data['email']}")
            # Actualizar los datos del usuario
            user.username = admin_data['username']
            user.name = admin_data['name']
            user.password_hash = generate_password_hash(admin_data['password'])
            user.role = admin_data['role']
            user.last_login = datetime.utcnow()
        else:
            print(f"Creando nuevo usuario administrador: {admin_data['email']}")
            # Crear un nuevo usuario administrador
            user = User(
                username=admin_data['username'],
                name=admin_data['name'],
                email=admin_data['email'],
                password_hash=generate_password_hash(admin_data['password']),
                role=admin_data['role'],
                last_login=datetime.utcnow()
            )
            db.session.add(user)
        
        # Guardar cambios
        db.session.commit()
        
        print(f"\nUsuario administrador creado/actualizado:")
        print(f"- Usuario: {user.username}")
        print(f"- Email: {user.email}")
        print(f"- Contraseña: {admin_data['password']}")
        print(f"- Rol: {user.role}")

if __name__ == '__main__':
    main() 