from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import date, timedelta
from django.db import transaction
from subscriptions.models import MealPlan, Subscription
from subscriptions.models import SubscriptionCycle, SubscriptionTransaction
User = get_user_model()


def home(request):
    return render(request, 'accounts/home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect_by_role(user)

        messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def redirect_by_role(user):
    if user.role == 'main_admin':
        return redirect('main_admin_dashboard')
    elif user.role == 'manager':
        return redirect('manager_dashboard')

    return redirect('user_dashboard')


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
def add_manager(request):

    if request.user.role != 'main_admin':
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method == 'POST':

        name = request.POST.get('name')
        contact = request.POST.get('contact')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')

        else:
            User.objects.create_user(
                username=username,
                password=password,
                name=name,
                contact=contact,
                role='manager',
                created_by=request.user
            )

            messages.success(request, 'Manager created successfully!')
            return redirect('manager_list')

    return render(request, 'main_admin/add_manager.html')


@login_required
def add_user(request):

    if request.user.role != 'manager':
        messages.error(request, 'Access denied.')
        return redirect('home')

    meal_plans = MealPlan.objects.filter(is_active=True)

    if request.method == 'POST':

        name = request.POST.get('name')
        contact = request.POST.get('contact')
        username = request.POST.get('username')
        password = request.POST.get('password')
        meal_plan_id = request.POST.get('meal_plan')
        start_date_value = request.POST.get('start_date')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')

        else:
            try:
                meal_plan = MealPlan.objects.get(
                    id=meal_plan_id,
                    is_active=True
                )

                start_date = date.fromisoformat(start_date_value)

                if start_date < date.today():
                    messages.error(
                        request,
                        'Subscription start date cannot be in the past.'
                    )
                    return render(
                        request,
                        'manager/add_user.html',
                        {'meal_plans': meal_plans}
                    )

                end_date = start_date + timedelta(
                    days=meal_plan.duration_days - 1
                )

                with transaction.atomic():

                    # Create User
                    new_user = User.objects.create_user(
                        username=username,
                        password=password,
                        name=name,
                        contact=contact,
                        role='user',
                        created_by=request.user
                    )

                    # Create Subscription
                    subscription = Subscription.objects.create(
                        user=new_user,
                        meal_plan=meal_plan,
                        assigned_by=request.user,
                        start_date=start_date,
                        end_date=end_date,
                        status='active'
                    )

                    # Create Initial Subscription Cycle
                    cycle = SubscriptionCycle.objects.create(
                        subscription=subscription,
                        cycle_number=1,
                        start_date=start_date,
                        end_date=end_date,
                        allocated_days=meal_plan.duration_days,
                        remaining_days=meal_plan.duration_days,
                        status='active'
                    )

                    # Record Initial Transaction
                    SubscriptionTransaction.objects.create(
                        cycle=cycle,
                        transaction_type='renewal',
                        days_changed=meal_plan.duration_days,
                        balance_after=meal_plan.duration_days,
                        description='Initial subscription assigned by manager.'
                    )

                messages.success(
                    request,
                    'User created and meal plan assigned successfully!'
                )

                return redirect('manager_users')

            except MealPlan.DoesNotExist:
                messages.error(request, 'Please select a valid meal plan.')

            except ValueError:
                messages.error(request, 'Please enter a valid start date.')

    context = {
    'meal_plans': meal_plans,
    'today': date.today(),
}

    return render(
        request,
        'manager/add_user.html',
        context
    )
