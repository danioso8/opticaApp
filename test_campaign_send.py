"""
Script para probar la campaña de promociones sin restricciones de horario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.promotions.models import Promotion, PromotionCampaign, PromotionMessage
from apps.promotions.services import CampaignSender, create_campaign_messages
from apps.organizations.models import Organization
from apps.patients.models import Patient
from django.contrib.auth import get_user_model
from django.utils import timezone
import time

User = get_user_model()

print("=" * 70)
print("🧪 PRUEBA DE CAMPAÑA DE PROMOCIONES")
print("=" * 70)

# Obtener organización
org = Organization.objects.filter(slug='compueasys').first()
if not org:
    print("❌ No se encontró la organización CompuEasys")
    exit()

print(f"\n✅ Organización: {org.name} (ID: {org.id})")

# Obtener usuario
user = User.objects.filter(username='danioso8329').first()
if not user:
    print("❌ No se encontró el usuario danioso8329")
    exit()

print(f"✅ Usuario: {user.username}")

# Obtener promoción más reciente
promotion = Promotion.objects.filter(organization=org).order_by('-created_at').first()
if not promotion:
    print("\n❌ No hay promociones creadas")
    exit()

print(f"\n📢 Promoción encontrada:")
print(f"   Código: {promotion.code}")
print(f"   Descuento: {promotion.discount_percentage}%")
print(f"   Categoría: {promotion.get_category_display()}")

# Contar pacientes con teléfono
patients_with_phone = Patient.objects.filter(
    organization=org,
    phone_number__isnull=False
).exclude(phone_number='').count()

print(f"\n👥 Pacientes con teléfono: {patients_with_phone}")

if patients_with_phone == 0:
    print("❌ No hay pacientes con teléfono para enviar")
    exit()

# Crear campaña de prueba
print("\n🔧 Creando campaña de prueba...")

campaign = PromotionCampaign.objects.create(
    organization=org,
    promotion=promotion,
    name=f"PRUEBA - {promotion.code}",
    message_template=f"""🎉 ¡Hola {{name}}!

{promotion.get_category_display_emoji()} Tenemos una promoción especial para ti:

💰 {promotion.discount_percentage}% de descuento en {promotion.get_category_display()}
🎁 Código: {promotion.code}

📅 Válido hasta el {promotion.end_date.strftime('%d/%m/%Y')}

¡Visítanos y aprovecha esta oferta!

- {{organization}}""",
    recipient_filter='with_phone',
    daily_limit=20,
    delay_seconds=5,  # Reducir delay para prueba
    send_hour_start=0,  # 🔓 SIN RESTRICCIÓN DE HORA
    send_hour_end=23,    # 🔓 PERMITIR TODO EL DÍA
    status='draft',
    created_by=user
)

print(f"✅ Campaña creada: {campaign.name}")

# Crear mensajes
print("\n📝 Creando mensajes para pacientes...")
recipients_count = create_campaign_messages(campaign)
print(f"✅ {recipients_count} mensajes creados")

# Mostrar destinatarios
print("\n📋 Destinatarios:")
messages = PromotionMessage.objects.filter(campaign=campaign)
for i, msg in enumerate(messages, 1):
    print(f"   {i}. {msg.patient.full_name} - {msg.phone_number}")

# Cambiar estado a in_progress
campaign.status = 'in_progress'
campaign.save()

print("\n" + "=" * 70)
print("🚀 INICIANDO ENVÍO DE MENSAJES (SIN RESTRICCIONES DE HORARIO)")
print("=" * 70)

# Crear sender
sender = CampaignSender(campaign)

# Verificar conexión WhatsApp
print("\n🔍 Verificando conexión de WhatsApp...")
if sender.check_whatsapp_connection():
    print("✅ WhatsApp conectado y listo")
else:
    print("❌ WhatsApp NO está conectado")
    print("⚠️  Asegúrate de que el servidor de WhatsApp esté corriendo:")
    print("   cd whatsapp-server && node server.js")
    exit()

# ENVIAR MENSAJES (FORZADO - sin verificaciones)
print(f"\n📤 Enviando mensajes a {recipients_count} destinatarios...")
print(f"   Delay: {campaign.delay_seconds} segundos entre mensajes")
print()

# Obtener mensajes pendientes
pending_messages = PromotionMessage.objects.filter(
    campaign=campaign,
    status='pending'
).order_by('created_at')

print(f"⚡ MODO PRUEBA: Omitiendo restricciones de horario")
print()

sent_count = 0
for message_obj in pending_messages:
    try:
        # Personalizar mensaje
        message_text = sender.personalize_message(message_obj)
        
        print(f"📱 Enviando a {message_obj.patient.full_name} ({message_obj.phone_number})...")
        
        # Enviar por WhatsApp
        success = sender.client.send_message(
            sender.org_id,
            message_obj.phone_number,
            message_text
        )
        
        if success:
            message_obj.status = 'sent'
            message_obj.sent_at = timezone.now()
            message_obj.send_attempts += 1
            message_obj.save()
            sent_count += 1
            print(f"   ✅ Enviado exitosamente")
        else:
            message_obj.status = 'failed'
            message_obj.send_attempts += 1
            message_obj.save()
            print(f"   ❌ Falló el envío")
        
        # Delay entre mensajes
        if message_obj != pending_messages.last():
            time.sleep(campaign.delay_seconds)
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        message_obj.status = 'failed'
        message_obj.send_attempts += 1
        message_obj.save()

try:
    
    # Actualizar estadísticas
    
    print("\n" + "=" * 70)
    print(f"✅ ENVÍO COMPLETADO: {sent_count} mensajes enviados")
    print("=" * 70)
    
    # Mostrar estadísticas
    campaign.update_stats()
    
    print(f"\n📊 Estadísticas de la campaña:")
    print(f"   Total destinatarios: {campaign.total_recipients}")
    print(f"   ✅ Enviados: {campaign.messages_sent}")
    print(f"   ⏳ Pendientes: {campaign.messages_pending}")
    print(f"   ❌ Fallidos: {campaign.messages_failed}")
    
    # Mostrar mensajes enviados
    print(f"\n📱 Mensajes enviados:")
    sent_messages = PromotionMessage.objects.filter(campaign=campaign, status='sent')
    for msg in sent_messages:
        print(f"   ✅ {msg.patient.full_name} ({msg.phone_number}) - {msg.sent_at.strftime('%H:%M:%S')}")
    
    # Mostrar mensajes fallidos
    failed_messages = PromotionMessage.objects.filter(campaign=campaign, status='failed')
    if failed_messages.exists():
        print(f"\n❌ Mensajes fallidos:")
        for msg in failed_messages:
            print(f"   ❌ {msg.patient.full_name} ({msg.phone_number})")
    
    print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
    print(f"\n💡 Puedes ver más detalles en:")
    print(f"   http://127.0.0.1:8000/dashboard/promociones/campanas/{campaign.id}/")
    
except Exception as e:
    print(f"\n❌ ERROR durante el envío:")
    print(f"   {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
