from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CreateOrderView, OrderListView, OrderKanbanView, OrderDetailView,
    AddServiceToOrderView, RegisterPaymentView, ActivityLogView,
    DashboardStatsView, ServiceItemViewSet, SmartQueueView,
    RequestPaymentView, GenerateInvoiceView
)

router = DefaultRouter()
router.register(r'service-items', ServiceItemViewSet, basename='service-item')

urlpatterns = [
    # Order Management
    path('orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/kanban/', OrderKanbanView.as_view(), name='order-kanban'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/add-service/', AddServiceToOrderView.as_view(), name='add-service'),
    path('orders/<int:order_id>/payments/', RegisterPaymentView.as_view(), name='register-payment'),
    path('orders/<int:order_id>/request-payment/', RequestPaymentView.as_view(), name='request-payment'),
    path('orders/<int:order_id>/invoice/', GenerateInvoiceView.as_view(), name='generate-invoice'),
    path('orders/<int:order_id>/activity-log/', ActivityLogView.as_view(), name='activity-log'),
    
    # Dashboard & Queue
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('smart-queue/', SmartQueueView.as_view(), name='smart-queue'),
] + router.urls
