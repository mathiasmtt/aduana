// Funcionalidades para la página de búsqueda

// Inicializar cuando DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar DataTables si existe la tabla de resultados
    initializeDataTable();
    
    // Mejorar elementos de la página
    enhancePageElements();
    
    // Inicializar sistema de notas expandibles
    initializeExpandableNotes();
    
    // Aplicar efectos visuales
    applyVisualEffects();
});

// Inicialización de DataTables
function initializeDataTable() {
    const tablaResultados = document.getElementById('tabla-resultados');
    
    if (tablaResultados && tablaResultados.tBodies[0].rows.length > 0) {
        // Si no está ya inicializada
        if (!$.fn.DataTable.isDataTable('#tabla-resultados')) {
            $('#tabla-resultados').DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
                },
                responsive: true,
                pageLength: 25,
                order: [[0, 'asc']],
                // Mejorar estilo de elementos DataTables
                initComplete: function(settings, json) {
                    // Agregar clases a los elementos de búsqueda y paginación
                    $('.dataTables_filter input').addClass('search-input');
                    $('.dataTables_paginate .paginate_button').addClass('pagination-button');
                }
            });
        }
    }
}

// Mejorar elementos de la página
function enhancePageElements() {
    // Añadir clases a elementos de formulario
    const searchContainer = document.querySelector('form').closest('div');
    if (searchContainer) {
        searchContainer.classList.add('search-container');
    }
    
    const searchInput = document.getElementById('q');
    if (searchInput) {
        searchInput.classList.add('search-input');
    }
    
    const searchButton = document.querySelector('form button[type="submit"]');
    if (searchButton) {
        searchButton.classList.add('search-button');
    }
    
    // Mejorar tabla de resultados
    const resultTable = document.getElementById('tabla-resultados');
    if (resultTable) {
        resultTable.classList.add('results-table');
    }
    
    // Añadir clases a enlaces de acción
    const actionLinks = document.querySelectorAll('a[href*="ver_arancel"]');
    actionLinks.forEach(link => {
        link.classList.add('action-link');
    });
    
    // Si no hay resultados, mejorar el contenedor
    const noResults = document.querySelector('.px-4.py-5.sm\\:px-6.text-center');
    if (noResults) {
        noResults.classList.add('no-results');
    }
}

// Funcionalidad para notas expandibles
function initializeExpandableNotes() {
    // Si existe la nota de sección
    const sectionNote = document.getElementById('section-note');
    if (sectionNote) {
        // Añadir indicador de expansión si el contenido es más alto que el contenedor
        if (sectionNote.scrollHeight > sectionNote.clientHeight) {
            const indicator = document.createElement('div');
            indicator.className = 'expand-indicator';
            indicator.id = 'section-note-indicator';
            sectionNote.appendChild(indicator);
        }
        
        // Agregar clases
        sectionNote.classList.add('note-content');
        const sectionNoteContainer = sectionNote.closest('.border-b');
        if (sectionNoteContainer) {
            sectionNoteContainer.classList.add('note-container');
        }
        
        // Botones
        const toggleButtons = document.querySelectorAll('[id^="section-note-"]');
        toggleButtons.forEach(button => {
            button.classList.add('note-toggle');
        });
        
        // Contenido
        const noteText = sectionNote.querySelector('pre');
        if (noteText) {
            noteText.classList.add('note-text');
        }
    }
    
    // Si existe la nota de capítulo
    const chapterNote = document.getElementById('chapter-note');
    if (chapterNote) {
        // Añadir indicador de expansión si el contenido es más alto que el contenedor
        if (chapterNote.scrollHeight > chapterNote.clientHeight) {
            const indicator = document.createElement('div');
            indicator.className = 'expand-indicator';
            indicator.id = 'chapter-note-indicator';
            chapterNote.appendChild(indicator);
        }
        
        // Agregar clases
        chapterNote.classList.add('note-content');
        const chapterNoteContainer = chapterNote.closest('.border-b');
        if (chapterNoteContainer) {
            chapterNoteContainer.classList.add('note-container');
        }
        
        // Botones
        const toggleButtons = document.querySelectorAll('[id^="chapter-note-"]');
        toggleButtons.forEach(button => {
            button.classList.add('note-toggle');
        });
        
        // Contenido
        const noteText = chapterNote.querySelector('pre');
        if (noteText) {
            noteText.classList.add('note-text');
        }
    }
}

// Función para manejar la expansión de notas
function toggleNote(id) {
    const note = document.getElementById(id);
    const expandBtn = document.getElementById(id + '-expand');
    const collapseBtn = document.getElementById(id + '-collapse');
    const indicator = document.getElementById(id + '-indicator');
    
    if (note.classList.contains('max-h-40')) {
        note.classList.remove('max-h-40');
        note.classList.add('max-h-full');
        if (expandBtn) expandBtn.classList.add('hidden');
        if (collapseBtn) collapseBtn.classList.remove('hidden');
        if (indicator) indicator.classList.add('hidden');
    } else {
        note.classList.add('max-h-40');
        note.classList.remove('max-h-full');
        if (expandBtn) expandBtn.classList.remove('hidden');
        if (collapseBtn) collapseBtn.classList.add('hidden');
        if (indicator) indicator.classList.remove('hidden');
    }
}

// Aplicar efectos visuales adicionales
function applyVisualEffects() {
    // Agregar efecto de carga bajo demanda para tabla grande
    const resultRows = document.querySelectorAll('#tabla-resultados tbody tr');
    if (resultRows.length > 0) {
        // Aplicar efecto de entrada escalonada a las filas
        resultRows.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateY(10px)';
            row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            setTimeout(() => {
                row.style.opacity = '1';
                row.style.transform = 'translateY(0)';
            }, 50 * (index % 10)); // Limitar a solo las primeras 10 filas para rendimiento
        });
    }
} 