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