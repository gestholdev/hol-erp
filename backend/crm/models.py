from django.db import models
from django.utils import timezone
import uuid

class Client(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True, null=True)
    identity_doc = models.CharField(max_length=50, blank=True, null=True, help_text="DNI, NIE, Pasaporte")
    is_collaborator = models.BooleanField(default=False, help_text="Es un socio comercial con precios preferenciales?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({'Colaborador' if self.is_collaborator else 'Cliente'})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PROCESSING', 'En Proceso'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    # Global Status for Kanban View
    GLOBAL_STATUS_CHOICES = [
        ('NEW_REQUEST', 'Solicitud Nueva'),
        ('PENDING_PAYMENT', 'Pendiente de Pago'),
        ('IN_PROCESS_PARTIAL', 'En Proceso (Pago Parcial)'),
        ('IN_PROCESS_PAID', 'En Proceso (Pagado)'),
        ('READY_DELIVERY', 'Finalizado/Para Entrega'),
        ('CLOSED', 'Cerrado/Archivado'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PARTIAL', 'Pago Parcial'),
        ('PAID', 'Pagado Completo'),
    ]
    
    CURRENCY_CHOICES = [
        ('EUR', 'Euro'),
        ('USD', 'US Dollar'),
        ('CUP', 'Peso Cubano'),
    ]

    # ID Format: CLIENTNAME_DATE_UUID
    order_friendly_id = models.CharField(max_length=100, unique=True, blank=True)
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_orders')
    assigned_to = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders', help_text="Gestor responsable")
    
    # Status fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    global_status = models.CharField(max_length=20, choices=GLOBAL_STATUS_CHOICES, default='NEW_REQUEST')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    # Financial fields
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='EUR')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_margin = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total pagado por el cliente")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True)

    def update_totals(self):
        """
        Recalculate totals based on child items.
        """
        items = self.items.all()
        self.total_amount = sum(item.price for item in items)
        self.total_cost = sum(item.cost for item in items)
        self.total_margin = sum(item.margin for item in items)
        # Use update to avoid triggering save signal recursion
        Order.objects.filter(pk=self.pk).update(
            total_amount=self.total_amount,
            total_cost=self.total_cost,
            total_margin=self.total_margin
        )

    def save(self, *args, **kwargs):
        if not self.order_friendly_id:
            # Simple generation logic: Name_Date_ShortUUID
            date_str = timezone.now().strftime('%Y%m%d')
            clean_name = self.client.full_name.replace(' ', '').upper()[:5]
            short_uuid = str(uuid.uuid4())[:4].upper()
            self.order_friendly_id = f"{clean_name}_{date_str}_{short_uuid}"
        super().save(*args, **kwargs)

    def __str__(self):
        # Format: "Client Name - DD/MM/YYYY"
        date_str = self.created_at.strftime('%d/%m/%Y') if self.created_at else ''
        return f"{self.client.full_name} - {date_str}" if date_str else self.order_friendly_id

class ServiceItem(models.Model):
    """
    Replaces the old 'Procedure' model. Represents a single line item in an Order.
    Example: 1 Legalization of Birth Certificate.
    """
    SERVICE_TYPES = [
        ('LEGALIZATION', 'Legalización Minjus/Consulado'),
        ('VISA', 'Visado/Cita'),
        ('SHIPPING', 'Envío/Paquetería'),
        ('OTHER', 'Otro'),
    ]
    
    # Document types with abbreviations for display
    DOCUMENT_TYPE_CHOICES = [
        ('ANTECEDENTES_PENALES', 'Antecedentes Penales'),  # AP
        ('NACIMIENTO', 'Certificado de Nacimiento'),  # NAC
        ('MATRIMONIO', 'Certificado de Matrimonio'),  # MAT
        ('DIVORCIO', 'Certificado de Divorcio'),  # DIV
        ('SOLTERIA', 'Certificado de Soltería'),  # SOL
        ('DEFUNCION', 'Certificado de Defunción'),  # DEF
        ('ESTADO_CONYUGAL', 'Certificado de Estado Conyugal'),  # EC
        ('PODER_NOTARIAL', 'Poder Notarial'),  # PN
        ('PASAPORTE', 'Pasaporte'),  # PAS
        ('TITULO_ACADEMICO', 'Título Académico'),  # TIT
        ('PLAN_ESTUDIOS', 'Plan de Estudios'),  # PE
        ('NOTAS', 'Notas Académicas'),  # NOT
        ('OTRO', 'Otro'),  # OTR
    ]
    
    DOCUMENT_ABBREVIATIONS = {
        'ANTECEDENTES_PENALES': 'AP',
        'NACIMIENTO': 'NAC',
        'MATRIMONIO': 'MAT',
        'DIVORCIO': 'DIV',
        'SOLTERIA': 'SOL',
        'DEFUNCION': 'DEF',
        'ESTADO_CONYUGAL': 'EC',
        'PODER_NOTARIAL': 'PN',
        'PASAPORTE': 'PAS',
        'TITULO_ACADEMICO': 'TIT',
        'PLAN_ESTUDIOS': 'PE',
        'NOTAS': 'NOT',
        'OTRO': 'OTR',
    }
    
    LEGALIZATION_TYPE_CHOICES = [
        ('MINJUS', 'Solo MINJUS'),
        ('CONSULADO', 'Solo Consulado'),
        ('MINJUS_CONSULADO', 'MINJUS + Consulado'),
    ]
    
    DELIVERY_DESTINATION_CHOICES = [
        ('INTERNACIONAL', 'Envío Internacional (España)'),
        ('HABANA', 'Recoger en La Habana'),
        ('CAMAGUEY', 'Recoger en Camagüey'),
    ]
    
    # Responsable (¿Quién lo tiene?)
    RESPONSIBLE_CHOICES = [
        ('OFICINA_CUBA', 'Oficina Cuba'),
        ('OFICINA_ESPANA', 'Oficina España'),
        ('GESTOR_CAMPO', 'Gestor de Campo'),
        ('AGENCIA_INTERNA', 'Agencia Interna'),
        ('COURIER_EXTERNO', 'Courier Externo'),
        ('CLIENTE', 'Cliente/Asociado'),
    ]
    
    # Estado Logístico (¿Qué acción ocurre?)
    LOGISTICS_STATUS_CHOICES = [
        ('NA', 'N/A (En Gestión)'),
        ('PENDING_PICKUP', 'Pendiente de Recogida'),
        ('LOCAL_DELIVERY', 'En Reparto Local'),
        ('INTER_OFFICE', 'Tránsito Inter-Oficinas'),
        ('FINAL_SHIPPING', 'Envío Paquetería Final'),
        ('RECEIVING', 'En Recepción/Entrante'),
        ('DELIVERED', 'Entregado'),
    ]
    
    # Ubicación (¿Dónde?)
    LOCATION_CHOICES = [
        ('OFICINA_HABANA', 'Oficina Habana'),
        ('OFICINA_ESPANA', 'Oficina España'),
        ('VICECONSULADO_CAMAGUEY', 'Viceconsulado Camagüey'),
        ('DOMICILIO_CLIENTE', 'Domicilio Cliente'),
        ('OFICINA_ASOCIADO', 'Oficina Asociado'),
        ('MINJUS', 'MINJUS'),
        ('CONSULADO', 'Consulado'),
    ]
    
    STATUS_CHOICES = [
        ('INIT', 'Iniciado/Solicitado'),
        ('PENDING_RECEIVE', 'Pendiente Recibir Documento'),
        ('RECEIVED', 'Documento Recibido'),
        ('MINJUS_IN', 'Entrada Minjus'),
        ('MINJUS_OUT', 'Salida Minjus'),
        ('CONSULATE_IN', 'Entrada Consulado'),
        ('CONSULATE_OUT', 'Salida Consulado'),
        ('LEGALIZED', 'Legalizado'),
        ('SENT_SPAIN', 'Enviado a España'),
        ('SENT_CLIENT', 'Enviado al Cliente'),
        ('SENT_CAMAGUEY', 'Enviado a Camagüey'),
        ('READY_PICKUP', 'Listo para Recoger'),
        ('READY', 'Listo para Entrega'),
        ('DELIVERED', 'Entregado'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='LEGALIZATION')
    
    # Specifics for Legalizations
    document_type = models.CharField(max_length=100, blank=True, help_text="Ej: Nacimiento, Penales")
    legalization_type = models.CharField(max_length=100, blank=True, help_text="Ej: Apostilla, Legalización Consular")
    titular_name = models.CharField(max_length=255, blank=True, help_text="Nombre del titular del documento")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INIT')
    
    # Delivery Destination
    delivery_destination = models.CharField(
        max_length=20,
        choices=DELIVERY_DESTINATION_CHOICES,
        default='INTERNACIONAL',
        help_text="Destino de entrega del documento"
    )
    
    # Assignment and Location
    assigned_tramitador = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_items', help_text="Tramitador asignado")
    
    # Logistics Tracking (3 campos vinculados)
    responsible = models.CharField(
        max_length=20,
        choices=RESPONSIBLE_CHOICES,
        default='OFICINA_CUBA',
        help_text="¿Quién tiene el documento?"
    )
    logistics_status = models.CharField(
        max_length=20,
        choices=LOGISTICS_STATUS_CHOICES,
        default='NA',
        help_text="¿Qué acción logística ocurre?"
    )
    current_location = models.CharField(
        max_length=30,
        choices=LOCATION_CHOICES,
        default='OFICINA_HABANA',
        help_text="¿Dónde está el documento físicamente?"
    )
    
    # Financial
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Coste interno")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Precio al cliente")
    margin = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    
    # SLA & Prioritization
    PRIORITY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('EXPRESS', 'Express (Urgente)'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    deadline = models.DateTimeField(null=True, blank=True)
    
    # Phase tracking (JSON field for flexibility)
    phase_dates = models.JSONField(default=dict, blank=True, help_text="Fechas de cada fase del proceso")
    
    # Document management
    final_document = models.FileField(upload_to='final_documents/', null=True, blank=True, help_text="Documento final legalizado")
    notes = models.TextField(blank=True, help_text="Notas específicas del trámite")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_overdue(self):
        """Check if item is past its deadline"""
        if self.deadline and self.status not in ['READY', 'DELIVERED']:
            return timezone.now() > self.deadline
        return False
    
    def get_workflow_phases(self):
        """Return workflow phases based on legalization type AND delivery destination"""
        workflows = {
            'MINJUS': {
                'INTERNACIONAL': ['INIT', 'MINJUS_OUT', 'SENT_SPAIN', 'SENT_CLIENT', 'DELIVERED'],
                'HABANA': ['INIT', 'MINJUS_OUT', 'READY_PICKUP', 'DELIVERED'],
                'CAMAGUEY': ['INIT', 'MINJUS_OUT', 'SENT_CAMAGUEY', 'READY_PICKUP', 'DELIVERED'],
            },
            'CONSULADO': {
                'INTERNACIONAL': ['PENDING_RECEIVE', 'RECEIVED', 'LEGALIZED', 'SENT_SPAIN', 'SENT_CLIENT', 'DELIVERED'],
                'HABANA': ['PENDING_RECEIVE', 'RECEIVED', 'LEGALIZED', 'READY_PICKUP', 'DELIVERED'],
                'CAMAGUEY': ['PENDING_RECEIVE', 'RECEIVED', 'LEGALIZED', 'SENT_CAMAGUEY', 'READY_PICKUP', 'DELIVERED'],
            },
            'MINJUS_CONSULADO': {
                'INTERNACIONAL': ['INIT', 'MINJUS_OUT', 'CONSULATE_OUT', 'SENT_SPAIN', 'SENT_CLIENT', 'DELIVERED'],
                'HABANA': ['INIT', 'MINJUS_OUT', 'CONSULATE_OUT', 'READY_PICKUP', 'DELIVERED'],
                'CAMAGUEY': ['INIT', 'MINJUS_OUT', 'CONSULATE_OUT', 'SENT_CAMAGUEY', 'READY_PICKUP', 'DELIVERED'],
            },
        }
        
        return workflows.get(self.legalization_type, {}).get(self.delivery_destination, ['INIT', 'DELIVERED'])
    
    def get_document_abbreviation(self):
        """Get abbreviation for document type"""
        return self.DOCUMENT_ABBREVIATIONS.get(self.document_type, 'DOC')
    
    def get_display_name(self):
        """Return just the titular name for display"""
        return self.titular_name
    
    def get_legalization_display(self):
        """Format legalization type for display"""
        leg_type_map = {
            'MINJUS_CONSULADO': 'MINJUS + Consulado',
            'MINJUS': 'MINJUS',
            'CONSULADO': 'Consulado',
        }
        return leg_type_map.get(self.legalization_type, '')

    def save(self, *args, **kwargs):
        from decimal import Decimal
        # Ensure Decimal types for calculation
        self.margin = Decimal(str(self.price)) - Decimal(str(self.cost))
        
        # Calculate Deadline if not set
        if not self.deadline and self.created_at:
            # Simple SLA Logic: Express=3 days, Normal=15 days
            days = 3 if self.priority == 'EXPRESS' else 15
            self.deadline = self.created_at + timezone.timedelta(days=days)
        elif not self.deadline:
             # Fallback for first save when created_at might be None
             days = 3 if self.priority == 'EXPRESS' else 15
             self.deadline = timezone.now() + timezone.timedelta(days=days)

        super().save(*args, **kwargs)
        # Trigger parent update
        self.order.update_totals()

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.titular_name}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Efectivo'),
        ('TRANSFER', 'Transferencia'),
        ('STRIPE', 'Pasarela Online'),
    ]
    
    ACCOUNT_CHOICES = [
        ('SPAIN', 'Cuenta España'),
        ('CUBA', 'Cuenta Cuba'),
        ('OTHER', 'Otra'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Order.CURRENCY_CHOICES, default='EUR')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='TRANSFER')
    destination_account = models.CharField(max_length=20, choices=ACCOUNT_CHOICES, default='SPAIN', help_text="Cuenta de destino")
    receipt_sent = models.BooleanField(default=False, help_text="¿Se envió recibo al cliente?")
    proof_file = models.FileField(upload_to='payments/', blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.amount} {self.currency} - {self.order.order_friendly_id}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update order's total_paid
        order = self.order
        total_paid = sum(p.amount for p in order.payments.all())
        
        # Update payment_status
        if total_paid >= order.total_amount:
            payment_status = 'PAID'
        elif total_paid > 0:
            payment_status = 'PARTIAL'
        else:
            payment_status = 'PENDING'
        
        Order.objects.filter(pk=order.pk).update(
            total_paid=total_paid,
            payment_status=payment_status
        )


class ActivityLog(models.Model):
    """
    Registro de actividad para tracking de cambios en órdenes
    """
    ACTION_TYPES = [
        ('STATUS_CHANGE', 'Cambio de Estado'),
        ('PAYMENT', 'Registro de Pago'),
        ('EMAIL', 'Email Enviado'),
        ('NOTE', 'Nota Añadida'),
        ('ASSIGNMENT', 'Asignación'),
        ('DOCUMENT_UPLOAD', 'Documento Subido'),
        ('SERVICE_ADDED', 'Servicio Añadido'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True, help_text="Datos adicionales de la acción")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Registro de Actividad'
        verbose_name_plural = 'Registros de Actividad'
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.order.order_friendly_id} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
