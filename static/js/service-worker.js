// Service Worker para notificaciones push en segundo plano
const CACHE_NAME = 'optica-dashboard-v1';

// Instalación del Service Worker
self.addEventListener('install', (event) => {
    console.log('[ServiceWorker] Instalado');
    self.skipWaiting();
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
    console.log('[ServiceWorker] Activado');
    event.waitUntil(self.clients.claim());
});

// Escuchar mensajes desde la página principal
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'NEW_APPOINTMENT') {
        const { patient_name, appointment_date, appointment_time } = event.data;
        
        // Mostrar notificación
        self.registration.showNotification('Nueva Cita Agendada 🔔', {
            body: `${patient_name} - ${appointment_date} a las ${appointment_time}`,
            icon: '/static/icons/appointment-icon.png',
            badge: '/static/icons/badge-icon.png',
            vibrate: [200, 100, 200],
            tag: 'new-appointment',
            requireInteraction: true,
            actions: [
                { action: 'view', title: 'Ver Cita' },
                { action: 'dismiss', title: 'Cerrar' }
            ]
        });
    }
});

// Manejar clics en las notificaciones
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    if (event.action === 'view') {
        // Abrir dashboard en la sección de citas
        event.waitUntil(
            clients.openWindow('/dashboard/appointments/')
        );
    }
});

// Fetch event (opcional, para cache)
self.addEventListener('fetch', (event) => {
    // Dejar pasar todas las peticiones sin cachear por ahora
    event.respondWith(fetch(event.request));
});
