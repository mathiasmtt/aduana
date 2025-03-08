# Importación de modelos para facilitar el acceso desde otros módulos
# Aseguramos importar la misma instancia de db usada en toda la aplicación
from .. import db

# Importamos los modelos después de importar db
from .arancel import Arancel
from .chapter_note import ChapterNote
from .section_note import SectionNote
from .user import User
from .auxiliares import CodigoPaises, init_auxiliares_db
