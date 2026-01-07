# Sistema de Promociones con Envío Controlado

## 🎯 Problema Resuelto

**Necesidad:** Enviar promociones por WhatsApp a todos los clientes sin que WhatsApp bloquee el número.

**Solución:** Sistema inteligente que envía gradualmente, respetando límites seguros.

---

## 📊 Cómo Funciona el Sistema de No Repetición

### Base de Datos

Cada paciente recibe UN mensaje por campaña con estos estados:

```
┌─────────────────────────────────────┐
│ PromotionMessage                    │
├─────────────────────────────────────┤
│ id: 1                              │
│ patient: "Daniel Osorio"           │
│ phone: "3009787566"                │
│ status: "pending" ← HOY           │
│ sent_at: null                      │
└─────────────────────────────────────┘

Después de enviar:

┌─────────────────────────────────────┐
│ id: 1                              │
│ patient: "Daniel Osorio"           │
│ phone: "3009787566"                │
│ status: "sent" ← MARCADO          │
│ sent_at: 2026-01-03 10:15:00      │
└─────────────────────────────────────┘
```

### Estados Posibles

- **`pending`** = Esperando ser enviado
- **`sent`** = Ya enviado (NO SE VOLVERÁ A ENVIAR)
- **`failed`** = Falló el envío (se puede reintentar)
- **`skipped`** = Omitido intencionalmente

---

## 📅 Flujo Día por Día

### **DÍA 1 - Viernes 3 Enero 2026**

```
Base de datos: 100 pacientes
Límite diario: 20 mensajes

ESTADO INICIAL:
├── Pendientes: 100
├── Enviados: 0
└── Fallidos: 0

EJECUCIÓN:
10:00 AM - Se ejecuta: python manage.py process_campaigns

QUERY QUE SE EJECUTA:
SELECT * FROM promotion_messages 
WHERE campaign_id = 1 
AND status = 'pending'  ← Solo los que NO han sido enviados
ORDER BY created_at
LIMIT 20;

RESULTADO:
├── Paciente 1: Daniel Osorio → ✅ Enviado (status = 'sent')
├── Paciente 2: María García → ✅ Enviado (status = 'sent')
├── Paciente 3: Juan Pérez → ✅ Enviado (status = 'sent')
├── ... (17 más)
└── Paciente 20: Ana López → ✅ Enviado (status = 'sent')

ESTADO FINAL:
├── Pendientes: 80
├── Enviados: 20 ← Marcados como 'sent'
└── Fallidos: 0
```

---

### **DÍA 2 - Lunes 6 Enero 2026**
(No se envía en fin de semana)

```
ESTADO INICIAL:
├── Pendientes: 80
├── Enviados: 20
└── Fallidos: 0

EJECUCIÓN:
10:00 AM - Se ejecuta: python manage.py process_campaigns

QUERY QUE SE EJECUTA:
SELECT * FROM promotion_messages 
WHERE campaign_id = 1 
AND status = 'pending'  ← Los 20 del día 1 YA NO APARECEN
ORDER BY created_at
LIMIT 20;

RESULTADO:
├── Paciente 21: Carlos Ruiz → ✅ Enviado
├── Paciente 22: Laura Silva → ✅ Enviado
├── ... (18 más)
└── Paciente 40: Pedro Díaz → ✅ Enviado

ESTADO FINAL:
├── Pendientes: 60
├── Enviados: 40
└── Fallidos: 0
```

---

### **DÍA 3 - Martes 7 Enero 2026**

```
ESTADO INICIAL:
├── Pendientes: 60
├── Enviados: 40
└── Fallidos: 0

QUERY:
SELECT * FROM promotion_messages 
WHERE status = 'pending'  ← Solo quedan 60
ORDER BY created_at
LIMIT 20;

RESULTADO:
20 mensajes más enviados (41-60)

ESTADO FINAL:
├── Pendientes: 40
├── Enviados: 60
└── Fallidos: 0
```

---

### **Continúa hasta...**

### **DÍA 5 - Jueves 9 Enero 2026**

