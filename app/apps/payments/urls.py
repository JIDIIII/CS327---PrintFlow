from django.urls import path

from . import views


app_name = "payments"

urlpatterns = [
    path("", views.payment_list, name="list"),
    path("orders/<int:order_id>/new/", views.payment_create, name="create"),
]
