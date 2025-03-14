// Función para inicializar el sistema
function initImportGroupSystem(containerId, userRole = '', sections = {}) {
  const manager = new ImportGroupManager(containerId, userRole, sections);
  manager.init();
  return manager;
}

// Inicialización automática cuando se carga el documento
document.addEventListener('DOMContentLoaded', function() {
  // Obtener datos del elemento JSON
  const dataElement = document.getElementById('sistema-grupo-data');
  
  if (dataElement) {
    try {
      const data = JSON.parse(dataElement.textContent);
      
      // Obtener referencias a las secciones
      const sections = {
        controlsSection: document.getElementById(data.controlsSectionId),
        userPanel: document.getElementById(data.userPanelId),
        availableGroups: document.getElementById(data.availableGroupsId)
      };
      
      // Inicializar el sistema con los datos obtenidos
      initImportGroupSystem(data.containerId, data.userRole, sections);
    } catch (error) {
      console.error('Error al inicializar el sistema de grupos:', error);
    }
  } else {
    console.warn('No se encontraron datos para inicializar el sistema de grupos');
  }
});

// Definición de la clase principal que manejará todo el sistema
class ImportGroupManager {
  constructor(containerId, userRole, sections = {}) {
    this.container = document.getElementById(containerId);
    this.userRole = userRole; // El rol del usuario actual en el sistema de importación
    this.sections = sections; // Referencias a las secciones del DOM
    this.activeGroups = [];
    this.partTypes = [
      'Transportista', 
      'Corredor de Seguros', 
      'Despachante de Aduana', 
      'Importador', 
      'Profesional Asociado'
    ];
    
    // Mapeo entre los roles en la base de datos y los tipos en el sistema
    this.roleMapping = {
      'transportista': 'Transportista',
      'corredor': 'Corredor de Seguros',
      'despachante': 'Despachante de Aduana',
      'importador': 'Importador',
      'profesional': 'Profesional Asociado'
    };
    
    // Nombres variados para los grupos de importación
    this.groupNames = [
      'Importación Marítima',
      'Importación Aérea',
      'Envío Internacional',
      'Transporte Multi-Modal',
      'Carga Internacional',
      'Consolidado de Carga',
      'Logística Especial',
      'Carga Prioritaria',
      'Importación Express',
      'Envío Comercial'
    ];
    
    // Tipos de mercadería
    this.cargoTypes = [
      {name: 'Mercadería Seca', color: 'amber'},
      {name: 'Mercadería Congelada', color: 'sky'},
      {name: 'Mercadería Fría', color: 'cyan'}
    ];
    
    // Tipos de transporte
    this.transportTypes = [
      {id: 'terrestre', name: 'Terrestre', color: 'emerald', icon: '🚚'},
      {id: 'aereo', name: 'Aéreo', color: 'blue', icon: '✈️'},
      {id: 'maritimo', name: 'Marítimo', color: 'indigo', icon: '🚢'}
    ];
    
    // Países de procedencia
    this.originCountries = [
      {name: 'China', color: 'red', icon: '🇨🇳'},
      {name: 'Japón', color: 'pink', icon: '🇯🇵'},
      {name: 'Argentina', color: 'purple', icon: '🇦🇷'},
      {name: 'Alemania', color: 'yellow', icon: '🇩🇪'},
      {name: 'Estados Unidos', color: 'blue', icon: '🇺🇸'},
      {name: 'Brasil', color: 'green', icon: '🇧🇷'},
      {name: 'España', color: 'orange', icon: '🇪🇸'}
    ];
    
    // Rangos de peso bruto
    this.weightRanges = [
      {name: 'Liviano (< 500 kg)', color: 'lime', icon: '⚖️'},
      {name: 'Mediano (500-2000 kg)', color: 'amber', icon: '⚖️'},
      {name: 'Pesado (2-10 ton)', color: 'orange', icon: '⚖️'},
      {name: 'Muy pesado (> 10 ton)', color: 'red', icon: '⚖️'}
    ];
    
    // Filtros activos
    this.activeFilters = [];
  }

  // Inicializa el sistema
  init() {
    // Renderizar los controles en la sección de controles
    if (this.sections.controlsSection) {
      this.renderControls(this.sections.controlsSection);
    } else {
      // Si no se proporcionó una sección de controles, los renderizamos directamente en el contenedor
      this.renderControls(this.container);
    }
    
    // Si es admin o no tiene rol definido, inicia el modo demo automático
    // Si es un usuario con rol específico, muestra la interfaz según su rol
    if (!this.userRole || this.userRole === '') {
      this.startDemoMode();
    } else {
      this.initUserInterface();
    }
  }
  
