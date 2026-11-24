from decimal import Decimal

from django import forms

from .models import Payment


class PaymentCreateForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("amount", "payment_method", "reference", "note")
        widgets = {
            "amount": forms.NumberInput(attrs={"min": "0.01", "step": "0.01", "inputmode": "decimal"}),
            "payment_method": forms.TextInput(attrs={"placeholder": "Cash, card, bank transfer"}),
            "reference": forms.TextInput(attrs={"autocomplete": "off"}),
            "note": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, order, **kwargs):
        self.order = order
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        paid = self.order.amount_paid
        remaining = max(self.order.total_price - paid, Decimal("0.00"))
        if amount > remaining:
            raise forms.ValidationError(
                f"Payment cannot exceed the remaining balance of ₱{remaining:.2f}."
            )
        return amount

    def save_for_user(self, user):
        payment = super().save(commit=False)
        payment.order = self.order
        payment.recorded_by = user
        payment.save()
        return payment
