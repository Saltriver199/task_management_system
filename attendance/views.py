from django.shortcuts import render, redirect
from django.utils.timezone import now, localtime
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import Attendance

@login_required
def clock_in(request):
    employee = request.user.employee
    today = now().date()
    current_dt = now()  # aware UTC datetime

    # Get latest attendance record for today
    latest = Attendance.objects.filter(employee=employee, date=today).order_by('-clock_in').first()

    if not latest or latest.clock_out:
        attendance = Attendance.objects.create(
            employee=employee,
            date=today,
            clock_in=current_dt,
            status='Present'
        )
        # Convert to local time before formatting
        local_in = localtime(attendance.clock_in)
        time_str = local_in.strftime('%H:%M:%S')

        messages.success(request, f"Clock-in recorded at {time_str}")

        # Email using local time in body
        send_mail(
            subject="Clock In Confirmation",
            message=f"You clocked in at {time_str} on {today}.",
            from_email=None,
            recipient_list=[employee.user.email],
            fail_silently=True,
        )
    else:
        messages.warning(request, "You must clock out before clocking in again.")

    return redirect('employee_dashboard')


@login_required
def clock_out(request):
    employee = request.user.employee
    today = now().date()
    current_dt = now()  # aware UTC datetime

    # Find last attendance without clock_out
    attendance = Attendance.objects.filter(
        employee=employee, date=today, clock_out__isnull=True
    ).order_by('-clock_in').first()

    if attendance:
        attendance.clock_out = current_dt
        attendance.save()

        # Convert to local time before formatting
        local_out = localtime(attendance.clock_out)
        time_str = local_out.strftime('%H:%M:%S')

        messages.success(request, f"Clock-out recorded at {time_str}")

        send_mail(
            subject="Clock Out Confirmation",
            message=f"You clocked out at {time_str} on {today}.",
            from_email=None,
            recipient_list=[employee.user.email],
            fail_silently=True,
        )
    else:
        messages.warning(request, "No active clock-in session found.")

    return redirect('employee_dashboard')


@staff_member_required
def attendance_list(request):
    # No change needed here for timezone—template will handle display
    records = Attendance.objects.select_related('employee__user').order_by('-date', '-clock_in')
    return render(request, 'attendance/attendance_list.html', {'records': records})
