
from functools import wraps
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from accounts.models import User
from subscriptions.models import Subscription, SubscriptionCycle
from reservations.models import MealReservation
from leaves.models import LeaveRequest


# -----------------------------------------
# ROLE-BASED ACCESS DECORATOR
# -----------------------------------------

def role_required(*roles):

    def decorator(view_func):

        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):

            if request.user.role not in roles:
                return redirect('home')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


# -----------------------------------------
# MAIN ADMIN DASHBOARD
# -----------------------------------------

@role_required('main_admin')
def main_admin_dashboard(request):

    total_managers = User.objects.filter(
        role='manager'
    ).count()

    total_users = User.objects.filter(
        role='user'
    ).count()

    total_accounts = User.objects.count()

    context = {
        'total_managers': total_managers,
        'total_users': total_users,
        'total_accounts': total_accounts,
    }

    return render(
        request,
        'main_admin/dashboard.html',
        context
    )


# -----------------------------------------
# MAIN ADMIN - MANAGER LIST
# -----------------------------------------

@role_required('main_admin')
def manager_list(request):

    managers = User.objects.filter(
        role='manager'
    ).order_by('-created_at')

    context = {
        'managers': managers,
    }

    return render(
        request,
        'main_admin/managers.html',
        context
    )


# -----------------------------------------
# MAIN ADMIN - ALL USERS
# -----------------------------------------

@role_required('main_admin')
def admin_user_list(request):

    users = User.objects.filter(
        role='user'
    ).order_by('-created_at')

    context = {
        'users': users,
    }

    return render(
        request,
        'main_admin/users.html',
        context
    )


# -----------------------------------------
# MANAGER DASHBOARD
# -----------------------------------------

@role_required('manager')
def manager_dashboard(request):

    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    # Get users created by this manager
    manager_users = User.objects.filter(
        role='user',
        created_by=request.user
    )

    # Active subscriptions
    active_subscriptions = Subscription.objects.filter(
        user__in=manager_users,
        status='active',
        start_date__lte=today,
        end_date__gte=today
    ).count()

    # Tomorrow's meal reservations
    tomorrow_reservations = MealReservation.objects.filter(
        user__in=manager_users,
        date=tomorrow
    )

    # Count selected meals
    breakfast_count = tomorrow_reservations.filter(
        breakfast=True
    ).count()

    lunch_count = tomorrow_reservations.filter(
        lunch=True
    ).count()

    dinner_count = tomorrow_reservations.filter(
        dinner=True
    ).count()

    # Pending leave requests
    pending_leaves = LeaveRequest.objects.filter(
        user__in=manager_users,
        status='pending'
    ).count()

    context = {
        'total_users': manager_users.count(),
        'active_subscriptions': active_subscriptions,
        'breakfast_count': breakfast_count,
        'lunch_count': lunch_count,
        'dinner_count': dinner_count,
        'pending_leaves': pending_leaves,
        'tomorrow': tomorrow,
    }

    return render(
        request,
        'manager/dashboard.html',
        context
    )


# -----------------------------------------
# MANAGER - MANAGED USERS
# -----------------------------------------

@role_required('manager')
def manager_users(request):

    users = User.objects.filter(
        role='user',
        created_by=request.user
    ).order_by('-created_at')

    context = {
        'users': users,
    }

    return render(
        request,
        'manager/users.html',
        context
    )


# -----------------------------------------
# USER DASHBOARD
# -----------------------------------------

@role_required('user')
def user_dashboard(request):

    today = timezone.localdate()

    # Find the user's active subscription
    subscription = Subscription.objects.filter(
        user=request.user,
        status='active',
        start_date__lte=today,
        end_date__gte=today
    ).select_related('meal_plan').first()

    current_cycle = None

    # Find the current subscription cycle
    if subscription:

        current_cycle = SubscriptionCycle.objects.filter(
            subscription=subscription,
            status='active',
            start_date__lte=today,
            end_date__gte=today
        ).first()

    context = {
        'subscription': subscription,
        'current_cycle': current_cycle,
    }

    return render(
        request,
        'user/dashboard.html',
        context
    )
