from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home:home")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Account created successfully. You can now log in.",
        )
        return redirect("login:login")

    return render(request, "register/register.html", {"form": form})
