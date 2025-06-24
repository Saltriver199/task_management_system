from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from .models import LeaveRequest, LeaveType
from people_management.models import Employee
from django.core.mail import send_mail
from django.conf import settings

@login_required
def apply_leave(request):
    if request.method == 'POST':
        leave_type_id = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        emergency_contact =  request.POST.get('emergency_contact')
        work_handover = request.POST.get('work_handover')
        employee = request.user.employee
        leave_type = get_object_or_404(LeaveType, pk=leave_type_id)

        LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            emergency_contact=emergency_contact,
            work_handover=work_handover
        )
        hr_email = 'saltriveradtskerala@gmail.com'
        send_mail(
            subject='New Leave Application Submitted',
            message=(
                f"Employee: {employee.user.username}\n"
                f"Leave Type: {leave_type.name}\n"
                f"Start Date: {start_date}\n"
                f"End Date: {end_date}\n"
                f"Reason: {reason}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[hr_email],
            fail_silently=False,
        )
        return redirect('employee_dashboard')

    leave_types = LeaveType.objects.all()
    return render(request, 'leave_management/apply_leave.html', {'leave_types': leave_types})

@login_required
def leave_history(request):
    approved = LeaveRequest.objects.filter(status='approved')
    return render(request, 'leave_management/leave_history.html', {'approved': approved})

@permission_required('leave_management.change_leaverequest')
def review_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        leave.status = 'approved' if action == 'approve' else 'rejected'
        leave.reviewer = request.user
        leave.reviewed_at = timezone.now()
        leave.save()
        employee_email = leave.employee.user.email
        status_text = 'approved' if leave.status == 'approved' else 'rejected'

        send_mail(
            subject=f'Leave Request {status_text.title()}',
            message=(
                f"Dear {leave.employee.user.username},\n\n"
                f"Your leave request from {leave.start_date} to {leave.end_date} has been {status_text}.\n\n"
                f"Regards,\n{request.user.username}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[employee_email],
            fail_silently=False,
        )

        return redirect('leave_review_list')
    return render(request, 'leave_management/review_leave.html', {'leave': leave})

@permission_required('leave_management.view_leaverequest')
def leave_review_list(request):
    pending = LeaveRequest.objects.filter(status='pending')
    return render(request, 'leave_management/leave_review_list.html', {'pending': pending})