```
ESTADO INICIAL:
├── Pendientes: 20 ← Últimos
├── Enviados: 80
└── Fallidos: 0

QUERY:
SELECT * FROM promotion_messages 
WHERE status = 'pending'
ORDER BY created_at
LIMIT 20;

RESULTADO:
20 mensajes finales enviados (81-100)

ESTADO FINAL:
├── Pendientes: 0 ← ¡COMPLETADO!
├── Enviados: 100
└── Fallidos: 0

🎉 CAMPAÑA COMPLETADA
```

---

## 🔒 Garantía de No Repetición

### Código que lo Asegura

```python
# 1. Al crear la campaña
for patient in recipients:
    PromotionMessage.objects.create(
        campaign=campaign,
        patient=patient,  # UNA VEZ por paciente
        phone_number=patient.phone_number,
        status='pending'
    )

# 2. Al enviar
pending_messages = PromotionMessage.objects.filter(
    campaign=self.campaign,
    status='pending'  # ← SOLO los que NO se han enviado
).order_by('created_at')[:20]

# 3. Al marcar como enviado
message_obj.status = 'sent'
message_obj.sent_at = timezone.now()
message_obj.save()

# 4. Al siguiente día
# La query del paso 2 se repite
# Los mensajes con status='sent' YA NO aparecen
# Solo quedan los 'pending'
```

### Constraints de Base de Datos

```python
class Meta:
    indexes = [
        models.Index(fields=['campaign', 'status']),  # Búsqueda rápida
    ]
```

---

## 📊 Monitoreo en Tiempo Real

### Dashboard

```
http://localhost:8001/dashboard/promociones/campanas/

┌─────────────────────────────────────────┐
│ Campaña: Navidad 2026                  │
├─────────────────────────────────────────┤
│ Total: 100 pacientes                   │
│ ✅ Enviados: 40 (40%)                  │
│ ⏳ Pendientes: 60 (60%)                │
│ ❌ Fallidos: 0                         │
│                                         │
│ [████████████░░░░░░░░░░░░] 40%        │
│                                         │
│ Estado: En Progreso                    │
│ Próximo envío: Mañana 10:00 AM         │
└─────────────────────────────────────────┘
```

### Verificar en Python

```python
from apps.promotions.models import PromotionCampaign

campaign = PromotionCampaign.objects.get(id=1)
campaign.update_stats()

print(f"Enviados: {campaign.messages_sent}")
print(f"Pendientes: {campaign.messages_pending}")
print(f"Fallidos: {campaign.messages_failed}")

# Ver quiénes ya recibieron
enviados = campaign.messages.filter(status='sent')
for msg in enviados:
    print(f"✅ {msg.patient.full_name} - {msg.sent_at}")

# Ver quiénes faltan
pendientes = campaign.messages.filter(status='pending')
for msg in pendientes:
    print(f"⏳ {msg.patient.full_name}")
```

---

## ⚙️ Configuración de Automatización

### Windows Task Scheduler

1. **Abrir Programador de Tareas**
   - Win + R → `taskschd.msc`

2. **Crear Tarea Básica**
   - Nombre: `Envío Promociones OpticaApp`
   - Descripción: `Envía 20 mensajes diarios de campaña`

3. **Desencadenador**
   - Diario
   - Hora: 10:00 AM
   - Repetir: Todos los días

4. **Acción**
   - Programa: `python`
   - Argumentos: `manage.py process_campaigns`
   - Iniciar en: `D:\ESCRITORIO\OpticaApp`

5. **Condiciones**
   - Solo ejecutar si el equipo está encendido
   - Despertar equipo para ejecutar (opcional)

### Alternativa: Ejecutar Manualmente

```powershell
# Cada día a las 10 AM ejecutar:
cd D:\ESCRITORIO\OpticaApp
python manage.py process_campaigns
```

---

## 🔐 Límites de Seguridad

### Configuración por Defecto

```python
# En PromotionCampaign
daily_limit = 20  # Máximo 20 mensajes/día
delay_seconds = 10  # 10 segundos entre cada uno
send_hour_start = 9  # Desde las 9 AM
send_hour_end = 19  # Hasta las 7 PM
```

