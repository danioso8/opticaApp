"""
Script para actualizar los límites de WhatsApp en los planes existentes
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaapp.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan

# Actualizar planes con límites de WhatsApp
plans_config = {
    'basic': {
        'whatsapp_messages_included': 100,
        'whatsapp_overage_price': 0.020,
    },
    'professional': {
        'whatsapp_messages_included': 500,
        'whatsapp_overage_price': 0.015,
    },
    'enterprise': {
        'whatsapp_messages_included': 2000,
        'whatsapp_overage_price': 0.010,
    },
}

for plan_type, config in plans_config.items():
    try:
        plan = SubscriptionPlan.objects.get(plan_type=plan_type)
        plan.whatsapp_messages_included = config['whatsapp_messages_included']
        plan.whatsapp_overage_price = config['whatsapp_overage_price']
        plan.save()
        print(f"✅ Plan '{plan.name}' actualizado: {config['whatsapp_messages_included']} mensajes, ${config['whatsapp_overage_price']}/mensaje")
    except SubscriptionPlan.DoesNotExist:
        print(f"❌ Plan '{plan_type}' no encontrado")
    except Exception as e:
        print(f"❌ Error actualizando plan '{plan_type}': {e}")

print("\n📊 Resumen de planes:")
for plan in SubscriptionPlan.objects.all():
    print(f"\n{plan.name} ({plan.plan_type}):")
    print(f"  - Mensajes incluidos: {plan.whatsapp_messages_included}")
    print(f"  - Precio por excedente: ${plan.whatsapp_overage_price}")
