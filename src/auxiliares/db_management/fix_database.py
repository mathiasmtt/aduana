from app import get_app, db
from app.models.user import User
from datetime import datetime
import logging
import os
import sqlite3

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def check_database_integrity():
    """Verifica la integridad de la base de datos SQLite."""
    app = get_app()
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    if not os.path.exists(db_path):
        logging.error(f"Base de datos no encontrada en: {db_path}")
        return False
    
    try:
        # Conectar directamente a SQLite para verificar integridad
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar integridad
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        
        if result[0] == 'ok':
            logging.info("Verificación de integridad de la base de datos: OK")
            return True
        else:
            logging.error(f"Problemas de integridad en la base de datos: {result[0]}")
            return False
    except Exception as e:
        logging.error(f"Error al verificar la integridad de la base de datos: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def reset_user_sessions():
    """Resetea las sesiones de todos los usuarios."""
    try:
        app = get_app()
        with app.app_context():
            # Obtener todos los usuarios
            users = User.query.all()
            
            for user in users:
                logging.info(f"Actualizando usuario: {user.username} ({user.email})")
                
                # Actualizar último login
                user.last_login = datetime.utcnow()
                
                # Actualizar expiración de sesión para usuarios gratuitos
                if user.role in ['free', 'user']:
                    user.update_session_expiry()
                    logging.info(f"  Nueva expiración: {user.session_expires_at}")
                
            # Guardar cambios
            db.session.commit()
            logging.info(f"Se actualizaron {len(users)} usuarios correctamente")
            return True
    except Exception as e:
        logging.error(f"Error al resetear sesiones de usuarios: {str(e)}")
        if 'db' in locals() and hasattr(db, 'session'):
            db.session.rollback()
        return False

if __name__ == "__main__":
    print("=== Verificación y reparación de la base de datos ===")
    
    # Verificar integridad
    if check_database_integrity():
        print("✅ La base de datos está en buen estado")
    else:
        print("❌ Se encontraron problemas con la base de datos")
        
    # Resetear sesiones
    if reset_user_sessions():
        print("✅ Sesiones de usuarios actualizadas correctamente")
    else:
        print("❌ Error al actualizar sesiones de usuarios")
        
    print("\nPara completar la solución:")
    print("1. Reinicia el servidor Flask")
    print("2. Borra las cookies del navegador")
    print("3. Intenta iniciar sesión nuevamente") 