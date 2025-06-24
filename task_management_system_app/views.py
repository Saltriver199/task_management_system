from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Category, Task, EmployeeLogin
from people_management.forms import CustomUserCreationForm
from people_management.models import Complains, Employee, Repair
from django.db.models import Count, Q
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from .forms import CategoryForm, TaskForm, EmployeeTaskStatusForm
from leave_management.models import LeaveRequest
from django.core.mail import send_mail
import logging
import pytz

logger = logging.getLogger(__name__)

def is_admin(user):
    return user.is_superuser

admin_required = user_passes_test(lambda user: user.is_superuser)

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not user.is_superuser:
                EmployeeLogin.objects.create(employee=user)
                today = timezone.now().date()
                login_count_today = EmployeeLogin.objects.filter(
                    employee=user, login_time__date=today).count()
                if login_count_today == 1:
                    daily_tasks = Task.objects.filter(assigned_to=user, frequency='daily')
                    for task in daily_tasks:
                        if task.status != 'complete':
                            task.reset_timer()
                        logger.debug(f"Task {task.name} reset: end_date={task.end_date}")
            return redirect('employee_dashboard' if not user.is_superuser else '/dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'people_management/login.html', {'form': form})

@login_required
def employee_dashboard(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect('logout')
    
    tasks_queryset = Task.objects.filter(assigned_to=request.user).select_related('category')
    complaints_queryset = Complains.objects.filter(user=request.user)
    
    task_counts = {
        'total': tasks_queryset.count(),
        'completed': tasks_queryset.filter(status='complete').count(),
        'pending': tasks_queryset.filter(status='pending').count(),
        'in_progress': tasks_queryset.filter(status='in_progress').count(),
        'suspend': tasks_queryset.filter(status='suspend').count(),
        'ready': tasks_queryset.filter(status='ready').count(),
        'delete': tasks_queryset.filter(status='delete').count(),
    }
    
    leave_requests = LeaveRequest.objects.filter(employee=employee)
    pending_leaves = leave_requests.filter(status='pending').count()
    approved_leaves = leave_requests.filter(status='approved').count()
    
    assigned_repairs = Repair.objects.filter(assigned_to=employee).order_by('-id')
    total_repairs_count = assigned_repairs.count()
    in_progress_repairs_count = assigned_repairs.filter(is_completed=False).count()
    
    for task in tasks_queryset:
        task.remaining_time = task.get_remaining_time()
        task.remaining_seconds = int(task.remaining_time.total_seconds()) if task.remaining_time else 0
        logger.debug(f"Task {task.name}: remaining_seconds={task.remaining_seconds}")
    
    context = {
        'employee': employee,
        'task_counts': task_counts,
        'total_tasks': task_counts['total'],
        'completed_tasks': task_counts['completed'],
        'pending_tasks_count': task_counts['pending'],
        'in_progress_tasks_count': task_counts['in_progress'],
        'tasks': tasks_queryset,
        'complaints': complaints_queryset,
        'leave_requests': leave_requests,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'assigned_repairs': assigned_repairs,
        'total_repairs_count': total_repairs_count,
        'in_progress_repairs_count': in_progress_repairs_count,
    }
    return render(request, 'task_management_system_app/employee_dashboard.html', context)

@login_required
def employee_task(request):
    tasks = Task.objects.filter(assigned_to=request.user).select_related('category')
    for task in tasks:
        task.remaining_time = task.get_remaining_time()
        task.remaining_seconds = int(task.remaining_time.total_seconds()) if task.remaining_time else 0
    return render(request, 'task_management_system_app/employee_task.html', {'tasks': tasks})

@login_required
def clock_out(request):
    if request.method == 'POST':
        user = request.user
        today = timezone.now().date()
        incomplete_tasks = Task.objects.filter(
            assigned_to=user, frequency='daily', last_reset_date=today,
            status__in=['pending', 'suspend', 'ready'])
        if incomplete_tasks:
            admin_emails = [u.email for u in User.objects.filter(is_superuser=True) if u.email]
            subject = f"Incomplete Tasks for {user.username} on {today}"
            message = f"Dear {user.username},\n\nThe following daily tasks are incomplete:\n\n"
            for task in incomplete_tasks:
                message += f"- Task: {task.name}\n  Category: {task.category.name}\n  Status: {task.get_status_display()}\n\n"
            message += "Please complete your tasks on time.\n\nBest regards,\nTaskManager Team"
            try:
                send_mail(subject, message, 'yashpatel342212@gmail.com', [user.email] + admin_emails)
                messages.success(request, "Clocked out. Email sent for incomplete tasks.")
            except Exception as e:
                messages.warning(request, f"Clocked out, but email failed: {e}")
        else:
            messages.success(request, "Clocked out successfully.")
        logout(request)
        return redirect('login')
    return redirect('employee_dashboard')

@login_required
def view_assigned_repairs(request):
    assigned_repairs = Repair.objects.filter(assigned_to__user=request.user).select_related('task', 'complain', 'department').order_by('-id')
    return render(request, 'task_management_system_app/assigned_repairs.html', {'assigned_repairs': assigned_repairs})

class RegistrationForm(CustomUserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'people_management/register.html', {'form': form})

def LogoutPage(request):
    logout(request)
    return redirect("/")

@login_required
@admin_required
def delete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        category_id = task.category.id
        task.delete()
        return redirect(reverse('category_tasks', args=[category_id]))

@login_required
@admin_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            if task.frequency == 'daily':
                task.start_date = None
                task.end_date = None
                task.deadline = None
            task.save()
            if task.frequency == 'daily':
                task.reset_timer()
            user = task.assigned_to
            subject = f"New Task Assigned: {task.name}"
            message = (
                f"Hello {user.username},\n\n"
                f"You have been assigned a new task:\n\n"
                f"Task: {task.name}\n"
                f"Category: {task.category.name}\n"
                f"Frequency: {task.frequency}\n"
                f"Priority: {task.priority}\n"
                f"Status: {task.status}\n"
                f"Description: {task.description}\n"
                f"Location: {task.location}\n"
                f"Organizer: {task.organizer}\n\n"
                f"Please log in to view and manage the task."
            )
            try:
                send_mail(subject, message, 'yashpatel342212@gmail.com', [user.email])
                messages.success(request, f'Task created and email sent to {user.email}.')
            except Exception as e:
                messages.warning(request, f'Task created, but email failed: {e}')
            return redirect('category_tasks', category_id=task.category.id)
    else:
        form = TaskForm()
    return render(request, 'task_management_system_app/create_task.html', {'form': form})

@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user.is_superuser:
        if request.method == 'POST':
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                task = form.save(commit=False)
                if task.frequency == 'daily':
                    task.start_date = None
                    task.end_date = None
                    task.deadline = None
                    task.reset_timer()
                task.save()
                if task.assigned_to.email:
                    subject = f"Task Updated: {task.name}"
                    message = (
                        f"Hello {task.assigned_to.username},\n\n"
                        f"Your task has been updated:\n\n"
                        f"Name: {task.name}\n"
                        f"Category: {task.category.name}\n"
                        f"Frequency: {task.frequency}\n"
                        f"Priority: {task.priority}\n"
                        f"Status: {task.status}\n"
                        f"Location: {task.location}\n"
                        f"Organizer: {task.organizer}\n"
                        f"Description: {task.description}\n\n"
                        f"Please log in to view details."
                    )
                    try:
                        send_mail(subject, message, 'yashpatel342212@gmail.com', [task.assigned_to.email])
                        messages.success(request, f'Task updated and notification sent.')
                    except Exception as e:
                        messages.warning(request, f'Task updated, but email failed: {e}')
                return redirect('category_tasks', category_id=task.category.id)
        else:
            form = TaskForm(instance=task)
        return render(request, 'task_management_system_app/update_task.html', {'form': form, 'task': task})
    return redirect('employee_update_task_status', task_id=task_id)

@login_required
def employee_update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    if request.method == 'POST':
        form = EmployeeTaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.name}" status updated.')
            return redirect('employee_task')
    else:
        form = EmployeeTaskStatusForm(instance=task)
    return render(request, 'task_management_system_app/employee_update_task_status.html', {'form': form, 'task': task})

@login_required
@admin_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'task_management_system_app/category_list.html', {'categories': categories})

@login_required
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'task_management_system_app/category_update.html', {'form': form})

@login_required
@admin_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'task_management_system_app/create_category.html', {'form': form, 'title': 'Create New Category'})

@login_required
@admin_required
def delete_category(request, category_id):
    category = Category.objects.get(pk=category_id)
    if category.task_set.exists():
        messages.error(request, "Cannot delete category with tasks.")
    else:
        category.delete()
        messages.success(request, "Category deleted successfully.")
    return redirect('category_list')

@login_required
@admin_required
def category_tasks(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    tasks = category.task_set.all()
    return render(request, 'task_management_system_app/category_tasks.html', {'category': category, 'tasks': tasks})