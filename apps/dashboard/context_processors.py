"""
Context processors para agregar datos globales a los templates
"""
from apps.organizations.models import OrganizationMember


def user_permissions(request):
    """
    Agrega los permisos del usuario a todos los templates
    
    Uso en templates:
        {% if user_perms.is_admin %}
        {% if user_perms.patients.can_create %}
    """
    if not request.user.is_authenticated:
        return {'user_perms': {}}
    
    membership = OrganizationMember.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('organization').first()
    
    if not membership:
        return {'user_perms': {}, 'user_membership': None}
    
    # Owner y Admin tienen todos los permisos
    if membership.role in ['owner', 'admin']:
        return {
            'user_perms': {'is_admin': True, 'all_access': True},
            'user_membership': membership,
            'user_organization': membership.organization,
        }
    
    from apps.organizations.models import MemberModulePermission
    
    permissions = {}
    for perm in MemberModulePermission.objects.filter(member=membership).select_related('module'):
        permissions[perm.module.code] = {
            'can_view': perm.can_view,
            'can_create': perm.can_create,
            'can_edit': perm.can_edit,
            'can_delete': perm.can_delete,
        }
    
    return {
        'user_perms': permissions,
        'user_membership': membership,
        'user_organization': membership.organization,
    }
