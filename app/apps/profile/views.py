from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm, UserProfileForm
from .models import Profile


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    user_form = UserProfileForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, instance=profile)

    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile:profile")

    return render(
        request,
        "profile/profile.html",
        {"user_form": user_form, "profile_form": profile_form, "profile": profile},
    )
