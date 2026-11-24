from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.customers.models import Customer
from apps.orders.models import Order, PrintService
from .models import Payment


class PaymentRecordingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="paymentoperator",
            password="PrintFlow!2026Demo",
        )
        self.customer = Customer.objects.create(name="Sam Rivera")
        self.service = PrintService.objects.create(
            name="Flyer printing",
            price=Decimal("20.00"),
        )
        self.order = Order.objects.create(
            order_number="PF-PAYMENT001",
            customer=self.customer,
            service=self.service,
            size="A5",
            quantity=2,
            total_price=Decimal("40.00"),
            deadline=timezone.now() + timedelta(days=3),
            created_by=self.user,
        )
        self.client.force_login(self.user)

    def test_payment_is_recorded_for_order_and_user(self):
        response = self.client.post(
            reverse("payments:create", args=[self.order.pk]),
            {"amount": "15.00", "payment_method": "Cash", "reference": "RCPT-18", "note": "Deposit"},
        )
        self.assertRedirects(response, reverse("orders:detail", args=[self.order.pk]))
        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.amount, Decimal("15.00"))
        self.assertEqual(payment.recorded_by, self.user)
        self.assertEqual(payment.payment_method, "Cash")
        self.assertEqual(self.order.remaining_balance, Decimal("25.00"))

    def test_payment_over_remaining_balance_is_rejected(self):
        Payment.objects.create(
            order=self.order,
            amount=Decimal("35.00"),
            recorded_by=self.user,
        )
        response = self.client.post(
            reverse("payments:create", args=[self.order.pk]),
            {"amount": "6.00", "payment_method": "Cash", "reference": "", "note": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment cannot exceed the remaining balance")
        self.assertEqual(Payment.objects.filter(order=self.order).count(), 1)

    def test_payment_entry_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("payments:create", args=[self.order.pk]))
        expected = f"{reverse('login:login')}?next={reverse('payments:create', args=[self.order.pk])}"
        self.assertRedirects(response, expected)
