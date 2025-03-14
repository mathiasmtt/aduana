// Script para la página de arancel
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar cualquier funcionalidad específica de la página de arancel
    console.log("Página de arancel cargada");
    
    // Función para mejorar la visualización de las tablas en dispositivos móviles
    const tables = document.querySelectorAll('.overflow-x-auto table');
    if (tables.length > 0) {
        tables.forEach(table => {
            table.classList.add('responsive-table');
        });
    }
    
    // Función para añadir tooltips a elementos con información adicional
    const infoElements = document.querySelectorAll('[data-info]');
    if (infoElements.length > 0) {
        infoElements.forEach(element => {
            element.setAttribute('title', element.getAttribute('data-info'));
        });
    }
    
    // Expandir/colapsar notas largas si hay alguna
    setupExpandableNotes();
})

// Función para manejar notas expandibles
function setupExpandableNotes() {
    const MAX_HEIGHT = 100; // Altura máxima en píxeles antes de colapsar
    const noteContainers = document.querySelectorAll('.bg-gray-50.dark\\:bg-gray-700 p-4');
    
    noteContainers.forEach(container => {
        if (container.scrollHeight > MAX_HEIGHT) {
            // La nota es larga, añadimos funcionalidad para expandir/colapsar
            container.style.maxHeight = MAX_HEIGHT + 'px';
            container.style.overflow = 'hidden';
            container.style.position = 'relative';
            container.style.transition = 'max-height 0.3s ease';
            
            const expandButton = document.createElement('button');
            expandButton.textContent = 'Ver más';
            expandButton.className = 'text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 text-sm mt-2 focus:outline-none';
            expandButton.style.position = 'absolute';
            expandButton.style.bottom = '0';
            expandButton.style.right = '0';
            expandButton.style.background = 'linear-gradient(to left, rgba(249, 250, 251, 1) 30%, rgba(249, 250, 251, 0))';
            expandButton.style.padding = '3px 8px';
            expandButton.style.borderRadius = '3px';
            
            // Ajustar el fondo para modo oscuro
            if (document.documentElement.classList.contains('dark')) {
                expandButton.style.background = 'linear-gradient(to left, rgba(55, 65, 81, 1) 30%, rgba(55, 65, 81, 0))';
            }
            
            expandButton.addEventListener('click', function() {
                if (container.style.maxHeight === MAX_HEIGHT + 'px') {
                    container.style.maxHeight = container.scrollHeight + 'px';
                    this.textContent = 'Ver menos';
                } else {
                    container.style.maxHeight = MAX_HEIGHT + 'px';
                    this.textContent = 'Ver más';
                }
            });
            
            container.appendChild(expandButton);
        }
    });
} 