from app import create_app, db
from app.models import Arancel

# Mapeo completo de todos los capítulos del NCM
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
    
    # Sección VI: Productos de las industrias químicas
    '28': {'chapter': '28 - Productos químicos inorgánicos', 'section': 'VI - Productos de las industrias químicas'},
    '29': {'chapter': '29 - Productos químicos orgánicos', 'section': 'VI - Productos de las industrias químicas'},
    '30': {'chapter': '30 - Productos farmacéuticos', 'section': 'VI - Productos de las industrias químicas'},
    '31': {'chapter': '31 - Abonos', 'section': 'VI - Productos de las industrias químicas'},
    '32': {'chapter': '32 - Extractos curtientes o tintóreos', 'section': 'VI - Productos de las industrias químicas'},
    '33': {'chapter': '33 - Aceites esenciales y resinoides', 'section': 'VI - Productos de las industrias químicas'},
    '34': {'chapter': '34 - Jabón, agentes de superficie orgánicos', 'section': 'VI - Productos de las industrias químicas'},
    '35': {'chapter': '35 - Materias albuminoideas', 'section': 'VI - Productos de las industrias químicas'},
    '36': {'chapter': '36 - Pólvoras y explosivos', 'section': 'VI - Productos de las industrias químicas'},
    '37': {'chapter': '37 - Productos fotográficos o cinematográficos', 'section': 'VI - Productos de las industrias químicas'},
    '38': {'chapter': '38 - Productos diversos de las industrias químicas', 'section': 'VI - Productos de las industrias químicas'},
    
    # Sección VII: Plástico y caucho
    '39': {'chapter': '39 - Plástico y sus manufacturas', 'section': 'VII - Plástico y caucho'},
    '40': {'chapter': '40 - Caucho y sus manufacturas', 'section': 'VII - Plástico y caucho'},
    
    # Sección VIII: Pieles, cueros y peletería
    '41': {'chapter': '41 - Pieles (excepto la peletería) y cueros', 'section': 'VIII - Pieles, cueros y peletería'},
    '42': {'chapter': '42 - Manufacturas de cuero', 'section': 'VIII - Pieles, cueros y peletería'},
    '43': {'chapter': '43 - Peletería y confecciones de peletería', 'section': 'VIII - Pieles, cueros y peletería'},
    
    # Sección IX: Madera, carbón vegetal y corcho
    '44': {'chapter': '44 - Madera, carbón vegetal y manufacturas de madera', 'section': 'IX - Madera, carbón vegetal y corcho'},
    '45': {'chapter': '45 - Corcho y sus manufacturas', 'section': 'IX - Madera, carbón vegetal y corcho'},
    '46': {'chapter': '46 - Manufacturas de espartería o cestería', 'section': 'IX - Madera, carbón vegetal y corcho'},
    
    # Sección X: Pasta de madera, papel y cartón
    '47': {'chapter': '47 - Pasta de madera o de otras materias fibrosas celulósicas', 'section': 'X - Pasta de madera, papel y cartón'},
    '48': {'chapter': '48 - Papel y cartón; manufacturas de pasta de celulosa', 'section': 'X - Pasta de madera, papel y cartón'},
    '49': {'chapter': '49 - Productos editoriales, de la prensa y similares', 'section': 'X - Pasta de madera, papel y cartón'},
    
    # Sección XI: Materias textiles y sus manufacturas
    '50': {'chapter': '50 - Seda', 'section': 'XI - Materias textiles y sus manufacturas'},
    '51': {'chapter': '51 - Lana y pelo fino u ordinario', 'section': 'XI - Materias textiles y sus manufacturas'},
    '52': {'chapter': '52 - Algodón', 'section': 'XI - Materias textiles y sus manufacturas'},
    '53': {'chapter': '53 - Las demás fibras textiles vegetales', 'section': 'XI - Materias textiles y sus manufacturas'},
    '54': {'chapter': '54 - Filamentos sintéticos o artificiales', 'section': 'XI - Materias textiles y sus manufacturas'},
    '55': {'chapter': '55 - Fibras sintéticas o artificiales discontinuas', 'section': 'XI - Materias textiles y sus manufacturas'},
    '56': {'chapter': '56 - Guata, fieltro y tela sin tejer', 'section': 'XI - Materias textiles y sus manufacturas'},
    '57': {'chapter': '57 - Alfombras y demás revestimientos para el suelo', 'section': 'XI - Materias textiles y sus manufacturas'},
    '58': {'chapter': '58 - Tejidos especiales', 'section': 'XI - Materias textiles y sus manufacturas'},
    '59': {'chapter': '59 - Telas impregnadas, recubiertas o revestidas', 'section': 'XI - Materias textiles y sus manufacturas'},
    '60': {'chapter': '60 - Tejidos de punto', 'section': 'XI - Materias textiles y sus manufacturas'},
    '61': {'chapter': '61 - Prendas y complementos de vestir, de punto', 'section': 'XI - Materias textiles y sus manufacturas'},
    '62': {'chapter': '62 - Prendas y complementos de vestir, excepto los de punto', 'section': 'XI - Materias textiles y sus manufacturas'},
    '63': {'chapter': '63 - Los demás artículos textiles confeccionados', 'section': 'XI - Materias textiles y sus manufacturas'},
    
    # Sección XII: Calzado, sombreros y paraguas
    '64': {'chapter': '64 - Calzado, polainas y artículos análogos', 'section': 'XII - Calzado, sombreros y paraguas'},
    '65': {'chapter': '65 - Sombreros, demás tocados, y sus partes', 'section': 'XII - Calzado, sombreros y paraguas'},
    '66': {'chapter': '66 - Paraguas, sombrillas, quitasoles, bastones', 'section': 'XII - Calzado, sombreros y paraguas'},
    '67': {'chapter': '67 - Plumas y plumón preparados', 'section': 'XII - Calzado, sombreros y paraguas'},
    
    # Sección XIII: Manufacturas de piedra, yeso y similares
    '68': {'chapter': '68 - Manufacturas de piedra, yeso, cemento, amianto, mica', 'section': 'XIII - Manufacturas de piedra, yeso y similares'},
    '69': {'chapter': '69 - Productos cerámicos', 'section': 'XIII - Manufacturas de piedra, yeso y similares'},
    '70': {'chapter': '70 - Vidrio y sus manufacturas', 'section': 'XIII - Manufacturas de piedra, yeso y similares'},
    
    # Sección XIV: Perlas, piedras preciosas o semipreciosas, metales preciosos
    '71': {'chapter': '71 - Perlas finas o cultivadas, piedras preciosas, metales preciosos', 'section': 'XIV - Perlas, piedras preciosas o semipreciosas, metales preciosos'},
    
    # Sección XV: Metales comunes y sus manufacturas
    '72': {'chapter': '72 - Fundición, hierro y acero', 'section': 'XV - Metales comunes y sus manufacturas'},
    '73': {'chapter': '73 - Manufacturas de fundición, hierro o acero', 'section': 'XV - Metales comunes y sus manufacturas'},
    '74': {'chapter': '74 - Cobre y sus manufacturas', 'section': 'XV - Metales comunes y sus manufacturas'},
    '75': {'chapter': '75 - Níquel y sus manufacturas', 'section': 'XV - Metales comunes y sus manufacturas'},
    '76': {'chapter': '76 - Aluminio y sus manufacturas', 'section': 'XV - Metales comunes y sus manufacturas'},
    '78': {'chapter': '78 - Plomo y sus manufacturas', 'section': 'XV - Metales comunes y sus manufacturas'},
    '79': {'chapter': '79 - Cinc y sus manufacturas', 'section': 'XV - Metales comunes y sus manufacturas'},
    '80': {'chapter': '80 - Estaño y sus manufacturas', 'section': 'XV - Metales comunes y sus manufacturas'},
    '81': {'chapter': '81 - Los demás metales comunes', 'section': 'XV - Metales comunes y sus manufacturas'},
    '82': {'chapter': '82 - Herramientas y útiles, artículos de cuchillería', 'section': 'XV - Metales comunes y sus manufacturas'},
    '83': {'chapter': '83 - Manufacturas diversas de metal común', 'section': 'XV - Metales comunes y sus manufacturas'},
    
    # Sección XVI: Máquinas, aparatos y material eléctrico
    '84': {'chapter': '84 - Reactores nucleares, calderas, máquinas', 'section': 'XVI - Máquinas, aparatos y material eléctrico'},
    '85': {'chapter': '85 - Máquinas, aparatos y material eléctrico', 'section': 'XVI - Máquinas, aparatos y material eléctrico'},
    
    # Sección XVII: Material de transporte
    '86': {'chapter': '86 - Vehículos y material para vías férreas', 'section': 'XVII - Material de transporte'},
    '87': {'chapter': '87 - Vehículos automóviles, tractores, velocípedos', 'section': 'XVII - Material de transporte'},
    '88': {'chapter': '88 - Aeronaves, vehículos espaciales, y sus partes', 'section': 'XVII - Material de transporte'},
    '89': {'chapter': '89 - Barcos y demás artefactos flotantes', 'section': 'XVII - Material de transporte'},
    
    # Sección XVIII: Instrumentos y aparatos de óptica, fotografía, medida, control o precisión
    '90': {'chapter': '90 - Instrumentos y aparatos de óptica, fotografía', 'section': 'XVIII - Instrumentos y aparatos de óptica, fotografía, medida, control o precisión'},
    '91': {'chapter': '91 - Aparatos de relojería y sus partes', 'section': 'XVIII - Instrumentos y aparatos de óptica, fotografía, medida, control o precisión'},
    '92': {'chapter': '92 - Instrumentos musicales; sus partes y accesorios', 'section': 'XVIII - Instrumentos y aparatos de óptica, fotografía, medida, control o precisión'},
    
    # Sección XIX: Armas, municiones, y sus partes y accesorios
    '93': {'chapter': '93 - Armas, municiones, y sus partes y accesorios', 'section': 'XIX - Armas, municiones, y sus partes y accesorios'},
    
    # Sección XX: Mercancías y productos diversos
    '94': {'chapter': '94 - Muebles; mobiliario medicoquirúrgico', 'section': 'XX - Mercancías y productos diversos'},
    '95': {'chapter': '95 - Juguetes, juegos y artículos para recreo o deporte', 'section': 'XX - Mercancías y productos diversos'},
    '96': {'chapter': '96 - Manufacturas diversas', 'section': 'XX - Mercancías y productos diversos'},
    
    # Sección XXI: Objetos de arte o colección y antigüedades
    '97': {'chapter': '97 - Objetos de arte o colección y antigüedades', 'section': 'XXI - Objetos de arte o colección y antigüedades'},
}

