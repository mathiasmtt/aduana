from app import get_app, db
from app.models.user import User
from datetime import datetime, timedelta
from flask_login import login_user, current_user
import flask
import json

app = get_app()
with app.app_context():
    print('=== Depuración de sesiones de usuario ===')
    
    # Cargar el usuario de prueba
    user = User.query.filter_by(email='free@aduana.com').first()
    
    if not user:
        print('Error: Usuario free@aduana.com no encontrado')
        exit(1)
    
    print(f'Usuario encontrado: {user.username}, rol: {user.role}')
    print(f'Última actividad: {user.last_login}')
    print(f'Expiración de sesión: {user.session_expires_at}')
    
    # Verificar expiración
    if user.session_expires_at:
        now = datetime.utcnow()
        print(f'Hora actual (UTC): {now}')
        
        if now > user.session_expires_at:
            print('ALERTA: La sesión ha expirado')
        else:
            time_left = user.session_expires_at - now
            print(f'Tiempo restante: {time_left.total_seconds() / 60:.2f} minutos')
    
    # Actualizar la expiración de sesión
    print('\nActualizando expiración de sesión...')
    user.update_session_expiry()
    db.session.commit()
    
    print(f'Nueva expiración: {user.session_expires_at}')
    time_left = user.session_expires_at - datetime.utcnow()
    print(f'Nuevo tiempo restante: {time_left.total_seconds() / 60:.2f} minutos')
    
    # Probar métodos de validación de sesión
    print('\nValidación de sesión:')
    print(f'is_session_valid(): {user.is_session_valid()}')
    print(f'session_remaining_time: {user.session_remaining_time} minutos')
    
    # Verificar cookie de sesión
    print('\nPrueba de configuración de sesión de Flask:')
    print(f'Configuración secreta: {app.config.get("SECRET_KEY")[:10]}...')
    print(f'Permanencia de sesión: {app.config.get("PERMANENT_SESSION_LIFETIME")}')
    
    # Verificar otras configuraciones relevantes
    print('\nConfiguración general:')
    print(f'Flask-Login cookie: {app.config.get("REMEMBER_COOKIE_DURATION")}')
    print(f'Flask-Login refresh: {getattr(app.config, "REMEMBER_COOKIE_REFRESH_EACH_REQUEST", "No configurado")}') 