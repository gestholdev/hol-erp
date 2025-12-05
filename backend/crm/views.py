from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, fields, Case, When, Value, IntegerField
from django.utils import timezone
from .models import Client, Order, ServiceItem, Payment, ActivityLog
from .serializers import (
    ClientSerializer, OrderSerializer, OrderListSerializer, OrderDetailSerializer,
    ServiceItemSerializer, PaymentSerializer, ActivityLogSerializer
)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class CreateOrderView(APIView):
    """
    Smart Cart: Create an Order with multiple ServiceItems in one request
    """
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            
            # Create activity log
            ActivityLog.objects.create(
                order=order,
                user=request.user if request.user.is_authenticated else None,
                action_type='SERVICE_ADDED',
                description=f"Orden creada con {order.items.count()} servicios"
            )
            
            return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderKanbanView(APIView):
    """
    Get orders grouped by global_status for Kanban view
    """
    def get(self, request):
        # Get filter parameters
        assigned_to_me = request.query_params.get('assigned_to_me', None)
        with_debt = request.query_params.get('with_debt', None)
        urgent = request.query_params.get('urgent', None)
        location = request.query_params.get('location', None)
        
        queryset = Order.objects.all()
        
        # Apply filters
        if assigned_to_me and request.user.is_authenticated:
            queryset = queryset.filter(assigned_to=request.user)
        
        if with_debt:
            queryset = queryset.filter(total_paid__lt=F('total_amount'))
        
        if urgent:
            queryset = queryset.filter(items__priority='EXPRESS').distinct()
        
        if location:
            queryset = queryset.filter(items__current_location=location).distinct()
        
        # Group by global_status
        kanban_data = {}
        for choice_value, choice_label in Order.GLOBAL_STATUS_CHOICES:
            orders = queryset.filter(global_status=choice_value).order_by('-created_at')
            kanban_data[choice_value] = {
                'label': choice_label,
                'orders': OrderListSerializer(orders, many=True).data
            }
        
        return Response(kanban_data)

