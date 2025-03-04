# Sistema de Diseño - Flask Web

Un sistema de diseño coherente y moderno para aplicaciones web construidas con Flask y TailwindCSS. Este documento sirve como guía definitiva para mantener consistencia visual y de experiencia de usuario en todo el proyecto.

## 🎯 Principios de Diseño

Estos principios fundamentales guían todas nuestras decisiones de diseño e implementación:

### Consistencia

Mantenemos patrones uniformes en toda la interfaz para crear una experiencia predecible y confiable. Los elementos con funciones similares deben verse y comportarse de manera similar.

### Jerarquía Visual

Utilizamos tamaño, color, espaciado y tipografía para establecer claramente la importancia relativa de los elementos y guiar al usuario a través de la interfaz.

### Simplicidad y Claridad

Priorizamos la funcionalidad sobre la decoración. Cada elemento debe tener un propósito claro y contribuir a los objetivos del usuario.

### Accesibilidad

Diseñamos para todos los usuarios, independientemente de sus capacidades. Seguimos las pautas WCAG 2.1 nivel AA como mínimo.

### Feedback Inmediato

Proporcionamos retroalimentación clara e inmediata para todas las acciones del usuario, reduciendo la incertidumbre y aumentando la confianza.

## 🎨 Paleta de Colores

Nuestra paleta combina profesionalismo con personalidad, manteniendo un alto contraste para accesibilidad.

### Colores Primarios

Los colores primarios representan nuestra identidad principal y se utilizan para elementos destacados y acciones principales.

| Nombre | Hex | Tailwind | Uso |
|--------|-----|----------|-----|
| Primary Blue | `#3B82F6` | `blue-500` | Botones de acción principal, enlaces, elementos destacados |
| Primary Dark | `#1E40AF` | `blue-800` | Estados hover/active, cabeceras, acentos |

### Colores Secundarios

Complementan a los primarios y se utilizan para acciones secundarias y categorización.

| Nombre | Hex | Tailwind | Uso |
|--------|-----|----------|-----|
| Secondary Green | `#10B981` | `emerald-500` | Éxito, confirmación, indicadores positivos |
| Secondary Purple | `#8B5CF6` | `violet-500` | Acentos, categorías alternativas |

### Colores Neutros

Base para textos, fondos y elementos estructurales.

| Nombre | Hex | Tailwind | Uso |
|--------|-----|----------|-----|
| Dark Gray | `#1F2937` | `gray-800` | Texto principal, encabezados (modo claro) |
| Medium Gray | `#6B7280` | `gray-500` | Texto secundario, bordes |
| Light Gray | `#F3F4F6` | `gray-100` | Fondos alternativos, separadores |
| White | `#FFFFFF` | `white` | Fondo principal (modo claro) |
| Black | `#000000` | `black` | Sombras, superposiciones |

### Colores de Estado

Comunican estados y tipos de mensajes al usuario.

| Nombre | Hex | Tailwind | Uso |
|--------|-----|----------|-----|
| Success | `#10B981` | `emerald-500` | Confirmaciones, éxito |
| Warning | `#F59E0B` | `amber-500` | Advertencias, precaución |
| Error | `#EF4444` | `red-500` | Errores, alertas críticas |
| Info | `#3B82F6` | `blue-500` | Información, notificaciones |

### Tema Oscuro

Para el tema oscuro, invertimos el esquema manteniendo el contraste y legibilidad.

| Nombre | Hex | Tailwind | Uso |
|--------|-----|----------|-----|
| Dark Background | `#111827` | `gray-900` | Fondo principal (modo oscuro) |
| Dark Surface | `#1F2937` | `gray-800` | Tarjetas, contenedores (modo oscuro) |
| Dark Text | `#F9FAFB` | `gray-50` | Texto principal (modo oscuro) |
| Dark Text Secondary | `#D1D5DB` | `gray-300` | Texto secundario (modo oscuro) |

### Variables CSS

