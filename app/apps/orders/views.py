from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from apps.customers.models import Customer

from .forms import OrderCreateForm
from .models import Order, OrderStatus, PaymentStatus, PrintService


@login_required
def order_list(request):
    orders = Order.objects.select_related("customer", "service").annotate(
        paid_total=Coalesce(
            Sum("payments__amount"),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    ).order_by("deadline", "created_at", "pk")
    search = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    if search:
        orders = orders.filter(
            Q(order_number__icontains=search)
            | Q(customer__name__icontains=search)
            | Q(service__name__icontains=search)
        )
    valid_statuses = {value for value, _label in OrderStatus.choices}
    if selected_status in valid_statuses:
        orders = orders.filter(status=selected_status)
    else:
        selected_status = ""
    parsed_from = parse_date(date_from)
    parsed_to = parse_date(date_to)
    if parsed_from:
        orders = orders.filter(created_at__date__gte=parsed_from)
    if parsed_to:
        orders = orders.filter(created_at__date__lte=parsed_to)

    summary = Order.objects.aggregate(
        total=Count("pk"),
        pending=Count("pk", filter=Q(status=OrderStatus.PENDING)),
        in_progress=Count("pk", filter=Q(status=OrderStatus.IN_PROGRESS)),
        ready=Count("pk", filter=Q(status=OrderStatus.READY_FOR_PICKUP)),
        completed=Count("pk", filter=Q(status=OrderStatus.COMPLETED)),
    )
    page_obj = Paginator(orders, 20).get_page(request.GET.get("page"))
    for order in page_obj.object_list:
        paid_total = order.paid_total or Decimal("0.00")
        if paid_total <= 0:
            order.payment_label = PaymentStatus.UNPAID.label
            order.payment_key = "unpaid"
        elif paid_total < order.total_price:
            order.payment_label = PaymentStatus.PARTIALLY_PAID.label
            order.payment_key = "partial"
        else:
            order.payment_label = PaymentStatus.PAID.label
            order.payment_key = "paid"

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": page_obj,
            "summary": summary,
            "search": search,
            "selected_status": selected_status,
            "date_from": parsed_from.isoformat() if parsed_from else "",
            "date_to": parsed_to.isoformat() if parsed_to else "",
            "status_choices": OrderStatus.choices,
        },
    )


@login_required
def order_create(request):
    form = OrderCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        order = form.save_for_user(request.user)
        messages.success(request, f"Order {order.order_number} was created.")
        return redirect("orders:detail", pk=order.pk)

    return render(
        request,
        "orders/order_form.html",
        {
            "form": form,
            "has_customers": Customer.objects.exists(),
            "has_services": PrintService.objects.filter(is_active=True).exists(),
        },
    )


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("customer", "service", "created_by").prefetch_related(
            "items__service", "payments", "status_history__changed_by"
        ),
        pk=pk,
    )
    order.paid_total = sum((payment.amount for payment in order.payments.all()), Decimal("0.00"))
    if order.paid_total <= 0:
        order.payment_label = PaymentStatus.UNPAID.label
    elif order.paid_total < order.total_price:
        order.payment_label = PaymentStatus.PARTIALLY_PAID.label
    else:
        order.payment_label = PaymentStatus.PAID.label
    order.remaining_display = max(order.total_price - order.paid_total, Decimal("0.00"))
    return render(request, "orders/order_detail.html", {"order": order})
