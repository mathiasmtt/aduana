from app import create_app, db
from app.models import Arancel

# Mapeo de primeros 2 dígitos del NCM a información de capítulo y sección
TAXONOMY = {
    # Sección I: Animales vivos y productos del reino animal
    '01': {'chapter': '01 - Animales vivos', 'section': 'I - Animales vivos y productos del reino animal'},
    '02': {'chapter': '02 - Carne y despojos comestibles', 'section': 'I - Animales vivos y productos del reino animal'},
    '03': {'chapter': '03 - Pescados y crustáceos, moluscos y demás invertebrados acuáticos', 'section': 'I - Animales vivos y productos del reino animal'},
    '04': {'chapter': '04 - Leche y productos lácteos; huevos de ave; miel natural', 'section': 'I - Animales vivos y productos del reino animal'},
    '05': {'chapter': '05 - Los demás productos de origen animal', 'section': 'I - Animales vivos y productos del reino animal'},
    
    # Sección II: Productos del reino vegetal
    '06': {'chapter': '06 - Plantas vivas y productos de la floricultura', 'section': 'II - Productos del reino vegetal'},
    '07': {'chapter': '07 - Hortalizas, plantas, raíces y tubérculos alimenticios', 'section': 'II - Productos del reino vegetal'},
    '08': {'chapter': '08 - Frutas y frutos comestibles', 'section': 'II - Productos del reino vegetal'},
    '09': {'chapter': '09 - Café, té, yerba mate y especias', 'section': 'II - Productos del reino vegetal'},
    '10': {'chapter': '10 - Cereales', 'section': 'II - Productos del reino vegetal'},
    '11': {'chapter': '11 - Productos de la molinería; malta; almidón y fécula', 'section': 'II - Productos del reino vegetal'},
    '12': {'chapter': '12 - Semillas y frutos oleaginosos; semillas y frutos diversos', 'section': 'II - Productos del reino vegetal'},
    '13': {'chapter': '13 - Gomas, resinas y demás jugos y extractos vegetales', 'section': 'II - Productos del reino vegetal'},
    '14': {'chapter': '14 - Materias trenzables y demás productos de origen vegetal', 'section': 'II - Productos del reino vegetal'},
    
    # Sección III: Grasas y aceites
    '15': {'chapter': '15 - Grasas y aceites animales o vegetales', 'section': 'III - Grasas y aceites animales o vegetales'},
    
    # Sección IV: Productos de las industrias alimentarias
    '16': {'chapter': '16 - Preparaciones de carne, pescado o de crustáceos', 'section': 'IV - Productos de las industrias alimentarias'},
    '17': {'chapter': '17 - Azúcares y artículos de confitería', 'section': 'IV - Productos de las industrias alimentarias'},
    '18': {'chapter': '18 - Cacao y sus preparaciones', 'section': 'IV - Productos de las industrias alimentarias'},
    '19': {'chapter': '19 - Preparaciones a base de cereales, harina, almidón, fécula o leche', 'section': 'IV - Productos de las industrias alimentarias'},
    '20': {'chapter': '20 - Preparaciones de hortalizas, frutas u otros frutos', 'section': 'IV - Productos de las industrias alimentarias'},
    '21': {'chapter': '21 - Preparaciones alimenticias diversas', 'section': 'IV - Productos de las industrias alimentarias'},
    '22': {'chapter': '22 - Bebidas, líquidos alcohólicos y vinagre', 'section': 'IV - Productos de las industrias alimentarias'},
    '23': {'chapter': '23 - Residuos y desperdicios de las industrias alimentarias', 'section': 'IV - Productos de las industrias alimentarias'},
    '24': {'chapter': '24 - Tabaco y sucedáneos del tabaco elaborados', 'section': 'IV - Productos de las industrias alimentarias'},
    
    # Sección V: Productos minerales
    '25': {'chapter': '25 - Sal; azufre; tierras y piedras; yesos, cales y cementos', 'section': 'V - Productos minerales'},
    '26': {'chapter': '26 - Minerales metalíferos, escorias y cenizas', 'section': 'V - Productos minerales'},
    '27': {'chapter': '27 - Combustibles minerales, aceites minerales', 'section': 'V - Productos minerales'},
}

def update_chapter_section():
    """Actualiza la información de capítulo y sección en la base de datos."""
    app = create_app()
    with app.app_context():
        # Obtener todos los aranceles
        aranceles = Arancel.query.all()
        
        updates = 0
        for arancel in aranceles:
            # Extraer los primeros 2 dígitos del NCM
            prefix = arancel.NCM[:2]
            
            # Buscar en el mapeo
            if prefix in TAXONOMY:
                arancel.CHAPTER = TAXONOMY[prefix]['chapter']
                arancel.SECTION = TAXONOMY[prefix]['section']
                updates += 1
        
        # Commit a la base de datos
        db.session.commit()
        
        print(f"Se actualizaron {updates} registros de {len(aranceles)} en total.")
        
        # Verificar capítulos y secciones distintas después de la actualización
        capitulos_count = db.session.query(Arancel.CHAPTER).distinct().filter(Arancel.CHAPTER != "").count()
        secciones_count = db.session.query(Arancel.SECTION).distinct().filter(Arancel.SECTION != "").count()
        
        print(f"Ahora hay {capitulos_count} capítulos distintos y {secciones_count} secciones distintas.")

if __name__ == "__main__":
    update_chapter_section()
