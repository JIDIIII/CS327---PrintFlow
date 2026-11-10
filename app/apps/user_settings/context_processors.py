from .models import UserSettings


def printflow_ui_settings(request):
    if not request.user.is_authenticated:
        return {"ui_settings": None}
    return {
        "ui_settings": UserSettings.objects.filter(user=request.user).only("dark_mode").first()
    }
