import pandas as pd
import re

def main():
    """Verificar los capítulos presentes en el Excel original."""
    # Leer el archivo Excel
    df = pd.read_excel('data/Arancel Nacional_Abril 2024.xlsx', header=None)
    
    capitulos = []
    capnum_set = set()  # Para evitar duplicados por errores de formato
    
    for i, row in df.iterrows():
        # Buscar filas que contengan "Capítulo X"
        if isinstance(row[0], str) and 'Capítulo' in row[0]:
            cap_match = re.search(r'Capítulo (\d+)', row[0])
            if cap_match:
                cap_num = cap_match.group(1)
                
                # Buscar la descripción del capítulo (suele estar en la fila siguiente)
                if i+1 < len(df) and isinstance(df.iloc[i+1, 0], str):
                    desc = df.iloc[i+1, 0]
                    
                    # Filtrar descripciones que no parecen ser realmente descripciones de capítulos
                    # como notas, referencias a otros capítulos, etc.
                    if not any(x in desc.lower() for x in ['nota', 'partida', ')', 'capítulo']):
                        if cap_num not in capnum_set:  # Evitar duplicados
                            capitulos.append((cap_num, desc))
                            capnum_set.add(cap_num)
    
    # Ordenar capítulos por número
    capitulos.sort(key=lambda x: int(x[0]))
    
    # Mostrar los capítulos encontrados
    print(f'Total de capítulos encontrados en el Excel: {len(capitulos)}\n')
    print("Lista de capítulos del Arancel Nacional:")
    for cap_num, desc in capitulos:
        # Formatear la salida para que sea más legible
        formatted_desc = desc.replace('\n', ' ').strip()
        if len(formatted_desc) > 100:
            formatted_desc = formatted_desc[:97] + '...'
        print(f'Capítulo {cap_num.zfill(2)}: {formatted_desc}')
    
    # Verificar qué capítulos no están en nuestro mapeo actual
    from update_taxonomy import TAXONOMY
    
    # Extraer los números de capítulo del mapeo actual (quitando los ceros iniciales)
    mapped_chapters = {prefix[:1] if prefix.startswith('0') else prefix for prefix in TAXONOMY.keys()}
    
    # Encontrar capítulos que están en el Excel pero no en nuestro mapeo
    missing_chapters = []
    for cap_num, desc in capitulos:
        if cap_num not in mapped_chapters:
            missing_chapters.append((cap_num, desc))
    
    if missing_chapters:
        print(f'\nHay {len(missing_chapters)} capítulos en el Excel que no están en nuestro mapeo:')
        for cap_num, desc in missing_chapters:
            formatted_desc = desc.replace('\n', ' ').strip()
            if len(formatted_desc) > 100:
                formatted_desc = formatted_desc[:97] + '...'
            print(f'Capítulo {cap_num.zfill(2)}: {formatted_desc}')
    else:
        print('\nTodos los capítulos del Excel están en nuestro mapeo.')

if __name__ == "__main__":
    main()
