from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from apps.customers.models import Customer


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    READY_FOR_PICKUP = "READY_FOR_PICKUP", "Ready for Pickup"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class PaymentStatus(models.TextChoices):
    UNPAID = "UNPAID", "Unpaid"
    PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
    PAID = "PAID", "Paid"


class PrintService(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    category = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Order(models.Model):
    order_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    service = models.ForeignKey(
        PrintService,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    size = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    deadline = models.DateTimeField(db_index=True)
    special_instructions = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_orders",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["deadline", "created_at"]

    def __str__(self):
        return f"{self.order_number} - {self.customer}"

    def save(self, *args, **kwargs):
        if self.status == OrderStatus.COMPLETED and self.completed_at is None:
            self.completed_at = timezone.now()
        elif self.status != OrderStatus.COMPLETED:
            self.completed_at = None

        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"completed_at"}

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return (
            self.status not in {OrderStatus.COMPLETED, OrderStatus.CANCELLED}
            and self.deadline < timezone.now()
        )

    @property
    def amount_paid(self):
        total = self.payments.aggregate(total=Sum("amount"))["total"]
        return total or Decimal("0.00")

    @property
    def remaining_balance(self):
        return max(self.total_price - self.amount_paid, Decimal("0.00"))

    @property
    def payment_status(self):
        amount_paid = self.amount_paid
        if amount_paid <= 0:
            return PaymentStatus.UNPAID
        if amount_paid < self.total_price:
            return PaymentStatus.PARTIALLY_PAID
        return PaymentStatus.PAID


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    from_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        blank=True,
    )
    to_status = models.CharField(max_length=20, choices=OrderStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="order_status_changes",
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-changed_at", "-id"]
        verbose_name_plural = "order status histories"

    def __str__(self):
        return f"{self.order.order_number}: {self.get_to_status_display()}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    service = models.ForeignKey(
        PrintService,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item {self.pk} - Order {self.order_id}"


class ProductionStatus(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="production_statuses",
    )
    status = models.CharField(max_length=50)
    remarks = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_id} - {self.status}"
