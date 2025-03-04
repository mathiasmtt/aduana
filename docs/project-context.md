# Contexto del Proyecto

## Estructura Base del Proyecto
La estructura del proyecto sigue un patrón modular y organizado:

```
proyecto/
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── data/
│   └── (datos del proyecto)
├── docs/
│   └── (documentación)
└── requirements.txt
```

## Convenciones y Estándares

### Organización del Código
- Todo el código fuente debe residir en el directorio `src/`
- Cada módulo debe ser independiente y reutilizable
- Implementar patrones de diseño que faciliten el mantenimiento
- Seguir el principio de responsabilidad única por módulo

### Estilo de Código
- Seguir PEP 8 para el estilo de código Python
- Documentar todas las funciones y clases con docstrings
- Utilizar type hints para mejorar la legibilidad y el soporte IDE
- Mantener un máximo de 80 caracteres por línea

### Gestión de Dependencias
- Todas las dependencias deben estar listadas en `requirements.txt`
- Utilizar el entorno virtual específico del proyecto
- Minimizar el uso de dependencias externas cuando sea posible

### Testing
- Implementar tests unitarios para cada módulo en `tests/`
- Mantener una cobertura de código mínima del 80%
- Los tests deben ser independientes y autocontenidos

### Documentación
- Mantener el README.md actualizado con la información esencial
- Documentar cambios significativos en el directorio `docs/`
- Incluir ejemplos de uso para funcionalidades principales

### Control de Versiones
- Utilizar commits semánticos
- Crear ramas feature/ para nuevas funcionalidades
- Crear ramas hotfix/ para correcciones urgentes
- Mantener main/master siempre en estado deployable

## Flujo de Desarrollo

1. Creación de Proyecto
   - Utilizar project-setup.py para inicializar la estructura
   - Configurar el entorno virtual
   - Actualizar README.md con información específica del proyecto

2. Desarrollo de Funcionalidades
   - Crear rama feature/ desde main
   - Implementar tests primero (TDD cuando sea posible)
   - Desarrollar funcionalidad
   - Documentar cambios

3. Revisión y Merge
   - Ejecutar suite completa de tests
   - Realizar code review
   - Actualizar documentación si es necesario
   - Merge a main