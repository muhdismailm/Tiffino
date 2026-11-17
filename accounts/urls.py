from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Main Admin
    path('add-manager/', views.add_manager, name='add_manager'),

    # Manager
    path('add-user/', views.add_user, name='add_user'),
]