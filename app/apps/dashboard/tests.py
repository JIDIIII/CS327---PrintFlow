from django.contrib.auth import get_user_model
from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.customers.models import Customer
from apps.orders.models import Order, OrderStatus, PrintService


class ProtectedPageTests(TestCase):
    def test_home_is_public_and_shows_guest_actions(self):
        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("login:login"))
        self.assertContains(response, reverse("register:register"))

    def test_anonymous_dashboard_access_redirects_to_login(self):
        response = self.client.get(reverse("dashboard:dashboard"))
        expected = f"{reverse('login:login')}?next={reverse('dashboard:dashboard')}"

        self.assertRedirects(response, expected)

    def test_authenticated_user_can_open_home_and_dashboard(self):
        user = get_user_model().objects.create_user(
            username="printflowuser",
            password="PrintFlow!2026Demo",
        )
        self.client.force_login(user)

        home_response = self.client.get(reverse("home:home"))
        dashboard_response = self.client.get(reverse("dashboard:dashboard"))

        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, reverse("dashboard:dashboard"))
        self.assertContains(home_response, "Hello, printflowuser")
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, reverse("home:home"))

    def test_dashboard_summary_uses_real_orders_and_customers(self):
        user = get_user_model().objects.create_user(username="dashboardoperator")
        customer = Customer.objects.create(name="Taylor Park")
        service = PrintService.objects.create(name="Business cards")
        Order.objects.create(
            order_number="PF-DASH001",
            customer=customer,
            service=service,
            size="90 × 55 mm",
            quantity=250,
            total_price=Decimal("45.00"),
            deadline=timezone.now() + timedelta(days=2),
            status=OrderStatus.IN_PROGRESS,
            created_by=user,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard:dashboard"))

        self.assertContains(response, "PF-DASH001")
        self.assertEqual(response.context["summary"]["total"], 1)
        self.assertEqual(response.context["summary"]["in_progress"], 1)
        self.assertEqual(response.context["customer_count"], 1)
