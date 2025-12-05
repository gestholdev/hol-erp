from django.core.management.base import BaseCommand
from crm.models import Client, Procedure
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Procedure.objects.all().delete()
        Client.objects.all().delete()

        # Create clients
        clients_data = [
            {'full_name': 'María García', 'email': 'maria@example.com', 'phone': '+34 600 123 456'},
            {'full_name': 'John Smith', 'email': 'john@example.com', 'phone': '+1 555 0100'},
            {'full_name': 'Ahmed Hassan', 'email': 'ahmed@example.com', 'phone': '+20 100 123 4567'},
            {'full_name': 'Li Wei', 'email': 'liwei@example.com', 'phone': '+86 138 0000 0000'},
            {'full_name': 'Sofia Rossi', 'email': 'sofia@example.com', 'phone': '+39 320 123 4567'},
        ]

        clients = []
        for data in clients_data:
            client = Client.objects.create(**data)
            clients.append(client)
            self.stdout.write(self.style.SUCCESS(f'Created client: {client.full_name}'))

        # Create procedures
        procedures_data = [
            {'client': clients[0], 'visa_type': 'Golden Visa', 'status': 'RECEPCION', 'deadline': date.today() + timedelta(days=30)},
            {'client': clients[1], 'visa_type': 'Residencia Temporal', 'status': 'REVISION', 'deadline': date.today() + timedelta(days=15)},
            {'client': clients[2], 'visa_type': 'Permiso de Trabajo', 'status': 'PRESENTACION', 'deadline': date.today() + timedelta(days=45)},
            {'client': clients[3], 'visa_type': 'Reagrupación Familiar', 'status': 'APROBACION', 'deadline': date.today() + timedelta(days=10)},
            {'client': clients[4], 'visa_type': 'Golden Visa', 'status': 'RECEPCION', 'deadline': date.today() + timedelta(days=60)},
            {'client': clients[0], 'visa_type': 'Renovación NIE', 'status': 'REVISION', 'deadline': date.today() + timedelta(days=20)},
            {'client': clients[1], 'visa_type': 'Nacionalidad', 'status': 'PRESENTACION', 'deadline': date.today() + timedelta(days=90)},
        ]

        for data in procedures_data:
            procedure = Procedure.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'Created procedure: {procedure.visa_type} for {procedure.client.full_name}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Database populated successfully!'))
