from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from crm.models import Order, Client

class ClientPortalTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.url = reverse('order-list')
        
        # Client A
        self.client_a = Client.objects.create(email="alice@test.com", full_name="Alice")
        self.order_a = Order.objects.create(client=self.client_a)
        
        # Client B
        self.client_b = Client.objects.create(email="bob@test.com", full_name="Bob")
        self.order_b = Order.objects.create(client=self.client_b)

    def test_filter_by_email(self):
        """
        Test that passing ?client_email=... filters the orders.
        """
        # 1. Filter for Alice
        response = self.client_api.get(self.url, {'client_email': 'alice@test.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order_a.id)

        # 2. Filter for Bob
        response = self.client_api.get(self.url, {'client_email': 'bob@test.com'})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order_b.id)

        # 3. Filter for Unknown
        response = self.client_api.get(self.url, {'client_email': 'unknown@test.com'})
        self.assertEqual(len(response.data), 0)

        # 4. No Filter (Should return all)
        response = self.client_api.get(self.url)
        self.assertEqual(len(response.data), 2)
