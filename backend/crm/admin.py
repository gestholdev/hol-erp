from django.contrib import admin
from .models import Client, Order, ServiceItem, Payment, ActivityLog

class ServiceItemInline(admin.TabularInline):
    model = ServiceItem
    extra = 0
    fields = ('service_type', 'titular_name', 'status', 'assigned_tramitador', 'priority', 'price')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('amount', 'currency', 'method', 'destination_account', 'payment_date')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'is_collaborator', 'created_at')
    search_fields = ('full_name', 'email', 'identity_doc')
    list_filter = ('is_collaborator',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_friendly_id', 'client', 'global_status', 'payment_status', 'total_amount', 'total_paid', 'currency', 'created_at')
    list_filter = ('global_status', 'payment_status', 'currency', 'created_at')
    search_fields = ('order_friendly_id', 'client__full_name', 'client__email')
    readonly_fields = ('order_friendly_id', 'total_amount', 'total_cost', 'total_margin', 'total_paid')
    inlines = [ServiceItemInline, PaymentInline]

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'order', 'status', 'assigned_tramitador', 'priority', 'current_location', 'deadline')
    list_filter = ('status', 'service_type', 'priority')
    search_fields = ('titular_name', 'order__order_friendly_id')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'currency', 'method', 'destination_account', 'receipt_sent', 'payment_date')
    list_filter = ('method', 'destination_account', 'receipt_sent')
    search_fields = ('order__order_friendly_id',)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'action_type', 'user', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('order__order_friendly_id', 'description')
    readonly_fields = ('timestamp',)
