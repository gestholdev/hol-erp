from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from crm.models import Order, ServiceItem, Client

class SmartCartTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.url = reverse('create-order')
        
        # Pre-create client
        self.test_client = Client.objects.create(
            email="test@example.com",
            full_name="Juan Perez",
            phone="+5355555555"
        )

    def test_create_smart_cart_order(self):
        """
        Test creating an order with multiple service items (Smart Cart).
        """
        payload = {
            "client": self.test_client.id,  # Use client ID
            "items": [
                {
                    "service_type": "LEGALIZATION",
                    "document_type": "Antecedentes Penales",
                    "titular_name": "Juan Perez",
                    "cost": 50.00,
                    "price": 150.00
                },
                {
                    "service_type": "VISA",
                    "titular_name": "Maria Perez",
                    "cost": 100.00,
                    "price": 300.00
                }
            ],
            "currency": "EUR"
        }

        response = self.client_api.post(self.url, payload, format='json')
        
        # Debug: Print response if error
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        
        # Check HTTP 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check Database
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(ServiceItem.objects.count(), 2)
        
        order = Order.objects.first()
        self.assertEqual(order.client.email, "test@example.com")
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.currency, "EUR")
        
        # Check Friendly ID generation
        self.assertTrue(order.order_friendly_id.startswith("JUANP"))
        
        # Check totals were calculated
        self.assertEqual(order.total_amount, 450.00)
