# Asistente de Git para el Sistema de Aranceles

Este script de Python está diseñado para simplificar el trabajo con Git en tu proyecto del Sistema de Aranceles.

## ¿Qué problemas resuelve?

- Automatiza tareas repetitivas de Git
- Simplifica el trabajo con ramas (branches)
- Facilita la recuperación en caso de errores
- No necesitas recordar comandos complejos de Git

## Requisitos

- Python 3.6 o superior
- Git instalado y configurado en tu sistema
- Librería termcolor (`pip install termcolor`)

## Instalación

1. Descarga el archivo `git_helper.py` en la carpeta raíz de tu proyecto.
2. Asegúrate de que el script tenga permisos de ejecución:

```bash
chmod +x git_helper.py
```

## Uso

Para iniciar el asistente, simplemente ejecuta:

```bash
python git_helper.py
```

O, si le has dado permisos de ejecución:

```bash
./git_helper.py
```

## Funcionalidades

### 1. Ver y seleccionar ramas

Te muestra todas las ramas disponibles en tu repositorio y te permite cambiar a cualquiera de ellas con solo seleccionar el número correspondiente.

### 2. Crear una nueva rama

Te permite crear una nueva rama a partir de la rama actual. Útil cuando quieres desarrollar una nueva característica sin afectar el código principal.

### 3. Actualizar rama desde el remoto

Actualiza la rama actual con los cambios que existan en el repositorio remoto (GitHub).

### 4. Ver estado del repositorio

Muestra los archivos modificados, añadidos o eliminados que aún no han sido confirmados.

### 5. Añadir cambios y hacer commit

Añade todos los cambios al área de staging y realiza un commit. Puedes especificar un mensaje personalizado o usar uno generado automáticamente.

### 6. Subir cambios al remoto

Sube los cambios confirmados a la rama actual en GitHub.

### 7. Ver historial de commits

Muestra el historial de los últimos commits, incluyendo mensaje, autor y tiempo transcurrido.

### 8. Restaurar a un commit anterior

Te permite volver a una versión anterior del código en caso de que algo salga mal. **¡Úsalo con precaución!**

### 9. Fusionar ramas

Permite combinar los cambios de una rama en otra. Útil cuando has completado el desarrollo en una rama y quieres integrar los cambios en la rama principal.

## Ejemplos de uso

### Flujo de trabajo básico

1. Selecciona la opción 1 para ver las ramas y cambiar a "desarrollo"
2. Selecciona la opción 3 para actualizar la rama con los últimos cambios
3. Realiza tus modificaciones al código
4. Selecciona la opción 5 para añadir y confirmar tus cambios
5. Selecciona la opción 6 para subir tus cambios a GitHub

### Crear una nueva característica

1. Selecciona la opción 2 para crear una nueva rama (ej: "nueva-feature")
2. Realiza tus modificaciones al código
3. Usa las opciones 5 y 6 para confirmar y subir los cambios
4. Cuando la característica esté completa, usa la opción 9 para fusionar en "main" o "desarrollo"

### Recuperación de errores

1. Selecciona la opción 7 para ver el historial de commits
2. Identifica el commit al que quieres volver
3. Selecciona la opción 8 e ingresa el hash del commit
4. Confirma la acción

## Solución de problemas

Si encuentras algún error al ejecutar el script, asegúrate de:

1. Estar en un repositorio Git válido
2. Tener Git correctamente instalado y configurado
3. Tener conexión a Internet para operaciones con el remoto
4. Tener instalada la librería termcolor (`pip install termcolor`)

## Extensión del script

Este script puede ser extendido con más funcionalidades según tus necesidades. Algunas ideas:
- Gestión de etiquetas (tags)
- Gestión de stash
- Visualización gráfica del árbol de commits

¡Feliz codificación! 