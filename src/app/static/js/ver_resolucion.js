/**
 * Funcionalidad JavaScript para la página de visualización de resoluciones
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar la funcionalidad de administración si estamos en modo admin
    initAdminFunctions();
});

/**
 * Inicializar funcionalidades específicas para administradores
 */
function initAdminFunctions() {
    // Verificar si existen los elementos de administración
    const btnEditar = document.getElementById('btnEditar');
    const btnEliminar = document.getElementById('btnEliminar');
    const dataElement = document.getElementById('resolucion-data');
    
    // Solo proceder si todos los elementos necesarios están presentes
    if (btnEditar && btnEliminar && dataElement) {
        // Obtener los datos de la resolución desde el elemento JSON
        let resolucionData;
        try {
            resolucionData = JSON.parse(dataElement.textContent);
        } catch (error) {
            console.error('Error al parsear los datos de resolución:', error);
            return;
        }
        
        // Configurar el botón Editar
        btnEditar.addEventListener('click', function() {
            redirigirAEdicion(resolucionData);
        });
        
        // Configurar el botón Eliminar
        btnEliminar.addEventListener('click', function() {
            confirmarEliminacion(resolucionData);
        });
    }
}

/**
 * Redirige al usuario a la página de edición de resoluciones
 * @param {Object} data - Datos de la resolución
 */
function redirigirAEdicion(data) {
    window.location.href = data.urlResoluciones + "?edit=true&id=" + data.id;
}

/**
 * Muestra una confirmación y procede con la eliminación si se confirma
 * @param {Object} data - Datos de la resolución
 */
function confirmarEliminacion(data) {
    // Mostrar diálogo de confirmación
    const mensaje = `¿Está seguro que desea eliminar la Resolución ${data.year}/${data.numero}?`;
    
    if (confirm(mensaje)) {
        // Crear un formulario para enviar la solicitud de eliminación
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = data.urlEliminar;
        
        // Agregar token CSRF para seguridad
        const csrfToken = document.createElement('input');
        csrfToken.type = 'hidden';
        csrfToken.name = 'csrf_token';
        csrfToken.value = data.csrfToken;
        form.appendChild(csrfToken);
        
        // Agregar el ID de la resolución a eliminar
        const idInput = document.createElement('input');
        idInput.type = 'hidden';
        idInput.name = 'id';
        idInput.value = data.id;
        form.appendChild(idInput);
        
        // Añadir el formulario al DOM y enviarlo
        document.body.appendChild(form);
        form.submit();
    }
}

/**
 * Abre enlaces externos en una nueva pestaña
 * @param {string} url - URL a abrir
 */
function abrirEnlaceExterno(url) {
    if (!url) return;
    
    // Verificar si la URL incluye protocolo
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'http://' + url;
    }
    
    window.open(url, '_blank');
}

/**
 * Formatea el texto de la resolución para mejor visualización
 * @param {string} texto - Texto a formatear
 * @returns {string} Texto formateado con HTML
 */
function formatearTexto(texto) {
    if (!texto) return '';
    
    // Reemplazar saltos de línea por elementos <br>
    return texto
        .replace(/\n/g, '<br>')
        .replace(/\r/g, '')
        .trim();
}

/**
 * Copia el texto NCM al portapapeles
 * @param {string} ncm - Código NCM a copiar
 */
function copiarNCM(ncm) {
    if (!ncm) return;
    
    // Usar la API de portapapeles si está disponible
    if (navigator.clipboard) {
        navigator.clipboard.writeText(ncm)
            .then(() => {
                mostrarTooltip('NCM copiado al portapapeles');
            })
            .catch(err => {
                console.error('Error al copiar al portapapeles:', err);
            });
    } else {
        // Fallback para navegadores que no soportan clipboard API
        const textarea = document.createElement('textarea');
        textarea.value = ncm;
        textarea.style.position = 'fixed';
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            const exito = document.execCommand('copy');
            if (exito) {
                mostrarTooltip('NCM copiado al portapapeles');
            } else {
                console.error('Falló la copia al portapapeles');
            }
        } catch (err) {
            console.error('Error al copiar al portapapeles:', err);
        }
        
        document.body.removeChild(textarea);
    }
}

/**
 * Muestra un mensaje de tooltip temporal
 * @param {string} mensaje - Mensaje a mostrar
 */
function mostrarTooltip(mensaje) {
    // Crear elemento tooltip
    const tooltip = document.createElement('div');
    tooltip.textContent = mensaje;
    tooltip.style.position = 'fixed';
    tooltip.style.bottom = '20px';
    tooltip.style.left = '50%';
    tooltip.style.transform = 'translateX(-50%)';
    tooltip.style.padding = '8px 16px';
    tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    tooltip.style.color = 'white';
    tooltip.style.borderRadius = '4px';
    tooltip.style.zIndex = '9999';
    tooltip.style.transition = 'opacity 0.3s ease-in-out';
    
    // Añadir al DOM
    document.body.appendChild(tooltip);
    
    // Eliminar después de 2 segundos
    setTimeout(() => {
        tooltip.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(tooltip);
        }, 300);
    }, 2000);
} 