  // Crea la interfaz específica según el rol del usuario
  initUserInterface() {
    const userTypeName = this.roleMapping[this.userRole] || 'Usuario';
    
    // Crear el panel de usuario en la sección apropiada
    const userPanelSection = this.sections.userPanel || this.container;
    
    // Crear el panel de usuario
    const userPanel = document.createElement('div');
    userPanel.className = 'bg-white dark:bg-gray-700 rounded-lg shadow-md p-4';
    
    const title = document.createElement('h2');
    title.className = 'text-lg font-medium mb-3 dark:text-gray-200';
    title.textContent = `Panel de ${userTypeName}`;
    
    const description = document.createElement('p');
    description.className = 'mb-4 text-gray-600 dark:text-gray-300';
    description.textContent = this.getRoleDescription(userTypeName);
    
    const actionButtons = document.createElement('div');
    actionButtons.className = 'flex space-x-4';
    
    if (this.userRole === 'importador') {
      // Los importadores pueden crear nuevos grupos
      const createButton = document.createElement('button');
      createButton.className = 'bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded dark:bg-blue-600 dark:hover:bg-blue-700';
      createButton.textContent = 'Crear Nueva Importación';
      createButton.addEventListener('click', () => this.createUserImportGroup());
      actionButtons.appendChild(createButton);
    } else {
      // Otros roles pueden unirse a grupos existentes
      const joinButton = document.createElement('button');
      joinButton.className = 'bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded dark:bg-green-600 dark:hover:bg-green-700';
      joinButton.textContent = 'Unirse a un Grupo';
      joinButton.addEventListener('click', () => this.showAvailableGroups());
      actionButtons.appendChild(joinButton);
    }
    
    userPanel.appendChild(title);
    userPanel.appendChild(description);
    userPanel.appendChild(actionButtons);
    
    // Añadir el panel a la sección correspondiente
    userPanelSection.innerHTML = ''; // Limpiar cualquier contenido anterior
    userPanelSection.appendChild(userPanel);
    
    // Usar la sección de grupos disponibles si existe
    this.availableGroupsSection = this.sections.availableGroups || null;
    if (!this.availableGroupsSection) {
      // Si no hay sección específica, crear un contenedor en el panel de usuario
      this.availableGroupsContainer = document.createElement('div');
      this.availableGroupsContainer.className = 'mt-4 hidden';
      this.availableGroupsContainer.innerHTML = '<h3 class="text-lg font-medium mb-3 dark:text-gray-200">Grupos Disponibles</h3>';
      userPanelSection.appendChild(this.availableGroupsContainer);
    } else {
      this.availableGroupsContainer = this.availableGroupsSection;
      this.availableGroupsContainer.innerHTML = '<h3 class="text-lg font-medium mb-3 dark:text-gray-200">Grupos Disponibles</h3>';
    }
    
    // Crear demos para mostrar grupos disponibles
    this.createDemoGroups();
  }
  
  // Obtiene descripción del rol
  getRoleDescription(role) {
    const descriptions = {
      'Transportista': 'Como transportista, puedes unirte a grupos de importación existentes para ofrecer tus servicios de transporte.',
      'Corredor de Seguros': 'Como corredor de seguros, puedes unirte a grupos de importación para proporcionar seguros para la mercancía.',
      'Despachante de Aduana': 'Como despachante, puedes unirte a grupos para gestionar los trámites aduaneros de la importación.',
      'Importador': 'Como importador, puedes crear nuevos grupos de importación e invitar a otros profesionales.',
      'Profesional Asociado': 'Como profesional asociado, puedes unirte a grupos para ofrecer servicios complementarios.'
    };
    
    return descriptions[role] || 'Rol no definido';
  }
  
  // Crea algunos grupos de demostración para que los usuarios puedan unirse
  createDemoGroups() {
    // Crear 2 grupos que necesiten el tipo de parte del usuario actual
    for (let i = 0; i < 2; i++) {
      const group = this.createRandomImportGroup();
      
      // Asegurarse de que el grupo no tenga el tipo del usuario actual
      const userPartType = this.roleMapping[this.userRole];
      
      // Asegurarse de que el grupo esté incompleto pero con varias partes
      const randomParts = Math.floor(Math.random() * 3) + 1; // 1-3 partes aleatorias
      
      for (let j = 0; j < randomParts; j++) {
        const availableTypes = this.partTypes.filter(type => 
          type !== userPartType && !group.hasPart(type)
        );
        
        if (availableTypes.length > 0) {
          const randomType = availableTypes[Math.floor(Math.random() * availableTypes.length)];
          group.addPart(randomType);
        }
      }
    }
  }
  
