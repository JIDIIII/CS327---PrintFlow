from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginFlowTests(TestCase):
    def test_login_page_renders(self):
        self.assertEqual(self.client.get(reverse("login:login")).status_code, 200)

    def test_valid_login_redirects_to_home_and_logout_ends_session(self):
        get_user_model().objects.create_user(
            username="alexprinter",
            password="PrintFlow!2026Demo",
        )

        login_response = self.client.post(
            reverse("login:login"),
            {"username": "alexprinter", "password": "PrintFlow!2026Demo"},
        )
        self.assertRedirects(login_response, reverse("home:home"))
        self.assertEqual(self.client.get(reverse("home:home")).status_code, 200)

        logout_response = self.client.post(reverse("login:logout"))
        self.assertRedirects(logout_response, reverse("home:home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_invalid_login_stays_on_login_page(self):
        response = self.client.post(
            reverse("login:login"),
            {"username": "unknown", "password": "incorrect"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")
