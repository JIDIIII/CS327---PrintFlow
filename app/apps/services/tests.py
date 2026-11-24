from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.orders.models import PrintService


class ServiceManagementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="serviceoperator")
        self.client.force_login(self.user)

    def test_service_can_be_created_and_edited(self):
        response = self.client.post(
            reverse("services:create"),
            {"name": "Window decals", "category": "Signage", "description": "Outdoor vinyl", "price": "12.50", "is_active": "on"},
        )
        self.assertRedirects(response, reverse("services:list"))
        service = PrintService.objects.get(name="Window decals")
        self.assertEqual(service.price, Decimal("12.50"))
        response = self.client.post(
            reverse("services:edit", args=[service.pk]),
            {"name": "Window decals", "category": "Vinyl", "description": "Weatherproof", "price": "14.00"},
        )
        self.assertRedirects(response, reverse("services:list"))
        service.refresh_from_db()
        self.assertEqual(service.price, Decimal("14.00"))
        self.assertFalse(service.is_active)

    def test_services_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("services:list"))
        self.assertEqual(response.status_code, 302)
