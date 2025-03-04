# Instrucciones para la Actualización del Arancel Nacional

Este documento describe el proceso para cargar un nuevo archivo Excel del Arancel Nacional en el sistema versionado de bases de datos.

## Procedimiento de actualización

### 1. Ubicación del archivo Excel
Coloca el archivo Excel con el nuevo Arancel Nacional en el directorio `/Users/mat/Code/aduana/data/excel/`. 
Recomendación: utiliza un nombre que incluya la fecha (ej: `Arancel_Nacional_YYYYMM.xlsx`).

### 2. Cargar los datos a una nueva base de datos versionada
Ejecuta el script `load_version_db.py` para crear una nueva base de datos con los datos del Excel:

```bash
source /Users/mat/CODE/python_environments/aduana_env/bin/activate
cd /Users/mat/Code/aduana
PYTHONPATH=/Users/mat/Code/aduana python src/load_version_db.py --file /Users/mat/Code/aduana/data/excel/Arancel_Nacional_YYYYMM.xlsx --version YYYYMMDD
```

Parámetros:
- `--file`: Ruta completa al archivo Excel
- `--version`: Fecha efectiva del arancel en formato YYYYMMDD (ej: "20250401" para 1 de abril de 2025)

### 3. Actualizar los metadatos de la versión
Después de cargar los datos, actualiza los metadatos de la versión usando el script `update_version_metadata.py`:

```bash
PYTHONPATH=/Users/mat/Code/aduana python src/update_version_metadata.py --version YYYYMMDD --descripcion "Actualización Arancel Nacional Mes YYYY"
```

Parámetros:
- `--version`: La misma fecha utilizada en el paso anterior
- `--descripcion`: Descripción breve de esta versión

### 4. Sincronizar las notas de sección y capítulo
Para asegurar que las notas estén actualizadas correctamente:

```bash
# Sincronizar notas de sección
PYTHONPATH=/Users/mat/Code/aduana python src/sync_section_notes.py --version YYYYMMDD --file /Users/mat/Code/aduana/data/excel/Arancel_Nacional_YYYYMM.xlsx

# Sincronizar notas de capítulo
PYTHONPATH=/Users/mat/Code/aduana python src/sync_chapter_notes.py --version YYYYMMDD --file /Users/mat/Code/aduana/data/excel/Arancel_Nacional_YYYYMM.xlsx
```

### 5. Verificar la carga
1. Levanta el servidor: 
   ```bash
   source /Users/mat/CODE/python_environments/aduana_env/bin/activate && cd /Users/mat/Code/aduana && PYTHONPATH=/Users/mat/Code/aduana python src/run.py
   ```
2. Accede a la aplicación en el navegador: http://127.0.0.1:5051/
3. Comprueba que:
   - La nueva versión aparezca en el selector de versiones
   - Puedas cambiar entre la versión actual y la nueva
   - Las estadísticas (total de aranceles, capítulos y secciones) sean correctas para la nueva versión

## Solución de problemas comunes

### Error al cargar Excel
- Verifica que el formato del Excel sea compatible con el sistema
- Asegúrate que las columnas esperadas existan y tengan los nombres correctos

### Error en sincronización de notas
- Revisa que la estructura del Excel no haya cambiado significativamente
- Verifica que las secciones y capítulos sean accesibles en el archivo

### Problemas con la selección de versiones
- Verifica que el enlace simbólico `arancel_latest.sqlite3` apunte a la versión más reciente
- Comprueba los permisos de los archivos de base de datos

## Referencia

### Tablas importantes en la base de datos
- `arancel_nacional`: Contiene todos los códigos NCM y sus descripciones
- `chapter_notes`: Almacena las notas de capítulo
- `section_notes`: Almacena las notas de sección
- `version_metadata`: Contiene información sobre las versiones disponibles

### Ubicación de archivos clave
- Bases de datos versionadas: `/Users/mat/Code/aduana/data/db_versions/`
- Archivos Excel: `/Users/mat/Code/aduana/data/excel/`
- Scripts de actualización: `/Users/mat/Code/aduana/src/`
