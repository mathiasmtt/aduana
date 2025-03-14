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
    
    // Efecto de revelación al cargar la página
    const navItems = document.querySelectorAll('.nav-link');
    navItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(10px)';
        setTimeout(() => {
            item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 100 + (index * 100));
    });
    
    // Efecto al hacer hover en los iconos
    const navbarIcons = document.querySelectorAll('.navbar-icon');
    navbarIcons.forEach(icon => {
        icon.addEventListener('mouseover', function() {
            this.style.color = '#93c5fd'; // Un tono azul claro
        });
        icon.addEventListener('mouseout', function() {
            this.style.color = '';
        });
    });
    
    // Resaltar menú activo
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.nav-link');
    menuItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href)) {
            item.classList.add('active-nav-item');
        }
    });
    
    // Control para menú móvil
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            if (mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.remove('hidden');
                mobileMenu.style.maxHeight = '0';
                setTimeout(() => {
                    mobileMenu.style.transition = 'max-height 0.3s ease';
                    mobileMenu.style.maxHeight = '500px';
                }, 10);
            } else {
                mobileMenu.style.maxHeight = '0';
                setTimeout(() => {
                    mobileMenu.classList.add('hidden');
                }, 300);
            }
        });
    }
    
    // Script para el temporizador de usuario free
    const timerButton = document.getElementById('timer-button');
    
    if (timerButton) {
        const tiempoRestante = document.getElementById("tiempo-restante");
        const tiempoDetallado = document.getElementById("tiempo-detallado");
        const barraProgreso = document.getElementById("barra-progreso");
        
        if (tiempoRestante && tiempoDetallado && barraProgreso) {
            let minutos = parseInt(timerButton.getAttribute('data-remaining-time') || '0');
            const tiempoTotal = 60; // La sesión es de 60 minutos (1 hora)
            
            // Configurar el ancho inicial de la barra de progreso
            barraProgreso.style.width = (minutos / tiempoTotal * 100) + "%";
            
            // Aplicar efectos visuales iniciales según el tiempo restante
            if (minutos <= 5) {
                tiempoRestante.classList.add("text-red-500");
                tiempoDetallado.classList.remove("text-yellow-400");
                tiempoDetallado.classList.add("text-red-500");
                barraProgreso.classList.remove("bg-yellow-400");
                barraProgreso.classList.add("bg-red-500");
            }
            
            function actualizarTiempo() {
                minutos = minutos - 1;
                
                // Actualizar texto y barra de progreso
                if (minutos > 0) {
                    tiempoRestante.textContent = minutos + "m";
                    tiempoDetallado.textContent = minutos + " minutos";
                    barraProgreso.style.width = (minutos / tiempoTotal * 100) + "%";
                    
                    // Cambiar a rojo cuando quedan 5 minutos o menos
                    if (minutos <= 5 && !tiempoRestante.classList.contains("text-red-500")) {
                        tiempoRestante.classList.add("text-red-500");
                        tiempoDetallado.classList.remove("text-yellow-400");
                        tiempoDetallado.classList.add("text-red-500");
                        barraProgreso.classList.remove("bg-yellow-400");
                        barraProgreso.classList.add("bg-red-500");
                        
                        // Hacer que el botón del temporizador parpadee cuando queda poco tiempo
                        timerButton.classList.add("animate-pulse");
                    }
                } else {
                    // Tiempo expirado, redireccionar a logout
                    window.location.href = "/auth/logout";
                }
            }
            
            // Actualizar cada minuto
            setInterval(actualizarTiempo, 60000);
        }
    }
}); 