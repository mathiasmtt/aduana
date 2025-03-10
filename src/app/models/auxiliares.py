from flask import current_app
import os
from pathlib import Path
from .. import db  # Importar la instancia principal de SQLAlchemy

# Ya no necesitamos crear una nueva instancia de SQLAlchemy
# auxiliares_db = SQLAlchemy()

class CodigoPaises(db.Model):
    """
    Modelo para la tabla CODIGO_PAISES que contiene los códigos de países.
    """
    __tablename__ = 'CODIGO_PAISES'
    __bind_key__ = 'auxiliares'  # Especificar que esta tabla usa el bind 'auxiliares'
    
    # Definición de campos
    id = db.Column(db.Integer, primary_key=True)
    codigo_num = db.Column(db.String(3), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    codigo_letras = db.Column(db.String(3), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<País {self.codigo_letras} ({self.codigo_num}): {self.nombre}>"

def init_auxiliares_db(app):
    """
    Inicializa la conexión a la base de datos auxiliares.
    """
    # No necesitamos hacer nada aquí, ya que la instancia principal de db
    # ya está configurada con el bind 'auxiliares' en __init__.py
    pass

def create_auxiliares_tables():
    """
    Crea las tablas en la base de datos auxiliares.
    """
    # Verificar que el directorio data exista
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    data_dir = base_dir / 'data'
    
    if not data_dir.exists():
        os.makedirs(data_dir)
    
    # Crear la conexión y las tablas
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/data/auxiliares.sqlite3"
    app.config['SQLALCHEMY_BINDS'] = {
        'auxiliares': f"sqlite:///{base_dir}/data/auxiliares.sqlite3"
    }
    
    # Inicializar la base de datos
    db.init_app(app)
    
    with app.app_context():
        # Actualizado para ser compatible con SQLAlchemy 2.0
        with db.engine.connect() as conn:
            db.metadata.create_all(bind=db.engines['auxiliares'])
        print("Tablas de auxiliares creadas correctamente.")

if __name__ == "__main__":
    create_auxiliares_tables() 