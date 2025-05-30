from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reunion
from django.core.mail import send_mail

@receiver(post_save, sender=Reunion)
def enviar_notificaciones(sender, instance, created, **kwargs):
    if created:
        participantes = instance.participantes.all()
        emails = [u.email for u in participantes if u.email]
        
        send_mail(
            subject=f"Nueva Reunión: {instance.get_motivo_display()}",
            message=f"""
            Se ha agendado una reunión:
            - Fecha: {instance.fecha}
            - Lugar: {instance.lugar}
            - Convocante: {instance.convocante.get_full_name()}
            """,
            from_email="notificaciones@juntavecinos.cl",
            recipient_list=emails,
            fail_silently=True
        )