# Sistema de Consulta y Gestión de Aranceles

Sistema para consultar y gestionar información sobre aranceles nacionales de importación y exportación, con soporte para múltiples versiones históricas de los aranceles. Esta aplicación permite a usuarios consultar códigos NCM (Nomenclatura Común del MERCOSUR), visualizar información detallada de aranceles, y acceder a notas explicativas de secciones y capítulos.

## Características principales

- **Consulta de aranceles**: Búsqueda por código NCM (con y sin puntos), descripción o texto parcial
- **Navegación jerárquica**: Exploración por secciones, capítulos y partidas
- **Sistema de versiones**: Acceso a diferentes versiones históricas de aranceles
- **Notas explicativas**: Visualización de notas de secciones y capítulos para facilitar la clasificación
- **Gestión de resoluciones**: Almacenamiento y consulta de resoluciones de clasificación arancelaria
- **API completa**: Acceso programático a todos los datos del sistema
- **Sistema de usuarios**: Control de acceso y personalización de la experiencia

## Requisitos

- Python 3.7+
- Flask
- SQLAlchemy
- SQLite3
- Navegador web moderno

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/usuario/aduana.git
cd aduana
```

2. Crear un entorno virtual e instalar dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Iniciar la aplicación:
```bash
python src/run.py
```

La aplicación estará disponible en `http://localhost:5051`

## Estructura del proyecto

```
aduana/
├── data/                  # Datos y bases de datos
│   ├── aduana/            # Base de datos de resoluciones
│   ├── db_versions/       # Versiones históricas de bases de datos
│   ├── excel/             # Archivos Excel originales
│   └── users/             # Base de datos de usuarios
├── docs/                  # Documentación adicional
├── src/                   # Código fuente
│   ├── app/               # Aplicación principal Flask
│   │   ├── models/        # Modelos de datos (SQLAlchemy)
│   │   ├── routes/        # Rutas y controladores
│   │   ├── static/        # Archivos estáticos (CSS, JS)
│   │   ├── templates/     # Plantillas HTML (Jinja2)
│   │   ├── __init__.py    # Inicialización de la aplicación
│   │   ├── config.py      # Configuración de la aplicación
│   │   └── db_utils.py    # Utilidades para manejo de bases de datos
│   ├── auxiliares/        # Scripts auxiliares
│   │   ├── db_management/ # Gestión de bases de datos
│   │   ├── debug/         # Herramientas de depuración
│   │   ├── tools/         # Herramientas diversas
│   │   └── updates/       # Actualizaciones de datos
│   ├── aduana/            # Módulo específico para resoluciones
│   └── run.py             # Script principal de ejecución
└── tests/                 # Pruebas y verificaciones
    ├── comparison/        # Comparación entre versiones
    ├── fixes/             # Correcciones de datos
    ├── tools/             # Herramientas para pruebas
    ├── updates/           # Scripts de actualización
    └── verification/      # Verificación de integridad
```

## Módulos principales

### Sistema de aranceles

El sistema de aranceles permite consultar información detallada sobre códigos NCM, incluyendo:

- Descripción del producto
- Alícuotas de importación y exportación
- Aranceles externos comunes (AEC)
- Tratamientos especiales por acuerdos comerciales
- Notas interpretativas de secciones y capítulos

### Sistema de versiones

El sistema soporta múltiples versiones de aranceles, permitiendo:

- Consultar información histórica de aranceles
- Comparar cambios entre diferentes versiones
- Acceder a notas específicas de cada versión
- Filtrar búsquedas por fecha o versión específica

### Módulo de resoluciones

El módulo de resoluciones gestiona dictámenes oficiales de clasificación arancelaria:

- Almacenamiento de resoluciones completas con dictámenes técnicos
- Búsqueda por año, número, referencia o texto
- Descarga automática de resoluciones desde fuentes oficiales
- Archivado de documentos PDF relacionados

## API REST

La API proporciona acceso completo a los datos del sistema, incluyendo:

### Endpoints principales

- `GET /api/arancel/<ncm>` - Información de un código NCM específico
- `GET /api/arancel/buscar?q=<texto>` - Búsqueda por texto en descripción
- `GET /api/secciones` - Lista de todas las secciones
- `GET /api/capitulos/<seccion>` - Capítulos de una sección específica
- `GET /api/versiones` - Versiones disponibles de aranceles
- `GET /api/notas/seccion/<num>` - Notas de una sección específica
- `GET /api/notas/capitulo/<num>` - Notas de un capítulo específico
- `GET /api/resoluciones` - Búsqueda de resoluciones con filtros

## Gestión de bases de datos

El sistema utiliza múltiples bases de datos para distintos propósitos:

1. **Base de datos de usuarios**: Almacena usuarios, roles y preferencias
2. **Base de datos de aranceles**: Contiene información de aranceles en versiones específicas
3. **Base de datos de resoluciones**: Gestiona resoluciones de clasificación

Las bases de datos se gestionan mediante SQLAlchemy y SQLite, con soporte para:

- Versionado automático de bases de datos
- Migración de datos entre versiones
- Verificación de integridad
- Backup y restauración

## Desarrollo y contribuciones

Para contribuir al proyecto:

1. Crear un fork del repositorio
2. Crear una rama para su característica (`git checkout -b feature/nueva-caracteristica`)
3. Hacer commit de los cambios (`git commit -am 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear un Pull Request

### Guía de estilo

- Seguir PEP 8 para código Python
- Documentar funciones y clases con docstrings
- Usar nombres descriptivos en español
- Agregar pruebas para nuevas funcionalidades

## Licencia

Este proyecto está licenciado bajo la licencia MIT.

## Soporte y contacto

Para reportar problemas o solicitar ayuda:

- Crear un issue en el repositorio
- Contactar a los desarrolladores principales 