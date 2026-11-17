
from django.urls import path
from . import views

urlpatterns = [

    # User
    path('select/', views.meal_selection, name='meal_selection'),

    path('history/', views.reservation_history,name='reservation_history'),

    # Manager
    path('manager/', views.manager_reservations,name='manager_reservations'),
]
