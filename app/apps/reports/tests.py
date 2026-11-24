from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.customers.models import Customer
from apps.orders.models import Order, OrderStatus, PrintService
from apps.payments.models import Payment


class ReportSummaryTests(TestCase):
    def test_report_calculates_orders_completed_payments_and_balance_for_range(self):
        user = get_user_model().objects.create_user(username="reportoperator")
        customer = Customer.objects.create(name="Nico Santos")
        service = PrintService.objects.create(name="Report test print", price=Decimal("40.00"))
        order = Order.objects.create(
            order_number="PF-REPORT001",
            customer=customer,
            service=service,
            size="A4",
            quantity=1,
            total_price=Decimal("40.00"),
            deadline=timezone.now() + timedelta(days=2),
            status=OrderStatus.COMPLETED,
            created_by=user,
        )
        Payment.objects.create(order=order, amount=Decimal("15.00"), recorded_by=user)
        self.client.force_login(user)
        today = timezone.localdate().isoformat()
        response = self.client.get(reverse("reports:summary"), {"date_from": today, "date_to": today})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["created"]["count"], 1)
        self.assertEqual(response.context["created"]["value"], Decimal("40.00"))
        self.assertEqual(response.context["completed"]["count"], 1)
        self.assertEqual(response.context["payments"]["value"], Decimal("15.00"))
        self.assertEqual(response.context["outstanding"], Decimal("25.00"))
