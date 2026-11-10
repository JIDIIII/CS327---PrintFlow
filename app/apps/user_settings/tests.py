from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import UserSettings


class UserSettingsFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="settingsuser",
            password="PrintFlow!2026Demo",
        )

    def test_settings_requires_authentication(self):
        response = self.client.get(reverse("user_settings:settings"))
        self.assertRedirects(
            response,
            f"{reverse('login:login')}?next={reverse('user_settings:settings')}",
        )

    def test_settings_are_created_and_saved_for_current_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("user_settings:settings"),
            {"dark_mode": "on"},
        )

        self.assertRedirects(response, reverse("user_settings:settings"))
        record = UserSettings.objects.get(user=self.user)
        self.assertTrue(record.dark_mode)
        self.assertFalse(record.email_notifications)

        dashboard = self.client.get(reverse("dashboard:dashboard"))
        self.assertContains(dashboard, 'data-theme="dark"')