```css
:root {
  /* Colores primarios */
  --color-primary: 59, 130, 246; /* rgb values for #3B82F6 */
  --color-primary-dark: 30, 64, 175;
  
  /* Colores secundarios */
  --color-secondary: 16, 185, 129;
  --color-secondary-alt: 139, 92, 246;
  
  /* Colores neutros */
  --color-text: 31, 41, 55;
  --color-text-light: 107, 114, 128;
  --color-background: 255, 255, 255;
  --color-background-alt: 243, 244, 246;
  
  /* Colores de estado */
  --color-success: 16, 185, 129;
  --color-warning: 245, 158, 11;
  --color-error: 239, 68, 68;
  --color-info: 59, 130, 246;
}

.dark {
  --color-text: 249, 250, 251;
  --color-text-light: 209, 213, 219;
  --color-background: 17, 24, 39;
  --color-background-alt: 31, 41, 55;
}
```

## 🔤 Tipografía

Un sistema tipográfico claro y jerárquico que prioriza la legibilidad en todas las situaciones.

### Fuentes

| Familia | Uso | Fallbacks |
|---------|-----|-----------|
| Inter | UI general, párrafos, encabezados | system-ui, sans-serif |
| Fira Code | Código, datos técnicos | monospace |

#### Configuración en Tailwind

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
}
```

### Escala Tipográfica

Sistema coherente y proporcional de tamaños de fuente.

| Nombre | Tamaño | Tailwind | Uso |
|--------|--------|----------|-----|
| Display | 48px (3rem) | `text-5xl` | Títulos principales, heroes |
| H1 | 36px (2.25rem) | `text-4xl` | Encabezados de página |
| H2 | 30px (1.875rem) | `text-3xl` | Encabezados de sección |
| H3 | 24px (1.5rem) | `text-2xl` | Subencabezados |
| H4 | 20px (1.25rem) | `text-xl` | Títulos de tarjetas, modales |
| H5 | 18px (1.125rem) | `text-lg` | Subtítulos, encabezados de grupo |
| Body | 16px (1rem) | `text-base` | Texto de párrafo principal |
| Small | 14px (0.875rem) | `text-sm` | Texto secundario, anotaciones |
| XSmall | 12px (0.75rem) | `text-xs` | Texto legal, metadatos |

### Pesos y Estilos

| Peso | Valor | Tailwind | Uso |
|------|-------|----------|-----|
| Regular | 400 | `font-normal` | Texto de párrafo principal |
| Medium | 500 | `font-medium` | Énfasis leve, subtítulos |
| Semibold | 600 | `font-semibold` | Encabezados, elementos interactivos |
| Bold | 700 | `font-bold` | Énfasis fuerte, títulos principales |

### Interlineado

| Nombre | Valor | Tailwind | Uso |
|--------|-------|----------|-----|
| Tight | 1.25 | `leading-tight` | Encabezados, textos cortos |
| Normal | 1.5 | `leading-normal` | Texto de párrafo principal |
| Relaxed | 1.75 | `leading-relaxed` | Textos largos, bloques de contenido |

### Mejores Prácticas Tipográficas

- Limitar líneas de texto a **65-75 caracteres** para óptima legibilidad
- Usar alineación a la izquierda para la mayoría de los textos
- Mantener jerarquía visual clara con combinación de tamaños y pesos
- Asegurar contraste suficiente entre texto y fondo (ratio 4.5:1 mínimo)
- Evitar texto en todas mayúsculas excepto para etiquetas cortas

## 📏 Espaciado y Layout

Un sistema coherente de espaciado que crea ritmo visual y mejora la legibilidad.

### Sistema de Espaciado

Utilizamos un sistema de espaciado basado en múltiplos de 4px, siguiendo la escala de Tailwind.

| Nombre | Valor | Tailwind | Uso |
|--------|-------|----------|-----|
| Minúsculo | 4px (0.25rem) | `p-1`, `m-1` | Espaciado entre elementos relacionados (ícono y texto) |
| Pequeño | 8px (0.5rem) | `p-2`, `m-2` | Espaciado interior de elementos compactos |
| Medio | 16px (1rem) | `p-4`, `m-4` | Espaciado estándar entre elementos |
| Grande | 24px (1.5rem) | `p-6`, `m-6` | Espaciado entre secciones relacionadas |
| Extra Grande | 32px (2rem) | `p-8`, `m-8` | Espaciado entre secciones principales |
| Enorme | 48px (3rem) | `p-12`, `m-12` | Espaciado entre bloques de contenido mayores |

### Sistema de Grid

Utilizamos un sistema de grid flexible basado en 12 columnas para layouts complejos.

```html
<!-- Ejemplo de grid de 3 columnas con espacio entre ellas -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
  <div>Columna 1</div>
  <div>Columna 2</div>
  <div>Columna 3</div>
