// Gestión de pestañas
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('[data-tabs-target]');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Ocultar todas las pestañas
            tabContents.forEach(content => {
                content.classList.add('hidden');
                content.classList.remove('active');
            });
            
            // Desactivar todos los botones
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.setAttribute('aria-selected', 'false');
            });
            
            // Activar la pestaña seleccionada
            const target = document.querySelector(button.dataset.tabsTarget);
            target.classList.remove('hidden');
            target.classList.add('active');
            
            // Activar el botón
            button.classList.add('active');
            button.setAttribute('aria-selected', 'true');
        });
    });
    
    // Inicializar tabla de permisos
    initPermisosTab();
    
    // Inicializar eventos de usuarios
    initUsuariosEvents();

    // Añadir efectos de animación a las cards y badges
    initAnimations();
    
    // Manejar los botones de acción de usuarios con data-attributes
    initActionButtons();

    // Reemplazar iconos con emojis y aplicar badges
    reemplazarIconosConEmojis();
    
    // Asegurar que los badges estén correctamente aplicados
    aplicarBadgesMejorados();
});

// Mapeo de roles a emojis
const rolEmojis = {
    'admin': '👑',
    'vip': '🌟',
    'free': '👤',
    'user': '👤',
    'transportista': '🚚',
    'corredor': '🛡️',
    'despachante': '📦',
    'importador': '🏢',
    'profesional': '👨‍💼'
};

// Mapeo de estados de roles
const rolEstados = {
    'admin': 'danger',
    'vip': 'warning',
    'free': 'basic',
    'user': 'basic',
    'transportista': 'warning',
    'corredor': 'purple',
    'despachante': 'success',
    'importador': 'info',
    'profesional': 'success'
};

