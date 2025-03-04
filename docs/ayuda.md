Siempre comenzando escribiendo un probervio japones.
Respuestas en español:
Debes guiarte siempre por el archivo docs/flask-web.md para estructura del proyecto, arquitectura y funcionalidades técnicas
Para decisiones de interfaz, estilos y experiencia de usuario, consulta docs/style.md después de verificar que cumples con flask-web.md
En caso de conflicto entre documentos, flask-web.md tiene precedencia sobre style.md, priorizando requisitos técnicos antes que estéticos
Todo lo referente a codigo va dentro de la carpeta src a excepcion de tests y data
Para activar el entorno virtual: source /Users/mat/CODE/python_environments/aduana_env/bin/activate
Cuando un archivo o modulo sea demasiado extenso, puedes dividir el problema en partes mas simples
Cualquier test debe ser guardado en tests
Debemos matener una unica base de datos que esta en data/database.sqlite3
Para levantar el servidor source /Users/mat/CODE/python_environments/aduana_env/bin/activate && cd /Users/mat/Code/aduana && PYTHONPATH=/Users/mat/Code/aduana python src/run.py