  // Muestra grupos disponibles para unirse
  showAvailableGroups() {
    // Mostrar el contenedor de grupos disponibles
    this.availableGroupsContainer.classList.remove('hidden');
    
    // Limpiar el contenedor, manteniendo el título si existe
    const title = this.availableGroupsContainer.querySelector('h3');
    this.availableGroupsContainer.innerHTML = '';
    
    if (title) {
      this.availableGroupsContainer.appendChild(title);
    } else {
      const newTitle = document.createElement('h3');
      newTitle.className = 'text-lg font-medium mb-3 dark:text-gray-200';
      newTitle.textContent = 'Grupos Disponibles';
      this.availableGroupsContainer.appendChild(newTitle);
    }
    
    // Crear lista de grupos
    const newGroupsList = document.createElement('div');
    newGroupsList.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4';
    
    // Si no hay grupos activos, mostrar mensaje
    if (this.activeGroups.length === 0) {
      const emptyMessage = document.createElement('div');
      emptyMessage.className = 'col-span-2 text-center p-8 bg-gray-100 dark:bg-gray-800 rounded-lg';
      emptyMessage.innerHTML = '<p class="text-gray-500 dark:text-gray-400">No hay grupos disponibles en este momento.</p>';
      newGroupsList.appendChild(emptyMessage);
    } else {
      // Filtrar grupos que necesitan el tipo de parte del usuario actual
      const userPartType = this.roleMapping[this.userRole];
      const availableGroups = this.activeGroups.filter(group => 
        !group.isCompleted && !group.hasPart(userPartType)
      );
      
      if (availableGroups.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'col-span-2 text-center p-8 bg-gray-100 dark:bg-gray-800 rounded-lg';
        emptyMessage.innerHTML = '<p class="text-gray-500 dark:text-gray-400">No hay grupos que requieran tus servicios en este momento.</p>';
        newGroupsList.appendChild(emptyMessage);
      } else {
        // Crear tarjetas para cada grupo disponible
        availableGroups.forEach(group => {
          const card = document.createElement('div');
          card.className = 'bg-white dark:bg-gray-700 rounded-lg shadow-md p-4';
          
          const header = document.createElement('div');
          header.className = 'flex justify-between items-center mb-3';
          
          const title = document.createElement('h3');
          title.className = 'text-lg font-semibold text-gray-800 dark:text-gray-200';
          title.innerHTML = `${group.transportType.icon} ${group.name} <span class="text-sm text-gray-500">#${Math.floor(Math.random() * 1000)}</span>`;
          
          const statusBadge = document.createElement('span');
          statusBadge.className = 'px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
          
          const percentage = Math.round((group.parts.length / this.partTypes.length) * 100);
          statusBadge.textContent = `En Formación ${percentage}%`;
          
          header.appendChild(title);
          header.appendChild(statusBadge);
          card.appendChild(header);
          
          // Agregar características del grupo
          const details = document.createElement('div');
          details.className = 'flex flex-wrap gap-1 mb-2';
          
          // Tipo de transporte
          const transportTypeEl = document.createElement('div');
          transportTypeEl.className = `px-2 py-1 rounded-md bg-${group.transportType.color}-100 text-${group.transportType.color}-800 text-xs dark:bg-${group.transportType.color}-900 dark:text-${group.transportType.color}-200`;
          transportTypeEl.innerHTML = `${group.transportType.icon} ${group.transportType.name}`;
          details.appendChild(transportTypeEl);
          
          // Tipo de mercadería
          const cargoTypeEl = document.createElement('div');
          cargoTypeEl.className = `px-2 py-1 rounded-md bg-${group.cargoType.color}-100 text-${group.cargoType.color}-800 text-xs dark:bg-${group.cargoType.color}-900 dark:text-${group.cargoType.color}-200`;
          cargoTypeEl.textContent = group.cargoType.name;
          details.appendChild(cargoTypeEl);
          
          card.appendChild(details);
          
          // Segunda fila de características
          const secondRow = document.createElement('div');
          secondRow.className = 'flex flex-wrap gap-1 mb-3';
          
          // País de origen
          const originEl = document.createElement('div');
          originEl.className = `px-2 py-1 rounded-md bg-${group.origin.color}-100 text-${group.origin.color}-800 text-xs dark:bg-${group.origin.color}-900 dark:text-${group.origin.color}-200`;
          originEl.innerHTML = `${group.origin.icon} ${group.origin.name}`;
          secondRow.appendChild(originEl);
          
          // Peso
          const weightEl = document.createElement('div');
          weightEl.className = `px-2 py-1 rounded-md bg-${group.weight.color}-100 text-${group.weight.color}-800 text-xs dark:bg-${group.weight.color}-900 dark:text-${group.weight.color}-200`;
          weightEl.innerHTML = `${group.weight.icon} ${group.weight.name}`;
          secondRow.appendChild(weightEl);
          
          card.appendChild(secondRow);
          
          // Botón para unirse
          const joinButton = document.createElement('button');
          joinButton.className = 'w-full mt-3 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded dark:bg-green-600 dark:hover:bg-green-700';
          joinButton.textContent = 'Unirse a este grupo';
          joinButton.addEventListener('click', () => {
            this.joinGroup(group);
            this.availableGroupsContainer.classList.add('hidden');
          });
          
          card.appendChild(joinButton);
          newGroupsList.appendChild(card);
        });
      }
    }
    
    this.availableGroupsContainer.appendChild(newGroupsList);
  }
  
