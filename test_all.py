import sqlite3; path = "/Users/mat/Code/aduana/data/db_versions/arancel_latest.sqlite3"; conn = sqlite3.connect(path); cursor = conn.cursor(); codigos = ["2004", "1905", "9503", "8517", "7308"]; for codigo in codigos: print(f"
Código {codigo}:"); cursor.execute(f"SELECT NCM FROM arancel_nacional WHERE NCM LIKE \"{codigo}%\" LIMIT 5"); print([row[0] for row in cursor.fetchall()]); conn.close()
