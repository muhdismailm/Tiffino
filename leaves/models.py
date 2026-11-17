from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class LeaveRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )

    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )

    from_date = models.DateField()
    to_date = models.DateField()

    reason = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leaves'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):

        # Ensure subscription belongs to the user
        if self.subscription_id and self.user_id and self.subscription.user_id != self.user_id:
                raise ValidationError(
                    "This subscription does not belong to this user."
                )

        # Only monthly subscription users can request leave
        if self.subscription_id and self.subscription.meal_plan.name != 'monthly':
                raise ValidationError(
                    "Leave requests are available only for monthly plans."
                )

        # Validate date range
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError(
                    "End date cannot be earlier than start date."
                )

            if self.from_date < timezone.localdate():
                raise ValidationError(
                    "You cannot request leave for past dates."
                )

        # Check overlapping leave requests
        if self.user_id and self.from_date and self.to_date:

            overlapping_requests = LeaveRequest.objects.filter(
                user=self.user,
                from_date__lte=self.to_date,
                to_date__gte=self.from_date,
                status__in=['pending', 'approved']
            )

            if self.pk:
                overlapping_requests = overlapping_requests.exclude(
                    pk=self.pk
                )

            if overlapping_requests.exists():
                raise ValidationError(
                    "You already have a pending or approved leave "
                    "request for these dates."
                )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.from_date} to {self.to_date}"
        )
