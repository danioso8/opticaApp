from apps.users.models import UserSubscription
from django.contrib.auth import get_user_model

User = get_user_model()

user = User.objects.get(username='danioso8329')
print(f'Usuario: {user.username}')
print(f'Email: {user.email}')

try:
    sub = UserSubscription.objects.get(user=user)
    print(f'\n=== Suscripción ===')
    print(f'Plan: {sub.plan.name}')
    print(f'Activa: {sub.is_active}')
    print(f'Vence: {sub.end_date}')
    
    print(f'\n=== Límites del Plan ===')
    print(f'Organizaciones: {sub.plan.max_organizations}')
    print(f'Usuarios: {sub.plan.max_users}')
    print(f'Citas/mes: {sub.plan.max_appointments_month}')
    print(f'Pacientes: {sub.plan.max_patients}')
    print(f'Productos: {sub.plan.max_products}')
    print(f'Doctores: {sub.plan.max_doctors}')
    print(f'Facturas/mes: {sub.plan.max_invoices_month}')
    print(f'Empleados: {sub.plan.max_employees}')
    print(f'Almacenamiento: {sub.plan.storage_limit_gb} GB')
    print(f'WhatsApp msgs: {sub.plan.max_whatsapp_messages}')
except UserSubscription.DoesNotExist:
    print('❌ No tiene suscripción')