// Función para reemplazar iconos Font Awesome con emojis y crear badges tipo flat pill con dot
function reemplazarIconosConEmojis() {
    // Reemplazar en las estadísticas
    const statsIcons = {
        'fa-users': '👥',
        'fa-crown': '👑',
        'fa-user': '👤'
    };

    document.querySelectorAll('.stat-icon i').forEach(icon => {
        const clases = Array.from(icon.classList);
        for (const clase of clases) {
            if (statsIcons[clase]) {
                const parent = icon.parentElement;
                const emojiSpan = document.createElement('span');
                emojiSpan.className = 'emoji-stat';
                emojiSpan.textContent = statsIcons[clase];
                parent.innerHTML = '';
                parent.appendChild(emojiSpan);
                break;
            }
        }
    });

    // Reemplazar en los encabezados de tabla
    const headerIcons = {
        'fa-user': '👤',
        'fa-envelope': '✉️',
        'fa-user-tag': '🏷️',
        'fa-file-import': '📋',
        'fa-calendar-plus': '📅',
        'fa-calendar-check': '📆',
        'fa-tools': '🛠️'
    };

    document.querySelectorAll('th i').forEach(icon => {
        const clases = Array.from(icon.classList);
        for (const clase of clases) {
            if (headerIcons[clase]) {
                const parent = icon.parentElement;
                const text = parent.textContent.trim();
                
                const emojiSpan = document.createElement('span');
                emojiSpan.className = 'emoji-header';
                emojiSpan.textContent = headerIcons[clase];
                
                parent.innerHTML = '';
                parent.appendChild(emojiSpan);
                parent.appendChild(document.createTextNode(' ' + text));
                break;
            }
        }
    });

    // Reemplazar en los botones de acción
    const actionIcons = {
        'fa-edit': '✏️',
        'fa-trash-alt': '🗑️',
        'fa-user-plus': '➕👤'
    };

    document.querySelectorAll('.action-btn i').forEach(icon => {
        const clases = Array.from(icon.classList);
        for (const clase of clases) {
            if (actionIcons[clase]) {
                const parent = icon.parentElement;
                const hasText = icon.nextSibling && 
                               icon.nextSibling.nodeType === Node.TEXT_NODE && 
                               icon.nextSibling.textContent.trim() !== '';
                
                const text = hasText ? parent.textContent.trim() : '';
                const emojiSpan = document.createElement('span');
                emojiSpan.className = 'emoji-btn';
                emojiSpan.textContent = actionIcons[clase];
                
                parent.innerHTML = '';
                parent.appendChild(emojiSpan);
                
                if (hasText) {
                    parent.appendChild(document.createTextNode(' ' + text));
                }
                break;
            }
        }
    });

    // Agregar badges para roles en la tabla con estilo flat pill with dot
    document.querySelectorAll('table tbody tr').forEach(row => {
        // Para la columna de rol
        const rolCell = row.querySelector('td:nth-child(3)');
        if (rolCell) {
            const rolText = rolCell.textContent.trim();
            if (rolText) {
                let rolKey = rolText.toLowerCase();
                const emoji = rolEmojis[rolKey] || '👤';
                
                const badge = document.createElement('span');
                
                // Aplicar estilo de badge según el rol
                if (rolKey === 'admin') {
                    badge.className = 'role-badge role-badge-admin';
                } else if (rolKey === 'vip') {
                    badge.className = 'role-badge role-badge-vip';
                } else if (rolKey === 'transportista' || rolKey.includes('trans')) {
                    badge.className = 'role-badge role-badge-transportista';
                } else if (rolKey === 'despachante' || rolKey.includes('despach')) {
                    badge.className = 'role-badge role-badge-despachante';
                } else {
                    badge.className = 'role-badge role-badge-' + rolKey;
                }
                
                // Añadir el dot
                const dot = document.createElement('span');
                dot.className = 'badge-dot';
                badge.appendChild(dot);
                
                // Añadir el emoji
                const emojiSpan = document.createElement('span');
                emojiSpan.className = 'emoji-badge';
                emojiSpan.textContent = emoji;
                badge.appendChild(emojiSpan);
                
                // Añadir el texto
                badge.appendChild(document.createTextNode(rolText));
                
                rolCell.innerHTML = '';
                rolCell.appendChild(badge);
            }
        }
        
        // Para la columna de rol de importación
        const importRolCell = row.querySelector('td:nth-child(4)');
        if (importRolCell) {
            const importRolText = importRolCell.textContent.trim();
            if (importRolText && importRolText !== 'No asignado' && importRolText !== '') {
                let rolKey = importRolText.toLowerCase().replace(/\s+/g, '');
                
                // Simplificar claves para roles de importación
                if (rolKey.includes('trans')) rolKey = 'transportista';
                if (rolKey.includes('corred')) rolKey = 'transportista';
                if (rolKey.includes('despach')) rolKey = 'despachante';
                if (rolKey.includes('import')) rolKey = 'transportista';
                
                const emoji = rolEmojis[rolKey] || '📦';
                
                const badge = document.createElement('span');
                
                // Aplicar estilo de badge según el rol
                if (rolKey === 'transportista' || rolKey.includes('trans')) {
                    badge.className = 'role-badge role-badge-transportista';
                } else if (rolKey === 'despachante' || rolKey.includes('despach')) {
                    badge.className = 'role-badge role-badge-despachante';
                } else {
                    badge.className = 'role-badge role-badge-' + rolKey;
                }
                
                // Añadir el dot
                const dot = document.createElement('span');
                dot.className = 'badge-dot';
                badge.appendChild(dot);
                
                // Añadir el emoji
                const emojiSpan = document.createElement('span');
                emojiSpan.className = 'emoji-badge';
                emojiSpan.textContent = emoji;
                badge.appendChild(emojiSpan);
                
                // Añadir el texto
                badge.appendChild(document.createTextNode(importRolText));
                
                importRolCell.innerHTML = '';
                importRolCell.appendChild(badge);
            }
        }
    });
}

