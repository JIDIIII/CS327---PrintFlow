from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.orders.models import PrintService
from .forms import PrintServiceForm


@login_required
def service_list(request):
    services = PrintService.objects.all()
    return render(request, "services/service_list.html", {"services": services})


@login_required
def service_create(request):
    form = PrintServiceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        service = form.save()
        messages.success(request, f"{service.name} was added to your services.")
        return redirect("services:list")
    return render(request, "services/service_form.html", {"form": form})


@login_required
def service_edit(request, pk):
    service = get_object_or_404(PrintService, pk=pk)
    form = PrintServiceForm(request.POST or None, instance=service)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{service.name} was updated.")
        return redirect("services:list")
    return render(request, "services/service_form.html", {"form": form, "service": service})
