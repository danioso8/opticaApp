"""
Actualiza los planes con las configuraciones de facturación electrónica DIAN
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan

print("\n" + "="*70)
print("🔧 CONFIGURANDO FACTURACIÓN ELECTRÓNICA POR PLAN")
print("="*70 + "\n")

# Plan Free: Sin facturación electrónica
free_plan = SubscriptionPlan.objects.get(name="Plan Free:")
free_plan.allow_electronic_invoicing = False
free_plan.max_invoices_month = 0
free_plan.save()
print("✅ Plan Free: Facturación Electrónica DESHABILITADA")

# Plan Básico: Sin facturación electrónica
basic_plan = SubscriptionPlan.objects.get(name="Plan Básico")
basic_plan.allow_electronic_invoicing = False
basic_plan.max_invoices_month = 0
basic_plan.save()
print("✅ Plan Básico: Facturación Electrónica DESHABILITADA")

# Plan Pro (Profesional): Con límite mensual
pro_plan = SubscriptionPlan.objects.get(name="Plan Pro")
pro_plan.allow_electronic_invoicing = True
pro_plan.max_invoices_month = 20  # 20 facturas por mes
pro_plan.save()
print("✅ Plan Pro (Profesional): Facturación Electrónica HABILITADA (20 facturas/mes)")

# Plan Empresarial: Ilimitado
enterprise_plan = SubscriptionPlan.objects.get(name="Plan Empresarial")
enterprise_plan.allow_electronic_invoicing = True
enterprise_plan.max_invoices_month = 0  # 0 = Ilimitado
enterprise_plan.save()
print("✅ Plan Empresarial: Facturación Electrónica HABILITADA (ILIMITADO)")

print("\n" + "="*70)
print("✅ CONFIGURACIÓN COMPLETADA")
print("="*70)

# Mostrar resumen
print("\n📋 RESUMEN DE PLANES:\n")
for plan in SubscriptionPlan.objects.all().order_by('id'):
    if plan.allow_electronic_invoicing:
        if plan.max_invoices_month == 0:
            status = "✅ HABILITADO (ILIMITADO)"
        else:
            status = f"✅ HABILITADO ({plan.max_invoices_month} facturas/mes)"
    else:
        status = "❌ DESHABILITADO"
    
    print(f"   {plan.name:20} → Facturación Electrónica: {status}")

print("\n")