// Manejador para los botones de acción que usan data-attributes
function initActionButtons() {
    // Delegación de eventos para los botones de acción
    document.addEventListener('click', function(e) {
        // Buscar si el click fue en un botón de acción o dentro de uno
        const actionButton = e.target.closest('[data-action]');
        
        if (actionButton) {
            const action = actionButton.dataset.action;
            const id = parseInt(actionButton.dataset.id);
            
            if (action === 'editar') {
                editarUsuario(id);
            } else if (action === 'eliminar') {
                const username = actionButton.dataset.username;
                confirmarEliminacion(id, username);
            }
        }
    });
}

// Gestión de usuarios
function initUsuariosEvents() {
    // Botón nuevo usuario
    document.getElementById('btn-nuevo-usuario').addEventListener('click', crearUsuario);
    
    // Cerrar modal
    document.getElementById('btn-cancelar').addEventListener('click', function() {
        document.getElementById('modal-usuario').classList.add('hidden');
    });
    
    // Envío del formulario de usuario - Ahora con botón guardar
    document.getElementById('btn-guardar-usuario').addEventListener('click', function() {
        const userData = {
            id: document.getElementById('usuario-id').value || null,
            username: document.getElementById('usuario-username').value,
            name: document.getElementById('usuario-name').value,
            email: document.getElementById('usuario-email').value,
            password: document.getElementById('usuario-password').value || '',
            role: document.getElementById('usuario-role').value,
            import_role: document.getElementById('usuario-import-role').value || null
        };
        
        // Obtener el token CSRF del formulario
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        
        // Enviar datos al servidor
        fetch('/admin/usuarios/guardar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(userData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                // Recargar la página para ver cambios
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error de conexión al servidor', 'error');
        });
    });
}

function editarUsuario(id) {
    // Mostrar el modal
    document.getElementById('modal-title').innerHTML = '<i class="fas fa-user-edit mr-2"></i><span>Editar Usuario</span>';
    document.getElementById('usuario-id').value = id;
    
    // Buscar datos del usuario en la tabla
    const fila = document.querySelector(`tr[data-user-id="${id}"]`);
    if (fila) {
        document.getElementById('usuario-username').value = fila.getAttribute('data-username');
        document.getElementById('usuario-name').value = fila.getAttribute('data-name');
        document.getElementById('usuario-email').value = fila.getAttribute('data-email');
        document.getElementById('usuario-role').value = fila.getAttribute('data-role');
        
        const importRole = fila.getAttribute('data-import-role') || '';
        document.getElementById('usuario-import-role').value = importRole;
    }
    
    document.getElementById('modal-usuario').classList.remove('hidden');
    
    // Añadir una animación de entrada al modal
    const modalContainer = document.querySelector('.admin-modal');
    modalContainer.classList.add('animate-fadeIn');
    setTimeout(() => {
        modalContainer.classList.remove('animate-fadeIn');
    }, 500);
}

function crearUsuario() {
    document.getElementById('modal-title').innerHTML = '<i class="fas fa-user-plus mr-2"></i><span>Nuevo Usuario</span>';
    document.getElementById('usuario-id').value = '';
    document.getElementById('form-usuario').reset();
    // Mostrar el modal
    document.getElementById('modal-usuario').classList.remove('hidden');
    
    // Añadir una animación de entrada al modal
    const modalContainer = document.querySelector('.admin-modal');
    modalContainer.classList.add('animate-fadeIn');
    setTimeout(() => {
        modalContainer.classList.remove('animate-fadeIn');
    }, 500);
}

