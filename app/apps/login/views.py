from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import PrintFlowAuthenticationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home:home")

    form = PrintFlowAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())

        if not request.POST.get("remember_me"):
            request.session.set_expiry(0)

        next_url = request.POST.get("next", "")
        if not url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = reverse("home:home")
        return redirect(next_url)

    return render(request, "login/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home:home")
