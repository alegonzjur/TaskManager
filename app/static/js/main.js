// Task Manager - Main JavaScript

// Configuración global de Axios
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Función para formatear fechas
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Función para calcular tiempo transcurrido
function getElapsedTime(startTime) {
    const start = new Date(startTime);
    const now = new Date();
    const diff = now - start;
    
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

// Función para mostrar mensajes de error
function showError(message, container = null) {
    const alert = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    if (container) {
        container.innerHTML = alert;
    } else {
        // Mostrar en la parte superior de la página
        const alertContainer = document.createElement('div');
        alertContainer.className = 'container mt-3';
        alertContainer.innerHTML = alert;
        document.querySelector('main').prepend(alertContainer);
        
        // Auto-dismiss después de 5 segundos
        setTimeout(() => {
            alertContainer.remove();
        }, 5000);
    }
}

// Función para mostrar mensajes de éxito
function showSuccess(message) {
    const alert = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const alertContainer = document.createElement('div');
    alertContainer.className = 'container mt-3';
    alertContainer.innerHTML = alert;
    document.querySelector('main').prepend(alertContainer);
    
    setTimeout(() => {
        alertContainer.remove();
    }, 3000);
}

// Función para confirmar acciones
function confirmAction(message) {
    return confirm(message);
}

// Manejador de errores global para Axios
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response) {
            // El servidor respondió con un código de error
            const message = error.response.data.error || 'Error en el servidor';
            console.error('Error de servidor:', message);
        } else if (error.request) {
            // La petición fue hecha pero no hubo respuesta
            console.error('No se recibió respuesta del servidor');
            showError('No se pudo conectar con el servidor');
        } else {
            // Algo pasó al configurar la petición
            console.error('Error:', error.message);
        }
        return Promise.reject(error);
    }
);

// Función para crear spinner de carga
function createSpinner() {
    return `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `;
}

// Función para crear mensaje de "sin datos"
function createEmptyMessage(message = 'No hay datos disponibles') {
    return `
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i> ${message}
        </div>
    `;
}

// Función para validar formularios
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    return form.checkValidity();
}

// Función para limpiar formularios
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
    }
}

// Función para obtener badge de estado
function getStatusBadge(status) {
    const badges = {
        'en_progreso': '<span class="badge bg-info">En Progreso</span>',
        'completada': '<span class="badge bg-success">Completada</span>',
        'pausada': '<span class="badge bg-warning text-dark">Pausada</span>'
    };
    
    return badges[status] || '<span class="badge bg-secondary">Desconocido</span>';
}

// Función para activar tooltips de Bootstrap
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Inicializar componentes de Bootstrap al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    
    // Auto-dismiss de alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Prevenir el envío de formularios con Enter (excepto en textareas)
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
        const form = e.target.closest('form');
        if (form && !e.target.classList.contains('allow-enter')) {
            e.preventDefault();
        }
    }
});

// Funciones de utilidad para localStorage
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error guardando en localStorage:', e);
        }
    },
    
    get: (key) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('Error leyendo de localStorage:', e);
            return null;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Error eliminando de localStorage:', e);
        }
    }
};

// Exportar funciones globales
window.TaskManager = {
    formatDate,
    formatDateTime,
    formatTime,
    getElapsedTime,
    showError,
    showSuccess,
    confirmAction,
    createSpinner,
    createEmptyMessage,
    validateForm,
    clearForm,
    getStatusBadge,
    storage
};