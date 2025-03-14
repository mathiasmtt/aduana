/**
 * Funcionalidad JavaScript para la página de cálculo de costos de importación
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configuración de la tabla de costos
    initCostosTable();
    
    // Inicialización de la vista de tarjetas para móviles
    initMobileCards();
});

/**
 * Inicializa la tabla de costos y configura los eventos
 */
function initCostosTable() {
    // Obtener todos los inputs
    const inputs = document.querySelectorAll('input[type="text"]');
    
    // Agregar evento de cambio a cada input
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            handleInputChange(this);
        });
    });
    
    // Configurar campos FCA (Free Carrier) para cada columna
    configureFcaFields();
    
    // Calcular valores iniciales
    calcularValores();
}

/**
 * Inicializa la vista de tarjetas para dispositivos móviles
 */
function initMobileCards() {
    // Configurar tabs para navegar entre mercaderías
    initTabs();
    
    // Configurar acordeones para secciones de cada mercadería
    initAccordions();
    
    // Sincronizar valores entre vista tabla y tarjetas
    syncInputValues();
}

/**
 * Inicializa el sistema de tabs para navegación entre mercaderías en móviles
 */
function initTabs() {
    const tabs = document.querySelectorAll('.costo-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remover clase activa de todas las tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Agregar clase activa a la tab seleccionada
            this.classList.add('active');
            
            // Mostrar el contenido correspondiente
            const tabId = this.getAttribute('data-tab');
            const tabContents = document.querySelectorAll('.costo-tab-content');
            
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.getAttribute('data-tab') === tabId) {
                    content.classList.add('active');
                }
            });
        });
    });
    
    // Activar la primera tab por defecto
    if (tabs.length > 0) {
        tabs[0].click();
    }
}

/**
 * Inicializa el sistema de acordeones para las secciones en móviles
 */
function initAccordions() {
    const accordionHeaders = document.querySelectorAll('.costo-accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const accordion = this.parentElement;
            accordion.classList.toggle('open');
        });
    });
    
    // Abrir el primer acordeón por defecto
    if (accordionHeaders.length > 0) {
        accordionHeaders[0].click();
    }
}

/**
 * Sincroniza los valores entre la vista de tabla y la vista de tarjetas
 */
function syncInputValues() {
    // Sincronia de tabla a tarjetas
    const tableInputs = document.querySelectorAll('.costo-table input');
    
    tableInputs.forEach(input => {
        input.addEventListener('input', function() {
            const id = this.id;
            const mobileInput = document.querySelector(`.costo-cards-container input[data-sync="${id}"]`);
            if (mobileInput) {
                mobileInput.value = this.value;
                
                // También actualizar los valores calculados
                updateCalculatedValuesInCards();
            }
        });
    });
    
    // Sincronia de tarjetas a tabla
    const cardInputs = document.querySelectorAll('.costo-cards-container input');
    
    cardInputs.forEach(input => {
        input.addEventListener('input', function() {
            const syncId = this.getAttribute('data-sync');
            const tableInput = document.getElementById(syncId);
            if (tableInput) {
                tableInput.value = this.value;
                
                // Disparar el evento input para activar los cálculos
                const event = new Event('input', { bubbles: true });
                tableInput.dispatchEvent(event);
            }
        });
    });
}

/**
 * Actualiza los valores calculados en la vista de tarjetas
 */
function updateCalculatedValuesInCards() {
    // Actualizar CIF, VNA, Monto Imponible y Total para cada mercadería
    for (let i = 1; i <= 5; i++) {
        // Recuperar valores calculados desde la tabla
        const cifValue = document.getElementById(`cif_${i}`).textContent;
        const vnaValue = document.getElementById(`vna_${i}`).textContent;
        const imponibleValue = document.getElementById(`imponible_${i}`).textContent;
        const totalValue = document.getElementById(`total_${i}`).textContent;
        
        // Actualizar los valores en las tarjetas
        const cifCard = document.querySelector(`.costo-card[data-mercaderia="${i}"] .costo-card-value[data-calc="cif"]`);
        const vnaCard = document.querySelector(`.costo-card[data-mercaderia="${i}"] .costo-card-value[data-calc="vna"]`);
        const imponibleCard = document.querySelector(`.costo-card[data-mercaderia="${i}"] .costo-card-value[data-calc="imponible"]`);
        const totalCard = document.querySelector(`.costo-card[data-mercaderia="${i}"] .costo-card-total-value`);
        
        if (cifCard) cifCard.textContent = cifValue;
        if (vnaCard) vnaCard.textContent = vnaValue;
        if (imponibleCard) imponibleCard.textContent = imponibleValue;
        if (totalCard) totalCard.textContent = totalValue;
    }
    
    // Actualizar los totales generales en la vista móvil
    updateMobileTotals();
}

/**
 * Actualiza los totales generales en la vista móvil
 */