  // Permite a un usuario unirse a un grupo
  joinGroup(group) {
    const userPartType = this.roleMapping[this.userRole];
    group.addUserPart(userPartType);
    
    // Verificar si el grupo está completo
    if (group.isComplete()) {
      this.completeGroup(group);
    }
  }
  
  // Crea un grupo iniciado por un usuario importador
  createUserImportGroup() {
    // Permitir al usuario seleccionar las características
    // Por simplicidad, crearemos uno aleatorio
    
    const group = this.createRandomImportGroup();
    
    // Añadir automáticamente al usuario como importador
    group.addUserPart(this.roleMapping[this.userRole]);
    
    return group;
  }

  // Renderiza los controles de la aplicación
  renderControls(container) {
    const controlsDiv = document.createElement('div');
    controlsDiv.className = 'flex flex-wrap justify-between items-center gap-2 p-4 bg-white dark:bg-gray-700 rounded-lg shadow-md';
    
    // Sección izquierda: botón de crear
    const leftSection = document.createElement('div');
    leftSection.className = 'flex-shrink-0';
    
    const button = document.createElement('button');
    button.textContent = 'Crear Nueva Importación';
    button.className = 'bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded dark:bg-blue-600 dark:hover:bg-blue-700';
    button.addEventListener('click', () => this.createRandomImportGroup());
    
    leftSection.appendChild(button);
    controlsDiv.appendChild(leftSection);
    
    // Sección derecha: filtros
    const rightSection = document.createElement('div');
    rightSection.className = 'flex flex-wrap gap-2 items-center';
    
    const filterLabel = document.createElement('span');
    filterLabel.className = 'text-sm text-gray-600 dark:text-gray-300';
    filterLabel.textContent = 'Filtrar por:';
    rightSection.appendChild(filterLabel);
    
    // Crear un badge para "Todos"
    const allBadge = document.createElement('button');
    allBadge.className = 'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600';
    allBadge.textContent = 'Todos';
    allBadge.addEventListener('click', () => this.clearFilters());
    rightSection.appendChild(allBadge);
    
    // Crear los badges para cada tipo de transporte
    for (const transport of this.transportTypes) {
      const badge = document.createElement('button');
      badge.className = `inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-${transport.color}-100 text-${transport.color}-800 hover:bg-${transport.color}-200 dark:bg-${transport.color}-900 dark:text-${transport.color}-200`;
      badge.innerHTML = `${transport.icon} ${transport.name}`;
      badge.dataset.transportId = transport.id;
      badge.addEventListener('click', () => this.toggleFilter(transport.id));
      rightSection.appendChild(badge);
    }
    
    controlsDiv.appendChild(rightSection);
    container.appendChild(controlsDiv);
  }

  // Activa/desactiva un filtro de transporte
  toggleFilter(transportType) {
    const index = this.activeFilters.indexOf(transportType);
    if (index > -1) {
      this.activeFilters.splice(index, 1);
    } else {
      this.activeFilters.push(transportType);
    }
    
    this.updateFilterUI();
    this.applyFilters();
  }

