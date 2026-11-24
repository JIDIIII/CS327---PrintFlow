from django import forms

from apps.orders.models import PrintService


class PrintServiceForm(forms.ModelForm):
    class Meta:
        model = PrintService
        fields = ("name", "category", "description", "price", "is_active")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "off"}),
            "category": forms.TextInput(attrs={"placeholder": "e.g. Signage, stationery"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01", "inputmode": "decimal"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_active"].label = "Available for new orders"
