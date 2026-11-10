from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerForm
from .models import Customer


def _initials(name):
    parts = name.strip().split()
    if not parts:
        return "?"
    return "".join(part[0] for part in (parts[:2] if len(parts) > 1 else parts)).upper()


@login_required
def customer_list(request):
    search = request.GET.get("q", "").strip()
    customers = Customer.objects.annotate(order_count=Count("orders", distinct=True)).order_by("name", "pk")
    if search:
        customers = customers.filter(
            Q(name__icontains=search)
            | Q(contact_number__icontains=search)
            | Q(email__icontains=search)
            | Q(user__username__icontains=search)
            | Q(user__email__icontains=search)
        )

    page_obj = Paginator(customers, 20).get_page(request.GET.get("page"))
    for customer in page_obj.object_list:
        customer.initials = _initials(customer.name)

    return render(
        request,
        "customers/customer_list.html",
        {
            "customers": page_obj,
            "total_customers": Customer.objects.count(),
            "search": search,
        },
    )


@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        customer = form.save()
        messages.success(request, f"{customer.name} was added to your customers.")
        return redirect("customers:detail", pk=customer.pk)
    return render(request, "customers/customer_form.html", {"form": form, "is_new": True})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    recent_orders = customer.orders.select_related("service").order_by("-created_at")[:8]
    name_parts = customer.name.split()
    customer.initials = "".join(part[0] for part in name_parts[:2]).upper()
    return render(
        request,
        "customers/customer_detail.html",
        {
            "customer": customer,
            "recent_orders": recent_orders,
            "order_count": customer.orders.count(),
        },
    )


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == "POST" and form.is_valid():
        customer = form.save()
        messages.success(request, f"{customer.name}'s details were updated.")
        return redirect("customers:detail", pk=customer.pk)
    return render(
        request,
        "customers/customer_form.html",
        {"form": form, "customer": customer, "is_new": False},
    )
