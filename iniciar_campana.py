"""
Script para INICIAR campaña de promociones
Envía a 20 pacientes hoy, marca los enviados, mañana envía a otros 20 diferentes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.promotions.models import PromotionCampaign, PromotionMessage
from apps.promotions.services import start_campaign, CampaignSender

print("=" * 70)
print("ENVÍO DE CAMPAÑA - CONTROL INTELIGENTE")
print("=" * 70)

# Obtener organización
org = Organization.objects.get(slug='compueasys')
print(f"\n✅ Organización: {org.name}")

# Buscar campaña activa
campaigns = PromotionCampaign.objects.filter(
    organization=org,
    status__in=['draft', 'in_progress', 'scheduled']
).order_by('-created_at')

if not campaigns.exists():
    print("\n❌ No hay campañas disponibles")
    print("   Primero ejecuta: python test_promotions_demo.py")
    exit(1)

campaign = campaigns.first()
print(f"\n📢 Campaña: {campaign.name}")
print(f"   Promoción: {campaign.promotion.code} - {campaign.promotion.discount_percentage}% OFF")

# Mostrar estado actual
print("\n" + "=" * 70)
print("📊 ESTADO ACTUAL DE LA CAMPAÑA:")
print("=" * 70)

campaign.update_stats()

total = campaign.total_recipients
enviados = campaign.messages_sent
fallidos = campaign.messages_failed
pendientes = campaign.messages_pending

print(f"""
Total de destinatarios: {total}
✅ Enviados: {enviados}
❌ Fallidos: {fallidos}
⏳ Pendientes: {pendientes}
""")

# Calcular progreso
if total > 0:
    progreso = (enviados / total) * 100
    print(f"Progreso: {progreso:.1f}%")
    
    # Barra de progreso visual
    barras = int(progreso / 2)
    barra = "█" * barras + "░" * (50 - barras)
    print(f"[{barra}]")

# Mostrar próximos destinatarios
print("\n" + "=" * 70)
print("👥 PRÓXIMOS DESTINATARIOS (Primeros 20 pendientes):")
print("=" * 70)

proximos = PromotionMessage.objects.filter(
    campaign=campaign,
    status='pending'
).select_related('patient').order_by('created_at')[:20]

if not proximos.exists():
    print("\n✅ ¡Todos los mensajes han sido enviados!")
    print("   La campaña está COMPLETADA")
else:
    print(f"\nSe enviarán a estos {proximos.count()} pacientes:\n")
    for i, msg in enumerate(proximos, 1):
        print(f"  {i}. {msg.patient.full_name} - {msg.phone_number}")

# Verificar estado de WhatsApp
print("\n" + "=" * 70)
print("🔌 VERIFICANDO CONEXIÓN WHATSAPP:")
print("=" * 70)

sender = CampaignSender(campaign)

if sender.check_whatsapp_connection():
    print("✅ WhatsApp está conectado y listo")
else:
    print("❌ WhatsApp NO está conectado")
    print("   Ve a: http://localhost:8001/dashboard/whatsapp-baileys/")
    print("   Escanea el código QR para conectar")
    exit(1)

# Verificar horario
print("\n" + "=" * 70)
print("⏰ VERIFICANDO HORARIO:")
print("=" * 70)

if sender.is_sending_allowed():
    print("✅ Horario permitido para enviar (9 AM - 7 PM, Lunes-Viernes)")
else:
    print("⏸️  Fuera de horario de envío")
    print("   Los mensajes se enviarán en horario laboral (9 AM - 7 PM)")

# Verificar límite diario
print("\n" + "=" * 70)
print("📊 LÍMITE DIARIO:")
print("=" * 70)

enviados_hoy = sender.get_daily_sent_count()
limite = campaign.daily_limit

print(f"Enviados hoy: {enviados_hoy}/{limite}")
print(f"Disponibles: {limite - enviados_hoy}")

if sender.can_send_more_today():
    print("✅ Se pueden enviar más mensajes hoy")
else:
    print("⏸️  Límite diario alcanzado")
    print("   Los mensajes continuarán mañana automáticamente")

# Preguntar si iniciar
print("\n" + "=" * 70)
print("🚀 ¿INICIAR ENVÍO?")
print("=" * 70)

respuesta = input("\n¿Deseas iniciar el envío ahora? (s/n): ").lower()

if respuesta == 's':
    print("\n🚀 Iniciando campaña...")
    print("=" * 70)
    
    # Cambiar estado a in_progress si está en draft
    if campaign.status == 'draft':
        campaign.status = 'in_progress'
        campaign.save()
    
    # Procesar lote
    sent = sender.process_batch()
    
    print(f"\n✅ Lote procesado: {sent} mensajes enviados")
    
    # Actualizar y mostrar nuevo estado
    campaign.update_stats()
    
    print("\n" + "=" * 70)
    print("📊 NUEVO ESTADO:")
    print("=" * 70)
    print(f"""
Enviados totales: {campaign.messages_sent}
Pendientes: {campaign.messages_pending}
Fallidos: {campaign.messages_failed}
""")
    
    if campaign.messages_pending > 0:
        print("\n📅 PRÓXIMO ENVÍO:")
        print("   Los siguientes mensajes se enviarán mañana automáticamente")
        print("   O puedes ejecutar manualmente:")
        print("   python manage.py process_campaigns")
    else:
        print("\n🎉 ¡CAMPAÑA COMPLETADA!")
        print("   Todos los mensajes han sido enviados")

else:
    print("\n⏸️  Envío cancelado")
    print("\nPara iniciar la campaña puedes:")
    print("1. Ejecutar este script nuevamente")
    print("2. Usar: python manage.py process_campaigns")
    print("3. Desde el dashboard web")

print("\n" + "=" * 70)
print("CÓMO FUNCIONA EL SISTEMA:")
print("=" * 70)
print("""
1️⃣  HOY: 
   - Se envían 20 mensajes a los primeros 20 pacientes
   - Se marcan como "enviados" en la base de datos
   - Quedan 10 segundos entre cada mensaje

2️⃣  MAÑANA:
   - El sistema busca los siguientes 20 que NO han recibido
   - Los envía automáticamente (si está programado)
   - Marca esos como "enviados"

3️⃣  CONTINÚA:
   - El proceso se repite día tras día
   - Siempre envía a los que están "pendientes"
   - NUNCA repite a la misma persona
   - Hasta completar TODOS los pacientes

⚙️  CONFIGURACIÓN SEGURA:
   ✅ Máximo 20 mensajes/día (configurable)
   ✅ 10 segundos entre mensajes
   ✅ Solo horario laboral (9 AM - 7 PM)
   ✅ No envía fines de semana
   ✅ Cada mensaje personalizado con el nombre
""")

print("\n" + "=" * 70)
print("📅 AUTOMATIZACIÓN (RECOMENDADO):")
print("=" * 70)
print("""
Para que los mensajes se envíen automáticamente cada día:

1. Crear tarea programada en Windows:
   - Abrir "Programador de tareas"
   - Crear tarea básica
   - Nombre: "Envío Promociones OpticaApp"
   - Trigger: Diario a las 10:00 AM
   - Acción: python manage.py process_campaigns
   - Ruta: D:\\ESCRITORIO\\OpticaApp

2. O ejecutar manualmente cada día:
   python manage.py process_campaigns
""")

print("\n✅ Script completado\n")
