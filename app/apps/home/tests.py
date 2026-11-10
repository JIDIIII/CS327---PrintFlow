from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_is_public_and_shows_guest_actions(self):
        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("login:login"))
        self.assertContains(response, reverse("register:register"))

    def test_authenticated_home_shows_account_navigation(self):
        user = get_user_model().objects.create_user(
            username="printflowuser",
            first_name="Print",
            password="PrintFlow!2026Demo",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, Print")
        self.assertContains(response, reverse("dashboard:dashboard"))
        self.assertContains(response, reverse("profile:profile"))
        self.assertContains(response, reverse("user_settings:settings"))
        self.assertContains(response, reverse("orders:list"))
        self.assertContains(response, reverse("customers:list"))
