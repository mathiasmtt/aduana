$(document).ready(function() {
    $('#tabla-capitulos').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
        },
        responsive: true,
        pageLength: 25,
        order: [[0, 'asc']]
    });
}); 