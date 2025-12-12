// Sistema de notificaciones push en tiempo real
class DashboardNotifications {
    constructor() {
        this.pollingInterval = 30000; // 30 segundos
        this.intervalId = null;
        this.serviceWorkerRegistration = null;
        this.notificationSound = null;
        this.isInitialized = false;
        this.audioContext = null;
    }

    initSound() {
        // Intentar cargar archivo de sonido
        this.notificationSound = new Audio('/static/sounds/notification.mp3');
        this.notificationSound.volume = 0.7;
        
        // Configurar fallback si no se puede cargar el archivo
        this.notificationSound.addEventListener('error', () => {
            console.warn('[Notifications] No se pudo cargar el archivo de sonido, usando beep generado');
            this.notificationSound = null;
        });
    }

    playNotificationSound() {
        // Intentar reproducir el archivo de sonido
        if (this.notificationSound) {
            this.notificationSound.play().catch(error => {
                console.warn('[Notifications] Error reproduciendo archivo de sonido, usando beep:', error);
                this.playBeep();
            });
        } else {
            // Fallback: generar beep con Web Audio API
            this.playBeep();
        }
    }

    playBeep() {
        try {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            // Primer tono
            const oscillator1 = this.audioContext.createOscillator();
            const gainNode1 = this.audioContext.createGain();
            oscillator1.connect(gainNode1);
            gainNode1.connect(this.audioContext.destination);
            oscillator1.frequency.value = 800;
            oscillator1.type = 'sine';
            gainNode1.gain.setValueAtTime(0.3, this.audioContext.currentTime);
            oscillator1.start(this.audioContext.currentTime);
            oscillator1.stop(this.audioContext.currentTime + 0.15);
            
            // Segundo tono
            setTimeout(() => {
                const oscillator2 = this.audioContext.createOscillator();
                const gainNode2 = this.audioContext.createGain();
                oscillator2.connect(gainNode2);
                gainNode2.connect(this.audioContext.destination);
                oscillator2.frequency.value = 600;
                oscillator2.type = 'sine';
                gainNode2.gain.setValueAtTime(0.3, this.audioContext.currentTime);
                oscillator2.start(this.audioContext.currentTime);
                oscillator2.stop(this.audioContext.currentTime + 0.15);
            }, 100);
        } catch (error) {
            console.error('[Notifications] Error generando beep:', error);
        }
    }

    async init() {
        if (this.isInitialized) return;
        
        console.log('[Notifications] Inicializando sistema de notificaciones...');
        
        // Sistema de sonido con fallback a beep generado
        this.initSound();
        
        // Registrar Service Worker
        await this.registerServiceWorker();
        
        // Solicitar permiso para notificaciones
        await this.requestNotificationPermission();
        
        // Iniciar polling
        this.startPolling();
        
        this.isInitialized = true;
        console.log('[Notifications] Sistema inicializado correctamente');
    }

    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
                this.serviceWorkerRegistration = registration;
                console.log('[ServiceWorker] Registrado correctamente');
            } catch (error) {
                console.error('[ServiceWorker] Error al registrar:', error);
            }
        }
    }

    async requestNotificationPermission() {
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                console.log('[Notifications] Permiso:', permission);
            }
        }
    }

    startPolling() {
        // Verificar inmediatamente
        this.checkNewAppointments();
        
        // Luego cada 30 segundos
        this.intervalId = setInterval(() => {
            this.checkNewAppointments();
        }, this.pollingInterval);
        
        console.log('[Notifications] Polling iniciado (cada 30 segundos)');
    }

    stopPolling() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
            console.log('[Notifications] Polling detenido');
        }
    }

    async checkNewAppointments() {
        try {
            const response = await fetch('/dashboard/api/notifications/new-appointments/');
            const data = await response.json();
            
            if (data.success && data.count > 0) {
                console.log(`[Notifications] ${data.count} nueva(s) cita(s) encontrada(s)`);
                
                // Procesar cada notificación
                for (const notification of data.notifications) {
                    await this.showNotification(notification);
                }
            }
        } catch (error) {
            console.error('[Notifications] Error al verificar citas:', error);
        }
    }

    async showNotification(notification) {
        const { patient_name, appointment_date, appointment_time, doctor_name } = notification;
        
        // Reproducir sonido (con fallback automático a beep)
        this.playNotificationSound();
        
        // Mostrar notificación del navegador
        if ('Notification' in window && Notification.permission === 'granted') {
            if (this.serviceWorkerRegistration) {
                // Enviar mensaje al Service Worker
                this.serviceWorkerRegistration.active.postMessage({
                    type: 'NEW_APPOINTMENT',
                    patient_name,
                    appointment_date,
                    appointment_time,
                    doctor_name
                });
            } else {
                // Fallback: notificación directa
                const notif = new Notification('Nueva Cita Agendada 🔔', {
                    body: `${patient_name}\n${appointment_date} a las ${appointment_time}\nDoctor: ${doctor_name}`,
                    icon: '/static/icons/appointment-icon.png',
                    vibrate: [200, 100, 200],
                    tag: 'new-appointment'
                });
                
                notif.onclick = () => {
                    window.focus();
                    window.location.href = '/dashboard/appointments/';
                };
            }
        }
        
        // Mostrar alerta visual en la página
        this.showInPageAlert(notification);
    }

    showInPageAlert(notification) {
        const { patient_name, appointment_date, appointment_time, doctor_name, appointment_id } = notification;
        
        // Crear elemento de alerta
        const alert = document.createElement('div');
        alert.className = 'fixed top-4 right-4 z-50 bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-4 rounded-lg shadow-2xl max-w-md animate-slide-in';
        alert.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                </div>
                <div class="ml-3 flex-1">
                    <h3 class="text-sm font-bold mb-1">🔔 Nueva Cita Agendada</h3>
                    <p class="text-sm font-semibold">${patient_name}</p>
                    <p class="text-xs mt-1 opacity-90">${appointment_date} a las ${appointment_time}</p>
                    <p class="text-xs opacity-90">Doctor: ${doctor_name}</p>
                    <div class="mt-3 flex gap-2">
                        <a href="/dashboard/appointments/${appointment_id}/" 
                           class="text-xs bg-white text-blue-600 px-3 py-1 rounded font-semibold hover:bg-blue-50 transition">
                            Ver Cita
                        </a>
                        <button onclick="this.closest('.animate-slide-in').remove()" 
                                class="text-xs bg-blue-700 text-white px-3 py-1 rounded hover:bg-blue-800 transition">
                            Cerrar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(alert);
        
        // Auto-remover después de 10 segundos
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(400px)';
            setTimeout(() => alert.remove(), 300);
        }, 10000);
    }

    destroy() {
        this.stopPolling();
        this.isInitialized = false;
    }
}

// Instancia global
const dashboardNotifications = new DashboardNotifications();

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si estamos en el dashboard
    if (window.location.pathname.includes('/dashboard')) {
        dashboardNotifications.init();
    }
});

// Limpiar al salir
window.addEventListener('beforeunload', () => {
    dashboardNotifications.destroy();
});

// Agregar estilos para la animación
const style = document.createElement('style');
style.textContent = `
    @keyframes slide-in {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    .animate-slide-in {
        animation: slide-in 0.3s ease-out;
        transition: all 0.3s ease-out;
    }
`;
document.head.appendChild(style);
