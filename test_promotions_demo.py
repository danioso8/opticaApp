"""
Script de Prueba - Sistema de Promociones
Demuestra cómo crear promociones y campañas seguras
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.promotions.models import Promotion, PromotionCampaign
from apps.promotions.services import create_campaign_messages, start_campaign

print("=" * 70)
print("SISTEMA DE PROMOCIONES - DEMO")
print("=" * 70)

# 1. Obtener organización
org = Organization.objects.get(slug='compueasys')
print(f"\n✅ Organización: {org.name} (ID: {org.id})")

# 2. Crear promoción
print("\n📝 Creando promoción de Navidad...")
promotion, created = Promotion.objects.get_or_create(
    organization=org,
    code='NAVIDAD2026',
    defaults={
        'name': 'Promoción de Navidad 2026',
        'description': 'Descuento especial en monturas durante esta temporada navideña',
        'discount_percentage': 30,
        'category': 'frames',
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=30),
        'status': 'active',
    }
)

if created:
    print(f"✅ Promoción creada: {promotion.code} - {promotion.discount_percentage}% OFF")
else:
    print(f"ℹ️  Promoción ya existe: {promotion.code}")

# 3. Crear campaña
print("\n📢 Creando campaña de WhatsApp...")

message_template = """🎄 ¡Hola {name}!

{category_emoji} Tenemos una promoción especial de NAVIDAD para ti:

💰 {discount}% de descuento en {category}
🎁 Código: {code}

📅 Válido hasta el {end_date}

¡Visítanos y aprovecha esta oferta!

- {organization} ✨"""

campaign, created = PromotionCampaign.objects.get_or_create(
    organization=org,
    promotion=promotion,
    name='Campaña Navidad 2026',
    defaults={
        'message_template': message_template,
        'recipient_filter': 'all',  # Todos los clientes
        'daily_limit': 20,  # Solo 20 mensajes por día (SEGURO)
        'delay_seconds': 10,  # 10 segundos entre mensajes
        'send_hour_start': 9,  # Desde las 9 AM
        'send_hour_end': 19,  # Hasta las 7 PM
        'status': 'draft',
    }
)

if created:
    print(f"✅ Campaña creada: {campaign.name}")
else:
    print(f"ℹ️  Campaña ya existe: {campaign.name}")

# 4. Mostrar destinatarios potenciales
print("\n👥 Analizando destinatarios...")
recipients = campaign.get_recipients()
print(f"   Total de clientes con teléfono: {recipients.count()}")

# 5. Crear mensajes (sin enviar todavía)
if campaign.messages.count() == 0:
    print("\n📝 Creando mensajes individuales...")
    count = create_campaign_messages(campaign)
    print(f"✅ {count} mensajes creados y listos para enviar")
else:
    print(f"\nℹ️  Ya existen {campaign.messages.count()} mensajes en la campaña")

# 6. Mostrar estadísticas
print("\n📊 ESTADÍSTICAS DE LA CAMPAÑA:")
print(f"   Total destinatarios: {campaign.total_recipients}")
print(f"   Mensajes pendientes: {campaign.messages_pending}")
print(f"   Mensajes enviados: {campaign.messages_sent}")
print(f"   Mensajes fallidos: {campaign.messages_failed}")

# 7. Instrucciones de uso
print("\n" + "=" * 70)
print("📖 CÓMO USAR EL SISTEMA:")
print("=" * 70)

print("""
1. CREAR PROMOCIÓN:
   - Ve a http://localhost:8001/dashboard/promociones/
   - Click en "Nueva Promoción"
   - Ingresa código, descuento, fechas
   
2. CREAR CAMPAÑA:
   - Ve a http://localhost:8001/dashboard/promociones/campanas/crear/
   - Selecciona la promoción
   - Personaliza el mensaje
   - Configura límites de envío (20 mensajes/día recomendado)
   
3. INICIAR CAMPAÑA:
   - La campaña enviará mensajes gradualmente
   - Respeta horario laboral (9 AM - 7 PM)
   - 10 segundos de delay entre mensajes
   - Máximo 20 mensajes por día
   
4. MONITOREAR:
   - Ver progreso en tiempo real
   - Revisar mensajes enviados/fallidos
   - Pausar/reanudar cuando quieras
""")

print("\n⚠️  LÍMITES DE SEGURIDAD PARA EVITAR BLOQUEO:")
print("=" * 70)
print("""
✅ Máximo 20-30 mensajes por día
✅ Delay de 8-15 segundos entre mensajes
✅ Solo en horario laboral (9 AM - 7 PM)
✅ No enviar fines de semana
✅ Cada mensaje ligeramente diferente (personalización)
✅ Solo a clientes con teléfono registrado

❌ NO enviar más de 50 mensajes/día
❌ NO enviar fuera de horario
❌ NO enviar mensajes idénticos
❌ NO enviar a números desconocidos
""")

print("\n🚀 EJECUTAR CAMPAÑA:")
print("=" * 70)
print("""
# Opción 1: Desde Python
from apps.promotions.services import start_campaign
start_campaign(campaign_id)

# Opción 2: Desde interfaz web
http://localhost:8001/dashboard/promociones/campanas/

# Opción 3: Automático con cron job (recomendado)
# Agregar a Windows Task Scheduler:
python manage.py process_campaigns  # Ejecutar cada hora
""")

print("\n" + "=" * 70)
print("✅ DEMO COMPLETADA")
print("=" * 70)
