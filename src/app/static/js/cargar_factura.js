document.addEventListener('DOMContentLoaded', function() {
    // Función para calcular el total
    function calcularTotal() {
        const valorTotal = parseFloat(document.getElementById('valor_total').value) || 0;
        const flete = parseFloat(document.getElementById('flete').value) || 0;
        const seguro = parseFloat(document.getElementById('seguro').value) || 0;
        
        const total = valorTotal + flete + seguro;
        document.getElementById('total_calculado').value = total.toFixed(2);
    }
    
    // Calcular al inicio
    calcularTotal();
    
    // Calcular cuando cambie cualquiera de los campos
    document.getElementById('valor_total').addEventListener('input', calcularTotal);
    document.getElementById('flete').addEventListener('input', calcularTotal);
    document.getElementById('seguro').addEventListener('input', calcularTotal);
    
    // Funcionalidad para agregar productos
    document.getElementById('agregarProducto').addEventListener('click', function() {
        // Ocultar mensaje de "no hay productos"
        document.getElementById('sinProductos').style.display = 'none';
        
        // Crear nueva fila
        const newRow = document.createElement('tr');
        newRow.className = 'bg-white dark:bg-gray-800';
        
        // Contenido de la fila
        newRow.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                <input type="text" name="codigo[]" 
                    class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
                        placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500
                        dark:bg-gray-700 dark:text-white text-sm">
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                <select name="unidad_medida[]" 
                    class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
                        focus:outline-none focus:ring-blue-500 focus:border-blue-500
                        dark:bg-gray-700 dark:text-white text-sm">
                    <option value="">Seleccionar</option>
                    <option value="unidades">Unidades</option>
                    <option value="cajas">Cajas</option>
                    <option value="kilos">Kilos</option>
                </select>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                <input type="text" name="descripcion[]" 
                    class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
                        placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500
                        dark:bg-gray-700 dark:text-white text-sm">
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                <input type="text" name="nomenclatura[]" 
                    class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
                        placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500
                        dark:bg-gray-700 dark:text-white text-sm">
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                <input type="text" name="pais_origen[]" 
                    class="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
                        placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500
                        dark:bg-gray-700 dark:text-white text-sm">
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right">
                <button type="button" class="eliminarProducto text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        // Agregar fila a la tabla
        document.getElementById('tablaProductos').appendChild(newRow);
        
        // Agregar evento para eliminar la fila
        newRow.querySelector('.eliminarProducto').addEventListener('click', function() {
            newRow.remove();
            
            // Si no hay más filas, mostrar mensaje de "no hay productos"
            const filas = document.querySelectorAll('#tablaProductos tr:not(#sinProductos)');
            if (filas.length === 0) {
                document.getElementById('sinProductos').style.display = '';
            }
        });
    });
}); 