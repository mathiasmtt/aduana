import sqlite3; from pathlib import Path; BASE_DIR = Path("/Users/mat/Code/aduana"); DB_PATH = BASE_DIR / "data" / "db_versions" / "arancel_latest.sqlite3"; print(f"Usando base de datos: {DB_PATH}")
