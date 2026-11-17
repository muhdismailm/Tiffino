
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from dashboard.views import role_required
from accounts.models import User

from .models import (
    MealPlan,
    Subscription,
    SubscriptionCycle,
    SubscriptionTransaction
)


@role_required('manager')
def subscription_list(request):

    users = User.objects.filter(
        role='user',
        created_by=request.user
    )

    subscriptions = Subscription.objects.filter(
        user__in=users
    ).select_related('user', 'meal_plan').order_by('-created_at')

    return render(request, 'manager/subscriptions.html', {
        'subscriptions': subscriptions
    })


@role_required('manager')
def assign_subscription(request):

    users = User.objects.filter(
        role='user',
        created_by=request.user,
        is_active=True
    )

    meal_plans = MealPlan.objects.filter(is_active=True)

    if request.method == 'POST':
        try:
            user = users.get(pk=request.POST.get('user'))
            plan = meal_plans.get(pk=request.POST.get('meal_plan'))

            start_date = datetime.strptime(
                request.POST.get('start_date'),
                '%Y-%m-%d'
            ).date()

            if start_date < timezone.localdate():
                raise ValueError('Start date cannot be in the past.')

            end_date = start_date + timedelta(
                days=plan.duration_days - 1
            )

            # Expire any previous active subscription.
            Subscription.objects.filter(
                user=user,
                status='active'
            ).update(status='expired')

            subscription = Subscription.objects.create(
                user=user,
                meal_plan=plan,
                assigned_by=request.user,
                start_date=start_date,
                end_date=end_date,
                status='active'
            )

            cycle = SubscriptionCycle.objects.create(
                subscription=subscription,
                cycle_number=1,
                start_date=start_date,
                end_date=end_date,
                allocated_days=plan.duration_days,
                remaining_days=plan.duration_days,
                status='active'
            )

            SubscriptionTransaction.objects.create(
                cycle=cycle,
                transaction_type='renewal',
                days_changed=plan.duration_days,
                balance_after=plan.duration_days,
                description='Initial subscription cycle.'
            )

            messages.success(request, 'Subscription assigned successfully.')
            return redirect('manager_subscriptions')

        except (User.DoesNotExist, MealPlan.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Please enter valid subscription details.')

    return render(request, 'manager/assign_subscription.html', {
        'users': users,
        'meal_plans': meal_plans
    })


@role_required('manager')
def renew_subscription(request, subscription_id):

    if request.method != 'POST':
        return redirect('manager_subscriptions')

    users = User.objects.filter(
        role='user',
        created_by=request.user
    )

    subscription = Subscription.objects.filter(
        pk=subscription_id,
        user__in=users
    ).select_related('meal_plan').first()

    if not subscription:
        messages.error(request, 'Subscription not found.')
        return redirect('manager_subscriptions')

    previous_cycle = subscription.cycles.order_by(
        '-cycle_number'
    ).first()

    if previous_cycle and previous_cycle.remaining_days > 0:
        messages.error(request, 'Current cycle still has remaining days.')
        return redirect('manager_subscriptions')

    cycle_number = previous_cycle.cycle_number + 1 if previous_cycle else 1

    start_date = timezone.localdate()
    duration = subscription.meal_plan.duration_days
    end_date = start_date + timedelta(days=duration - 1)

    cycle = SubscriptionCycle.objects.create(
        subscription=subscription,
        cycle_number=cycle_number,
        start_date=start_date,
        end_date=end_date,
        allocated_days=duration,
        remaining_days=duration,
        status='active'
    )

    subscription.start_date = start_date
    subscription.end_date = end_date
    subscription.status = 'active'
    subscription.save()

    SubscriptionTransaction.objects.create(
        cycle=cycle,
        transaction_type='renewal',
        days_changed=duration,
        balance_after=duration,
        description='New cycle manually created.'
    )

    messages.success(request, 'Subscription renewed successfully.')
    return redirect('manager_subscriptions')
