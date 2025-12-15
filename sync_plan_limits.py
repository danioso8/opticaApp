#!/usr/bin/env python
"""
Script para sincronizar automáticamente los límites de planes
desde plan_limits_config.py a la base de datos
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan
from plan_limits_config import PLAN_CONFIGURATIONS, format_limit

print("\n" + "="*70)
print("🔄 SINCRONIZACIÓN AUTOMÁTICA DE LÍMITES DE PLANES")
print("="*70 + "\n")

print("📖 Leyendo configuración desde plan_limits_config.py...")
print(f"   Planes a sincronizar: {len(PLAN_CONFIGURATIONS)}\n")

# Contador de cambios
changes_made = 0
plans_created = 0
plans_updated = 0

for plan_type, config in PLAN_CONFIGURATIONS.items():
    print(f"\n{'─'*70}")
    print(f"📦 Procesando: {config['name']} ({plan_type})")
    print(f"{'─'*70}")
    
    try:
        # Buscar o crear el plan
        plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type=plan_type,
            defaults={
                'name': config['name'],
                'slug': config['name'].lower().replace(' ', '-'),
                'price_monthly': config['price_monthly'],
                'price_yearly': config['price_yearly'],
            }
        )
        
        if created:
            plans_created += 1
            print(f"   ✨ Plan CREADO")
        else:
            print(f"   ✓  Plan existente - actualizando...")
        
        # Lista de cambios
        changes = []
        
        # Actualizar información básica
        if plan.name != config['name']:
            changes.append(f"Nombre: {plan.name} → {config['name']}")
            plan.name = config['name']
        
        if plan.price_monthly != config['price_monthly']:
            changes.append(f"Precio mensual: ${plan.price_monthly} → ${config['price_monthly']}")
            plan.price_monthly = config['price_monthly']
        
        if plan.price_yearly != config['price_yearly']:
            changes.append(f"Precio anual: ${plan.price_yearly} → ${config['price_yearly']}")
            plan.price_yearly = config['price_yearly']
        
        # Actualizar límites
        limits = config['limits']
        
        if plan.max_users != limits['max_users']:
            changes.append(f"Max usuarios: {plan.max_users} → {limits['max_users']}")
            plan.max_users = limits['max_users']
        
        if plan.max_organizations != limits['max_organizations']:
            changes.append(f"Max organizaciones: {plan.max_organizations} → {limits['max_organizations']}")
            plan.max_organizations = limits['max_organizations']
        
        if plan.max_appointments_month != limits['max_appointments_month']:
            changes.append(f"Max citas/mes: {plan.max_appointments_month} → {limits['max_appointments_month']}")
            plan.max_appointments_month = limits['max_appointments_month']
        
        if plan.max_patients != limits['max_patients']:
            changes.append(f"Max pacientes: {plan.max_patients} → {limits['max_patients']}")
            plan.max_patients = limits['max_patients']
        
        if plan.max_storage_mb != limits['max_storage_mb']:
            changes.append(f"Max almacenamiento: {plan.max_storage_mb}MB → {limits['max_storage_mb']}MB")
            plan.max_storage_mb = limits['max_storage_mb']
        
        # Actualizar facturación electrónica
        invoicing = config['electronic_invoicing']
        
        if plan.allow_electronic_invoicing != invoicing['enabled']:
            changes.append(f"Facturación: {plan.allow_electronic_invoicing} → {invoicing['enabled']}")
            plan.allow_electronic_invoicing = invoicing['enabled']
        
        if plan.max_invoices_month != invoicing['max_invoices_month']:
            changes.append(f"Max facturas/mes: {plan.max_invoices_month} → {invoicing['max_invoices_month']}")
            plan.max_invoices_month = invoicing['max_invoices_month']
        
        # Actualizar características legacy
        features = config['features_legacy']
        
        if plan.whatsapp_integration != features['whatsapp_integration']:
            changes.append(f"WhatsApp: {plan.whatsapp_integration} → {features['whatsapp_integration']}")
            plan.whatsapp_integration = features['whatsapp_integration']
        
        if plan.custom_branding != features['custom_branding']:
            changes.append(f"Branding: {plan.custom_branding} → {features['custom_branding']}")
            plan.custom_branding = features['custom_branding']
        
        if plan.api_access != features['api_access']:
            changes.append(f"API: {plan.api_access} → {features['api_access']}")
            plan.api_access = features['api_access']
        
        if plan.priority_support != features['priority_support']:
            changes.append(f"Soporte: {plan.priority_support} → {features['priority_support']}")
            plan.priority_support = features['priority_support']
        
        if plan.analytics != features['analytics']:
            changes.append(f"Analytics: {plan.analytics} → {features['analytics']}")
            plan.analytics = features['analytics']
        
        if plan.multi_location != features['multi_location']:
            changes.append(f"Multi-ubicación: {plan.multi_location} → {features['multi_location']}")
            plan.multi_location = features['multi_location']
        
        # Guardar cambios
        if changes:
            plan.save()
            plans_updated += 1
            changes_made += len(changes)
            
            print(f"\n   📝 Cambios aplicados:")
            for change in changes:
                print(f"      • {change}")
        else:
            print(f"   ✅ Sin cambios necesarios")
        
        # Mostrar resumen del plan
        print(f"\n   📊 Configuración actual:")
        print(f"      💰 Precio: ${plan.price_monthly:,.2f}/mes")
        print(f"      👥 Usuarios: {format_limit(plan.max_users)}")
        print(f"      🏢 Organizaciones: {format_limit(plan.max_organizations)}")
        print(f"      📅 Citas/mes: {format_limit(plan.max_appointments_month)}")
        print(f"      🏥 Pacientes: {format_limit(plan.max_patients)}")
        print(f"      💾 Almacenamiento: {plan.max_storage_mb} MB")
        print(f"      📄 Facturación: {'✅ Habilitada' if plan.allow_electronic_invoicing else '❌ Deshabilitada'}")
        if plan.allow_electronic_invoicing:
            if plan.max_invoices_month == 0:
                print(f"         Facturas/mes: ∞ Ilimitadas")
            else:
                print(f"         Facturas/mes: {plan.max_invoices_month}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")

# Resumen final
print(f"\n{'='*70}")
print("✅ SINCRONIZACIÓN COMPLETADA")
print(f"{'='*70}")
print(f"\n📊 Resumen:")
print(f"   • Planes creados: {plans_created}")
print(f"   • Planes actualizados: {plans_updated}")
print(f"   • Total de cambios: {changes_made}")
print(f"\n{'='*70}\n")

# Verificar usuarios afectados
from apps.users.models import UserSubscription

total_users = UserSubscription.objects.count()
if total_users > 0 and changes_made > 0:
    print("⚠️  ATENCIÓN:")
    print(f"   Hay {total_users} usuarios con suscripciones activas.")
    print(f"   Los cambios en límites les afectarán inmediatamente.")
    print()
