from app import get_app, db
from app.models.user import User
from datetime import datetime
from flask_login import login_user, current_user
import flask
from flask import session as flask_session

app = get_app()
with app.app_context():
    print('=== Simulando proceso de login ===')
    
    # Cargar el usuario de prueba
    user = User.query.filter_by(email='free@aduana.com').first()
    
    if not user:
        print('Error: Usuario free@aduana.com no encontrado')
        exit(1)
    
    print(f'Usuario encontrado: {user.username}, rol: {user.role}')
    
    # Crear un contexto de solicitud ficticio
    with app.test_request_context():
        # Simular inicio de sesión
        print('\nIniciando sesión...')
        login_result = login_user(user)
        print(f'Resultado de login_user(): {login_result}')
        
        # Verificar si el usuario está autenticado
        print(f'Usuario autenticado: {current_user.is_authenticated}')
        
        # Actualizar último acceso y expiración
        user.last_login = datetime.utcnow()
        user.update_session_expiry()
        flask_session['last_active'] = datetime.utcnow().timestamp()
        
        db.session.commit()
        
        print(f'Expiración de sesión actualizada: {user.session_expires_at}')
        print(f'Tiempo restante: {user.session_remaining_time} minutos')
        
        # Verificar las cookies de sesión
        print('\nDatos de sesión Flask:')
        print(f'Session ID: {flask_session.get("_id", "No disponible")}')
        print(f'Session last_active: {flask_session.get("last_active", "No disponible")}')
        print(f'Session permanent: {flask_session.get("_permanent", "No disponible")}')
        
        # Verificar el id de usuario en la sesión
        print('\nDatos de Flask-Login:')
        user_id = flask_session.get('_user_id')
        print(f'User ID en sesión: {user_id}')
        
        # Verificar si coincide con el usuario actual
        if user_id and int(user_id) == user.id:
            print('El ID de usuario en la sesión coincide con el usuario logueado ✅')
        else:
            print('¡ALERTA! El ID de usuario en la sesión NO coincide ❌')
        
        # Recargar el usuario para asegurarse de que la sesión está actualizada
        user = User.query.get(user.id)
        print(f'\nEstado de la sesión del usuario después del login:')
        print(f'Sesión válida: {user.is_session_valid()}')
        print(f'Tiempo restante: {user.session_remaining_time} minutos') 