/**
 * Funcionalidad JavaScript para la página principal del Sistema de Aranceles
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado, iniciando carga de estadísticas...');
    
    // Obtener referencias a los elementos que mostrarán las estadísticas
    const totalAranceles = document.getElementById('total-aranceles');
    const totalCapitulos = document.getElementById('total-capitulos');
    const totalSecciones = document.getElementById('total-secciones');
    
    // Función para mostrar indicadores de carga
    function mostrarCargando() {
        if (totalAranceles) totalAranceles.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        if (totalCapitulos) totalCapitulos.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        if (totalSecciones) totalSecciones.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    // Función para mostrar error en los contenedores
    function mostrarError() {
        if (totalAranceles) totalAranceles.innerHTML = '<span class="text-red-500">Error</span>';
        if (totalCapitulos) totalCapitulos.innerHTML = '<span class="text-red-500">Error</span>';
        if (totalSecciones) totalSecciones.innerHTML = '<span class="text-red-500">Error</span>';
    }
    
    // Cargar estadísticas desde la API
    function cargarEstadisticas() {
        // Mostrar indicadores de carga
        mostrarCargando();
        
        // Crear la solicitud AJAX
        fetch('/api/estadisticas')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Datos de estadísticas:', data);
                
                // Actualizar los valores en la página
                if (totalAranceles) totalAranceles.textContent = data.total_registros;
                if (totalCapitulos) totalCapitulos.textContent = data.total_capitulos;
                if (totalSecciones) totalSecciones.textContent = data.total_secciones;
                
                // Aplicar animación
                animarNumeros();
                
                console.log('Estadísticas actualizadas correctamente');
            })
            .catch(error => {
                console.error('Error al obtener estadísticas:', error);
                mostrarError();
            });
    }
    
    // Función para animar los números al aparecer
    function animarNumeros() {
        const elementos = document.querySelectorAll('.estadisticas-valor');
        elementos.forEach(elem => {
            elem.classList.add('animate__animated', 'animate__fadeIn');
        });
    }
    
    // Llamar a la función para cargar estadísticas
    cargarEstadisticas();
    
    // Configurar el evento para el selector de versiones
    const versionSelector = document.getElementById('version-selector');
    if (versionSelector) {
        console.log('Configurando evento para el selector de versiones');
        versionSelector.addEventListener('change', function() {
            // Mostrar indicadores de carga
            mostrarCargando();
            
            // Retrasar la redirección para que se vean los indicadores de carga
            setTimeout(function() {
                const versionValue = versionSelector.value;
                const url = versionValue ? 
                    `/set_version?version=${versionValue}` : 
                    '/reset_version';
                    
                console.log('Redirigiendo a:', url);
                window.location.href = url;
            }, 500);
        });
    } else {
        console.log('Selector de versiones no encontrado');
    }
    
    // Añadir eventos de hover a las tarjetas de características
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        const icon = card.querySelector('.feature-icon');
        
        // Animar icono al hacer hover
        card.addEventListener('mouseenter', function() {
            if (icon) {
                icon.style.transform = 'scale(1.2)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            if (icon) {
                icon.style.transform = 'scale(1)';
            }
        });
    });
}); 