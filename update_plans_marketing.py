"""
Script para actualizar los planes existentes con información de marketing
basada en el análisis de la competencia
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan
from decimal import Decimal

def update_plans_marketing():
    """Actualiza los planes con información de marketing competitiva"""
    
    print("\n" + "="*80)
    print("🚀 ACTUALIZANDO PLANES CON INFORMACIÓN DE MARKETING")
    print("="*80 + "\n")
    
    # ==========================================================================
    # PLAN GRATUITO
    # ==========================================================================
    try:
        free_plan = SubscriptionPlan.objects.filter(plan_type='free').first()
        if not free_plan:
            raise SubscriptionPlan.DoesNotExist
        print(f"📦 Actualizando {free_plan.name}...")
        
        free_plan.coverage_description = "Perfecto para comenzar tu presencia digital y probar el sistema sin compromiso"
        free_plan.ideal_for = "Profesionales independientes o ópticas nuevas"
        free_plan.plan_badge = ""  # Sin badge
        
        free_plan.highlighted_features = """Landing page personalizable
Gestión básica de citas (50/mes)
Registro de pacientes (hasta 100)
Recordatorios por email
Panel de administración intuitivo
Historial clínico básico"""
        
        free_plan.main_benefits = """Sin tarjeta de crédito requerida
Comienza gratis inmediatamente
Ideal para probar el sistema
Actualiza cuando estés listo"""
        
        free_plan.additional_features = """Soporte por email
Tutoriales en video
Base de conocimiento"""
        
        free_plan.includes_landing_page = True
        
        # Límites ilimitados
        free_plan.unlimited_users = False
        free_plan.unlimited_patients = False
        free_plan.unlimited_appointments = False
        free_plan.unlimited_organizations = False
        free_plan.unlimited_storage = False
        
        free_plan.save()
        print(f"   ✅ {free_plan.name} actualizado\n")
        
    except SubscriptionPlan.DoesNotExist:
        print("   ⚠️  Plan Free no encontrado\n")
    
    # ==========================================================================
    # PLAN BÁSICO
    # ==========================================================================
    try:
        basic_plan = SubscriptionPlan.objects.filter(plan_type='basic').first()
        if not basic_plan:
            raise SubscriptionPlan.DoesNotExist
        print(f"📦 Actualizando {basic_plan.name}...")
        
        # Ajustar precios en PESOS COLOMBIANOS (COP)
        basic_plan.price_monthly = Decimal('159900')
        basic_plan.price_yearly = Decimal('1599000')
        
        # Ajustar límites mejorados
        basic_plan.max_users = 3
        basic_plan.max_organizations = 3
        basic_plan.max_appointments_month = 200
        basic_plan.max_patients = 500
        basic_plan.max_storage_mb = 1024  # 1 GB
        
        basic_plan.coverage_description = "Ideal para ópticas pequeñas en crecimiento que buscan digitalizar sus operaciones"
        basic_plan.ideal_for = "Ópticas pequeñas con 2-3 empleados"
        basic_plan.plan_badge = ""
        
        basic_plan.highlighted_features = """Landing page personalizable
WhatsApp Business integrado
Recordatorios automáticos vía WhatsApp y Email
Gestión de citas (200/mes)
Analytics básicos
Hasta 500 pacientes
3 usuarios simultáneos
1 GB de almacenamiento"""
        
        basic_plan.main_benefits = """Ahorra tiempo con recordatorios automáticos
Reduce ausencias con WhatsApp
Mejora la experiencia del paciente
Dashboard con métricas clave"""
        
        basic_plan.additional_features = """Exportación de reportes PDF
Soporte por email y chat
Capacitación inicial incluida
Actualizaciones automáticas"""
        
        basic_plan.includes_landing_page = True
        basic_plan.whatsapp_integration = True
        basic_plan.analytics = True
        
        # Límites ilimitados
        basic_plan.unlimited_users = False
        basic_plan.unlimited_patients = False
        basic_plan.unlimited_appointments = False
        basic_plan.unlimited_organizations = False
        basic_plan.unlimited_storage = False
        
        basic_plan.save()
        print(f"   ✅ {basic_plan.name} actualizado\n")
        
    except SubscriptionPlan.DoesNotExist:
        print("   ⚠️  Plan Basic no encontrado\n")
    
    # ==========================================================================
    # PLAN PROFESIONAL
    # ==========================================================================
    try:
        pro_plan = SubscriptionPlan.objects.filter(plan_type='professional').first()
        if not pro_plan:
            raise SubscriptionPlan.DoesNotExist
        print(f"📦 Actualizando {pro_plan.name}...")
        
        # Ajustar precios en PESOS COLOMBIANOS (COP)
        pro_plan.price_monthly = Decimal('359900')
        pro_plan.price_yearly = Decimal('3599000')
        
        # Ajustar límites mejorados
        pro_plan.max_users = 10
        pro_plan.max_organizations = 3  # Múltiples sucursales
        pro_plan.max_appointments_month = 1500
        pro_plan.max_patients = 3000
        pro_plan.max_storage_mb = 5120  # 5 GB
        pro_plan.allow_electronic_invoicing = True
        pro_plan.max_invoices_month = 50  # 50 facturas DIAN/mes
        
        pro_plan.coverage_description = "Para ópticas establecidas que buscan digitalización completa y optimización de procesos"
        pro_plan.ideal_for = "Ópticas medianas con 5-10 empleados o múltiples sucursales"
        pro_plan.plan_badge = "MÁS POPULAR"
        
        pro_plan.highlighted_features = """Landing page premium personalizable
