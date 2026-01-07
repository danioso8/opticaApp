"""
Modelo para rastrear el uso de mensajes WhatsApp por organización
"""
from django.db import models
from django.utils import timezone
from datetime import datetime


class WhatsAppUsage(models.Model):
    """
    Registra el consumo mensual de mensajes WhatsApp por organización
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='whatsapp_usage'
    )
    year = models.IntegerField()
    month = models.IntegerField()  # 1-12
    
    # Contadores
    messages_sent = models.IntegerField(default=0)
    messages_included = models.IntegerField(default=100)  # Del plan
    messages_overage = models.IntegerField(default=0)  # Excedentes
    
    # Facturación
    overage_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cost_per_message = models.DecimalField(max_digits=6, decimal_places=4, default=0.02)
    
    # Alertas enviadas
    alert_80_sent = models.BooleanField(default=False)
    alert_100_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('organization', 'year', 'month')
        ordering = ['-year', '-month']
        verbose_name = 'Uso de WhatsApp'
        verbose_name_plural = 'Usos de WhatsApp'
    
    def __str__(self):
        return f"{self.organization.name} - {self.year}/{self.month:02d} - {self.messages_sent} msgs"
    
    @classmethod
    def get_current_usage(cls, organization):
        """
        Obtiene o crea el registro de uso del mes actual
        """
        now = timezone.now()
        usage, created = cls.objects.get_or_create(
            organization=organization,
            year=now.year,
            month=now.month,
            defaults={
                'messages_included': organization.subscription.plan.whatsapp_messages_included if hasattr(organization, 'subscription') else 100
            }
        )
        return usage
    
    def increment_message(self):
        """
        Incrementa el contador de mensajes y calcula sobrecargos
        """
        self.messages_sent += 1
        
        # Calcular excedentes
        if self.messages_sent > self.messages_included:
            self.messages_overage = self.messages_sent - self.messages_included
            self.overage_cost = float(self.messages_overage) * float(self.cost_per_message)
        
        self.save()
        
        # Verificar si necesita enviar alertas
        self._check_and_send_alerts()
    
    def _check_and_send_alerts(self):
        """
        Verifica y envía alertas cuando se alcanza 80% o 100% del límite
        """
        percentage = (self.messages_sent / self.messages_included * 100) if self.messages_included > 0 else 0
        
        # Alerta al 80%
        if percentage >= 80 and not self.alert_80_sent:
            self._send_usage_alert(80)
            self.alert_80_sent = True
            self.save()
        
        # Alerta al 100%
        if percentage >= 100 and not self.alert_100_sent:
            self._send_usage_alert(100)
            self.alert_100_sent = True
            self.save()
    
    def _send_usage_alert(self, percentage):
        """
        Envía alerta por email al administrador de la organización
        """
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Obtener email del admin
        admin_email = self.organization.owner.email if self.organization.owner else None
        if not admin_email:
            return
        
        subject = f"⚠️ Alerta: Uso de WhatsApp al {percentage}%"
        
        if percentage >= 100:
            message = f"""
Hola {self.organization.owner.get_full_name()},

Tu organización "{self.organization.name}" ha alcanzado el {percentage}% del límite de mensajes WhatsApp incluidos en tu plan.

📊 Uso actual:
- Mensajes enviados: {self.messages_sent}
- Mensajes incluidos: {self.messages_included}
- Mensajes excedentes: {self.messages_overage}
- Costo adicional: ${self.overage_cost:.2f} USD

⚠️ A partir de ahora, cada mensaje adicional tendrá un costo de ${self.cost_per_message:.2f} USD.

💡 Considera actualizar tu plan para obtener más mensajes incluidos.

Saludos,
Equipo OpticaApp
            """
        else:
            remaining = self.messages_included - self.messages_sent
            message = f"""
Hola {self.organization.owner.get_full_name()},

Tu organización "{self.organization.name}" ha utilizado el {percentage:.0f}% de los mensajes WhatsApp incluidos en tu plan.

📊 Uso actual:
- Mensajes enviados: {self.messages_sent}
- Mensajes incluidos: {self.messages_included}
- Mensajes restantes: {remaining}

💡 Te quedan {remaining} mensajes este mes. Una vez alcanzado el límite, se aplicará un cargo de ${self.cost_per_message:.2f} USD por mensaje adicional.

Saludos,
Equipo OpticaApp
            """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error enviando alerta de uso WhatsApp: {e}")
    
    def get_usage_percentage(self):
        """
        Retorna el porcentaje de uso
        """
        if self.messages_included == 0:
            return 0
        return min((self.messages_sent / self.messages_included * 100), 100)
    
    def get_remaining_messages(self):
        """
        Retorna mensajes restantes (puede ser negativo si hay excedentes)
        """
        return self.messages_included - self.messages_sent
    
    def is_over_limit(self):
        """
        Indica si ya superó el límite incluido
        """
        return self.messages_sent > self.messages_included
