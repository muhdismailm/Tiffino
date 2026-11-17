
from django.contrib import admin
from .models import MealReservation


@admin.register(MealReservation)
class MealReservationAdmin(admin.ModelAdmin):

    # Fields displayed in the reservation list
    list_display = (
        'user',
        'date',
        'breakfast',
        'lunch',
        'dinner',
        'rejected_dinner',
        'rejected_all',
        'submitted_at',
    )

    # Filters on the right side
    list_filter = (
        'date',
        'breakfast',
        'lunch',
        'dinner',
    )

    # Search reservations by username
    search_fields = (
        'user__username',
        'user__name',
    )

    # Default ordering
    ordering = ('-date',)

    # Make these fields read-only
    readonly_fields = (
        'submitted_at',
        'updated_at',
    )

    # Number of records per page
    list_per_page = 25
