// Tema Dark/Light
// Verificar si hay una preferencia guardada
if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
} else {
    document.documentElement.classList.remove('dark');
}

// Función para cambiar el tema
function toggleDarkMode() {
    if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.theme = 'light';
        document.querySelector('.fa-moon').classList.remove('hidden');
        document.querySelector('.fa-sun').classList.add('hidden');
    } else {
        document.documentElement.classList.add('dark');
        localStorage.theme = 'dark';
        document.querySelector('.fa-moon').classList.add('hidden');
        document.querySelector('.fa-sun').classList.remove('hidden');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Establecer el icono correcto al cargar la página
    if (document.documentElement.classList.contains('dark')) {
        document.querySelector('.fa-moon').classList.add('hidden');
        document.querySelector('.fa-sun').classList.remove('hidden');
    } else {
        document.querySelector('.fa-moon').classList.remove('hidden');
        document.querySelector('.fa-sun').classList.add('hidden');
    }
    
    // Aplicar animación a elementos con la clase auth-animate
    const authElements = document.querySelectorAll('.auth-animate');
    authElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.animationDelay = (index * 0.1) + 's';
    });
    
    // Mejorar la interactividad de los formularios
    enhanceFormInteractivity();
});

// Funciones para mejorar la interactividad de los formularios
function enhanceFormInteractivity() {
    // Añadir clases a los inputs para estilos específicos
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"], input[type="email"]');
    inputs.forEach(input => {
        input.classList.add('auth-input');
        
        // Efecto de focus
        input.addEventListener('focus', function() {
            this.parentNode.classList.add('ring-2', 'ring-blue-300', 'dark:ring-blue-700');
        });
        
        input.addEventListener('blur', function() {
            this.parentNode.classList.remove('ring-2', 'ring-blue-300', 'dark:ring-blue-700');
        });
    });
    
    // Añadir clases a los botones para estilos específicos
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.classList.add('auth-button');
    });
    
    // Verificación en tiempo real de validez de campos
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.checkValidity()) {
                this.classList.remove('border-red-500');
                this.classList.add('border-green-500');
            } else {
                this.classList.remove('border-green-500');
                if (this.value !== '') {
                    this.classList.add('border-red-500');
                } else {
                    this.classList.remove('border-red-500');
                }
            }
        });
    });
} 