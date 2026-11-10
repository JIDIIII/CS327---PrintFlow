from uuid import uuid4

from django import forms
from django.db import transaction
from django.utils import timezone

from apps.customers.models import Customer

from .models import Order, OrderItem, OrderStatus, OrderStatusHistory, PrintService


class OrderCreateForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={"type": "datetime-local", "autocomplete": "off"},
        ),
    )

    class Meta:
        model = Order
        fields = ("customer", "service", "size", "quantity", "deadline", "special_instructions")
        widgets = {
            "customer": forms.Select(attrs={"autocomplete": "off"}),
            "service": forms.Select(attrs={"autocomplete": "off"}),
            "size": forms.TextInput(attrs={"placeholder": "e.g. A4, 12 × 18 in"}),
            "quantity": forms.NumberInput(attrs={"min": 1, "inputmode": "numeric"}),
            "special_instructions": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Finishing, paper stock, or delivery notes"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.order_by("name", "id")
        self.fields["service"].queryset = PrintService.objects.filter(is_active=True)
        for name, field in self.fields.items():
            field.widget.attrs["aria-describedby"] = f"id_{name}-errors"

    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]
        if deadline <= timezone.now():
            raise forms.ValidationError("Choose a deadline in the future.")
        return deadline

    @transaction.atomic
    def save_for_user(self, user):
        order = super().save(commit=False)
        order.order_number = f"PF-{uuid4().hex[:10].upper()}"
        order.created_by = user
        order.total_price = order.service.price * order.quantity
        order.save()
        OrderItem.objects.create(
            order=order,
            service=order.service,
            quantity=order.quantity,
            subtotal=order.total_price,
        )
        OrderStatusHistory.objects.create(
            order=order,
            from_status="",
            to_status=OrderStatus.PENDING,
            changed_by=user,
        )
        self.save_m2m()
        return order
