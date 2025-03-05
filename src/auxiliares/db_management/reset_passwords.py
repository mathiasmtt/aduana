#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import get_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def main():
    app = get_app()
    with app.app_context():
        # Reset admin password
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.password_hash = generate_password_hash('admin123')
            print('Contraseña de admin restablecida a: admin123')
        
        # Reset vip_user password
        vip = User.query.filter_by(username='vip_user').first()
        if vip:
            vip.password_hash = generate_password_hash('vippass123')
            print('Contraseña de vip_user restablecida a: vippass123')
        
        # Reset free_user password
        free = User.query.filter_by(username='free_user').first()
        if free:
            free.password_hash = generate_password_hash('freepass123')
            print('Contraseña de free_user restablecida a: freepass123')
        
        # Commit changes
        db.session.commit()
        
        # Show all users
        users = User.query.all()
        print('\nUsuarios disponibles:')
        for u in users:
            password = 'admin123' if u.username == 'admin' else 'vippass123' if u.username == 'vip_user' else 'freepass123'
            print(f'- Username: {u.username}, Email: {u.email}, Password: {password}, Rol: {u.role}')

if __name__ == '__main__':
    main() 