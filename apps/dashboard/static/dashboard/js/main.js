// Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    
    // Inicializar toggle del sistema
    initSystemToggle();
});

// Toggle Sistema Abierto/Cerrado
function initSystemToggle() {
    const toggleButton = document.getElementById('system-toggle');
    if (!toggleButton) return;
    
    // Obtener estado inicial del sistema
    fetchSystemStatus();
    
    // No agregar listener aquí, el onclick ya está en el HTML
}

function toggleSystem() {
    const csrftoken = getCookie('csrftoken');
    
    fetch('/toggle-system/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateToggleUI(data.is_open);
            showNotification(data.message, 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al cambiar el estado del sistema', 'error');
    });
}

function updateToggleUI(isOpen) {
    const toggleBg = document.getElementById('toggle-bg');
    const toggleDot = document.getElementById('toggle-dot');
    const systemStatus = document.getElementById('system-status');
    
    if (isOpen) {
        toggleBg.classList.remove('bg-gray-300');
        toggleBg.classList.add('bg-green-500');
        toggleDot.classList.add('translate-x-5');
        systemStatus.textContent = 'Abierto';
        systemStatus.classList.add('text-green-600');
        systemStatus.classList.remove('text-red-600');
    } else {
        toggleBg.classList.remove('bg-green-500');
        toggleBg.classList.add('bg-gray-300');
        toggleDot.classList.remove('translate-x-5');
        systemStatus.textContent = 'Cerrado';
        systemStatus.classList.add('text-red-600');
        systemStatus.classList.remove('text-green-600');
    }
}

function fetchSystemStatus() {
    fetch('/api/configuration/')
        .then(response => response.json())
        .then(data => {
            updateToggleUI(data.is_open);
        })
        .catch(error => console.error('Error fetching system status:', error));
}

// Get CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show Notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-4 rounded-lg shadow-lg z-50 transition-all ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        type === 'warning' ? 'bg-yellow-500' :
        'bg-blue-500'
    } text-white`;
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${
                type === 'success' ? 'fa-check-circle' :
                type === 'error' ? 'fa-times-circle' :
                type === 'warning' ? 'fa-exclamation-triangle' :
                'fa-info-circle'
            } mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Confirm Dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Auto-save forms
function autoSave(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            console.log('Auto-saving...');
            // Implementar auto-save
        });
    });
}
