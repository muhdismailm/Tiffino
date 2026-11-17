
from django.urls import path
from . import views

urlpatterns = [
    # Main Admin
    path('main-admin/', views.main_admin_dashboard, name='main_admin_dashboard'),
    path('managers/', views.manager_list, name='manager_list'),
    path('all-users/', views.admin_user_list, name='admin_user_list'),

    # Manager
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/users/', views.manager_users, name='manager_users'),

    # User
    path('user/', views.user_dashboard, name='user_dashboard'),
]
