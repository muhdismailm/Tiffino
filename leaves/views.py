
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST

from dashboard.views import role_required
from accounts.models import User
from subscriptions.models import Subscription
from .models import LeaveRequest


# USER LEAVE REQUEST

@role_required('user')
def leave_calendar(request):

    today = timezone.localdate()

    subscription = Subscription.objects.filter(
        user=request.user,
        meal_plan__name='monthly',
        status='active',
        start_date__lte=today,
        end_date__gte=today
    ).first()

    if request.method == 'POST':

        if not subscription:
            messages.error(request, 'An active monthly plan is required.')
            return redirect('leave_calendar')

        try:
            from_date = datetime.strptime(
                request.POST.get('from_date'),
                '%Y-%m-%d'
            ).date()

            to_date = datetime.strptime(
                request.POST.get('to_date'),
                '%Y-%m-%d'
            ).date()

            leave = LeaveRequest(
                user=request.user,
                subscription=subscription,
                from_date=from_date,
                to_date=to_date,
                reason=request.POST.get('reason', '')
            )

            leave.full_clean()
            leave.save()

            messages.success(request, 'Leave request submitted.')
            return redirect('leave_calendar')

        except (ValueError, TypeError) as error:
            messages.error(request, str(error))

        except Exception as error:
            messages.error(request, str(error))

    leave_requests = LeaveRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'user/leave_calendar.html', {
        'active_subscription': subscription,
        'leave_requests': leave_requests
    })


# MANAGER LEAVE REQUESTS

@role_required('manager')
def manager_leave_requests(request):

    users = User.objects.filter(
        role='user',
        created_by=request.user
    )

    leave_requests = LeaveRequest.objects.filter(
        user__in=users
    ).select_related(
        'user',
        'subscription',
        'reviewed_by'
    ).order_by('-created_at')

    return render(request, 'manager/leave_requests.html', {
        'leave_requests': leave_requests
    })


# MANAGER APPROVE OR REJECT

@role_required('manager')
@require_POST
def review_leave(request, leave_id):

    users = User.objects.filter(
        role='user',
        created_by=request.user
    )

    leave = get_object_or_404(
        LeaveRequest,
        pk=leave_id,
        user__in=users
    )

    if leave.status != 'pending':
        messages.error(request, 'This request has already been reviewed.')
        return redirect('manager_leave_requests')

    status = request.POST.get('status')

    if status not in ['approved', 'rejected']:
        messages.error(request, 'Invalid action.')
        return redirect('manager_leave_requests')

    leave.status = status
    leave.reviewed_by = request.user
    leave.reviewed_at = timezone.now()

    leave.save(update_fields=[
        'status',
        'reviewed_by',
        'reviewed_at'
    ])

    messages.success(request, f'Leave request {status}.')
    return redirect('manager_leave_requests')
