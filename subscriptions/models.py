
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import Q, F


# ==========================================
# 1. MEAL PLAN MODEL
# ==========================================

class MealPlan(models.Model):

    PLAN_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    name = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        unique=True
    )

    duration_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_name_display()


# ==========================================
# 2. SUBSCRIPTION MODEL
# ==========================================

class Subscription(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    meal_plan = models.ForeignKey(
        MealPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_subscriptions'
    )

    start_date = models.DateField()

    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.meal_plan.name}"


# ==========================================
# 3. SUBSCRIPTION CYCLE MODEL
# ==========================================

class SubscriptionCycle(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    ]

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='cycles'
    )

    cycle_number = models.PositiveIntegerField()

    start_date = models.DateField()

    end_date = models.DateField()

    allocated_days = models.PositiveIntegerField(default=30)

    remaining_days = models.PositiveIntegerField(default=30)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ['cycle_number']

        constraints = [
            models.UniqueConstraint(
                fields=['subscription', 'cycle_number'],
                name='unique_subscription_cycle'
            ),

            models.CheckConstraint(
                condition=Q(
                    remaining_days__lte=F('allocated_days')
                ),
                name='remaining_days_not_above_allocated'
            ),
        ]

    def __str__(self):
        return (
            f"{self.subscription.user.username} "
            f"- Cycle {self.cycle_number}"
        )


# ==========================================
# 4. SUBSCRIPTION TRANSACTION MODEL
# ==========================================

class SubscriptionTransaction(models.Model):

    TRANSACTION_CHOICES = [
        ('deduction', 'Daily Deduction'),
        ('leave_adjustment', 'Leave Adjustment'),
        ('renewal', 'New Cycle'),
        ('manual_adjustment', 'Manual Adjustment'),
    ]

    cycle = models.ForeignKey(
        SubscriptionCycle,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    transaction_type = models.CharField(
        max_length=30,
        choices=TRANSACTION_CHOICES
    )

    days_changed = models.IntegerField()

    balance_after = models.PositiveIntegerField()

    description = models.TextField(
        blank=True,
        null=True
    )

    transaction_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ['-transaction_date']

    def __str__(self):
        return (
            f"{self.cycle} - "
            f"{self.transaction_type} "
            f"({self.days_changed})"
        )