### Qué Previene el Bloqueo

✅ **Límite diario:** No más de 20-30 mensajes  
✅ **Delay entre mensajes:** 10 segundos (parece humano)  
✅ **Horario laboral:** Solo 9 AM - 7 PM  
✅ **No fines de semana:** Lunes a Viernes solamente  
✅ **Personalización:** Cada mensaje tiene el nombre del paciente  
✅ **Variación:** Pequeñas diferencias en cada mensaje  

---

## 📱 Ejemplo de Mensaje Personalizado

### Template Original

```
🎄 ¡Hola {name}!

👓 Tenemos una promoción especial de NAVIDAD para ti:

💰 30% de descuento en Monturas
🎁 Código: NAVIDAD2026

📅 Válido hasta el 02/02/2026

¡Visítanos y aprovecha esta oferta!

- CompuEasys
```

### Mensajes Reales Enviados

**Paciente 1: Daniel Osorio**
```
🎄 ¡Hola Daniel!

👓 Tenemos una promoción especial de NAVIDAD para ti:

💰 30% de descuento en Monturas
🎁 Código: NAVIDAD2026

📅 Válido hasta el 02/02/2026

¡Visítanos y aprovecha esta oferta!

- CompuEasys ✨
```

**Paciente 2: María García**
```
🎄 ¡Hola María!

👓 Tenemos una promoción especial de NAVIDAD para ti:

💰 30% de descuento en Monturas
🎁 Código: NAVIDAD2026

📅 Válido hasta el 02/02/2026

¡Visítanos y aprovecha esta oferta!

- CompuEasys 😊
```

*Nota: El emoji final cambia aleatoriamente en cada mensaje*

---

## 🚀 Guía Rápida de Uso

### 1. Primera Vez

```bash
# Ejecutar demo
python test_promotions_demo.py

# Esto crea:
# - Promoción NAVIDAD2026 (30% OFF en monturas)
# - Campaña con todos los pacientes
# - Mensajes individuales en estado 'pending'
```

### 2. Iniciar Envío

```bash
# Iniciar campaña
python iniciar_campana.py

# Te mostrará:
# - Cuántos pacientes hay
# - Quiénes recibirán hoy
# - Estado de WhatsApp
# - Preguntará si iniciar
```

### 3. Automatizar

```bash
# Configurar tarea diaria en Windows
# O ejecutar manualmente cada día:
python manage.py process_campaigns
```

### 4. Monitorear

```
# En el navegador:
http://localhost:8001/dashboard/promociones/campanas/

# Ver progreso en tiempo real
# Pausar/reanudar si es necesario
```

---

## ❓ Preguntas Frecuentes

### ¿Se puede repetir a la misma persona?

**NO.** Una vez que un mensaje se marca como 'sent', NUNCA se vuelve a seleccionar en futuras ejecuciones.

### ¿Qué pasa si falla un mensaje?

Se marca como 'failed' y se puede reintentar hasta 3 veces. No afecta a los demás.

### ¿Puedo cambiar el límite de 20 mensajes/día?

Sí, pero **NO recomendado** subir de 30 para evitar bloqueo.

### ¿Qué pasa si WhatsApp se desconecta?

El sistema detecta la desconexión y no envía. Los mensajes quedan 'pending' para el próximo día.

### ¿Se puede pausar la campaña?

Sí, desde el dashboard o cambiando el status a 'paused'.

### ¿Los mensajes se envían en fin de semana?

NO. El sistema solo envía de Lunes a Viernes.

---

## ✅ Resumen

- ✅ Un mensaje por paciente por campaña
- ✅ Se marca como 'sent' después de enviar
- ✅ NUNCA se repite al mismo paciente
- ✅ Continúa automáticamente día tras día
- ✅ 20 mensajes diarios máximo
- ✅ 10 segundos entre cada mensaje
- ✅ Solo en horario laboral
- ✅ Hasta completar TODA la base de datos

---

**Fecha de Creación:** 3 de Enero de 2026  
**Sistema:** OpticaApp - Módulo de Promociones  
**Estado:** ✅ Producción
