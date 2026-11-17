
from django.urls import path
from . import views

urlpatterns = [

    path('', views.subscription_list,
         name='manager_subscriptions'),

    path('assign/', views.assign_subscription,
         name='assign_subscription'),

    path('renew/<int:subscription_id>/',
         views.renew_subscription,
         name='renew_subscription'),
]
