from datetime import date

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse

from apps.orders.models import Order
from .forms import PaymentCreateForm

from .models import Payment


def _parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@login_required
def payment_list(request):
    payments = Payment.objects.select_related(
        "order", "order__customer", "recorded_by"
    )

    search = request.GET.get("q", "").strip()[:100]
    selected_status = request.GET.get("status", "").strip()[:50]
    date_from = request.GET.get("date_from", "").strip()[:10]
    date_to = request.GET.get("date_to", "").strip()[:10]
    parsed_from = _parse_date(date_from)
    parsed_to = _parse_date(date_to)

    status_values = sorted(
        set(Payment.objects.order_by().values_list("payment_status", flat=True))
    )
    status_choices = [(value, value.replace("_", " ").title()) for value in status_values]
    if selected_status not in status_values:
        selected_status = ""

    if search:
        payments = payments.filter(
            Q(order__order_number__icontains=search)
            | Q(order__customer__name__icontains=search)
            | Q(payment_method__icontains=search)
            | Q(payment_status__icontains=search)
            | Q(reference__icontains=search)
        )
    if selected_status:
        payments = payments.filter(payment_status=selected_status)
    if parsed_from:
        payments = payments.filter(paid_at__date__gte=parsed_from)
    if parsed_to:
        payments = payments.filter(paid_at__date__lte=parsed_to)

    summary = payments.aggregate(
        count=Count("pk"),
        amount=Sum("amount"),
        orders=Count("order_id", distinct=True),
    )
    page = Paginator(payments, 10).get_page(request.GET.get("page"))

    return render(
        request,
        "payments/payment_list.html",
        {
            "payments": page,
            "summary": summary,
            "search": search,
            "status_choices": status_choices,
            "selected_status": selected_status,
            "date_from": date_from,
            "date_to": date_to,
            "date_error": bool((date_from and not parsed_from) or (date_to and not parsed_to)),
        },
    )


@login_required
def payment_create(request, order_id):
    order = get_object_or_404(Order.objects.select_related("customer"), pk=order_id)
    form = PaymentCreateForm(request.POST or None, order=order)
    if request.method == "POST" and form.is_valid():
        payment = form.save_for_user(request.user)
        messages.success(request, f"Payment #{payment.pk} was recorded.")
        return redirect(reverse("orders:detail", args=[order.pk]))

    return render(
        request,
        "payments/payment_form.html",
        {"form": form, "order": order, "remaining": order.remaining_balance},
    )
