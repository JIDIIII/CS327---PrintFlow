from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.orders.models import Order, PrintService

from .models import Customer


class CustomersPageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="customeroperator",
            password="PrintFlow!2026Demo",
        )
        self.customer = Customer.objects.create(
            name="Jamie Rivera",
            contact_number="09171234567",
            email="jamie@example.com",
        )
        self.service = PrintService.objects.create(name="Flyer printing")
        Order.objects.create(
            order_number="PF-CUSTOMER01",
            customer=self.customer,
            service=self.service,
            size="A5",
            quantity=100,
            total_price=Decimal("100.00"),
            deadline=timezone.now() + timedelta(days=3),
            created_by=self.user,
        )
        self.client.force_login(self.user)

    def test_customers_page_shows_real_contact_and_order_count(self):
        response = self.client.get(reverse("customers:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jamie Rivera")
        self.assertContains(response, "JR")
        self.assertContains(response, "jamie@example.com")
        self.assertEqual(response.context["customers"][0].order_count, 1)
        self.assertEqual(response.context["total_customers"], 1)

    def test_customer_search_and_empty_state(self):
        response = self.client.get(reverse("customers:list"), {"q": "0917"})
        self.assertContains(response, "Jamie Rivera")

        response = self.client.get(reverse("customers:list"), {"q": "not found"})
        self.assertContains(response, "No matching customers")

        Order.objects.all().delete()
        Customer.objects.all().delete()
        response = self.client.get(reverse("customers:list"))
        self.assertContains(response, "No customers yet")
        self.assertEqual(response.context["total_customers"], 0)

    def test_customer_create_detail_and_edit_use_existing_model(self):
        response = self.client.post(
            reverse("customers:create"),
            {
                "name": "Casey Tan",
                "contact_number": "09180000000",
                "email": "casey@example.com",
                "address": "Quezon City",
                "notes": "Prefers uncoated stock.",
            },
        )
        customer = Customer.objects.get(name="Casey Tan")
        self.assertRedirects(response, reverse("customers:detail", args=[customer.pk]))
        self.assertContains(self.client.get(reverse("customers:detail", args=[customer.pk])), "Casey Tan")

        response = self.client.post(
            reverse("customers:edit", args=[customer.pk]),
            {
                "name": "Casey Tan",
                "contact_number": "09181112222",
                "email": "casey@example.com",
                "address": "Quezon City",
                "notes": "Prefers uncoated stock.",
            },
        )
        self.assertRedirects(response, reverse("customers:detail", args=[customer.pk]))
        customer.refresh_from_db()
        self.assertEqual(customer.contact_number, "09181112222")

    def test_customers_require_login(self):
        self.client.logout()
        response = self.client.get(reverse("customers:list"))
        self.assertRedirects(
            response,
            f"{reverse('login:login')}?next={reverse('customers:list')}",
        )
