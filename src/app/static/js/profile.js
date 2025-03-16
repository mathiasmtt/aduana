/**
 * Funcionalidades JavaScript para la página de perfil
 */
document.addEventListener('DOMContentLoaded', function() {
    // Inicialización de componentes cuando el DOM esté listo
    initProfilePage();
});

/**
 * Inicializa la página de perfil
 */
function initProfilePage() {
    // Añadir efectos a los botones
    const actionButtons = document.querySelectorAll('.profile-action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.classList.add('pulse-effect');
        });
        
        button.addEventListener('mouseleave', function() {
            this.classList.remove('pulse-effect');
        });
    });
    
    // Añadir contador para usuarios free (si existe)
    const freeUserInfo = document.querySelector('.bg-blue-50.border-l-4.border-blue-500');
    if (freeUserInfo) {
        initSessionTimer();
    }
    
    // Para futuras funcionalidades como cambiar entre temas, actualizar datos, etc.
    console.log('Página de perfil inicializada correctamente');
}

/**
 * Inicializa un temporizador para mostrar el tiempo restante de sesión
 * para usuarios free
 */
function initSessionTimer() {
    // Esta función podría actualizarse para mostrar un contador en tiempo real
    // si se implementa la funcionalidad de actualización automática del tiempo restante
    
    // Por ahora, solo añade funcionalidad visual al tiempo restante
    const timeElement = document.querySelector('.bg-blue-50.border-l-4 strong');
    if (timeElement) {
        // Destacar visualmente el tiempo restante
        timeElement.classList.add('animate-pulse');
        
        // Podríamos actualizar el tiempo restante periódicamente con AJAX
        // pero por ahora sólo es un efecto visual
    }
} 