  // Limpia todos los filtros activos
  clearFilters() {
    this.activeFilters = [];
    this.updateFilterUI();
    this.applyFilters();
  }

  // Actualiza la UI para reflejar los filtros activos
  updateFilterUI() {
    const badges = this.container.querySelectorAll('button[data-transport-id]');
    badges.forEach(badge => {
      const transportId = badge.dataset.transportId;
      if (this.activeFilters.includes(transportId)) {
        badge.classList.add('ring-2', 'ring-offset-2', `ring-${badge.classList.toString().match(/bg-(\w+)-/)[1]}-500`);
      } else {
        badge.classList.remove('ring-2', 'ring-offset-2', `ring-${badge.classList.toString().match(/bg-(\w+)-/)?.[1] || 'blue'}-500`);
      }
    });
  }

  // Aplica los filtros a los grupos mostrados
  applyFilters() {
    const groupElements = this.container.querySelectorAll('.import-group');
    
    groupElements.forEach(groupElement => {
      const transportType = groupElement.dataset.transportType;
      
      if (this.activeFilters.length === 0 || this.activeFilters.includes(transportType)) {
        groupElement.classList.remove('hidden');
      } else {
        groupElement.classList.add('hidden');
      }
    });
  }

  // Inicia el modo de demostración automática
  startDemoMode() {
    // Crear un grupo inicial
    this.createRandomImportGroup();
    
    // Programar la creación de grupos cada cierto tiempo
    setInterval(() => {
      if (Math.random() < 0.3 && this.activeGroups.length < 5) {
        this.createRandomImportGroup();
      }
      
      // Agregar una parte aleatoria a un grupo aleatorio
      if (this.activeGroups.length > 0) {
        const randomGroup = this.activeGroups[Math.floor(Math.random() * this.activeGroups.length)];
        this.addRandomPartToGroup(randomGroup);
      }
    }, 3000);
  }

  // Crea un nuevo grupo aleatorio
  createRandomImportGroup() {
    // Seleccionar características aleatorias
    const name = this.groupNames[Math.floor(Math.random() * this.groupNames.length)];
    const cargoType = this.cargoTypes[Math.floor(Math.random() * this.cargoTypes.length)];
    const transportType = this.transportTypes[Math.floor(Math.random() * this.transportTypes.length)];
    const origin = this.originCountries[Math.floor(Math.random() * this.originCountries.length)];
    const weight = this.weightRanges[Math.floor(Math.random() * this.weightRanges.length)];
    
    // Crear el grupo
    const group = new ImportGroup(this, name, cargoType, transportType, origin, weight);
    
    // Agregar al arreglo de grupos activos
    this.activeGroups.push(group);
    
    // Agregar al DOM
    this.container.appendChild(group.element);
    
    // Agregar 1-3 partes aleatorias para empezar
    const initialParts = 1 + Math.floor(Math.random() * 3);
    for (let i = 0; i < initialParts; i++) {
      this.addRandomPartToGroup(group);
    }
    
    return group;
  }

  // Agrega una parte aleatoria a un grupo
  addRandomPartToGroup(group) {
    // Si el grupo ya está completo, no hacer nada
    if (group.isCompleted) return;
    
    // Determinar qué tipos de partes faltan
    const missingPartTypes = this.partTypes.filter(type => !group.hasPart(type));
    
    if (missingPartTypes.length === 0) {
      // El grupo está completo
      this.completeGroup(group);
      return;
    }
    
    // Seleccionar un tipo de parte aleatoria de las que faltan
    const randomType = missingPartTypes[Math.floor(Math.random() * missingPartTypes.length)];
    
    // Agregar la parte
    group.addPart(randomType);
    
    // Verificar si el grupo está completo
    if (group.isComplete()) {
      this.completeGroup(group);
    }
  }

  // Maneja un grupo completo
  completeGroup(group) {
    // Si el grupo ya está marcado como completo, no hacer nada
    if (group.isCompleted) return;
    
    // Marcar como completo en la UI
    group.markAsComplete();
    
    // Programar la eliminación después de un tiempo
    setTimeout(() => {
      // Animar la desaparición
      group.element.classList.add('opacity-0');
      
      // Quitar del DOM después de la animación
      setTimeout(() => {
        this.container.removeChild(group.element);
        
        // Quitar del arreglo de grupos activos
        const index = this.activeGroups.indexOf(group);
        if (index > -1) {
          this.activeGroups.splice(index, 1);
        }
      }, 500);
    }, 3000); // 3 segundos
  }
}

