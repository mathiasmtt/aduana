# Sistema de Aranceles

Sistema para consultar y gestionar información sobre aranceles nacionales de importación y exportación.

## Características

- Consulta de aranceles por código NCM (con y sin puntos)
- Visualización de secciones y capítulos del sistema arancelario
- Historial de versiones de aranceles
- Notas explicativas para secciones y capítulos
- API para acceso a datos de aranceles

## Requisitos

- Python 3.7+
- Flask
- SQLite3

## Instalación

1. Clonar el repositorio:
```
git clone https://github.com/tuusuario/aduana.git
cd aduana
```

2. Crear un entorno virtual e instalar dependencias:
```
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Iniciar la aplicación:
```
python src/run.py
```

## Estructura de directorios

- `src/` - Código fuente de la aplicación
  - `app/` - Aplicación Flask
    - `models/` - Modelos de datos
    - `routes/` - Rutas y endpoints
    - `templates/` - Plantillas HTML
    - `static/` - Archivos estáticos (CSS, JS)
- `data/` - Archivos de base de datos
  - `db_versions/` - Diferentes versiones de bases de datos de aranceles
- `docs/` - Documentación adicional

## Uso de la API

La API proporciona acceso a datos de aranceles a través de los siguientes endpoints:

- `GET /api/aranceles` - Listar aranceles con filtros opcionales
- `GET /api/aranceles/<ncm>` - Obtener información de un arancel específico
- `GET /api/secciones` - Listar todas las secciones disponibles
- `GET /api/capitulos` - Listar todos los capítulos disponibles

## Contribución

1. Crear un fork del repositorio
2. Crear una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Hacer commit de tus cambios (`git commit -am 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear un Pull Request

## Licencia

Este proyecto está licenciado bajo [insertar licencia aquí].

## Módulo Aduana

Este módulo permite gestionar una base de datos para almacenar y consultar resoluciones de clasificación arancelaria.

### Estructura de la base de datos

La base de datos `aduana.db` se almacena en el directorio `/data/aduana/` y contiene la siguiente tabla:

#### Tabla: resoluciones_clasificacion_arancelaria

| Columna      | Tipo      | Descripción                                |
|--------------|-----------|-------------------------------------------|
| id           | INTEGER   | Clave primaria autoincremental            |
| year         | INTEGER   | Año de la resolución                       |
| numero       | INTEGER   | Número de la resolución                    |
| fecha        | DATE      | Fecha de la resolución                      |
| referencia   | TEXT      | Texto de referencia sobre la resolución    |
| dictamen     | TEXT      | Texto del dictamen                         |
| resolucion   | TEXT      | Texto de la resolución final               |
| created_at   | TIMESTAMP | Fecha y hora de creación del registro      |
| updated_at   | TIMESTAMP | Fecha y hora de actualización del registro |

### Scripts disponibles

- `src/crear_db_aduana.py`: Crea la base de datos y la tabla de resoluciones.
- `src/agregar_ejemplos_aduana.py`: Agrega ejemplos de resoluciones a la base de datos.
- `src/consultar_resoluciones.py`: Permite consultar las resoluciones almacenadas.
- `src/descargar_resoluciones.py`: Descarga resoluciones de clasificación arancelaria desde el sitio web oficial de la Dirección Nacional de Aduanas de Uruguay.

### Ejemplos de uso

Para crear la base de datos:
```
python src/crear_db_aduana.py
```

Para agregar ejemplos a la base de datos:
```
python src/agregar_ejemplos_aduana.py
```

Para consultar todas las resoluciones:
```
python src/consultar_resoluciones.py
```

Para filtrar por año:
```
python src/consultar_resoluciones.py --year 2023
```

Para filtrar por año y número:
```
python src/consultar_resoluciones.py --year 2024 --numero 1
```

Para limitar el número de resultados:
```
python src/consultar_resoluciones.py --limit 3
```

Para descargar resoluciones de un año específico:
```
python src/descargar_resoluciones.py 2025
```

Este script descargará automáticamente:
- La información básica de cada resolución (número, fecha, referencia)
- Los PDFs del dictamen y resolución
- Guardará los PDFs en `data/aduana/{año}/`
- Registrará la información en la base de datos 