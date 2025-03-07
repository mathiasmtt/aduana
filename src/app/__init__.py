from flask import Flask, g, request, session, current_app, has_app_context, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import config
import logging
import os

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Inicializa las extensiones antes de crear la aplicación
# No se inicializa completamente hasta tener una aplicación
db = SQLAlchemy(session_options={"autoflush": False, "autocommit": False})
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Única instancia global de la aplicación
_app = None

def create_app(config_name='default'):
    """Fábrica de aplicación - crea una instancia de la aplicación Flask con la 
    configuración especificada.
    
    Args:
        config_name (str): Nombre de la configuración a utilizar (default, development, testing, production)
        
    Returns:
        Flask: Instancia de la aplicación Flask configurada
    """
    global _app, db
    
    # Inicializar solo una vez
    if _app is not None:
        logging.info("Usando instancia de aplicación existente")
        return _app
    
    logging.info(f"Creando nueva instancia de aplicación con configuración: {config_name}")
    
    # Crear nueva aplicación
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configuración crítica para SQLAlchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    config[config_name].init_app(app)
    
    # Guardar como instancia global
    _app = app
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Push manual del contexto de aplicación - SIEMPRE SE MANTIENE ACTIVO
    ctx = app.app_context()
    ctx.push()
    logging.info("Contexto de aplicación establecido globalmente")
    
    # Configuración del sistema de bases de datos versionadas
    from .db_utils import init_app as init_db_utils
    init_db_utils(app)
    
    # Verificar el contexto de aplicación
    if has_app_context():
        logging.info("Verificación: contexto de aplicación disponible")
    else:
        logging.error("Verificación: NO hay contexto de aplicación disponible")
    
    # Middleware para manejar la versión seleccionada
    @app.before_request
    def before_request():
        # Verificar si hay un parámetro 'version' en la URL
        version = request.args.get('version')
        if version:
            g.version = version
        else:
            # Si no hay versión en la URL, verificar si hay una versión almacenada en la sesión
            if 'arancel_version' in session:
                g.version = session.get('arancel_version')
            else:
                # Si no hay versión en la sesión, no establecemos ninguna versión específica
                # para que use la última por defecto (None o '')
                g.version = ''
    
    # Definir el cargador de usuarios para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        try:
            if not has_app_context():
                logging.error("load_user: No hay contexto de aplicación")
                # Forzar el contexto si no existe
                ctx = app.app_context()
                ctx.push()
                logging.info("load_user: Contexto de aplicación forzado")
                
            if user_id is None:
                return None
                
            # Importamos User aquí para evitar importaciones circulares
            from src.app.models.user import User
            
            # Usamos db.session.get que es más eficiente para búsquedas por clave primaria
            user = db.session.get(User, int(user_id))
            return user
        except Exception as e:
            logging.error(f"Error en load_user: {str(e)}")
            return None
    
    # Registrar blueprints
    from .routes.main import main_bp
    from .routes.api import api_bp
    from .routes.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Crear función para forzar HTTPS en producción
    @app.before_request
    def before_request_https():
        if current_app.config.get('ENV') == 'production':
            if request.url.startswith('http://'):
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)
    
    # Gestión del cierre de la conexión al finalizar
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        try:
            db.session.remove()
        except Exception as e:
            logging.error(f"Error al cerrar sesión de base de datos: {str(e)}")
    
    # Crear todas las tablas si no existen
    try:
        with app.app_context():
            db.create_all()
            logging.info("Tablas creadas/verificadas correctamente")
    except Exception as e:
        logging.error(f"Error al crear tablas: {str(e)}")
    
    return app

def get_app():
    """
    Devuelve la instancia actual de la aplicación Flask.
    Útil cuando se necesita acceder a la aplicación fuera del contexto normal.
    
    Returns:
        Flask: Instancia actual de la aplicación
    """
    global _app
    if _app is None:
        # Obtener configuración del entorno o usar la predeterminada
        config_name = os.environ.get('FLASK_CONFIG', 'default')
        # Si no hay instancia, crear una con la configuración por defecto
        _app = create_app(config_name)
    return _app

def has_db_context():
    """
    Verifica si existe un contexto de base de datos válido.
    
    Returns:
        bool: True si hay un contexto de base de datos válido, False en caso contrario
    """
    try:
        return has_app_context() and db.session is not None
    except Exception:
        return False
