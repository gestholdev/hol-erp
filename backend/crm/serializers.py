from rest_framework import serializers
from .models import Client, Order, ServiceItem, Payment, ActivityLog
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ServiceItemSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    assigned_tramitador_name = serializers.CharField(source='assigned_tramitador.username', read_only=True, allow_null=True)
    service_display_name = serializers.CharField(source='get_display_name', read_only=True)
    legalization_display = serializers.CharField(source='get_legalization_display', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    workflow_phases = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    document_abbreviation = serializers.CharField(source='get_document_abbreviation', read_only=True)
    
    class Meta:
        model = ServiceItem
        fields = [
            'id', 'service_type', 'document_type', 'legalization_type', 'titular_name', 'status', 
            'delivery_destination', 'assigned_tramitador', 'assigned_tramitador_name', 
            'responsible', 'logistics_status', 'current_location',
            'cost', 'price', 'margin', 'priority', 'deadline', 'phase_dates',
            'final_document', 'notes', 'is_overdue', 'created_at', 'updated_at',
            'service_display_name', 'legalization_display', 'document_type_display',
            'workflow_phases', 'days_until_deadline', 'document_abbreviation'
        ]
    
    def get_workflow_phases(self, obj):
        return obj.get_workflow_phases()
    
    def get_days_until_deadline(self, obj):
        if obj.deadline:
            from django.utils import timezone
            delta = obj.deadline - timezone.now()
            return delta.days
        return None

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'action_type', 'action_display', 'description', 'metadata', 'timestamp', 'user', 'user_name']

class OrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views (Kanban)"""
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_is_collaborator = serializers.BooleanField(source='client.is_collaborator', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    items_count = serializers.SerializerMethodField()
    has_express = serializers.SerializerMethodField()
    has_overdue = serializers.SerializerMethodField()
    payment_progress = serializers.SerializerMethodField()
    items = ServiceItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_friendly_id', 'client', 'client_name', 'client_is_collaborator',
            'global_status', 'payment_status', 'assigned_to', 'assigned_to_name',
            'currency', 'total_amount', 'total_paid', 'total_margin',
            'items_count', 'has_express', 'has_overdue', 'payment_progress',
            'created_at', 'updated_at', 'items'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_has_express(self, obj):
        return obj.items.filter(priority='EXPRESS').exists()
    
    def get_has_overdue(self, obj):
        return any(item.is_overdue for item in obj.items.all())
    
    def get_payment_progress(self, obj):
        if obj.total_amount > 0:
            return round((obj.total_paid / obj.total_amount) * 100, 1)
        return 0

class OrderDetailSerializer(serializers.ModelSerializer):
    """Complete serializer for detail view"""
    client_details = ClientSerializer(source='client', read_only=True)
    items = ServiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    activity_logs = ActivityLogSerializer(many=True, read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_friendly_id', 'client', 'client_details', 
            'assigned_to', 'assigned_to_details',
            'status', 'global_status', 'payment_status',
            'currency', 'total_amount', 'total_cost', 'total_margin', 'total_paid',
            'items', 'payments', 'activity_logs', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['order_friendly_id', 'total_amount', 'total_cost', 'total_margin', 'total_paid']

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for creating orders (Smart Cart)"""
    client_details = ClientSerializer(source='client', read_only=True)
    items = ServiceItemSerializer(many=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_friendly_id', 'client', 'client_details', 
            'status', 'global_status', 'currency', 'total_amount', 
            'created_at', 'items', 'payments', 'notes'
        ]
        read_only_fields = ['order_friendly_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            ServiceItem.objects.create(order=order, **item_data)
        return order