// Clase que representa un grupo de importación
class ImportGroup {
  constructor(manager, name, cargoType, transportType, origin, weight) {
    this.manager = manager;
    this.name = name;
    this.cargoType = cargoType;
    this.transportType = transportType;
    this.origin = origin;
    this.weight = weight;
    this.parts = [];
    this.isCompleted = false;
    
    this.createElements();
  }

  // Obtiene el emoji correspondiente a cada tipo de rol
  getRoleEmoji(roleType) {
    const roleEmojis = {
      'Transportista': '🚚',
      'Corredor de Seguros': '🛡️',
      'Despachante de Aduana': '📦',
      'Importador': '🏢',
      'Profesional Asociado': '👨‍💼'
    };
    
    return roleEmojis[roleType] || '⚙️'; // Emoji por defecto si no se encuentra
  }

  // Crea los elementos del DOM para el grupo
  createElements() {
    this.element = document.createElement('div');
    this.element.className = 'import-group bg-white dark:bg-gray-700 rounded-lg shadow-md p-4 transition-opacity duration-500';
    this.element.dataset.transportType = this.transportType.id;
    
    // Header con el nombre y el estado
    const header = document.createElement('div');
    header.className = 'flex justify-between items-center mb-3';
    
    const title = document.createElement('h3');
    title.className = 'text-lg font-semibold text-gray-800 dark:text-gray-200';
    title.innerHTML = `${this.transportType.icon} ${this.name} <span class="text-sm text-gray-500">#${Math.floor(Math.random() * 1000)}</span>`;
    
    this.statusBadge = document.createElement('span');
    this.statusBadge.className = 'px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    this.statusBadge.textContent = 'En Formación';
    
    header.appendChild(title);
    header.appendChild(this.statusBadge);
    this.element.appendChild(header);
    
    // Características del grupo
    const details = document.createElement('div');
    details.className = 'flex flex-wrap gap-1 mb-2';
    
    // Tipo de transporte
    const transportTypeEl = document.createElement('div');
    transportTypeEl.className = `px-2 py-1 rounded-md bg-${this.transportType.color}-100 text-${this.transportType.color}-800 text-xs dark:bg-${this.transportType.color}-900 dark:text-${this.transportType.color}-200`;
    transportTypeEl.innerHTML = `${this.transportType.icon} ${this.transportType.name}`;
    details.appendChild(transportTypeEl);
    
    // Tipo de mercadería
    const cargoTypeEl = document.createElement('div');
    cargoTypeEl.className = `px-2 py-1 rounded-md bg-${this.cargoType.color}-100 text-${this.cargoType.color}-800 text-xs dark:bg-${this.cargoType.color}-900 dark:text-${this.cargoType.color}-200`;
    cargoTypeEl.textContent = this.cargoType.name;
    details.appendChild(cargoTypeEl);
    
    this.element.appendChild(details);
    
    // Segunda fila de características
    const secondRow = document.createElement('div');
    secondRow.className = 'flex flex-wrap gap-1 mb-3';
    
    // País de origen
    const originEl = document.createElement('div');
    originEl.className = `px-2 py-1 rounded-md bg-${this.origin.color}-100 text-${this.origin.color}-800 text-xs dark:bg-${this.origin.color}-900 dark:text-${this.origin.color}-200`;
    originEl.innerHTML = `${this.origin.icon} ${this.origin.name}`;
    secondRow.appendChild(originEl);
    
    // Peso
    const weightEl = document.createElement('div');
    weightEl.className = `px-2 py-1 rounded-md bg-${this.weight.color}-100 text-${this.weight.color}-800 text-xs dark:bg-${this.weight.color}-900 dark:text-${this.weight.color}-200`;
    weightEl.innerHTML = `${this.weight.icon} ${this.weight.name}`;
    secondRow.appendChild(weightEl);
    
    this.element.appendChild(secondRow);
    
    // NUEVO: Contenedor para roles del grupo
    const rolesContainer = document.createElement('div');
    rolesContainer.className = 'mt-3 border-t pt-2 border-gray-200 dark:border-gray-600';
    
    // Título para la sección de roles
    const rolesTitle = document.createElement('div');
    rolesTitle.className = 'text-sm font-medium mb-2 text-gray-700 dark:text-gray-300';
    rolesTitle.textContent = 'Equipo de Importación:';
    rolesContainer.appendChild(rolesTitle);
    
    // Listas para roles cubiertos y faltantes
    this.rolesList = document.createElement('div');
    this.rolesList.className = 'mb-2';
    rolesContainer.appendChild(this.rolesList);
    
    // Guardar referencia al contenedor de partes para mantener compatibilidad
    this.partsContainer = rolesContainer;
    
    // Agregar el contenedor de roles al elemento principal
    this.element.appendChild(rolesContainer);
    
    // Actualizar la visualización inicial de roles
    this.updateRolesDisplay();
  }
  