function confirmarEliminacion(id, username) {
    if (confirm(`¿Está seguro que desea eliminar al usuario "${username}"?`)) {
        // Obtener el token CSRF del formulario
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        
        // Eliminar usuario
        fetch(`/admin/usuarios/eliminar/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                // Recargar la página para ver cambios
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error de conexión al servidor', 'error');
        });
    }
}

// Gestión de permisos
function initPermisosTab() {
    const permisosData = [
        { id: 'inicio', nombre: 'Inicio', descripcion: 'Acceso a la página principal' },
        { id: 'buscar', nombre: 'Búsqueda', descripcion: 'Búsqueda de códigos arancelarios' },
        { id: 'secciones', nombre: 'Secciones', descripcion: 'Navegación por secciones y capítulos' },
        { id: 'costos', nombre: 'Costos', descripcion: 'Cálculo de costos de importación' },
        { id: 'resoluciones', nombre: 'Resoluciones', descripcion: 'Acceso a resoluciones particulares' },
        { id: 'grupos', nombre: 'Grupos', descripcion: 'Sistema por grupos' },
        { id: 'configuracion', nombre: 'Configuración', descripcion: 'Ajustes de la cuenta' },
        { id: 'admin', nombre: 'Administración', descripcion: 'Panel de administración' },
    ];
    
    // Cargar permisos del rol seleccionado inicialmente
    cargarPermisosRol(document.getElementById('role-selector').value, permisosData);
    
    // Cargar permisos cuando cambia el rol
    document.getElementById('role-selector').addEventListener('change', function() {
        cargarPermisosRol(this.value, permisosData);
    });
    
    // Guardar cambios de permisos
    document.getElementById('btn-guardar-permisos').addEventListener('click', function() {
        const rol = document.getElementById('role-selector').value;
        const permisosActualizados = [];
        
        document.querySelectorAll('input[type="checkbox"][data-seccion]:checked').forEach(checkbox => {
            permisosActualizados.push(checkbox.dataset.seccion);
        });
        
        // Obtener el token CSRF del formulario
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        
        // Añadir animación al botón
        this.classList.add('saving');
        
        // Enviar al servidor
        fetch('/admin/permisos/guardar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                rol: rol,
                permisos: permisosActualizados
            })
        })
        .then(response => response.json())
        .then(data => {
            this.classList.remove('saving');
            if (data.success) {
                showNotification(data.message, 'success');
            } else {
                showNotification('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            this.classList.remove('saving');
            console.error('Error:', error);
            showNotification('Error de conexión al servidor', 'error');
        });
    });
    
    // Restablecer permisos
    document.getElementById('btn-restablecer').addEventListener('click', function() {
        const rol = document.getElementById('role-selector').value;
        cargarPermisosRol(rol, permisosData);
    });
}

function cargarPermisosRol(rol, permisosData) {
    // Obtener permisos del servidor
    fetch(`/admin/permisos/rol/${rol}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarPermisos(rol, permisosData, data.permisos);
            } else {
                showNotification('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error de conexión al servidor', 'error');
        });
}

