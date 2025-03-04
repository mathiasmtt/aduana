from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from .. import db

class User(UserMixin, db.Model):
    """Modelo para la tabla de usuarios."""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))  # Nombre completo del usuario
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='free')  # 'admin', 'vip', 'free'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    session_expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    verification_token = db.Column(db.String(64), nullable=True)  # Token para verificación de email
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        
        # Si no se proporcionó un username pero sí un email, usar la parte local del email
        if 'username' not in kwargs and 'email' in kwargs:
            self.username = kwargs['email'].split('@')[0]
            
        # Si no se proporcionó name pero sí username, usar el username como name
        if 'name' not in kwargs and hasattr(self, 'username'):
            self.name = self.username
            
        # Si el usuario es free, establecer la fecha de expiración de sesión
        if self.role == 'free':
            self.update_session_expiry()
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def password(self):
        raise AttributeError('La contraseña no es un atributo legible')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        try:
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            # Log the error
            import logging
            logging.error(f"Error al verificar contraseña: {str(e)}")
            return False
    
    def update_session_expiry(self):
        """Actualiza la fecha de expiración de la sesión para usuarios free."""
        if self.role in ['free', 'user']:
            # Los usuarios free tienen sesiones que expiran después de 1 hora
            self.session_expires_at = datetime.utcnow() + timedelta(hours=1)
        else:
            # Los usuarios admin y vip no tienen expiración
            self.session_expires_at = None
    
    def is_session_valid(self):
        """Verifica si la sesión del usuario sigue siendo válida."""
        if self.role in ['admin', 'vip']:
            return True
        return self.session_expires_at and datetime.utcnow() < self.session_expires_at
    
    @property
    def is_admin(self):
        """Verifica si el usuario tiene rol de administrador."""
        return self.role == 'admin'
    
    @property
    def is_vip(self):
        """Verifica si el usuario tiene rol VIP."""
        return self.role == 'vip'
    
    @property
    def is_free(self):
        """Verifica si el usuario tiene rol gratuito."""
        return self.role in ['free', 'user']
    
    @property
    def session_remaining_time(self):
        """Devuelve el tiempo restante de sesión en minutos para usuarios free."""
        if not self.session_expires_at:
            return None
        remaining = self.session_expires_at - datetime.utcnow()
        # Convertir a minutos
        return max(0, int(remaining.total_seconds() / 60))
