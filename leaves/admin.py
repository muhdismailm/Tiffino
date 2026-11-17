from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):

    # Columns displayed in the admin list
    list_display = (
        'user',
        'subscription',
        'from_date',
        'to_date',
        'status',
        'reviewed_by',
        'created_at',
    )

    # Filters on the right side
    list_filter = (
        'status',
        'from_date',
        'created_at',
    )

    # Search by username and subscription plan
    search_fields = (
        'user__username',
        'user__name',
        'reviewed_by__username',
    )

    # Latest requests first
    ordering = ('-created_at',)

    # Timestamp fields cannot be edited
    readonly_fields = (
        'created_at',
        'reviewed_at',
    )

    # Records per page
    list_per_page = 25

    # Organize fields in the detail page
    fieldsets = (
        ('Leave Information', {
            'fields': (
                'user',
                'subscription',
                'from_date',
                'to_date',
                'reason',
            )
        }),
        ('Approval Information', {
            'fields': (
                'status',
                'reviewed_by',
                'reviewed_at',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        }),
    )