WhatsApp Business + Recordatorios automatizados
Marca 100% personalizada (colores, logo)
Analytics avanzado con dashboards
API REST completa para integraciones
Múltiples ubicaciones (hasta 3 sucursales)
Facturación electrónica DIAN (50/mes)
Soporte prioritario
1,500 citas/mes
3,000 pacientes
10 usuarios simultáneos
5 GB de almacenamiento"""
        
        pro_plan.main_benefits = """Control total de tu marca
Gestiona múltiples sucursales
Cumple con DIAN automáticamente
Insights avanzados para mejorar ventas
Integraciones con otros sistemas"""
        
        pro_plan.additional_features = """Reportes personalizados
Exportación masiva de datos
Soporte telefónico prioritario
Capacitación personalizada del equipo
Migración asistida de datos
Webhooks para automatización"""
        
        pro_plan.includes_landing_page = True
        pro_plan.whatsapp_integration = True
        pro_plan.custom_branding = True
        pro_plan.api_access = True
        pro_plan.priority_support = True
        pro_plan.analytics = True
        pro_plan.multi_location = True
        
        # Límites ilimitados
        pro_plan.unlimited_users = False
        pro_plan.unlimited_patients = False
        pro_plan.unlimited_appointments = False
        pro_plan.unlimited_organizations = False
        pro_plan.unlimited_storage = False
        
        pro_plan.save()
        print(f"   ✅ {pro_plan.name} actualizado\n")
        
    except SubscriptionPlan.DoesNotExist:
        print("   ⚠️  Plan Professional no encontrado\n")
    
    # ==========================================================================
    # PLAN EMPRESARIAL
    # ==========================================================================
    try:
        enterprise_plan = SubscriptionPlan.objects.filter(plan_type='enterprise').first()
        if not enterprise_plan:
            raise SubscriptionPlan.DoesNotExist
        print(f"📦 Actualizando {enterprise_plan.name}...")
        
        # Ajustar precios en PESOS COLOMBIANOS (COP)
        enterprise_plan.price_monthly = Decimal('719900')
        enterprise_plan.price_yearly = Decimal('7199000')
        
        # ILIMITADOS REALES
        enterprise_plan.max_users = 999999
        enterprise_plan.max_organizations = 999999
        enterprise_plan.max_appointments_month = 999999
        enterprise_plan.max_patients = 999999
        enterprise_plan.max_storage_mb = 999999
        enterprise_plan.allow_electronic_invoicing = True
        enterprise_plan.max_invoices_month = 0  # 0 = ilimitado
        
        enterprise_plan.coverage_description = "Solución completa para cadenas de ópticas que requieren escalabilidad y personalización total"
        enterprise_plan.ideal_for = "Cadenas de ópticas con 3+ sucursales o grupos empresariales"
        enterprise_plan.plan_badge = "MEJOR VALOR"
        
        enterprise_plan.highlighted_features = """Landing page white-label empresarial
TODO ILIMITADO:
  • Usuarios ilimitados
  • Ubicaciones ilimitadas
  • Citas ilimitadas
  • Pacientes ilimitados
  • Almacenamiento ilimitado
  • Facturación DIAN ILIMITADA
WhatsApp Business Premium
API completa + Webhooks
Marca 100% personalizada
Soporte dedicado 24/7
Integraciones personalizadas
Onboarding personalizado
SLA garantizado"""
        
        enterprise_plan.main_benefits = """Sin límites de crecimiento
Escalabilidad empresarial
Soporte dedicado 24/7
Integraciones a medida
Cumplimiento normativo garantizado
ROI optimizado"""
        
        enterprise_plan.additional_features = """Account Manager dedicado
Reuniones mensuales de estrategia
Capacitación ilimitada del equipo
Desarrollo de funcionalidades custom
Migración completa asistida
Servidor dedicado opcional
White-label completo disponible
Respaldo prioritario de datos"""
        
        enterprise_plan.includes_landing_page = True
        enterprise_plan.whatsapp_integration = True
        enterprise_plan.custom_branding = True
        enterprise_plan.api_access = True
        enterprise_plan.priority_support = True
        enterprise_plan.analytics = True
        enterprise_plan.multi_location = True
        
        # ACTIVAR TODOS LOS LÍMITES ILIMITADOS
        enterprise_plan.unlimited_users = True
        enterprise_plan.unlimited_patients = True
        enterprise_plan.unlimited_appointments = True
        enterprise_plan.unlimited_organizations = True
        enterprise_plan.unlimited_storage = True
        
        enterprise_plan.save()
        print(f"   ✅ {enterprise_plan.name} actualizado\n")
        
    except SubscriptionPlan.DoesNotExist:
        print("   ⚠️  Plan Enterprise no encontrado\n")
    
    print("="*80)
    print("✅ ACTUALIZACIÓN COMPLETADA")
    print("="*80 + "\n")
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE PLANES:\n")
    for plan in SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly'):
        print(f"  {plan.name} ({plan.get_plan_type_display()})")
        print(f"    💰 ${plan.price_monthly}/mes | ${plan.price_yearly}/año")
        if plan.plan_badge:
            print(f"    🏷️  Badge: {plan.plan_badge}")
        if plan.ideal_for:
            print(f"    🎯 Ideal para: {plan.ideal_for}")
        print(f"    👥 Usuarios: {plan.get_max_users_display()}")
        print(f"    🏢 Organizaciones: {plan.get_max_organizations_display()}")
        print(f"    📅 Citas: {plan.get_max_appointments_display()}")
        print(f"    💾 Almacenamiento: {plan.get_max_storage_display()}")
        if plan.allow_electronic_invoicing:
            facturas = 'Ilimitadas' if plan.max_invoices_month == 0 else f"{plan.max_invoices_month}/mes"
            print(f"    📄 Facturas DIAN: {facturas}")
        print()


if __name__ == '__main__':
    update_plans_marketing()
