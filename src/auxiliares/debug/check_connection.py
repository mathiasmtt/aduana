import os
import sqlite3
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Rutas posibles para la base de datos
possible_paths = [
    '/Users/mat/Code/aduana/data/database.sqlite3',
    '/Users/mat/Code/aduana/data/db_versions/arancel_latest.sqlite3',
    '/Users/mat/Code/aduana/instance/database.sqlite3'
]

print("=== Verificación de conexión a la base de datos ===")

for db_path in possible_paths:
    print(f"\nVerificando: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Archivo no encontrado: {db_path}")
        continue
    
    try:
        # Intentar conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla de usuarios existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            print(f"✅ Tabla 'users' encontrada en: {db_path}")
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            print(f"   Total de usuarios: {count}")
            
            # Listar usuarios
            cursor.execute("SELECT id, username, email, role FROM users")
            users = cursor.fetchall()
            for user in users:
                print(f"   - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Rol: {user[3]}")
        else:
            print(f"❌ Tabla 'users' NO encontrada en: {db_path}")
            
            # Listar todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if tables:
                print("   Tablas disponibles:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("   No hay tablas en esta base de datos")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error al conectar a {db_path}: {str(e)}")

print("\n=== Verificación completada ===")
print("Si no se encontró la base de datos o la tabla de usuarios, es posible que:")
print("1. La ruta de la base de datos sea incorrecta")
print("2. La base de datos esté dañada")
print("3. Las tablas no se hayan creado correctamente") 