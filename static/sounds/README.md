# Archivo de sonido de notificación

El sonido de notificación debe ser un archivo MP3 llamado `notification.mp3`.

## Opciones para agregar el sonido:

### 1. Usar un generador online (Recomendado):
- https://notificationsounds.com/
- https://pixabay.com/sound-effects/
- https://freesound.org/

### 2. Crear con JavaScript (Temporal):
Si no tienes un archivo de sonido, puedes usar el siguiente código JavaScript como alternativa temporal:

```javascript
// Reemplazar en dashboard-notifications.js línea 11-12:
// this.notificationSound = new Audio('/static/sounds/notification.mp3');

// Por esto (genera un beep simple):
this.notificationSound = null;

// Y en la función showNotification, reemplazar:
// await this.notificationSound.play();

// Por esto:
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
const oscillator = audioContext.createOscillator();
const gainNode = audioContext.createGain();
oscillator.connect(gainNode);
gainNode.connect(audioContext.destination);
oscillator.frequency.value = 800;
oscillator.type = 'sine';
gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
oscillator.start(audioContext.currentTime);
oscillator.stop(audioContext.currentTime + 0.2);
setTimeout(() => {
    const oscillator2 = audioContext.createOscillator();
    oscillator2.connect(gainNode);
    oscillator2.frequency.value = 600;
    oscillator2.type = 'sine';
    oscillator2.start(audioContext.currentTime);
    oscillator2.stop(audioContext.currentTime + 0.2);
}, 100);
```

### 3. Deshabilitar sonido:
Simplemente comenta las líneas 93-97 en `dashboard-notifications.js`:

```javascript
// Reproducir sonido
// try {
//     await this.notificationSound.play();
// } catch (error) {
//     console.warn('[Notifications] No se pudo reproducir el sonido:', error);
// }
```

## Archivo recomendado:
Descarga un sonido de notificación corto (1-2 segundos) y guárdalo como:
`D:\ESCRITORIO\OpticaApp\static\sounds\notification.mp3`
