
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class MealReservation(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.PROTECT,
        related_name='reservations'
    )

    date = models.DateField()

    breakfast = models.BooleanField(default=False)
    lunch = models.BooleanField(default=False)
    dinner = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date'],
                name='unique_user_meal_reservation'
            )
        ]

    def clean(self):
        """
        Validate the reservation before saving.
        """

        # Ensure the selected user owns this subscription
        if self.subscription_id and self.user_id and self.subscription.user_id != self.user_id:
                raise ValidationError(
                    "This subscription does not belong to this user."
                )

        # Only allow reservations for future dates
        if self.date and self.date <= timezone.localdate():
            raise ValidationError(
                "You can only reserve meals for upcoming dates."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def rejected_all(self):
        """
        Returns True if the user rejects all three meals.
        """
        return not (
            self.breakfast or
            self.lunch or
            self.dinner
        )

    @property
    def rejected_dinner(self):
        """
        Returns True if the user rejects dinner
        but accepts at least one other meal.
        """
        return (
            not self.dinner and
            (self.breakfast or self.lunch)
        )

    def __str__(self):
        return f"{self.user.username} - {self.date}"
