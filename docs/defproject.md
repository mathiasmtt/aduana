# Definición del Proyecto Web

## Preguntas para Definir el Proyecto

### Objetivo y Funcionalidades Principales:
- ¿Cuál es el propósito principal de la página web (por ejemplo, un blog, una tienda online, un portafolio, una aplicación interactiva)? Una aplicacion interactiva web
- ¿Qué funcionalidades esenciales debe tener (autenticación, panel de administración, formularios de contacto, integración con APIs, etc.)? Debo ser capaz de realizar calculos, busquedas  y mostrarlos en una tabla o grilla inicialmente. 
- ¿Cuál sería la versión mínima viable (MVP) de tu proyecto? Debo ser capaz de realizar calculos, busquedas  y mostrarlos en una tabla o grilla inicialmente.

### Tecnologías y Herramientas:
- ¿Qué tecnologías te gustaría utilizar en el backend (por ejemplo, Flask, Django, FastAPI)? Flask
- ¿Y en el frontend? ¿Prefieres usar plantillas con Jinja, algun framework de CSS como Bootstrap o Tailwind, o incluso integrar algun framework de JavaScript (React, Vue, etc.) Usar plantillas con Jinja y Tailwind
- ¿Cuáles son las tecnologías mínimas necesarias para tu MVP? Por ejemplo, para una aplicación de gestión de tareas simple: Flask + SQLite + Jinja templates + CSS básico.

### Base de Datos y Modelo de Datos:
- ¿Qué sistema de gestión de base de datos planeas usar (SQLite, MySQL, PostgreSQL)? Sqlite3
- ¿Tienes ya definido un modelo de datos básico o necesitas ayuda en su diseño? necesito ayuda
- ¿Cuáles son las entidades y relaciones esenciales para tu MVP? Necesito ayuda para definir el modelo de datos.

### Estructura del Proyecto:
- ¿Te gustaría organizar el proyecto en módulos o blueprints (por ejemplo, separar la autenticación, la administración y las vistas públicas)? si me gustaria que fuese como lo describes
- Siempre estructura modular 
- ¿Qué estructura mínima necesitarías para comenzar rápidamente? blueprints desde el principio autotentificacion de usuarios y administracion

### Diseño y Experiencia de Usuario:
- ¿Tienes pautas de diseño o alguna idea visual (colores, tipografías, estilo general)? si leer archivo style.md me gustaria que fuese como lo describe
- ¿El sitio web debe ser responsive y adaptarse a dispositivos móviles? siempre
- ¿Cuál sería la interfaz mínima necesaria para validar tu concepto? Interfaz básica de login y administracion y busqueda de datos

### Integraciones y Funcionalidades Extra:
- ¿Necesitas integrar servicios externos, como pagos, envío de correos, APIs de terceros? no
- ¿Requieres características adicionales como manejo de sesiones, seguridad (protección contra ataques, cifrado, etc.)? no
- ¿Qué integraciones son esenciales versus las que podrían implementarse después? La integracion esencial es realizar calculos, mostrar graficos, hacer busquedas y mostrar en una tabla o grilla inicialmente.

### Escalabilidad y Mantenimiento:
- ¿Qué tan escalable debe ser la aplicación? ¿Esperas crecer en funcionalidades o usuarios en el futuro? siempre
- ¿Tienes alguna preferencia en cuanto a pruebas unitarias, integración continua o despliegue? leer archivo flask-web.md
- ¿Cómo planeas evolucionar desde el MVP a versiones más completas? Necesito ayuda
### Metodología de Desarrollo:
- ¿Estás utilizando alguna metodología ágil como Scrum o Kanban para gestionar el desarrollo? leer archivos flask-web.md y style.md
- ¿Cómo planeas priorizar las funcionalidades y determinar qué entra en cada iteración? flask-web.md
- ¿Cómo definirás el "hecho" para una funcionalidad del MVP? Por ejemplo, para una funcionalidad de registro de usuarios: ¿es suficiente con que se puedan registrar, o debe incluir también confirmación por correo, recuperación de contraseña y perfil editable? en principio no 