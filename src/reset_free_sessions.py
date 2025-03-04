from app import get_app, db
from app.models.user import User
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = get_app()
with app.app_context():
    print('=== Actualizando sesiones de usuarios gratuitos ===')
    
    # Obtener todos los usuarios gratuitos
    free_users = User.query.filter(User.role.in_(['free', 'user'])).all()
    
    print(f'Encontrados {len(free_users)} usuarios gratuitos')
    
    # Resetear la expiración de sesión para todos los usuarios gratuitos
    updated_count = 0
    for user in free_users:
        print(f'Usuario: {user.username}, Email: {user.email}')
        print(f'  Expiración actual: {user.session_expires_at}')
        
        # Actualizar la expiración
        user.update_session_expiry()
        print(f'  Nueva expiración: {user.session_expires_at}')
        
        # Actualizar el último login para que coincida
        user.last_login = datetime.utcnow()
        print(f'  Último login actualizado: {user.last_login}')
        
        updated_count += 1
    
    # Guardar los cambios en la base de datos
    if updated_count > 0:
        db.session.commit()
        print(f'\n✅ Se actualizaron correctamente {updated_count} usuarios')
    else:
        print('\n⚠️ No se realizaron cambios')
        
    print('\nPara asegurar que los cambios surtan efecto:')
    print('1. Reinicia el servidor Flask')
    print('2. Pide a los usuarios que cierren sesión y vuelvan a iniciar sesión')
    print('3. Verifica que pueden acceder al sistema correctamente') 