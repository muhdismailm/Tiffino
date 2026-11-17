
from datetime import datetime, timedelta, time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from dashboard.views import role_required
from accounts.models import User
from subscriptions.models import Subscription
from leaves.models import LeaveRequest

from .models import MealReservation


def reservation_deadline(target_date):
    previous_day = target_date - timedelta(days=1)

    deadline = datetime.combine(
        previous_day,
        time(20, 0)
    )

    return timezone.make_aware(
        deadline,
        timezone.get_current_timezone()
    )


# USER MEAL SELECTION

@role_required('user')
def meal_selection(request):

    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    if request.method == 'POST':

        try:
            target_date = datetime.strptime(
                request.POST.get('date'),
                '%Y-%m-%d'
            ).date()
        except (ValueError, TypeError):
            messages.error(request, 'Please select a valid date.')
            return redirect('meal_selection')

        if target_date <= today:
            messages.error(request, 'Select an upcoming date.')
            return redirect('meal_selection')

        if timezone.now() >= reservation_deadline(target_date):
            messages.error(request, 'The 8 PM deadline has passed.')
            return redirect('meal_selection')

        subscription = Subscription.objects.filter(
            user=request.user,
            status='active',
            start_date__lte=target_date,
            end_date__gte=target_date
        ).first()

        if not subscription:
            messages.error(request, 'No active subscription for this date.')
            return redirect('meal_selection')

        on_leave = LeaveRequest.objects.filter(
            user=request.user,
            status='approved',
            from_date__lte=target_date,
            to_date__gte=target_date
        ).exists()

        if on_leave:
            messages.error(request, 'You have approved leave on this date.')
            return redirect('meal_selection')

        reservation, created = MealReservation.objects.get_or_create(
            user=request.user,
            date=target_date,
            defaults={
                'subscription': subscription,
                'breakfast': 'breakfast' in request.POST,
                'lunch': 'lunch' in request.POST,
                'dinner': 'dinner' in request.POST
            }
        )

        if not created:
            reservation.subscription = subscription
            reservation.breakfast = 'breakfast' in request.POST
            reservation.lunch = 'lunch' in request.POST
            reservation.dinner = 'dinner' in request.POST
            reservation.save()

        messages.success(request, 'Meal selection saved successfully.')
        return redirect('reservation_history')

    return render(request, 'user/meal_selection.html', {
        'selected_date': tomorrow,
        'meal_fields': [
            ('breakfast', 'Breakfast'),
            ('lunch', 'Lunch'),
            ('dinner', 'Dinner')
        ]
    })


# USER RESERVATION HISTORY

@role_required('user')
def reservation_history(request):

    reservations = MealReservation.objects.filter(
        user=request.user
    ).order_by('-date')

    return render(request, 'user/reservation_history.html', {
        'reservations': reservations
    })


# MANAGER MEAL REQUIREMENTS

@role_required('manager')
def manager_reservations(request):

    users = User.objects.filter(
        role='user',
        created_by=request.user
    )

    target_date = timezone.localdate() + timedelta(days=1)

    if request.GET.get('date'):
        try:
            target_date = datetime.strptime(
                request.GET.get('date'),
                '%Y-%m-%d'
            ).date()
        except ValueError:
            messages.error(request, 'Invalid date.')

    subscriptions = Subscription.objects.filter(
        user__in=users,
        status='active',
        start_date__lte=target_date,
        end_date__gte=target_date
    )

    approved_leave_users = LeaveRequest.objects.filter(
        user__in=users,
        status='approved',
        from_date__lte=target_date,
        to_date__gte=target_date
    ).values_list('user_id', flat=True)

    reservations = MealReservation.objects.filter(
        user__in=users,
        subscription__in=subscriptions,
        date=target_date
    ).exclude(
        user_id__in=approved_leave_users
    ).select_related('user')

    counts = reservations.aggregate(
        breakfast_count=Count('id', filter=Q(breakfast=True)),
        lunch_count=Count('id', filter=Q(lunch=True)),
        dinner_count=Count('id', filter=Q(dinner=True)),
        rejected_dinner_count=Count(
            'id',
            filter=Q(dinner=False) & (Q(breakfast=True) | Q(lunch=True))
        ),
        rejected_all_count=Count(
            'id',
            filter=Q(breakfast=False, lunch=False, dinner=False)
        )
    )

    return render(request, 'manager/reservations.html', {
        'target_date': target_date,
        'reservations': reservations,
        'meal_counts': {
            'Breakfast': counts['breakfast_count'],
            'Lunch': counts['lunch_count'],
            'Dinner': counts['dinner_count']
        },
        'rejected_dinner_count': counts['rejected_dinner_count'],
        'rejected_all_count': counts['rejected_all_count']
    })