function updateMobileTotals() {
    const totalsToUpdate = ['exw', 'gastos_fab', 'fca', 'flete', 'seguro', 'cif', 'gastos', 'vna', 'imponible', 'irae', 'iva', 'anticipo_iva', 'imesi', 'total'];
    
    totalsToUpdate.forEach(item => {
        const tableTotal = document.getElementById(`${item}_total`);
        const mobileTotal = document.querySelector(`.costo-mobile-total-row[data-total="${item}"] .costo-mobile-total-value`);
        
        if (tableTotal && mobileTotal) {
            mobileTotal.textContent = tableTotal.textContent;
        }
    });
}

/**
 * Maneja el cambio de valor en cualquier input
 * @param {HTMLElement} input - El input que cambió
 */
function handleInputChange(input) {
    // Manejar la lógica de EXW, Gastos de Fabricación y FCA
    if (input.id.startsWith('exw_') || input.id.startsWith('gastos_fab_')) {
        handleExwGastosFabChange(input);
    } 
    else if (input.id.startsWith('fca_')) {
        handleFcaChange(input);
    }
    
    // Calcular todos los valores dependientes
    calcularValores();
    
    // Resaltar visualmente el cambio
    highlightChange(input);
    
    // Actualizar los valores en la vista de tarjetas
    updateCalculatedValuesInCards();
}

/**
 * Resalta visualmente un campo que ha cambiado
 * @param {HTMLElement} element - El elemento a resaltar
 */
function highlightChange(element) {
    // Eliminar la clase si ya existe
    element.classList.remove('highlight-change');
    
    // Forzar un reflow para reiniciar la animación
    void element.offsetWidth;
    
    // Agregar la clase para iniciar la animación
    element.classList.add('highlight-change');
}

/**
 * Maneja los cambios en los campos EXW o Gastos de Fabricación
 * @param {HTMLElement} input - El input que cambió
 */
function handleExwGastosFabChange(input) {
    const col = input.dataset.col;
    const exwInput = document.getElementById(`exw_${col}`);
    const gastosFabInput = document.getElementById(`gastos_fab_${col}`);
    const fcaInput = document.getElementById(`fca_${col}`);
    
    // Verificar si hay valores en EXW o Gastos de Fabricación
    const exwValue = parseFloat(exwInput.value) || 0;
    const gastosFabValue = parseFloat(gastosFabInput.value) || 0;
    
    // Calcular FCA y actualizar su valor
    fcaInput.value = exwValue + gastosFabValue;
    
    // Gestionar el estado habilitado/deshabilitado de FCA
    updateFcaFieldState(col, exwValue, gastosFabValue);
    
    // Actualizar también el campo FCA en la vista de tarjetas
    const fcaCardInput = document.querySelector(`.costo-cards-container input[data-sync="fca_${col}"]`);
    if (fcaCardInput) {
        fcaCardInput.value = fcaInput.value;
        fcaCardInput.disabled = fcaInput.disabled;
    }
}

/**
 * Maneja los cambios en el campo FCA
 * @param {HTMLElement} input - El input FCA que cambió
 */
function handleFcaChange(input) {
    const col = input.dataset.col;
    const exwInput = document.getElementById(`exw_${col}`);
    const gastosFabInput = document.getElementById(`gastos_fab_${col}`);
    
    // Limpiar los valores de EXW y Gastos de Fabricación
    exwInput.value = '';
    gastosFabInput.value = '';
    
    // Actualizar también los campos en la vista de tarjetas
    const exwCardInput = document.querySelector(`.costo-cards-container input[data-sync="exw_${col}"]`);
    const gastosFabCardInput = document.querySelector(`.costo-cards-container input[data-sync="gastos_fab_${col}"]`);
    
    if (exwCardInput) exwCardInput.value = '';
    if (gastosFabCardInput) gastosFabCardInput.value = '';
}

/**
 * Configura los campos FCA para todas las columnas
 */
function configureFcaFields() {
    for (let i = 1; i <= 5; i++) {
        const fcaInput = document.getElementById(`fca_${i}`);
        const exwInput = document.getElementById(`exw_${i}`);
        const gastosFabInput = document.getElementById(`gastos_fab_${i}`);
        
        fcaInput.addEventListener('click', function() {
            // Verificar si hay valores en EXW o Gastos de Fabricación
            const exwValue = parseFloat(exwInput.value) || 0;
            const gastosFabValue = parseFloat(gastosFabInput.value) || 0;
            
            // Solo permitir editar FCA si EXW y Gastos de Fabricación están vacíos o son cero
            if (exwValue === 0 && gastosFabValue === 0) {
                this.disabled = false;
                this.classList.remove('bg-gray-100', 'dark:bg-gray-700', 'cursor-not-allowed');
            } else {
                // Mostrar un mensaje explicativo
                alert('Para editar FCA directamente, primero debe borrar los valores de EXW y Gastos de Fabricación.');
            }
        });
        
        // Inicializar el estado del campo FCA
        const exwValue = parseFloat(exwInput.value) || 0;
        const gastosFabValue = parseFloat(gastosFabInput.value) || 0;
        updateFcaFieldState(i, exwValue, gastosFabValue);
    }
}

