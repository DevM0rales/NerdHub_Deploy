from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Perfil, Notificacao

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria automaticamente um perfil e configurações de notificação quando um usuário é criado
    """
    if created:
        # Criar perfil
        perfil = Perfil.objects.create(user=instance)
        
        # Criar configurações de notificação padrão
        Notificacao.objects.create(perfil=perfil)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Salva o perfil do usuário quando o usuário é salvo
    """
    if hasattr(instance, 'perfil'):
        instance.perfil.save()