</div>
```

### Breakpoints Responsivos

Diseñamos primero para móviles (mobile-first) y adaptamos para pantallas más grandes.

| Nombre | Ancho mínimo | Tailwind | Dispositivos típicos |
|--------|--------------|----------|----------------------|
| sm | 640px | `sm:` | Móviles en horizontal |
| md | 768px | `md:` | Tablets |
| lg | 1024px | `lg:` | Laptops, tablets horizontales |
| xl | 1280px | `xl:` | Desktops |
| 2xl | 1536px | `2xl:` | Monitores grandes |

### Contenedores y Máximos Anchos

Limitamos el ancho del contenido para mantener la legibilidad en pantallas grandes.

| Uso | Máximo ancho | Tailwind | Descripción |
|-----|--------------|----------|-------------|
| Contenido principal | 1280px | `max-w-7xl` | Ancho máximo para el contenido principal |
| Artículos, textos | 768px | `max-w-prose` | Ideal para textos largos |
| Tarjetas | 384px | `max-w-sm` | Para componentes tipo tarjeta |

### Estrategias de Layout

- **Centrado con `mx-auto`**: Para contenedores principales
- **Layout con flexbox**: Para alineamientos y distribuciones sencillas
- **Layout con grid**: Para estructuras más complejas y bidimensionales
- **Posicionamiento con `sticky`**: Para elementos como navegación y sidebars

### Técnicas de Composición

#### Secciones de Página

```html
<!-- Sección principal con padding responsivo -->
<section class="py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl mx-auto">
    <h2 class="text-3xl font-semibold mb-6">Título de sección</h2>
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <!-- Contenido de la sección -->
    </div>
  </div>
</section>
```

#### División en Columnas

```html
<!-- Dos columnas con proporción 2:1 en desktop, apiladas en móvil -->
<div class="mt-8 lg:grid lg:grid-cols-3 lg:gap-8">
  <div class="lg:col-span-2">
    <!-- Contenido principal (2/3) -->
  </div>
  <div class="mt-6 lg:mt-0">
    <!-- Barra lateral (1/3) -->
  </div>
</div>

## 🧩 Componentes UI

Componentes reutilizables diseñados para proporcionar una experiencia consistente.

### Botones

Utilizamos un sistema coherente de botones con variantes para diferentes propósitos y contextos.

#### Variantes Principales

| Variante | Descripción | Clases Base |
|----------|-------------|-------------|
| Primario | Acciones principales | `bg-primary text-white hover:bg-blue-600` |
| Secundario | Acciones secundarias | `bg-white text-gray-700 border border-gray-300 hover:bg-gray-50` |
| Outline | Acciones alternativas | `border border-primary text-primary hover:bg-blue-50` |
| Texto | Acciones terciarias | `text-primary hover:underline` |
| Danger | Acciones destructivas | `bg-red-500 text-white hover:bg-red-600` |

#### Tamaños

| Tamaño | Clases |
|--------|--------|
| Small | `px-3 py-1.5 text-sm` |
| Default | `px-4 py-2` |
| Large | `px-6 py-3 text-lg` |

#### Estados

| Estado | Modificadores |
|--------|--------------|
| Normal | Estado base |
| Hover | `hover:bg-[color]` |
| Focus | `focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary` |
| Active | `active:bg-[darker-color]` |
| Disabled | `opacity-50 cursor-not-allowed` |

#### Ejemplo de implementación

```html
<!-- Botón primario predeterminado -->
<button class="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
  Acción Principal
</button>

<!-- Botón secundario small -->
<button class="inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 rounded-md shadow-sm text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
  Acción Secundaria
</button>

<!-- Botón con icono -->
<button class="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
  <i class="fa-solid fa-plus mr-2"></i>
  Añadir Nuevo
</button>
```

### Formularios

Elementos de entrada consistentes y accesibles.

#### Inputs de Texto

```html
<div class="mb-4">
  <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
    Correo electrónico
  </label>
  <input type="email" name="email" id="email" 
         class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
                placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary
                dark:bg-gray-700 dark:text-white"
         placeholder="correo@ejemplo.com">
  <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Nunca compartiremos tu correo.</p>
</div>
```