  // Nuevo método para actualizar la visualización de roles
  updateRolesDisplay() {
    // Limpiar la lista actual
    this.rolesList.innerHTML = '';
    
    // Crear la lista de roles cubiertos
    const coveredRoles = document.createElement('div');
    coveredRoles.className = 'mb-2';
    
    if (this.parts.length > 0) {
      // Título para roles cubiertos
      const coveredTitle = document.createElement('div');
      coveredTitle.className = 'text-xs font-medium text-green-700 dark:text-green-400 mb-1';
      coveredTitle.textContent = 'Roles cubiertos:';
      coveredRoles.appendChild(coveredTitle);
      
      // Lista de roles cubiertos
      const coveredList = document.createElement('div');
      coveredList.className = 'grid grid-cols-1 gap-1';
      
      this.parts.forEach(part => {
        const roleItem = document.createElement('div');
        roleItem.className = `px-2 py-1 rounded flex items-center bg-${part.getColorForType()}-50 border border-${part.getColorForType()}-200 dark:bg-${part.getColorForType()}-900/30 dark:border-${part.getColorForType()}-800`;
        
        const roleIcon = document.createElement('span');
        roleIcon.className = 'mr-1';
        roleIcon.textContent = part.isRealUser ? '👤' : this.getRoleEmoji(part.type);
        
        const roleName = document.createElement('span');
        roleName.className = `text-xs font-medium text-${part.getColorForType()}-800 dark:text-${part.getColorForType()}-200`;
        roleName.textContent = `${part.type}: `;
        
        const companyName = document.createElement('span');
        companyName.className = 'text-xs text-gray-600 dark:text-gray-400';
        companyName.textContent = part.isRealUser ? 'Usuario' : part.generateRandomCompany();
        
        roleItem.appendChild(roleIcon);
        roleItem.appendChild(roleName);
        roleItem.appendChild(companyName);
        coveredList.appendChild(roleItem);
      });
      
      coveredRoles.appendChild(coveredList);
    }
    
    // Crear la lista de roles faltantes
    const missingRoles = document.createElement('div');
    
    // Determinar qué roles faltan
    const missingPartTypes = this.manager.partTypes.filter(type => !this.hasPart(type));
    
    if (missingPartTypes.length > 0) {
      // Título para roles faltantes
      const missingTitle = document.createElement('div');
      missingTitle.className = 'text-xs font-medium text-amber-700 dark:text-amber-400 mt-2 mb-1';
      missingTitle.textContent = 'Roles disponibles:';
      missingRoles.appendChild(missingTitle);
      
      // Lista de roles faltantes
      const missingList = document.createElement('div');
      missingList.className = 'grid grid-cols-1 gap-1';
      
      missingPartTypes.forEach(type => {
        const roleItem = document.createElement('div');
        roleItem.className = 'px-2 py-1 rounded flex items-center bg-gray-50 border border-dashed border-gray-300 dark:bg-gray-800/30 dark:border-gray-700';
        roleItem.dataset.partType = type;
        
        const roleIcon = document.createElement('span');
        roleIcon.className = 'mr-1 opacity-50';
        roleIcon.textContent = this.getRoleEmoji(type);
        
        const roleName = document.createElement('span');
        roleName.className = 'text-xs text-gray-500 dark:text-gray-400';
        roleName.textContent = type;
        
        roleItem.appendChild(roleIcon);
        roleItem.appendChild(roleName);
        missingList.appendChild(roleItem);
      });
      
      missingRoles.appendChild(missingList);
    }
    
    // Agregar listas al contenedor
    this.rolesList.appendChild(coveredRoles);
    this.rolesList.appendChild(missingRoles);
  }

  // Agrega una parte al grupo
  addPart(type) {
    const part = new ImportPart(type, this, false);
    this.parts.push(part);
    
    // Actualizar la visualización de roles
    this.updateRolesDisplay();
    this.updateStatus();
  }
  
