/**
 * Funcionalidad JavaScript para la página de secciones
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar DataTables con configuraciones específicas para la tabla de secciones
    if ($.fn.DataTable) {
        const tablaSecciones = $('#tabla-secciones');
        
        if (tablaSecciones.length > 0) {
            tablaSecciones.DataTable({
                // Configuración de idioma - español
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
                },
                // Habilitar respuesta adaptable
                responsive: true,
                // Cantidad de registros por página
                pageLength: 25,
                // Ordenamiento predeterminado: columna 0 (número de sección) ascendente
                order: [[0, 'asc']],
                // Personalización de clases para integrar con Tailwind
                dom: "<'flex flex-col md:flex-row justify-between items-start md:items-center mb-4'<'flex items-center'l><'mt-2 md:mt-0'f>>" +
                     "<'overflow-x-auto'tr>" +
                     "<'flex flex-col md:flex-row justify-between items-center mt-4'<'mb-2 md:mb-0'i><'flex'p>>",
                // Personalizar clases para tener un mejor aspecto
                initComplete: function() {
                    // Añadir clases a elementos de DataTables para integrar con Tailwind
                    $('.dataTables_length select').addClass('rounded border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white');
                    $('.dataTables_filter input').addClass('rounded border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white');
                    
                    // Aplicar tema oscuro si está activo
                    if (document.documentElement.classList.contains('dark')) {
                        aplicarTemaOscuro();
                    }
                }
            });
        }
    }
    
    // Mostrar tooltips para las acciones
    inicializarTooltips();
    
    // Observador para el cambio de tema (claro/oscuro)
    observarCambioDeTema();
});

/**
 * Aplicar estilos específicos para tema oscuro en DataTables
 */
function aplicarTemaOscuro() {
    // Seleccionar elementos de DataTables y aplicar clases para modo oscuro
    $('.dataTables_wrapper .dataTables_length, .dataTables_wrapper .dataTables_filter, .dataTables_wrapper .dataTables_info, .dataTables_wrapper .dataTables_paginate')
        .addClass('text-gray-300');
    
    $('.dataTables_wrapper .dataTables_length select, .dataTables_wrapper .dataTables_filter input')
        .addClass('bg-gray-700 border-gray-600 text-white');
    
    $('.dataTables_wrapper .dataTables_paginate .paginate_button')
        .addClass('bg-gray-700 border-gray-600 text-gray-300');
    
    $('.dataTables_wrapper .dataTables_paginate .paginate_button.current')
        .addClass('bg-blue-600 !text-white border-blue-600');
}

/**
 * Inicializar tooltips para botones de acción
 */
function inicializarTooltips() {
    // Verificar si Tippy.js está disponible (se puede usar otra biblioteca también)
    if (typeof tippy !== 'undefined') {
        // Inicializar tooltips para enlaces con título
        tippy('[title]', {
            content: (reference) => reference.getAttribute('title'),
            onMount(instance) {
                instance.reference.removeAttribute('title');
            }
        });
    }
}

/**
 * Observar cambios en el tema (claro/oscuro) para actualizar la interfaz
 */
function observarCambioDeTema() {
    // Observar cambios en el atributo class del elemento html
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                const isDarkMode = document.documentElement.classList.contains('dark');
                
                // Reinicializar DataTables para aplicar el nuevo tema
                const tabla = $('#tabla-secciones').DataTable();
                if (tabla) {
                    // Destruir y reinicializar la tabla
                    tabla.destroy();
                    $('#tabla-secciones').DataTable({
                        language: {
                            url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
                        },
                        responsive: true,
                        pageLength: 25,
                        order: [[0, 'asc']],
                        initComplete: function() {
                            if (isDarkMode) {
                                aplicarTemaOscuro();
                            }
                        }
                    });
                }
            }
        });
    });
    
    // Iniciar observación
    observer.observe(document.documentElement, { attributes: true });
}

/**
 * Mostrar detalles o notas de una sección específica
 * @param {number} seccionId - ID de la sección a mostrar
 */
function mostrarDetalleSecccion(seccionId) {
    // Esta función podría implementarse para mostrar un modal con detalles
    console.log(`Mostrando detalles de la sección ${seccionId}`);
    
    // Ejemplo de implementación con modal
    // $('#modal-detalles-seccion').modal('show');
    // $('#modal-detalles-seccion .modal-title').text(`Sección ${seccionId}`);
}

/**
 * Exportar datos de la tabla a Excel, CSV o PDF
 * @param {string} formato - Formato de exportación ('excel', 'csv', 'pdf')
 */
function exportarTabla(formato) {
    const tabla = $('#tabla-secciones').DataTable();
    
    if (!tabla) return;
    
    switch (formato) {
        case 'excel':
            tabla.button('.buttons-excel').trigger();
            break;
        case 'csv':
            tabla.button('.buttons-csv').trigger();
            break;
        case 'pdf':
            tabla.button('.buttons-pdf').trigger();
            break;
    }
} 