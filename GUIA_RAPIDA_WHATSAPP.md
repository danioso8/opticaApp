# 🚀 Guía Rápida: Activar WhatsApp en 5 minutos

## Para usuarios sin experiencia técnica

### ¿Qué necesitas?
- ✅ Un número de WhatsApp disponible
- ✅ Tu teléfono con WhatsApp instalado
- ✅ 5 minutos de tu tiempo

---

## 📱 Pasos Simples

### 1️⃣ Abre PowerShell
- Presiona las teclas `Windows` + `R` al mismo tiempo
- Escribe: `powershell`
- Presiona `Enter`

### 2️⃣ Navega a la carpeta
Copia y pega este comando (clic derecho para pegar):
```
cd D:\ESCRITORIO\OpticaApp\whatsapp-bot
```
Presiona `Enter`

### 3️⃣ Instala (solo la primera vez)
Copia y pega:
```
npm install
```
Presiona `Enter` y espera (puede tardar 1-2 minutos)

### 4️⃣ Inicia el servidor
Copia y pega:
```
npm start
```
Presiona `Enter`

Verás un mensaje:
```
🚀 Servidor WhatsApp Bot iniciado
   http://localhost:3000
```

### 5️⃣ Conecta tu WhatsApp
1. Abre tu navegador
2. Ve a: `http://localhost:3000/qr`
3. Verás un código QR grande

**En tu teléfono:**
1. Abre WhatsApp
2. Toca los 3 puntos (⋮) arriba a la derecha
3. Toca "Dispositivos vinculados"
4. Toca "Vincular un dispositivo"
5. Escanea el código QR que está en tu computadora

### ✅ ¡Listo!
El indicador en el dashboard cambiará a verde 🟢

---

## ❓ Problemas Comunes

### "npm no se reconoce..."
**Solución:** Instala Node.js desde https://nodejs.org/

### El QR no aparece
**Solución:** Espera 10 segundos y recarga la página

### Ya escaneé el QR pero sigue en rojo
**Solución:** En el dashboard, haz clic en "Actualizar"

---

## 💡 Consejos

- ✅ **No cierres** la ventana de PowerShell mientras uses el sistema
- ✅ Si reinicias la computadora, repite desde el paso 4️⃣
- ✅ El número de WhatsApp debe estar activo (no bloqueado)

---

## 🎯 ¿Funcionó?

Prueba enviando un mensaje de prueba:
1. En el dashboard, haz clic en "Probar"
2. Ingresa tu número: `3001234567`
3. Haz clic en "Enviar"
4. ¡Deberías recibir el mensaje!

---

## 🆘 ¿Necesitas ayuda?

Si algo no funciona:
1. Haz clic en "Actualizar" en el dashboard
2. Lee el mensaje de error
3. Revisa que todos los pasos estén completos
4. Reinicia desde el paso 2️⃣

---

**¡Eso es todo!** Ahora cada vez que alguien agenda una cita, recibirá automáticamente un mensaje de WhatsApp 🎉