  // Agrega una parte de usuario real al grupo
  addUserPart(type) {
    const part = new ImportPart(type, this, true); // true indica que es un usuario real
    this.parts.push(part);
    
    // Actualizar la visualización de roles
    this.updateRolesDisplay();
    this.updateStatus();
  }

  // Verifica si el grupo tiene una parte del tipo especificado
  hasPart(type) {
    return this.parts.some(part => part.type === type);
  }

  // Verifica si el grupo está completo
  isComplete() {
    return this.parts.length === this.manager.partTypes.length;
  }

  // Actualiza el estado del grupo en la UI
  updateStatus() {
    const percentage = Math.round((this.parts.length / this.manager.partTypes.length) * 100);
    this.statusBadge.textContent = `En Formación ${percentage}%`;
  }

  // Marca el grupo como completo
  markAsComplete() {
    if (this.isCompleted) return; // Si ya está completado, no hacer nada
    
    this.isCompleted = true;
    this.element.classList.add('border-l-4', 'border-green-500', 'dark:border-green-600');
    this.statusBadge.className = 'px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    this.statusBadge.textContent = 'Grupo Completo';
    
    // Actualizar la sección de roles para mostrar "Equipo completo"
    if (this.rolesList) {
      this.rolesList.innerHTML = '';
      
      const completedMsg = document.createElement('div');
      completedMsg.className = 'p-2 bg-green-50 border border-green-200 rounded-md text-center dark:bg-green-900/30 dark:border-green-800';
      
      const checkIcon = document.createElement('span');
      checkIcon.className = 'text-green-500 dark:text-green-400 mr-1';
      checkIcon.textContent = '✓';
      
      const msgText = document.createElement('span');
      msgText.className = 'text-sm text-green-700 dark:text-green-300';
      msgText.textContent = 'Equipo completo - El proceso de importación comenzará pronto';
      
      completedMsg.appendChild(checkIcon);
      completedMsg.appendChild(msgText);
      this.rolesList.appendChild(completedMsg);
    }
  }
}

// Clase que representa una parte del grupo de importación
class ImportPart {
  constructor(type, group, isRealUser = false) {
    this.type = type;
    this.group = group;
    this.isRealUser = isRealUser;
    
    this.createElements();
  }

  // Crea los elementos del DOM para la parte
  createElements() {
    this.element = document.createElement('div');
    
    // Si es un usuario real, destacar con un borde
    if (this.isRealUser) {
      this.element.className = `bg-${this.getColorForType()}-100 dark:bg-${this.getColorForType()}-900 rounded-md p-1 h-16 ring-2 ring-${this.getColorForType()}-500`;
    } else {
      this.element.className = `bg-${this.getColorForType()}-100 dark:bg-${this.getColorForType()}-900 rounded-md p-1 h-16`;
    }
    
    const content = document.createElement('div');
    content.className = 'flex flex-col h-full justify-center';
    
    const title = document.createElement('div');
    title.className = `font-medium text-${this.getColorForType()}-800 dark:text-${this.getColorForType()}-200 text-xs`;
    title.textContent = this.type.split(' ')[0]; // Solo mostrar la primera palabra
    
    const company = document.createElement('div');
    company.className = 'text-xs';
    
    if (this.isRealUser) {
      company.innerHTML = `<span class="font-medium text-xs">👤 Usuario</span>`;
    } else {
      company.textContent = this.generateRandomCompany();
      company.className = 'text-xs truncate';
    }
    
    content.appendChild(title);
    content.appendChild(company);
    this.element.appendChild(content);
  }

  // Genera un color basado en el tipo de parte
  getColorForType() {
    const colorMap = {
      'Transportista': 'blue',
      'Corredor de Seguros': 'purple',
      'Despachante de Aduana': 'emerald',
      'Importador': 'amber',
      'Profesional Asociado': 'pink'
    };
    
    return colorMap[this.type] || 'gray';
  }

  // Genera un nombre aleatorio de compañía
  generateRandomCompany() {
    const prefixes = ['GL', 'INT', 'TRS', 'MG', 'SUP', 'PRO', 'EXP', 'FS'];
    const suffixes = ['Log', 'Trp', 'Crg', 'Ship', 'Imp', 'Trd', 'Sol', 'SRL'];
    
    return `${prefixes[Math.floor(Math.random() * prefixes.length)]} ${suffixes[Math.floor(Math.random() * suffixes.length)]}`;
  }
} 