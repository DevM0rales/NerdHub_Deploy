from django import template
from usuarios.models import Perfil

register = template.Library()

@register.simple_tag(takes_context=True)
def get_user_profile(context):
    """
    Template tag to get the user profile.
    Usage: {% get_user_profile as user_profile %}
    """
    request = context['request']
    if request.user.is_authenticated:
        try:
            return request.user.perfil
        except Perfil.DoesNotExist:
            return None
    return None