def update_chapter_section():
    """Actualiza la información de capítulo y sección en la base de datos."""
    app = create_app()
    with app.app_context():
        # En lugar de cargar todos los registros en memoria, actualizaremos por lotes
        # para evitar problemas de consistencia en la base de datos
        
        # Contar el total de registros para el informe final
        total_registros = Arancel.query.count()
        
        updates = 0
        
        # Procesar cada prefijo NCM por separado
        for prefix, data in TAXONOMY.items():
            # Actualizar directamente en la base de datos sin cargar los objetos
            result = db.session.execute(
                db.update(Arancel)
                .where(Arancel.NCM.like(f'{prefix}%'))
                .values(CHAPTER=data['chapter'], SECTION=data['section'])
            )
            
            # Contar cuántos registros se actualizaron
            updates += result.rowcount
            
            # Commit después de cada lote para evitar grandes transacciones
            db.session.commit()
        
        print(f"Se actualizaron {updates} registros de {total_registros} en total.")
        
        # Verificar capítulos y secciones distintas después de la actualización
        capitulos_count = db.session.query(Arancel.CHAPTER).distinct().filter(Arancel.CHAPTER != "").count()
        secciones_count = db.session.query(Arancel.SECTION).distinct().filter(Arancel.SECTION != "").count()
        
        print(f"Ahora hay {capitulos_count} capítulos distintos y {secciones_count} secciones distintas.")

if __name__ == "__main__":
    update_chapter_section()
