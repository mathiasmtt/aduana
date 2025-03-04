from flask import Blueprint, render_template, request, url_for, flash, redirect, current_app, session as flask_session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import logging

from .. import db, has_app_context
from ..models.user import User

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constante para el tiempo de expiración de sesión (en minutos)
SESSION_EXPIRY_MINUTES = 60

def check_session_expiry():
    """
    Verifica si la sesión del usuario ha expirado.
    Si ha expirado, cierra la sesión y redirige al usuario a la página de inicio de sesión.
    
    Returns:
        None si la sesión es válida, o una redirección si ha expirado
    """
    # Si no hay usuario logueado, no hay nada que verificar
    if not current_user.is_authenticated:
        logging.debug("check_session_expiry: No hay usuario autenticado")
        return None
        
    # Verificar si existe el timestamp de la última actividad
    last_active = flask_session.get('last_active')
    if not last_active:
        # Si no existe, actualizar el timestamp y continuar
        logging.debug(f"check_session_expiry: No hay timestamp de última actividad para {current_user.email}, actualizando")
        flask_session['last_active'] = datetime.utcnow().timestamp()
        return None
        
    # Verificar si ha pasado más tiempo del permitido
    last_active_dt = datetime.fromtimestamp(last_active)
    expiry_time = last_active_dt + timedelta(minutes=SESSION_EXPIRY_MINUTES)
    
    logging.debug(f"check_session_expiry: Usuario: {current_user.email}, Última actividad: {last_active_dt}, Expiración: {expiry_time}")
    
    if datetime.utcnow() > expiry_time:
        # La sesión ha expirado, cerrar sesión
        logging.warning(f"check_session_expiry: Sesión expirada para {current_user.email}")
        logout_user()
        flask_session.pop('last_active', None)
        flash('Su sesión ha expirado. Por favor inicie sesión nuevamente.', 'warning')
        return redirect(url_for('auth.login'))
        
    # Actualizar el timestamp de última actividad
    logging.debug(f"check_session_expiry: Actualizando timestamp para {current_user.email}")
    flask_session['last_active'] = datetime.utcnow().timestamp()
    return None

