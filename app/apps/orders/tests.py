from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from apps.customers.models import Customer
from apps.payments.models import Payment

from .models import Order, OrderItem, OrderStatus, OrderStatusHistory, PrintService


class OrdersPageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="shopoperator",
            password="PrintFlow!2026Demo",
        )
        self.customer = Customer.objects.create(
            name="Morgan Lee",
            email="morgan@example.com",
        )
        self.service = PrintService.objects.create(
            name="Poster printing",
            price=Decimal("12.50"),
            is_active=True,
        )
        self.order = Order.objects.create(
            order_number="PF-ORDER0001",
            customer=self.customer,
            service=self.service,
            size="A3",
            quantity=2,
            total_price=Decimal("25.00"),
            deadline=timezone.now() + timedelta(days=2),
            created_by=self.user,
        )
        self.client.force_login(self.user)

    def test_orders_page_uses_actual_values_and_related_payment_data(self):
        Payment.objects.create(
            order=self.order,
            amount=Decimal("10.00"),
            recorded_by=self.user,
        )

        response = self.client.get(reverse("orders:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PF-ORDER0001")
        self.assertContains(response, "Morgan Lee")
        self.assertContains(response, "Partially Paid")
        self.assertEqual(response.context["summary"]["total"], 1)
        self.assertEqual(response.context["summary"]["pending"], 1)

    def test_search_and_status_filters_work(self):
        response = self.client.get(
            reverse("orders:list"),
            {"q": "Morgan", "status": OrderStatus.PENDING},
        )
        self.assertContains(response, "PF-ORDER0001")

        response = self.client.get(
            reverse("orders:list"),
            {"q": "Morgan", "status": OrderStatus.COMPLETED},
        )
        self.assertContains(response, "No matching orders")

    def test_empty_orders_state_and_zero_summary(self):
        Order.objects.all().delete()
        response = self.client.get(reverse("orders:list"))
        self.assertContains(response, "No orders yet")
        self.assertEqual(response.context["summary"]["total"], 0)

    def test_order_list_payment_summary_does_not_query_per_row(self):
        for index in range(5):
            Order.objects.create(
                order_number=f"PF-BATCH{index:04d}",
                customer=self.customer,
                service=self.service,
                size="A4",
                quantity=1,
                total_price=Decimal("12.50"),
                deadline=timezone.now() + timedelta(days=3),
                created_by=self.user,
            )

        with CaptureQueriesContext(connection) as captured:
            response = self.client.get(reverse("orders:list"))

        self.assertEqual(response.status_code, 200)
        payment_queries = [
            query for query in captured.captured_queries
            if "payments_payment" in query["sql"]
        ]
        self.assertLessEqual(len(payment_queries), 2)

    def test_new_order_is_created_with_existing_models_and_price(self):
        deadline = (timezone.now() + timedelta(days=4)).strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(
            reverse("orders:create"),
            {
                "customer": self.customer.pk,
                "service": self.service.pk,
                "size": "A4",
                "quantity": 3,
                "deadline": deadline,
                "special_instructions": "Matte finish",
            },
        )

        order = Order.objects.exclude(pk=self.order.pk).get()
        self.assertRedirects(response, reverse("orders:detail", args=[order.pk]))
        self.assertEqual(order.total_price, Decimal("37.50"))
        self.assertEqual(order.created_by, self.user)
        self.assertEqual(OrderItem.objects.filter(order=order).count(), 1)
        self.assertEqual(
            OrderStatusHistory.objects.filter(order=order, to_status=OrderStatus.PENDING).count(),
            1,
        )

    def test_orders_require_login_and_detail_does_not_expose_an_unknown_id(self):
        self.client.logout()
        response = self.client.get(reverse("orders:list"))
        self.assertRedirects(response, f"{reverse('login:login')}?next={reverse('orders:list')}")

        self.client.force_login(self.user)
        missing = self.client.get(reverse("orders:detail", args=[99999]))
        self.assertEqual(missing.status_code, 404)
