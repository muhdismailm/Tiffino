
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = [
        ('main_admin', 'Main Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )

    name = models.CharField(max_length=150)
    contact = models.CharField(max_length=15)

    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_accounts'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
