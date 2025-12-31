from django import template
from apps.organizations.models import OrganizationMember

register = template.Library()


@register.simple_tag
def get_user_organizations(user):
    """Obtiene todas las organizaciones del usuario"""
    if not user.is_authenticated:
        return []
    
    return OrganizationMember.objects.filter(
        user=user,
        is_active=True,
        organization__is_active=True
    ).select_related('organization').order_by('organization__name')
