from django.contrib import admin

from .models import Order, OrderItem, OrderStatusHistory, PrintService, ProductionStatus


admin.site.register([PrintService, Order, OrderItem, OrderStatusHistory, ProductionStatus])