#### Select

```html
<div class="mb-4">
  <label for="country" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
    País
  </label>
  <select id="country" name="country" 
          class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
                 focus:outline-none focus:ring-primary focus:border-primary
                 dark:bg-gray-700 dark:text-white">
    <option value="">Selecciona un país</option>
    <option value="es">España</option>
    <option value="mx">México</option>
    <option value="ar">Argentina</option>
  </select>
</div>
```

#### Checkbox y Radio

```html
<!-- Checkbox -->
<div class="mb-4">
  <div class="flex items-start">
    <div class="flex items-center h-5">
      <input id="terms" name="terms" type="checkbox" 
             class="h-4 w-4 text-primary focus:ring-primary border-gray-300 dark:border-gray-600 rounded
                    dark:bg-gray-700">
    </div>
    <div class="ml-3 text-sm">
      <label for="terms" class="font-medium text-gray-700 dark:text-gray-300">
        Acepto los términos y condiciones
      </label>
    </div>
  </div>
</div>

<!-- Radio Buttons -->
<div class="mb-4">
  <span class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
    Plan de suscripción
  </span>
  <div class="space-y-2">
    <div class="flex items-center">
      <input id="plan-free" name="plan" type="radio" value="free" 
             class="h-4 w-4 text-primary focus:ring-primary border-gray-300 dark:border-gray-600
                    dark:bg-gray-700">
      <label for="plan-free" class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
        Plan gratuito
      </label>
    </div>
    <div class="flex items-center">
      <input id="plan-premium" name="plan" type="radio" value="premium" 
             class="h-4 w-4 text-primary focus:ring-primary border-gray-300 dark:border-gray-600
                    dark:bg-gray-700">
      <label for="plan-premium" class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
        Plan premium
      </label>
    </div>
  </div>
</div>
```

### Tarjetas

Contenedores consistentes para agrupar información relacionada.

#### Tarjeta Básica

```html
<div class="bg-white dark:bg-gray-800 shadow overflow-hidden rounded-lg">
  <div class="px-4 py-5 sm:p-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white">
      Título de la tarjeta
    </h3>
    <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
      Contenido descriptivo de la tarjeta que proporciona contexto adicional.
    </p>
    <div class="mt-4">
      <button class="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-blue-600">
        Acción
      </button>
    </div>
  </div>
</div>
```

#### Tarjeta con Cabecera y Pie

```html
<div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
  <!-- Cabecera -->
  <div class="px-4 py-5 border-b border-gray-200 dark:border-gray-700 sm:px-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white">
      Información de perfil
    </h3>
    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
      Detalles personales y preferencias
    </p>
  </div>
  <!-- Cuerpo -->
  <div class="px-4 py-5 sm:p-6">
    <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
      <div>
        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
          Nombre completo
        </dt>
        <dd class="mt-1 text-sm text-gray-900 dark:text-white">
          Ana García Martínez
        </dd>
      </div>
      <div>
        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
          Correo electrónico
        </dt>
        <dd class="mt-1 text-sm text-gray-900 dark:text-white">
          ana.garcia@ejemplo.com
        </dd>
      </div>
    </dl>
  </div>
  <!-- Pie -->
  <div class="px-4 py-4 border-t border-gray-200 dark:border-gray-700 sm:px-6 text-right">
    <button class="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-blue-600">
      Editar
    </button>
  </div>
</div>

```

### Navegación

Componentes para guiar al usuario a través de la aplicación.

#### Barra de Navegación

```html
<nav class="bg-white dark:bg-gray-800 shadow">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16">
      <div class="flex">
        <!-- Logo -->
        <div class="flex-shrink-0 flex items-center">
          <a href="/" class="text-xl font-bold text-primary">MiApp</a>
        </div>
        
        <!-- Enlaces de navegación principal -->
        <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
          <a href="/" class="border-primary text-gray-900 dark:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
            Inicio
          </a>
          <a href="/about" class="border-transparent text-gray-500 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-700 hover:text-gray-700 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
            Acerca de
          </a>
          <a href="/contact" class="border-transparent text-gray-500 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-700 hover:text-gray-700 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
            Contacto
          </a>
        </div>
      </div>
      
      <!-- Botones de acción -->
      <div class="hidden sm:ml-6 sm:flex sm:items-center">
        <button class="p-1 rounded-full text-gray-500 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
          <span class="sr-only">Ver notificaciones</span>
          <i class="fa-solid fa-bell"></i>
        </button>
        
        <!-- Perfil dropdown -->
        <div class="ml-3 relative">
          <div>
            <button class="bg-white dark:bg-gray-800 rounded-full flex text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
              <span class="sr-only">Abrir menú de usuario</span>
              <img class="h-8 w-8 rounded-full" src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" alt="">
            </button>
          </div>
        </div>
      </div>
      
      <!-- Botón de menú móvil -->
      <div class="-mr-2 flex items-center sm:hidden">
        <button type="button" class="bg-white dark:bg-gray-800 inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary">
          <span class="sr-only">Abrir menú principal</span>
          <i class="fa-solid fa-bars"></i>
        </button>
      </div>
    </div>
  </div>
</nav>
```

