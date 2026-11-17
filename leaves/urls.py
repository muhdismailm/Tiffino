
from django.urls import path
from . import views

urlpatterns = [

    # User
    path('request/', views.leave_calendar,name='leave_calendar'),

    # Manager
    path('manager/', views.manager_leave_requests, name='manager_leave_requests'),

    path('review/<int:leave_id>/',views.review_leave, name='review_leave'),
]
