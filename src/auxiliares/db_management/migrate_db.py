#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import get_app, db

def main():
    """Actualiza la estructura de la base de datos."""
    app = get_app()
    with app.app_context():
        db.create_all()
        print("Base de datos actualizada correctamente")

if __name__ == '__main__':
    main() 