#### Migas de Pan (Breadcrumbs)

```html
<nav class="flex" aria-label="Breadcrumb">
  <ol class="inline-flex items-center space-x-1 md:space-x-3">
    <li class="inline-flex items-center">
      <a href="/" class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-primary dark:text-gray-400 dark:hover:text-white">
        <i class="fa-solid fa-home mr-2"></i>
        Inicio
      </a>
    </li>
    <li>
      <div class="flex items-center">
        <i class="fa-solid fa-chevron-right text-gray-400 mx-2"></i>
        <a href="/productos" class="text-sm font-medium text-gray-700 hover:text-primary dark:text-gray-400 dark:hover:text-white">
          Productos
        </a>
      </div>
    </li>
    <li aria-current="page">
      <div class="flex items-center">
        <i class="fa-solid fa-chevron-right text-gray-400 mx-2"></i>
        <span class="text-sm font-medium text-gray-500 dark:text-gray-300">
          Detalle del Producto
        </span>
      </div>
    </li>
  </ol>
</nav>
```

## 📝 Guía de Implementación

Lineamientos técnicos para implementar correctamente el sistema de diseño.

### Estructura de Archivos CSS

Organizamos nuestros estilos en una estructura modular y escalable:

```
/static
  /css
    /base
      _reset.css       # Normalización y reset
      _typography.css  # Reglas tipográficas
      _variables.css   # Variables CSS
    /components
      _buttons.css     # Estilos de botones
      _forms.css       # Estilos de formularios
      _cards.css       # Estilos de tarjetas
      _navigation.css  # Estilos de navegación
    /layouts
      _grid.css        # Sistema de grid
      _header.css      # Estilos de cabecera
      _footer.css      # Estilos de pie de página
    /utilities
      _spacing.css     # Utilidades de espaciado
      _colors.css      # Utilidades de color
      _flexbox.css     # Utilidades de flexbox
    style.css          # Archivo principal que importa todos los módulos
```

### Integración con TailwindCSS

Para aprovechar al máximo Tailwind, seguimos estas prácticas:

#### Configuración de Tailwind

