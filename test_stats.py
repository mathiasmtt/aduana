import sqlite3
from pathlib import Path
import re

# Conectar a la versión más reciente
BASE_DIR = Path('.')
db_path = BASE_DIR / 'data' / 'db_versions' / 'arancel_latest.sqlite3'

print(f'Usando base de datos: {db_path.resolve()}')

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Contar registros
cursor.execute('SELECT COUNT(*) as count FROM arancel_nacional')
row = cursor.fetchone()
print(f'Total registros: {row["count"]}')

# Contar secciones únicas
cursor.execute('SELECT COUNT(DISTINCT SECTION) as count FROM arancel_nacional WHERE SECTION IS NOT NULL AND SECTION != ""')
row = cursor.fetchone()
print(f'Total secciones únicas: {row["count"]}')

# Obtener y contar capítulos únicos
cursor.execute('SELECT DISTINCT CHAPTER FROM arancel_nacional WHERE CHAPTER IS NOT NULL AND CHAPTER != ""')
chapters = cursor.fetchall()

chapter_numbers = set()
for chapter in chapters:
    chapter_str = chapter['CHAPTER']
    if chapter_str:
        match = re.match(r'^(\d+)', chapter_str)
        if match:
            chapter_numbers.add(match.group(1))

print(f'Total capítulos únicos: {len(chapter_numbers)}')
print(f'Primeros 5 capítulos: {sorted(chapter_numbers)[:5]}')

conn.close() 