from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class ProfileFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="profileuser",
            password="PrintFlow!2026Demo",
        )

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile:profile"))
        self.assertRedirects(
            response,
            f"{reverse('login:login')}?next={reverse('profile:profile')}",
        )

    def test_profile_is_created_for_legacy_user_and_can_be_saved(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("profile:profile"),
            {
                "first_name": "Print",
                "last_name": "Operator",
                "email": "print@example.com",
                "full_name": "Print Operator",
                "bio": "Runs the print shop.",
            },
        )

        self.assertRedirects(response, reverse("profile:profile"))
        self.user.refresh_from_db()
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(self.user.email, "print@example.com")
        self.assertEqual(profile.full_name, "Print Operator")