Extendemos la configuración de Tailwind para incluir nuestras variables de diseño:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        'primary-dark': '#1E40AF',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      borderRadius: {
        'sm': '0.25rem',
        DEFAULT: '0.375rem',
        'md': '0.5rem',
        'lg': '0.75rem',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      }
    },
  },
  variants: {
    extend: {
      opacity: ['disabled'],
      cursor: ['disabled'],
      backgroundColor: ['active', 'dark'],
      textColor: ['dark'],
      borderColor: ['dark'],
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
  darkMode: 'class',
}
```

#### Componentes Personalizados con @apply

Para componentes reutilizables, utilizamos la directiva `@apply` de Tailwind:

```css
/* En _buttons.css */
.btn {
  @apply inline-flex items-center justify-center px-4 py-2 border rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors;
}

.btn-primary {
  @apply bg-primary border-transparent text-white hover:bg-blue-600 focus:ring-primary;
}

.btn-secondary {
  @apply bg-white border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-primary;
}

.btn-danger {
  @apply bg-red-500 border-transparent text-white hover:bg-red-600 focus:ring-red-500;
}
```

#### Uso en HTML

```html
<!-- Uso con clases directas de Tailwind -->
<button class="inline-flex items-center px-4 py-2 bg-primary text-white rounded-md">
  Botón Primario
</button>

<!-- Uso con clases personalizadas -->
<button class="btn btn-primary">
  Botón Primario
</button>
```

### JavaScript para Interacciones

Patrones comunes para interactividad con JavaScript:

#### Toggle de Tema Claro/Oscuro

```js
// En static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
  const themeToggleBtn = document.getElementById('theme-toggle');
  
  // Comprobar preferencia en localStorage
  const currentTheme = localStorage.getItem('theme') || 'light';
  if (currentTheme === 'dark') {
    document.documentElement.classList.add('dark');
  }
  
  // Gestionar cambio de tema
  themeToggleBtn.addEventListener('click', function() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  });
});
```

## 🛠️ Buenas Prácticas

### Rendimiento

- **Lazy Loading**: Cargar imágenes y recursos pesados solo cuando sean necesarios
- **Purge CSS**: Eliminar CSS no utilizado en producción con PurgeCSS (incluido en Tailwind)
- **Minificación**: Comprimir CSS, JS y HTML para producción

### Mantenibilidad

- **BEM para Nombres de Clase**: Usar Block__Element--Modifier para clases personalizadas
- **Comentarios**: Documentar secciones complejas y decisiones de diseño
- **Variables CSS**: Centralizar valores comunes en variables CSS

### Responsive Design

- **Mobile-First**: Diseñar primero para móviles y luego adaptar para pantallas más grandes
- **Breakpoints Estándar**: Usar los breakpoints consistentes de Tailwind
- **Pruebas en Múltiples Dispositivos**: Verificar la experiencia en diferentes tamaños de pantalla

### Accesibilidad

- **Contraste de Color**: Mantener ratio mínimo de 4.5:1 para texto normal
- **Navegación por Teclado**: Asegurar que todos los elementos interactivos sean accesibles por teclado
- **ARIA Roles**: Usar atributos ARIA donde sea necesario
- **Texto Alternativo**: Proporcionar alt text para todas las imágenes informativas

## 📊 Ejemplos Prácticos

### Página de Inicio

```html
{% extends 'base.html' %}

{% block content %}
<div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
  <!-- Hero Section -->
  <div class="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
    <div class="text-center">
      <h1 class="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl">
        Bienvenido a <span class="text-blue-200">MiApp</span>
      </h1>
      <p class="mt-3 max-w-md mx-auto text-lg text-blue-100 sm:text-xl md:mt-5 md:max-w-3xl">
        Una aplicación moderna construida con Flask y TailwindCSS.
      </p>
      <div class="mt-10 flex justify-center">
        <div class="inline-flex rounded-md shadow">
          <a href="/register" class="inline-flex items-center justify-center px-5 py-3 border border-transparent rounded-md text-base font-medium text-blue-600 bg-white hover:bg-blue-50">
            Comenzar
          </a>
        </div>
        <div class="ml-3 inline-flex">
          <a href="/about" class="inline-flex items-center justify-center px-5 py-3 border border-transparent rounded-md text-base font-medium text-white bg-blue-800 hover:bg-blue-900">
            Saber más
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Features Section -->
<div class="py-12 bg-white dark:bg-gray-900">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center">
      <h2 class="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">
        Características principales
      </h2>
      <p class="mt-4 max-w-2xl text-xl text-gray-500 dark:text-gray-300 mx-auto">
        Todo lo que necesitas para construir aplicaciones web modernas.
      </p>
    </div>

    <div class="mt-10">
      <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
        <!-- Feature 1 -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-blue-500 rounded-md p-3">
                <i class="fa-solid fa-bolt text-white text-xl"></i>
              </div>
              <div class="ml-5">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">Rápido y eficiente</h3>
                <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  Optimizado para rendimiento con Flask y TailwindCSS.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Feature 2 -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
                <i class="fa-solid fa-shield-alt text-white text-xl"></i>
              </div>
              <div class="ml-5">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">Seguro</h3>
                <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  Implementación de mejores prácticas de seguridad.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Feature 3 -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0 bg-purple-500 rounded-md p-3">
                <i class="fa-solid fa-paint-brush text-white text-xl"></i>
              </div>
              <div class="ml-5">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">Moderno y atractivo</h3>
                <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  Interfaz de usuario elegante y responsiva.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

Este documento sirve como referencia completa para nuestro sistema de diseño. Utilízalo como guía para mantener la consistencia y calidad en toda la aplicación web.
