from flask import Flask, g, request, session, current_app, has_app_context, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
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
csrf = CSRFProtect()

# Importamos aquí para evitar importaciones circulares
from .models.auxiliares import init_auxiliares_db

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
    
    app.config["SQLALCHEMY_BINDS"] = {
        'arancel': app.config['ARANCEL_DATABASE_URI'],
        'auxiliares': app.config['AUXILIARES_DATABASE_URI']
    }
    
    config[config_name].init_app(app)
    
    # Guardar como instancia global
    _app = app
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Inicializar base de datos auxiliares
    init_auxiliares_db(app)
    
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
            from app.models.user import User
            
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
            # Verificar si estamos usando una base de datos diferente a database.sqlite3
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'database.sqlite3' not in db_uri:
                db.create_all()
                logging.info("Tablas creadas/verificadas correctamente en la base de datos de usuarios")
            else:
                logging.info("Se omitió la creación automática de database.sqlite3")
                
            # Si estamos usando una base de datos en memoria para aranceles, 
            # necesitamos crear las tablas y añadir datos de ejemplo
            arancel_db_uri = app.config.get('ARANCEL_DATABASE_URI', '')
            if ':memory:' in arancel_db_uri:
                logging.info("Detectada base de datos en memoria para aranceles. Creando tablas...")
                # Actualizado para ser compatible con SQLAlchemy 2.0
                with db.engine.connect() as conn:
                    db.metadata.create_all(bind=db.engines['arancel'])
                
                # Crear datos de ejemplo básicos
                from .models.arancel import Arancel
                from .models.section_note import SectionNote
                from .models.chapter_note import ChapterNote
                
                # Verificar si ya hay datos
                if not db.session.query(Arancel).first():
                    logging.info("Creando datos de ejemplo para la base de datos de aranceles en memoria...")
                    
                    # Crear algunas secciones y capítulos de ejemplo
                    secciones_ejemplo = [
                        {
                            "NCM": "01.01.10.00",
                            "DESCRIPCION": "Caballos reproductores de raza pura",
                            "AEC": "0",
                            "SECTION": "I - ANIMALES VIVOS Y PRODUCTOS DEL REINO ANIMAL",
                            "CHAPTER": "01 - ANIMALES VIVOS"
                        },
                        {
                            "NCM": "02.01.10.00",
                            "DESCRIPCION": "Carne de bovinos fresca o refrigerada",
                            "AEC": "0",
                            "SECTION": "I - ANIMALES VIVOS Y PRODUCTOS DEL REINO ANIMAL",
                            "CHAPTER": "02 - CARNE Y DESPOJOS COMESTIBLES"
                        },
                        {
                            "NCM": "15.01.10.00",
                            "DESCRIPCION": "Manteca de cerdo",
                            "AEC": "10",
                            "SECTION": "III - GRASAS Y ACEITES ANIMALES O VEGETALES",
                            "CHAPTER": "15 - GRASAS Y ACEITES ANIMALES O VEGETALES"
                        },
                        {
                            "NCM": "25.01.00.11",
                            "DESCRIPCION": "Sal de mesa",
                            "AEC": "0",
                            "SECTION": "V - PRODUCTOS MINERALES",
                            "CHAPTER": "25 - SAL; AZUFRE; TIERRAS Y PIEDRAS"
                        }
                    ]
                    
                    for item in secciones_ejemplo:
                        arancel = Arancel(
                            NCM=item["NCM"],
                            DESCRIPCION=item["DESCRIPCION"],
                            AEC=item["AEC"],
                            SECTION=item["SECTION"],
                            CHAPTER=item["CHAPTER"]
                        )
                        db.session.add(arancel)
                    
                    # Crear algunas notas de sección de ejemplo
                    if not db.session.query(SectionNote).first():
                        section_note = SectionNote(
                            section_number="I",
                            note_text="Nota de ejemplo para la sección I"
                        )
                        db.session.add(section_note)
                    
                    # Crear algunas notas de capítulo de ejemplo
                    if not db.session.query(ChapterNote).first():
                        chapter_note = ChapterNote(
                            chapter_number="01",
                            note_text="Nota de ejemplo para el capítulo 01"
                        )
                        db.session.add(chapter_note)
                    
                    # Guardar cambios
                    db.session.commit()
                    logging.info("Datos de ejemplo creados correctamente para la base de datos en memoria")
    except Exception as e:
        logging.error(f"Error al crear tablas: {str(e)}")
    
    # Registrar manejadores de errores HTTP
    @app.errorhandler(404)
    def page_not_found(e):
        logging.error(f"Error 404: {request.path}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(e):
        logging.error(f"Error 403: {request.path}")
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logging.error(f"Error 500: {str(e)}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(503)
    def service_unavailable(e):
        logging.error(f"Error 503: {str(e)}")
        return render_template('errors/503.html'), 503
    
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
