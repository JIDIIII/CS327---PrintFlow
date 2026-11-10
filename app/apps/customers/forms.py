from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "contact_number", "email", "address", "notes")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "contact_number": forms.TextInput(
                attrs={"type": "tel", "autocomplete": "tel", "inputmode": "tel"}
            ),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "address": forms.Textarea(attrs={"rows": 3, "autocomplete": "street-address"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["aria-describedby"] = f"id_{name}-errors"