class OrderDetailView(APIView):
    """
    Get complete order details including items, payments, and activity log
    """
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        """Update order fields"""
        try:
            order = Order.objects.get(pk=pk)
            
            # Track changes for activity log
            changes = []
            if 'global_status' in request.data and request.data['global_status'] != order.global_status:
                old_status = order.get_global_status_display()
                order.global_status = request.data['global_status']
                new_status = order.get_global_status_display()
                changes.append(f"Estado cambiado de '{old_status}' a '{new_status}'")
            
            if 'assigned_to' in request.data:
                order.assigned_to_id = request.data['assigned_to']
                changes.append(f"Asignado a gestor")
            
            if 'notes' in request.data:
                order.notes = request.data['notes']
            
            order.save()
            
            # Log activity
            if changes:
                ActivityLog.objects.create(
                    order=order,
                    user=request.user if request.user.is_authenticated else None,
                    action_type='STATUS_CHANGE',
                    description='; '.join(changes)
                )
            
            return Response(OrderDetailSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class AddServiceToOrderView(APIView):
    """Add a new service item to an existing order"""
    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
            serializer = ServiceItemSerializer(data=request.data)
            
            if serializer.is_valid():
                service_item = serializer.save(order=order)
                
                # Log activity
                ActivityLog.objects.create(
                    order=order,
                    user=request.user if request.user.is_authenticated else None,
                    action_type='SERVICE_ADDED',
                    description=f"Servicio añadido: {service_item.get_service_type_display()}"
                )
                
                return Response(ServiceItemSerializer(service_item).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class RegisterPaymentView(APIView):
    """Register a payment for an order"""
    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
            data = request.data.copy()
            data['order'] = order.id
            
            serializer = PaymentSerializer(data=data)
            if serializer.is_valid():
                payment = serializer.save()
                
                # Log activity
                ActivityLog.objects.create(
                    order=order,
                    user=request.user if request.user.is_authenticated else None,
                    action_type='PAYMENT',
                    description=f"Pago registrado: {payment.amount} {payment.currency}",
                    metadata={'payment_id': payment.id, 'method': payment.method}
                )
                
                return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class RequestPaymentView(APIView):
    """(Mock) Send payment request email"""
    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
            # Here we would integrate with an email service
            
            ActivityLog.objects.create(
                order=order,
                user=request.user if request.user.is_authenticated else None,
                action_type='EMAIL_SENT',
                description="Solicitud de pago enviada al cliente"
            )
            return Response({'message': 'Payment request sent'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class GenerateInvoiceView(APIView):
    """(Mock) Generate invoice PDF"""
    def get(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
            # Here we would generate a real PDF
            
            ActivityLog.objects.create(
                order=order,
                user=request.user if request.user.is_authenticated else None,
                action_type='DOCUMENT_GENERATED',
                description="Factura generada"
            )
            
            # Mock file response
            response = Response("PDF CONTENT MOCK", content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_friendly_id}.txt"'
            return response
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class ActivityLogView(APIView):
    """Get activity log for an order"""
    def get(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
            logs = order.activity_logs.all()
            serializer = ActivityLogSerializer(logs, many=True)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class ServiceItemViewSet(viewsets.ModelViewSet):
    queryset = ServiceItem.objects.all()
    serializer_class = ServiceItemSerializer

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update service item status and location"""
        item = self.get_object()
        old_status = item.get_status_display()
        
        if 'status' in request.data:
            item.status = request.data['status']
        if 'current_location' in request.data:
            item.current_location = request.data['current_location']
        if 'assigned_tramitador' in request.data:
            item.assigned_tramitador_id = request.data['assigned_tramitador']
        if 'phase_dates' in request.data:
            item.phase_dates = request.data['phase_dates']
        
        item.save()
        
        # Log activity
        new_status = item.get_status_display()
        ActivityLog.objects.create(
            order=item.order,
            user=request.user if request.user.is_authenticated else None,
            action_type='STATUS_CHANGE',
            description=f"Servicio '{item.titular_name}': {old_status} → {new_status}"
        )
        
        return Response(ServiceItemSerializer(item).data)
    
    @action(detail=True, methods=['post'])
    def upload_final(self, request, pk=None):
        """Upload final document for service item"""
        item = self.get_object()
        
        if 'final_document' in request.FILES:
            item.final_document = request.FILES['final_document']
            item.save()
            
            # Log activity
            ActivityLog.objects.create(
                order=item.order,
                user=request.user if request.user.is_authenticated else None,
                action_type='DOCUMENT_UPLOAD',
                description=f"Documento final subido para '{item.titular_name}'"
            )
            
            return Response({'message': 'Document uploaded successfully'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

# Existing views
class OrderListView(APIView):
    def get(self, request):
        email = request.query_params.get('client_email', None)
        if email:
            orders = Order.objects.filter(client__email=email)
        else:
            orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class DashboardStatsView(APIView):
    def get(self, request):
        stats = {
            'active_orders': Order.objects.filter(status='PROCESSING').count(),
            'items_in_process': ServiceItem.objects.exclude(status__in=['READY', 'DELIVERED']).count(),
            'upcoming_deadlines': ServiceItem.objects.filter(
                deadline__lte=timezone.now() + timezone.timedelta(days=7),
                deadline__gte=timezone.now()
            ).count(),
            'total_revenue': Order.objects.filter(currency='EUR').aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'total_margin': Order.objects.filter(currency='EUR').aggregate(Sum('total_margin'))['total_margin__sum'] or 0,
        }
        return Response(stats)

class SmartQueueView(APIView):
    def get(self, request):
        now = timezone.now()
        
        items = ServiceItem.objects.exclude(status__in=['READY', 'DELIVERED']).annotate(
            urgency_score=Case(
                When(deadline__lt=now, then=Value(3)),  # Overdue
                When(priority='EXPRESS', then=Value(2)),  # Express
                default=Value(1),  # Normal
                output_field=IntegerField()
            )
        ).order_by('-urgency_score', 'deadline')
        
        serializer = ServiceItemSerializer(items, many=True)
        return Response(serializer.data)
