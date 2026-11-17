from django.contrib import admin
from .models import (
    MealPlan,
    Subscription,
    SubscriptionCycle,
    SubscriptionTransaction
)

admin.site.register(MealPlan)
admin.site.register(Subscription)
admin.site.register(SubscriptionCycle)
admin.site.register(SubscriptionTransaction)