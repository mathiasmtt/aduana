import os
from pathlib import Path

class Config:
    """Configuración base para la aplicación Flask."""
    # Ruta base del proyecto
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Configuración de seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-desarrollo')
    
    # Configuración de la base de datos principal (unificada para aranceles y usuarios)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/data/users/users.sqlite3"
    # URI para la base de datos de aranceles
    ARANCEL_DATABASE_URI = "sqlite:///:memory:"  # Base de datos en memoria
    # URI para la base de datos de auxiliares
    AUXILIARES_DATABASE_URI = f"sqlite:///{BASE_DIR}/data/auxiliares.sqlite3"
    
    # Deshabilitamos el tracking de modificaciones para mejorar el rendimiento
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración para el entorno de producción
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo."""
    DEBUG = True

class TestingConfig(Config):
    """Configuración para entorno de pruebas."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{Config.BASE_DIR}/data/test_database.sqlite3"
    # URI para la base de datos de aranceles
    ARANCEL_DATABASE_URI = f"sqlite:////Users/mat/Code/aduana/data/arancel.sqlite3"
    # URI para la base de datos de auxiliares
    AUXILIARES_DATABASE_URI = f"sqlite:///{Config.BASE_DIR}/data/auxiliares.sqlite3"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuración para entorno de producción."""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configuración de logs para producción
        import logging
        from logging.handlers import RotatingFileHandler
        
        handler = RotatingFileHandler(
            'logs/aduana.log', 
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Aplicación iniciada')

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
