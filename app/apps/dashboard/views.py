from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from apps.customers.models import Customer
from apps.orders.models import Order, OrderStatus


@login_required
def dashboard_view(request):
    summary = Order.objects.aggregate(
        total=Count("pk"),
        pending=Count("pk", filter=Q(status=OrderStatus.PENDING)),
        in_progress=Count("pk", filter=Q(status=OrderStatus.IN_PROGRESS)),
        ready=Count("pk", filter=Q(status=OrderStatus.READY_FOR_PICKUP)),
        completed=Count("pk", filter=Q(status=OrderStatus.COMPLETED)),
    )
    recent_orders = Order.objects.select_related("customer", "service").order_by("-created_at")[:6]
    upcoming_deadlines = (
        Order.objects.select_related("customer", "service")
        .filter(deadline__gte=timezone.now())
        .exclude(status__in=(OrderStatus.COMPLETED, OrderStatus.CANCELLED))
        .order_by("deadline")[:5]
    )
    return render(
        request,
        "dashboard/dashboard.html",
        {
            "summary": summary,
            "customer_count": Customer.objects.count(),
            "recent_orders": recent_orders,
            "upcoming_deadlines": upcoming_deadlines,
        },
    )
