from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UserSettingsForm
from .models import UserSettings


@login_required
def settings_view(request):
    settings_record, _ = UserSettings.objects.get_or_create(user=request.user)
    form = UserSettingsForm(request.POST or None, instance=settings_record)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your settings have been saved.")
        return redirect("user_settings:settings")

    return render(
        request,
        "user_settings/settings.html",
        {"form": form, "settings_record": settings_record},
    )
