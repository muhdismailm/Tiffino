from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('reservations/', include('reservations.urls')),
    path('leaves/', include('leaves.urls')),
]