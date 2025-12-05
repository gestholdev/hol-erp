from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Client, Order, ServiceItem, Payment, ActivityLog
from decimal import Decimal
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Populate database with test data for Kanban view'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        # Clear existing data
        ActivityLog.objects.all().delete()
        Payment.objects.all().delete()
        ServiceItem.objects.all().delete()
        Order.objects.all().delete()
        Client.objects.all().delete()
        
        # Create users
        self.stdout.write('Creating users...')
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@hol-crm.com', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin123')
        admin_user.save()
        
        gestor1, _ = User.objects.get_or_create(
            username='gestor1',
            defaults={'first_name': 'María', 'last_name': 'García', 'email': 'maria@hol-crm.com'}
        )
        
        gestor2, _ = User.objects.get_or_create(
            username='gestor2',
            defaults={'first_name': 'Carlos', 'last_name': 'López', 'email': 'carlos@hol-crm.com'}
        )
        
        tramitador1, _ = User.objects.get_or_create(
            username='tramitador1',
            defaults={'first_name': 'Ana', 'last_name': 'Martínez', 'email': 'ana@hol-crm.com'}
        )
        
        # Create clients
        self.stdout.write('Creating clients...')
        clients_data = [
            {'full_name': 'Juan Pérez', 'email': 'juan.perez@example.com', 'phone': '+34600111222', 'is_collaborator': False},
            {'full_name': 'María González', 'email': 'maria.gonzalez@example.com', 'phone': '+34600222333', 'is_collaborator': False},
            {'full_name': 'Pedro Rodríguez', 'email': 'pedro.rodriguez@example.com', 'phone': '+34600333444', 'is_collaborator': True},
            {'full_name': 'Ana Martín', 'email': 'ana.martin@example.com', 'phone': '+34600444555', 'is_collaborator': False},
            {'full_name': 'Luis Fernández', 'email': 'luis.fernandez@example.com', 'phone': '+34600555666', 'is_collaborator': False},
            {'full_name': 'Carmen Sánchez', 'email': 'carmen.sanchez@example.com', 'phone': '+34600666777', 'is_collaborator': True},
            {'full_name': 'Roberto Díaz', 'email': 'roberto.diaz@example.com', 'phone': '+34600777888', 'is_collaborator': False},
            {'full_name': 'Laura Torres', 'email': 'laura.torres@example.com', 'phone': '+34600888999', 'is_collaborator': False},
        ]
        
        clients = []
        for client_data in clients_data:
            client = Client.objects.create(**client_data)
            clients.append(client)
        
        # Create orders with different statuses
        self.stdout.write('Creating orders...')
        
        # Status distribution
        statuses = [
            'NEW_REQUEST',
            'PENDING_PAYMENT',
            'IN_PROCESS_PARTIAL',
            'IN_PROCESS_PAID',
            'READY_DELIVERY',
            'CLOSED'
        ]
        
        gestores = [gestor1, gestor2]
        
        for i, status in enumerate(statuses):
            # Create 2-3 orders per status
            num_orders = random.randint(2, 3)
            
            for j in range(num_orders):
                client = clients[(i * num_orders + j) % len(clients)]
                gestor = gestores[j % len(gestores)]
                
                # Create order
                order = Order.objects.create(
                    client=client,
                    created_by=admin_user,
                    assigned_to=gestor,
                    global_status=status,
                    currency='EUR',
                    created_at=timezone.now() - timezone.timedelta(days=random.randint(1, 30))
                )
                
                # Add service items
                num_items = random.randint(1, 3)
                is_express = random.choice([True, False])
                
                for k in range(num_items):
                    service_type = 'LEGALIZATION'  # Focus on legalizations
                    
                    # Document types using model choices
                    doc_types = ['ANTECEDENTES_PENALES', 'NACIMIENTO', 'MATRIMONIO', 'DIVORCIO', 'DEFUNCION']
                    leg_types = ['MINJUS', 'CONSULADO', 'MINJUS_CONSULADO']
                    destinations = ['INTERNACIONAL', 'HABANA', 'CAMAGUEY']
                    
                    document_type = random.choice(doc_types)
                    legalization_type = random.choice(leg_types)
                    delivery_destination = random.choice(destinations)
                    
                    cost = Decimal(random.randint(30, 80))
                    price = cost * Decimal('2.5')
                    
                    # Determine status based on order status, legalization type, and destination
                    if status in ['NEW_REQUEST', 'PENDING_PAYMENT']:
                        # Initial status depends on legalization type
                        if legalization_type == 'CONSULADO':
                            item_status = 'PENDING_RECEIVE'
                        else:
                            item_status = 'INIT'
                    elif status in ['IN_PROCESS_PARTIAL', 'IN_PROCESS_PAID']:
                        # Status depends on legalization type
                        if legalization_type == 'MINJUS_CONSULADO':
                            item_status = random.choice(['MINJUS_OUT', 'CONSULATE_OUT'])
                        elif legalization_type == 'MINJUS':
                            item_status = 'MINJUS_OUT'
                        else:  # CONSULADO
                            item_status = random.choice(['RECEIVED', 'LEGALIZED'])
                    elif status == 'READY_DELIVERY':
                        # Ready status depends on destination
                        if delivery_destination == 'INTERNACIONAL':
                            item_status = random.choice(['SENT_SPAIN', 'SENT_CLIENT'])
                        else:
                            item_status = 'READY_PICKUP'
                    else:
                        item_status = 'DELIVERED'
                    
                    # Create deadline (some overdue for testing)
                    days_until_deadline = random.choice([-5, -2, 3, 7, 10, 15])
                    deadline = timezone.now() + timezone.timedelta(days=days_until_deadline)
                    
                    # Titular names (different from client for variety)
                    titular_names = [client.full_name, 'José Martínez', 'Laura Rodríguez', 'Carlos Sánchez']
                    
                    # Logistics fields
                    responsible_options = ['OFICINA_CUBA', 'OFICINA_ESPANA', 'GESTOR_CAMPO']
                    location_options = ['OFICINA_HABANA', 'OFICINA_ESPANA', 'MINJUS', 'CONSULADO']
                    
                    item = ServiceItem.objects.create(
                        order=order,
                        service_type=service_type,
                        document_type=document_type,
                        legalization_type=legalization_type,
                        delivery_destination=delivery_destination,
                        titular_name=random.choice(titular_names),
                        status=item_status,
                        assigned_tramitador=tramitador1 if random.choice([True, False]) else None,
                        responsible=random.choice(responsible_options),
                        logistics_status='NA',
                        current_location=random.choice(location_options),
                        cost=cost,
                        price=price,
                        priority='EXPRESS' if is_express and k == 0 else 'NORMAL',
                        deadline=deadline
                    )
                
                # Add payments based on status
                if status in ['IN_PROCESS_PARTIAL', 'IN_PROCESS_PAID', 'READY_DELIVERY', 'CLOSED']:
                    # Add at least one payment
                    payment_amount = order.total_amount * Decimal('0.5')  # 50% payment
                    
                    Payment.objects.create(
                        order=order,
                        amount=payment_amount,
                        currency='EUR',
                        method='TRANSFER',
                        destination_account='SPAIN',
                        receipt_sent=True,
                        payment_date=order.created_at + timezone.timedelta(days=1)
                    )
                    
                    # For PAID status, add full payment
                    if status in ['IN_PROCESS_PAID', 'READY_DELIVERY', 'CLOSED']:
                        remaining = order.total_amount - payment_amount
                        Payment.objects.create(
                            order=order,
                            amount=remaining,
                            currency='EUR',
                            method='CASH',
                            destination_account='SPAIN',
                            receipt_sent=True,
                            payment_date=order.created_at + timezone.timedelta(days=5)
                        )
                
                # Add activity logs
                ActivityLog.objects.create(
                    order=order,
                    user=admin_user,
                    action_type='SERVICE_ADDED',
                    description=f'Orden creada con {order.items.count()} servicios',
                    timestamp=order.created_at
                )
                
                if order.payments.exists():
                    for payment in order.payments.all():
                        ActivityLog.objects.create(
                            order=order,
                            user=gestor,
                            action_type='PAYMENT',
                            description=f'Pago registrado: {payment.amount} EUR',
                            timestamp=payment.payment_date
                        )
                
                self.stdout.write(f'  Created order {order.order_friendly_id} - Status: {status}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {Order.objects.count()} orders!'))
        self.stdout.write(self.style.SUCCESS(f'✅ Total service items: {ServiceItem.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'✅ Total payments: {Payment.objects.count()}'))
        self.stdout.write('\nStatus distribution:')
        for status, label in Order.GLOBAL_STATUS_CHOICES:
            count = Order.objects.filter(global_status=status).count()
            self.stdout.write(f'  {label}: {count} orders')
