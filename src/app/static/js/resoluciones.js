/**
 * Funcionalidad JavaScript para la página de resoluciones
 */

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const eliminarBotones = document.querySelectorAll('.accion-eliminar');
    const guardarResolucionBtn = document.getElementById('guardarResolucion');
    const prepararEditarBotones = document.querySelectorAll('.accion-editar');
    const modalEditar = document.getElementById('editarModal');
    const cerrarModalBtn = document.querySelector('.modal-close');
    const cancelarBtn = document.getElementById('cancelarEdicion');
    const buscarBtn = document.getElementById('buscarBtn');
    const limpiarBtn = document.getElementById('limpiarBtn');
    
    // Manejo de búsqueda
    if (buscarBtn) {
        buscarBtn.addEventListener('click', function(e) {
            // El formulario se envía normalmente mediante el submit del form
        });
    }
    
    // Limpiar filtros de búsqueda
    if (limpiarBtn) {
        limpiarBtn.addEventListener('click', function(e) {
            const formInputs = document.querySelectorAll('#busquedaForm input, #busquedaForm select');
            formInputs.forEach(input => {
                input.value = '';
            });
            // Opcional: enviar el formulario automáticamente después de limpiar
            document.getElementById('busquedaForm').submit();
        });
    }
    
    // Formatear NCM con puntos
    const ncmInputs = document.querySelectorAll('input[name="ncm"]');
    ncmInputs.forEach(input => {
        input.addEventListener('blur', function() {
            formatearNCM(this);
        });
    });
    
    // Manejo de eliminación de resoluciones
    eliminarBotones.forEach(boton => {
        boton.addEventListener('click', function(e) {
            e.preventDefault();
            const resId = this.getAttribute('data-id');
            const anio = this.getAttribute('data-anio');
            const numero = this.getAttribute('data-numero');
            
            if (confirm(`¿Está seguro que desea eliminar la resolución ${anio}/${numero}?`)) {
                window.location.href = `/eliminar_resolucion/${resId}`;
            }
        });
    });
    
    // Preparar para editar resolución
    if (prepararEditarBotones.length > 0) {
        prepararEditarBotones.forEach(boton => {
            boton.addEventListener('click', function(e) {
                e.preventDefault();
                const resId = this.getAttribute('data-id');
                const anio = this.getAttribute('data-anio');
                const numero = this.getAttribute('data-numero');
                const fecha = this.getAttribute('data-fecha');
                const ncm = this.getAttribute('data-ncm');
                const concepto = this.getAttribute('data-concepto');
                
                // Llenar el formulario de edición con los datos actuales
                document.getElementById('editId').value = resId;
                document.getElementById('editAnio').value = anio;
                document.getElementById('editNumero').value = numero;
                document.getElementById('editFecha').value = formatearFechaParaInput(fecha);
                document.getElementById('editNcm').value = ncm;
                document.getElementById('editConcepto').value = concepto;
                
                // Mostrar el modal
                mostrarModal();
            });
        });
    }
    
    // Cerrar modal con el botón de cerrar
    if (cerrarModalBtn) {
        cerrarModalBtn.addEventListener('click', function() {
            ocultarModal();
        });
    }
    
    // Cerrar modal con el botón de cancelar
    if (cancelarBtn) {
        cancelarBtn.addEventListener('click', function(e) {
            e.preventDefault();
            ocultarModal();
        });
    }
    
    // Cerrar modal al hacer clic fuera del contenido
    window.addEventListener('click', function(e) {
        if (modalEditar && e.target === modalEditar) {
            ocultarModal();
        }
    });
    
    // Validar formularios antes de enviar
    const formularios = document.querySelectorAll('form');
    formularios.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            let formValido = true;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    formValido = false;
                    input.classList.add('error');
                } else {
                    input.classList.remove('error');
                }
            });
            
            if (!formValido) {
                e.preventDefault();
                alert('Por favor complete todos los campos requeridos.');
            }
        });
    });
});

/**
 * Funciones auxiliares
 */

// Formatear NCM con puntos para mejor legibilidad
function formatearNCM(input) {
    let valor = input.value.replace(/\./g, ''); // Eliminar puntos existentes
    
    if (valor.length === 8) {
        // Formato: XXXX.XX.XX
        valor = valor.substring(0, 4) + '.' + 
                valor.substring(4, 6) + '.' + 
                valor.substring(6, 8);
    }
    
    input.value = valor;
}

// Formatear fecha DD/MM/YYYY a YYYY-MM-DD para inputs de tipo date
function formatearFechaParaInput(fechaString) {
    if (!fechaString) return '';
    
    // Si la fecha ya está en formato YYYY-MM-DD, la devolvemos igual
    if (/^\d{4}-\d{2}-\d{2}$/.test(fechaString)) {
        return fechaString;
    }
    
    // Si la fecha está en formato DD/MM/YYYY, la convertimos
    const partes = fechaString.split('/');
    if (partes.length === 3) {
        return `${partes[2]}-${partes[1]}-${partes[0]}`;
    }
    
    return fechaString;
}

// Mostrar modal de edición
function mostrarModal() {
    const modal = document.getElementById('editarModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('fade-in');
        document.body.style.overflow = 'hidden'; // Evitar scroll en el fondo
    }
}

// Ocultar modal de edición
function ocultarModal() {
    const modal = document.getElementById('editarModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = ''; // Restaurar scroll
    }
} 