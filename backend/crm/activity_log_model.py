from django.db import models
from django.contrib.auth.models import User

class ActivityLog(models.Model):
    \"\"\"
    Registro de actividad para tracking de cambios en órdenes
    \"\"\"
    ACTION_TYPES = [
        ('STATUS_CHANGE', 'Cambio de Estado'),
        ('PAYMENT', 'Registro de Pago'),
        ('EMAIL', 'Email Enviado'),
        ('NOTE', 'Nota Añadida'),
        ('ASSIGNMENT', 'Asignación'),
        ('DOCUMENT_UPLOAD', 'Documento Subido'),
        ('SERVICE_ADDED', 'Servicio Añadido'),
    ]
    
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True, help_text=\"Datos adicionales de la acción\")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Registro de Actividad'
        verbose_name_plural = 'Registros de Actividad'
    
    def __str__(self):
        return f\"{self.get_action_type_display()} - {self.order.order_friendly_id} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}\"
