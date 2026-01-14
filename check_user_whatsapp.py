from django.contrib.auth.models import User
from apps.organizations.models import OrganizationMember
from apps.notifications.models_whatsapp_connection import WhatsAppConnection

u = User.objects.filter(username='danioso8329').first()
if u:
    print(f'Usuario: {u.username}')
    print(f'Email: {u.email}')
    print(f'ID: {u.id}')
    
    membership = OrganizationMember.objects.filter(user=u).first()
    if membership:
        print(f'\nOrganizacion: {membership.organization.name}')
        print(f'Org ID: {membership.organization.id}')
        
        # Verificar estado WhatsApp
        try:
            conn = WhatsAppConnection.objects.get(organization=membership.organization)
            print(f'\n=== ESTADO WHATSAPP ===')
            print(f'Status: {conn.status}')
            print(f'Phone: {conn.phone_number}')
            print(f'Session exists: {conn.session_exists}')
            print(f'Last connected: {conn.last_connected_at}')
            print(f'Last disconnected: {conn.last_disconnected_at}')
            print(f'Disconnection reason: {conn.disconnection_reason}')
            print(f'Manually disconnected: {conn.manually_disconnected}')
            print(f'Reconnect attempts: {conn.reconnect_attempts}')
            if conn.disconnected_by:
                print(f'Disconnected by: {conn.disconnected_by.username}')
        except WhatsAppConnection.DoesNotExist:
            print('\nNo hay registro de WhatsApp Connection')
    else:
        print('Sin organizacion')
else:
    print('Usuario no encontrado')
