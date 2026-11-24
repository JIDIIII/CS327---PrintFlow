from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from apps.orders.models import Order, OrderStatus
from apps.payments.models import Payment


def _date_value(value, fallback):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return fallback


@login_required
def report_summary(request):
    today = timezone.localdate()
    first_of_month = today.replace(day=1)
    raw_from = request.GET.get("date_from", "")
    raw_to = request.GET.get("date_to", "")
    date_from = _date_value(raw_from, first_of_month)
    date_to = _date_value(raw_to, today)
    date_error = bool((raw_from and _date_value(raw_from, None) is None) or (raw_to and _date_value(raw_to, None) is None))
    if date_from > date_to:
        date_error = True
        date_from, date_to = first_of_month, today

    created_orders = Order.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)
    created = created_orders.aggregate(
        count=Count("pk"),
        value=Coalesce(Sum("total_price"), Value(Decimal("0.00")), output_field=DecimalField(max_digits=14, decimal_places=2)),
    )
    completed = Order.objects.filter(
        status=OrderStatus.COMPLETED,
        completed_at__date__gte=date_from,
        completed_at__date__lte=date_to,
    ).aggregate(
        count=Count("pk"),
        value=Coalesce(Sum("total_price"), Value(Decimal("0.00")), output_field=DecimalField(max_digits=14, decimal_places=2)),
    )
    payments = Payment.objects.filter(paid_at__date__gte=date_from, paid_at__date__lte=date_to).aggregate(
        count=Count("pk"),
        value=Coalesce(Sum("amount"), Value(Decimal("0.00")), output_field=DecimalField(max_digits=14, decimal_places=2)),
    )
    balances = created_orders.annotate(
        paid_total=Coalesce(
            Sum("payments__amount"),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
    ).values_list("total_price", "paid_total")
    outstanding = sum((max(total - paid, Decimal("0.00")) for total, paid in balances), Decimal("0.00"))

    return render(
        request,
        "reports/summary.html",
        {
            "date_from": date_from,
            "date_to": date_to,
            "date_error": date_error,
            "created": created,
            "completed": completed,
            "payments": payments,
            "outstanding": outstanding,
        },
    )
