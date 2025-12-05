from django.test import TestCase
from crm.models import Order, ServiceItem, Client

class FinancialTests(TestCase):
    def setUp(self):
        self.client = Client.objects.create(email="finance@test.com", full_name="Finance Client")
        self.order = Order.objects.create(client=self.client, currency="EUR")

    def test_financial_calculations(self):
        """
        Test that Order totals are updated when ServiceItems are added/modified.
        """
        # 1. Add Item 1 (Price: 100, Cost: 20)
        item1 = ServiceItem.objects.create(
            order=self.order,
            service_type="LEGALIZATION",
            titular_name="Doc 1",
            price=100.00,
            cost=20.00
        )
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, 100.00)
        self.assertEqual(self.order.total_cost, 20.00)
        self.assertEqual(self.order.total_margin, 80.00)

        # 2. Add Item 2 (Price: 50, Cost: 10)
        item2 = ServiceItem.objects.create(
            order=self.order,
            service_type="VISA",
            titular_name="Doc 2",
            price=50.00,
            cost=10.00
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, 150.00)
        self.assertEqual(self.order.total_cost, 30.00)
        self.assertEqual(self.order.total_margin, 120.00)

        # 3. Update Item 1 Cost (Cost: 20 -> 50)
        item1.cost = 50.00
        item1.save()

        self.order.refresh_from_db()
        self.assertEqual(self.order.total_cost, 60.00) # 50 + 10
        self.assertEqual(self.order.total_margin, 90.00) # 150 - 60