function mostrarPermisos(rol, permisosData, permisos) {
    const permisosBody = document.getElementById('permisos-body');
    permisosBody.innerHTML = '';
    
    permisosData.forEach(seccion => {
        const tienePermiso = permisos.includes(seccion.id);
        
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 dark:hover:bg-gray-600';
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-white">${seccion.nombre}</div>
            </td>
            <td class="px-6 py-4">
                <div class="text-sm text-gray-500 dark:text-gray-400">${seccion.descripcion}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <label class="inline-flex items-center cursor-pointer">
                        <input type="checkbox" ${tienePermiso ? 'checked' : ''} class="form-checkbox rounded text-indigo-600 focus:ring-indigo-500 h-5 w-5" data-seccion="${seccion.id}">
                        <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">${tienePermiso ? 'Permitido' : 'Denegado'}</span>
                    </label>
                </div>
            </td>
        `;
        
        permisosBody.appendChild(row);
        
        // Actualizar texto al cambiar el checkbox
        const checkbox = row.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', function() {
            const label = this.parentElement.querySelector('span');
            label.textContent = this.checked ? 'Permitido' : 'Denegado';
        });
    });
}

// Funciones de animación y UI
function initAnimations() {
    // Ejemplo de filtros activos con badges flat pill con dot
    const tablaHeader = document.querySelector('.admin-table thead');
    if (tablaHeader) {
        const filterContainer = document.createElement('div');
        filterContainer.className = 'filtros-activos';
        filterContainer.innerHTML = `
            <span class="filtros-activos-label">Filtros activos:</span>
        `;
        
        // Crear algunos badges flat pill con dot 
        const filtros = [
            { texto: 'Activos', tipo: 'success', emoji: '✅' },
            { texto: 'Administradores', tipo: 'danger', emoji: '👑' },
            { texto: 'VIP', tipo: 'warning', emoji: '🌟' }
        ];
        
        filtros.forEach(filtro => {
            const badge = document.createElement('span');
            badge.className = `role-badge role-badge-${filtro.tipo === 'danger' ? 'admin' : filtro.tipo === 'warning' ? 'vip' : 'despachante'} badge-dismissible`;
            
            // Añadir dot
            const dot = document.createElement('span');
            dot.className = 'badge-dot';
            badge.appendChild(dot);
            
            // Añadir emoji
            const emojiSpan = document.createElement('span');
            emojiSpan.className = 'emoji-badge';
            emojiSpan.textContent = filtro.emoji;
            badge.appendChild(emojiSpan);
            
            // Añadir texto
            badge.appendChild(document.createTextNode(filtro.texto));
            
            // Añadir botón para eliminar
            const dismissBtn = document.createElement('button');
            dismissBtn.className = 'badge-dismiss-btn';
            dismissBtn.innerHTML = '×';
            dismissBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                badge.style.opacity = '0';
                setTimeout(() => {
                    badge.remove();
                    // Si no quedan filtros, ocultar el contenedor
                    if (filterContainer.querySelectorAll('.role-badge').length <= 1) { // Solo queda el "Filtros activos:"
                        filterContainer.style.display = 'none';
                    }
                }, 300);
            });
            
            badge.appendChild(dismissBtn);
            filterContainer.appendChild(badge);
        });
        
        tablaHeader.parentNode.insertBefore(filterContainer, tablaHeader);
    }
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    // Si ya existe una notificación, la eliminamos
    const existingNotification = document.querySelector('.admin-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Crear el elemento de notificación
    const notification = document.createElement('div');
    notification.className = `admin-notification ${type}`;
    
    // Icono según el tipo
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    notification.innerHTML = `
        <i class="fas fa-${icon} mr-2"></i>
        <span>${message}</span>
        <button class="ml-auto">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Añadir al DOM
    document.body.appendChild(notification);
    
    // Mostrar con animación
    setTimeout(() => {
        notification.classList.add('visible');
    }, 10);
    
    // Cerrar al hacer clic en el botón
    notification.querySelector('button').addEventListener('click', () => {
        notification.classList.remove('visible');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Auto cerrar después de 5 segundos
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.classList.remove('visible');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Exponer funciones para uso global
window.editarUsuario = editarUsuario;
window.confirmarEliminacion = confirmarEliminacion;

// Función para aplicar badges mejorados con dot
function aplicarBadgesMejorados() {
    // Aplicar estilos de badges específicos
    document.querySelectorAll('.role-badge').forEach(badge => {
        const text = badge.textContent.trim();
        const lowerText = text.toLowerCase();
        
        // Asegurar que se aplican los estilos correctos según el contenido
        if (lowerText.includes('vip')) {
            badge.classList.add('role-badge-vip');
        } else if (lowerText.includes('admin')) {
            badge.classList.add('role-badge-admin');
        } else if (lowerText.includes('trans')) {
            badge.classList.add('role-badge-transportista');
        } else if (lowerText.includes('despach')) {
            badge.classList.add('role-badge-despachante');
        }
        
        // Asegurar que cada badge tenga un dot
        if (!badge.querySelector('.badge-dot')) {
            const dot = document.createElement('span');
            dot.className = 'badge-dot';
            badge.insertBefore(dot, badge.firstChild);
        }
    });
}

// Inicializar badges después de la carga de la página
window.addEventListener('load', function() {
    // Quitar todos los efectos que pueden hacer la página borrosa
    document.querySelectorAll('.shine-effect').forEach(el => el.remove());
    
    // Aplicar nuevos estilos de badge
    aplicarBadgesMejorados();
    
    // Volver a aplicar después de un pequeño retraso para asegurar que todo está cargado
    setTimeout(aplicarBadgesMejorados, 200);
}); 