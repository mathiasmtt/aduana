/**
 * Funcionalidad JavaScript para la página de configuración del sistema
 */
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos DOM
    const versionSelector = document.getElementById('version-selector');
    const aplicarBtn = document.getElementById('aplicar-version');
    const searchLimit = document.getElementById('search-limit');
    const searchLimitValue = document.getElementById('search-limit-value');
    const confirmModal = document.getElementById('confirmModal');
    const confirmTitle = document.getElementById('confirmTitle');
    const confirmMessage = document.getElementById('confirmMessage');
    const confirmModalBtn = document.getElementById('confirmModalBtn');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    
    // Función para aplicar versión desde el selector principal
    if (aplicarBtn && versionSelector) {
        aplicarBtn.addEventListener('click', function() {
            const selectedVersion = versionSelector.value;
            cambiarVersion(selectedVersion);
        });
    }
    
    // Función para aplicar versión desde los radio toggles
    const versionToggles = document.querySelectorAll('input[name="version-toggle"]');
    versionToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            if (this.checked) {
                const version = this.value;
                cambiarVersion(version);
            }
        });
    });
    
    // Función común para cambiar de versión
    function cambiarVersion(version) {
        // Obtener la URL de redirección desde el data attribute o usar un valor predeterminado
        const redirectUrl = aplicarBtn.dataset.redirectUrl || '/configuracion';
        window.location.href = `/set_version?version=${version}&redirect=configuracion`;
    }
    
    // Actualizar el valor del límite de búsqueda
    if (searchLimit && searchLimitValue) {
        searchLimitValue.textContent = searchLimit.value;
        searchLimit.addEventListener('input', function() {
            searchLimitValue.textContent = this.value;
        });
        
        // Guardar el valor del límite cuando cambia
        searchLimit.addEventListener('change', function() {
            guardarConfiguracion('search_limit', this.value);
        });
    }
    
    // Función para mostrar el modal de confirmación
    function showConfirmModal(title, message, callback) {
        if (!confirmModal) return;
        
        confirmTitle.textContent = title;
        confirmMessage.textContent = message;
        confirmModal.classList.remove('hidden');
        
        // Botón de confirmación
        const confirmarAction = function() {
            callback();
            confirmModal.classList.add('hidden');
            confirmModalBtn.removeEventListener('click', confirmarAction);
        };
        
        confirmModalBtn.addEventListener('click', confirmarAction);
        
        // Botón de cancelar
        const cancelarAction = function() {
            confirmModal.classList.add('hidden');
            cancelModalBtn.removeEventListener('click', cancelarAction);
        };
        
        cancelModalBtn.addEventListener('click', cancelarAction);
    }
    
    // Botones de mantenimiento del sistema
    
    // Verificar integridad de la base de datos
    const btnVerificarDb = document.getElementById('btn-verificar-db');
    if (btnVerificarDb) {
        btnVerificarDb.addEventListener('click', function() {
            showConfirmModal(
                'Verificar integridad de la base de datos',
                '¿Desea realizar una verificación de integridad de la base de datos? Esta operación puede tardar varios minutos.',
                function() {
                    // Aquí iría la lógica para verificar la integridad (ajax o fetch)
                    alert('Verificación iniciada. Se le notificará cuando finalice.');
                }
            );
        });
    }
    
    // Backup de la base de datos
    const btnBackupDb = document.getElementById('btn-backup-db');
    if (btnBackupDb) {
        btnBackupDb.addEventListener('click', function() {
            showConfirmModal(
                'Backup de la base de datos',
                '¿Desea crear un backup de la base de datos actual?',
                function() {
                    // Aquí iría la lógica para crear un backup (ajax o fetch)
                    alert('Backup iniciado. Se le notificará cuando finalice.');
                }
            );
        });
    }
    
    // Actualizar índices
    const btnActualizarIndices = document.getElementById('btn-actualizar-indices');
    if (btnActualizarIndices) {
        btnActualizarIndices.addEventListener('click', function() {
            showConfirmModal(
                'Actualizar índices',
                '¿Desea actualizar los índices de la base de datos? Esto puede mejorar el rendimiento de las búsquedas.',
                function() {
                    // Aquí iría la lógica para actualizar índices (ajax o fetch)
                    alert('Actualización de índices iniciada. Se le notificará cuando finalice.');
                }
            );
        });
    }
    
    // Limpiar caché
    const btnLimpiarCache = document.getElementById('btn-limpiar-cache');
    if (btnLimpiarCache) {
        btnLimpiarCache.addEventListener('click', function() {
            showConfirmModal(
                'Limpiar caché',
                '¿Desea limpiar la caché del sistema? Esto puede ayudar a resolver problemas de rendimiento.',
                function() {
                    // Aquí iría la lógica para limpiar la caché (ajax o fetch)
                    alert('Limpieza de caché iniciada. Se le notificará cuando finalice.');
                }
            );
        });
    }
    
    // Guardar configuración de visualización y búsqueda
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            guardarConfiguracion(this.id, this.checked);
        });
    });
    
    // Función para guardar configuración mediante AJAX
    function guardarConfiguracion(clave, valor) {
        console.log(`Guardando configuración: ${clave} = ${valor}`);
        
        // Aquí se implementaría una llamada AJAX para guardar la configuración
        // Por ahora solo mostramos un mensaje en consola
        
        /* Ejemplo de implementación con fetch:
        fetch('/api/guardar_configuracion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                clave: clave,
                valor: valor
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Configuración guardada:', data);
        })
        .catch(error => {
            console.error('Error al guardar configuración:', error);
        });
        */
    }
}); 