/**
 * Actualiza el estado habilitado/deshabilitado de un campo FCA
 * @param {number} col - Número de columna
 * @param {number} exwValue - Valor del campo EXW
 * @param {number} gastosFabValue - Valor del campo Gastos de Fabricación
 */
function updateFcaFieldState(col, exwValue, gastosFabValue) {
    const fcaInput = document.getElementById(`fca_${col}`);
    
    // Si hay valores en EXW o Gastos de Fabricación, deshabilitar FCA
    if (exwValue > 0 || gastosFabValue > 0) {
        fcaInput.disabled = true;
        fcaInput.classList.add('bg-gray-100', 'dark:bg-gray-700', 'cursor-not-allowed');
    } else {
        fcaInput.disabled = false;
        fcaInput.classList.remove('bg-gray-100', 'dark:bg-gray-700', 'cursor-not-allowed');
    }
}

/**
 * Calcula todos los valores dependientes en la tabla
 */
function calcularValores() {
    // Calcular Valor CIF (FCA + Flete + Seguro) para cada columna
    for (let i = 1; i <= 5; i++) {
        calcularValoresPorColumna(i);
    }
    
    // Calcular totales por fila
    calcularTotalesPorFila();
}

/**
 * Calcula los valores para una columna específica
 * @param {number} col - Número de columna (1-5)
 */
function calcularValoresPorColumna(col) {
    // Obtener valores base
    const fca = parseFloat(document.getElementById(`fca_${col}`).value) || 0;
    const flete = parseFloat(document.getElementById(`flete_${col}`).value) || 0;
    const seguro = parseFloat(document.getElementById(`seguro_${col}`).value) || 0;
    
    // Calcular CIF
    const cif = fca + flete + seguro;
    document.getElementById(`cif_${col}`).textContent = `$${formatNumber(cif)}`;
    
    // Calcular VNA (CIF + Gastos)
    const gastos = parseFloat(document.getElementById(`gastos_${col}`).value) || 0;
    const vna = cif + gastos;
    document.getElementById(`vna_${col}`).textContent = `$${formatNumber(vna)}`;
    
    // Calcular Monto Imponible (VNA + TGA%)
    const tga = parseFloat(document.getElementById(`tga_${col}`).value) || 0;
    const montoImponible = vna * (1 + tga/100);
    document.getElementById(`imponible_${col}`).textContent = `$${formatNumber(montoImponible)}`;
    
    // Calcular el total de la columna
    const irae = parseFloat(document.getElementById(`irae_${col}`).value) || 0;
    const iva = parseFloat(document.getElementById(`iva_${col}`).value) || 0;
    const anticipoIva = parseFloat(document.getElementById(`anticipo_iva_${col}`).value) || 0;
    const imesi = parseFloat(document.getElementById(`imesi_${col}`).value) || 0;
    
    const subtotal = montoImponible + irae + iva + anticipoIva + imesi;
    document.getElementById(`total_${col}`).textContent = `$${formatNumber(subtotal)}`;
}

/**
 * Calcula los totales para cada fila de la tabla
 */
function calcularTotalesPorFila() {
    const filas = ['exw', 'gastos_fab', 'fca', 'flete', 'seguro', 'cif', 'gastos', 'vna', 'tga', 'imponible', 'irae', 'iva', 'anticipo_iva', 'imesi', 'total'];
    
    filas.forEach(fila => {
        // Saltar fila TGA que no tiene total numérico
        if (fila === 'tga') return;
        
        let total = 0;
        
        // Para filas con inputs
        if (['exw', 'gastos_fab', 'fca', 'flete', 'seguro', 'gastos', 'irae', 'iva', 'anticipo_iva', 'imesi'].includes(fila)) {
            for (let i = 1; i <= 5; i++) {
                const valor = parseFloat(document.getElementById(`${fila}_${i}`).value) || 0;
                total += valor;
            }
        } 
        // Para filas con spans (calculados)
        else if (['cif', 'vna', 'imponible', 'total'].includes(fila)) {
            for (let i = 1; i <= 5; i++) {
                const texto = document.getElementById(`${fila}_${i}`).textContent;
                const valor = parseFloat(texto.replace('$', '').replace(/,/g, '')) || 0;
                total += valor;
            }
        }
        
        // Actualizar el total en la tabla
        document.getElementById(`${fila}_total`).textContent = `$${formatNumber(total)}`;
    });
}

/**
 * Formatea un número para mostrar como moneda
 * @param {number} num - Número a formatear
 * @returns {string} - Número formateado
 */
function formatNumber(num) {
    return num.toLocaleString('es-ES');
} 