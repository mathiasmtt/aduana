#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import get_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from datetime import datetime
from .clean_users_db import clean_users_db

def main():
    """Crea 6 usuarios VIP con diferentes roles de importación."""
    app = get_app()
    with app.app_context():
        # Definición de los usuarios VIP
        vip_users = [
            {
                'username': 'transportista1',
                'name': 'Carlos Torres',
                'email': 'transportista1@aduana.com',
                'password': 'vippass123',
                'role': 'vip',
                'import_role': 'transportista'
            },
            {
                'username': 'transportista2',
                'name': 'Ana Rodríguez',
                'email': 'transportista2@aduana.com',
                'password': 'vippass123',
                'role': 'vip',
                'import_role': 'transportista'
            },
            {
                'username': 'despachante1',
                'name': 'Roberto Méndez',
                'email': 'despachante1@aduana.com',
                'password': 'vippass123',
                'role': 'vip',
                'import_role': 'despachante'
            },
            {
                'username': 'corredor1',
                'name': 'Laura Vázquez',
                'email': 'corredor1@aduana.com',
                'password': 'vippass123',
                'role': 'vip',
                'import_role': 'corredor'
            },
            {
                'username': 'importador1',
                'name': 'Sergio Díaz',
                'email': 'importador1@aduana.com',
                'password': 'vippass123',
                'role': 'vip',
                'import_role': 'importador'
            },
            {
                'username': 'profesional1',
                'name': 'Patricia Ruiz',
                'email': 'profesional1@aduana.com',
                'password': 'vippass123',
                'role': 'vip',
                'import_role': 'profesional'
            }
        ]
        
        # Crear o actualizar usuarios
        for user_data in vip_users:
            # Verificar si el usuario ya existe
            user = User.query.filter_by(email=user_data['email']).first()
            
            if user:
                print(f"Actualizando usuario existente: {user_data['email']}")
                # Actualizar los datos del usuario
                user.username = user_data['username']
                user.name = user_data['name']
                user.password_hash = generate_password_hash(user_data['password'])
                user.role = user_data['role']
                user.import_role = user_data['import_role']
                user.last_login = datetime.utcnow()
            else:
                print(f"Creando nuevo usuario: {user_data['email']}")
                # Crear un nuevo usuario
                user = User(
                    username=user_data['username'],
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data['role'],
                    import_role=user_data['import_role'],
                    last_login=datetime.utcnow()
                )
                db.session.add(user)
        
        # Guardar cambios
        db.session.commit()
        
        # Mostrar usuarios VIP
        print("\nUsuarios VIP creados:")
        vip_users = User.query.filter_by(role='vip').all()
        for user in vip_users:
            print(f"- {user.username} ({user.email}): Rol de importación: {user.import_role}")
        
    # Limpiar la base de datos para eliminar tablas no deseadas
    print("\nLimpiando la base de datos de usuarios...")
    clean_users_db()

if __name__ == '__main__':
    main() 