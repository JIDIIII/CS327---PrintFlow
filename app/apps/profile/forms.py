from django import forms
from django.contrib.auth.models import User

from .models import Profile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["aria-describedby"] = f"id_{name}-errors"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("full_name", "bio")
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "How should we address you?"}),
            "bio": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Tell us a little about your role."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["aria-describedby"] = f"id_{name}-errors"