@auth_bp.before_request
def update_last_active():
    """Actualizar timestamp de última actividad para cada solicitud."""
    if current_user.is_authenticated:
        logging.debug(f"update_last_active: Actualizando timestamp para {current_user.email}")
        flask_session['last_active'] = datetime.utcnow().timestamp()
        
        # Verificar si la sesión del usuario es válida según el modelo
        if not current_user.is_session_valid():
            logging.warning(f"update_last_active: Sesión inválida para {current_user.email} según el modelo")
            # Actualizar la expiración de sesión
            current_user.update_session_expiry()
            db.session.commit()
            logging.info(f"update_last_active: Expiración actualizada para {current_user.email}: {current_user.session_expires_at}")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para inicio de sesión."""
    # Si el usuario ya está autenticado, redirigir a la página principal
    if current_user.is_authenticated:
        logging.info(f"login: Usuario ya autenticado: {current_user.email}")
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember_me') else False
        
        # Logging de información recibida para diagnóstico
        logging.debug(f"Intento de login - Email: {email}, Remember: {remember}")
        logging.debug(f"Datos del formulario: {request.form}")
        
        # Asegurar que estamos en un contexto de aplicación
        if not has_app_context():
            logging.error("No hay un contexto de aplicación activo")
            flash('Error en el servidor. Por favor intente nuevamente.', 'danger')
            return render_template('auth/login.html')
        
        try:
            # Buscar usuario por email
            with db.session.no_autoflush:
                user = db.session.query(User).filter_by(email=email).first()
            
            # Verificar si el usuario existe
            if not user:
                logging.debug(f"Usuario no encontrado para email: {email}")
                flash('Credenciales incorrectas. Por favor intente nuevamente.', 'danger')
                return render_template('auth/login.html')
                
            # Verificar si la contraseña es correcta    
            if not user.verify_password(password):
                logging.debug(f"Contraseña incorrecta para usuario: {email}")
                flash('Credenciales incorrectas. Por favor intente nuevamente.', 'danger')
                return render_template('auth/login.html')
            
            # Iniciar sesión del usuario
            logging.info(f"Inicio de sesión exitoso para usuario: {email}")
            login_result = login_user(user, remember=remember)
            
            if not login_result:
                logging.error(f"Error en login_user para {email}, devolvió False")
                flash('Error al iniciar sesión. Por favor intente nuevamente.', 'danger')
                return render_template('auth/login.html')
                
            logging.debug(f"Usuario autenticado: {current_user.is_authenticated}")
            
            # Guardar timestamp de última actividad
            flask_session['last_active'] = datetime.utcnow().timestamp()
            
            # Actualizar último login y expiración de sesión
            user.last_login = datetime.utcnow()
            if user.role in ['free', 'user']:
                user.update_session_expiry()
                logging.info(f"Expiración de sesión actualizada para {email}: {user.session_expires_at}")
            
            db.session.commit()
            
            # Redirigir a la página solicitada o a la página principal
            next_page = request.args.get('next')
            
            if next_page:
                logging.info(f"Redirigiendo a la página solicitada: {next_page}")
                return redirect(next_page)
                
            logging.info(f"Redirigiendo a la página principal (main.index)")
            return redirect(url_for('main.index'))
        except Exception as e:
            # Registrar el error
            logging.error(f"Error en login: {str(e)}")
            # Hacer rollback para evitar que la sesión quede en un estado inconsistente
            db.session.rollback()
            flash('Error al iniciar sesión. Por favor intente nuevamente.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Ruta para registro de nuevos usuarios."""
    # Si el usuario ya está autenticado, redirigir a la página principal
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        # Logging para diagnóstico
        logging.debug(f"Intento de registro - Email: {email}, Nombre: {name}")
        
        # Asegurar que estamos en un contexto de aplicación
        if not has_app_context():
            logging.error("No hay un contexto de aplicación activo")
            flash('Error en el servidor. Por favor intente nuevamente.', 'danger')
            return render_template('auth/register.html')
        
        try:
            # Verificar si el email ya está en uso
            with db.session.no_autoflush:
                user = db.session.query(User).filter_by(email=email).first()
            
            if user:
                logging.debug(f"Email ya registrado: {email}")
                flash('El email ya está registrado. Intente con otro o inicie sesión.', 'warning')
                return render_template('auth/register.html')
            
            # Crear nuevo usuario (rol 'user' por defecto)
            new_user = User(
                email=email,
                username=name,  # Aseguramos que el username se establezca
                name=name,
                password_hash=generate_password_hash(password),
                role='user',
                # Generar un token de verificación (no se usa en este ejemplo)
                verification_token=secrets.token_urlsafe(32)
            )
            
            # Guardar el usuario en la base de datos
            db.session.add(new_user)
            db.session.commit()
            logging.info(f"Usuario registrado exitosamente: {email}")
            
            # Iniciar sesión del nuevo usuario
            login_user(new_user)
            
            # Guardar timestamp de última actividad
            flask_session['last_active'] = datetime.utcnow().timestamp()
            
            flash('¡Registro exitoso! Bienvenido a ADUANA.', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            # Registrar el error
            logging.error(f"Error en registro: {str(e)}")
            # Hacer rollback para evitar que la sesión quede en un estado inconsistente
            db.session.rollback()
            flash('Error al registrar usuario. Por favor intente nuevamente.', 'danger')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Ruta para cerrar sesión."""
    if current_user.is_authenticated:
        logging.info(f"Cierre de sesión para usuario: {current_user.email}")
    logout_user()
    flask_session.pop('last_active', None)
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Ruta para ver perfil de usuario."""
    # Verificar si la sesión ha expirado
    redirect_response = check_session_expiry()
    if redirect_response:
        return redirect_response
        
    return render_template('auth/profile.html')
