from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class RegistrationFlowTests(TestCase):
    registration_data = {
        "first_name": "Alex",
        "last_name": "Printer",
        "username": "alexprinter",
        "email": "alex@example.com",
        "password1": "PrintFlow!2026Demo",
        "password2": "PrintFlow!2026Demo",
    }

    def test_registration_creates_hashed_user_then_redirects_to_login(self):
        response = self.client.post(
            reverse("register:register"), self.registration_data
        )

        self.assertRedirects(response, reverse("login:login"))
        user = get_user_model().objects.get(username="alexprinter")
        self.assertTrue(user.check_password("PrintFlow!2026Demo"))
        self.assertNotEqual(user.password, "PrintFlow!2026Demo")

    def test_duplicate_username_displays_validation_error(self):
        get_user_model().objects.create_user(
            username="alexprinter",
            password="Existing!2026Password",
        )

        response = self.client.post(
            reverse("register:register"), self.registration_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "username",
            "A user with that username already exists.",
        )
