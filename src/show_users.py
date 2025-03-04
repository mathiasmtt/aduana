#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import get_app
from app.models.user import User

def main():
    app = get_app()
    with app.app_context():
        users = User.query.all()
        print('Usuarios encontrados:')
        if not users:
            print('- No hay usuarios en la base de datos')
        for u in users:
            print(f'- Username: {u.username}, Email: {u.email}, Rol: {u.role}, Activo: {u.is_active}')

if __name__ == '__main__':
    main() 