from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from crm.models import Order, ServiceItem, Client

class SmartQueueTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.crm_client = Client.objects.create(email="queue@test.com", full_name="Queue Client")
        self.order = Order.objects.create(client=self.crm_client)
        self.url = reverse('smart-queue')

    def test_queue_prioritization(self):
        """
        Test that the queue orders items by:
        1. Overdue (Critical)
        2. Express (High)
        3. Normal (Standard)
        """
        now = timezone.now()

        # 1. Create Normal Item (Deadline = Now + 15 days)
        normal_item = ServiceItem.objects.create(
            order=self.order,
            service_type="LEGALIZATION",
            titular_name="Normal Item",
            priority="NORMAL"
        )
        
        # 2. Create Express Item (Deadline = Now + 3 days)
        express_item = ServiceItem.objects.create(
            order=self.order,
            service_type="VISA",
            titular_name="Express Item",
            priority="EXPRESS"
        )

        # 3. Create Overdue Item (Deadline = Yesterday)
        overdue_item = ServiceItem.objects.create(
            order=self.order,
            service_type="LEGALIZATION",
            titular_name="Overdue Item",
            priority="NORMAL"
        )
        # Manually set deadline to past
        overdue_item.deadline = now - timezone.timedelta(days=1)
        overdue_item.save()

        # Call API
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data
        self.assertEqual(len(results), 3)
        
        # Verify Order
        self.assertEqual(results[0]['id'], overdue_item.id) # Overdue first
        self.assertEqual(results[1]['id'], express_item.id) # Express second
        self.assertEqual(results[2]['id'], normal_item.id) # Normal last
