from re import L
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from task_management_system_app.models import Category, Task
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm 
from .models import Employee , Department , Complains, Repair
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils import timezone


@login_required
def dashboard(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found. Please contact an administrator.")
        return redirect('logout') 


    tasks_queryset = Task.objects.all()
    complaints_queryset = Complains.objects.all()


    if not request.user.is_superuser:
        tasks_queryset = tasks_queryset.filter(assigned_to=request.user)
        complaints_queryset = complaints_queryset.filter(user=request.user)

 
    task_counts = {
        'pending': tasks_queryset.filter(status='pending').count(),
        'suspend': tasks_queryset.filter(status='suspend').count(),
        'ready': tasks_queryset.filter(status='ready').count(),
        'complete': tasks_queryset.filter(status='complete').count(),
        'delete': tasks_queryset.filter(status='delete').count(),
        'total': tasks_queryset.count(), 
    }

    
    recent_complaints = complaints_queryset.order_by('-created_at')[:2] 

    current_task = Task.objects.filter(assigned_to=request.user, status__in=['pending', 'ready', 'suspend']).order_by('-created_at').first()
    employee.current_task = current_task


    context = {
        'employee': employee,
        'task_counts': task_counts,
        'complaints': complaints_queryset, 
        'recent_complaints': recent_complaints, 
    }

    return render(request, 'people_management/dashboard.html', context)


def employee_list(request):
    employees = Employee.objects.select_related('user', 'department', 'default_category', 'current_task')
    return render(request, 'people_management/employee_list.html', {'employees': employees})

def create_employee(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            department = Department.objects.get(id=request.POST['department'])
            default_category = Category.objects.get(id=request.POST['default_category']) if request.POST.get('default_category') else None
            current_task = Task.objects.get(id=request.POST['current_task']) if request.POST.get('current_task') else None
            email = request.POST.get('email')
            Employee.objects.create(
                user=user,
                department=department,
                email=email,
                default_category=default_category,
                current_task=current_task
            )
            messages.success(request, 'Employee created successfully.')
            return redirect('employee_list')
    else:
        user_form = UserCreationForm()
    context = {
        'form': user_form,
        'departments': Department.objects.all(),
        'categories': Category.objects.all(),
        'tasks': Task.objects.all()
    }
    return render(request, 'people_management/create_employee.html', context)


def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    departments = Department.objects.all()
    categories = Category.objects.all()
    tasks = Task.objects.all()

    if request.method == 'POST':
        department_id = request.POST.get('department')
        email = request.POST.get('email')
        default_category_id = request.POST.get('default_category')
        current_task_id = request.POST.get('current_task')

        employee.department = get_object_or_404(Department, id=department_id)
        employee.email = email or None
        employee.default_category = Category.objects.filter(id=default_category_id).first() if default_category_id else None
        employee.current_task = Task.objects.filter(id=current_task_id).first() if current_task_id else None
        employee.save()

        messages.success(request, "Employee updated successfully.")
        return redirect('employee_list')

    context = {
        'employee': employee,
        'departments': departments,
        'categories': categories,
        'tasks': tasks
    }
    return render(request, 'people_management/update_employee.html', context)

def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, "Employee deleted successfully.")
        return redirect('employee_list')
    return render(request, 'people_management/delete_employee_confirm.html', {'employee': employee})

@login_required
def complain_list(request):
    complains = Complains.objects.filter(user=request.user)
    return render(request, 'people_management/complain_list.html', {'complains': complains})

@login_required
def complain_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        status = request.POST.get('status', 'new')

        if title and description:
            Complains.objects.create(
                user=request.user,
                title=title,
                description=description,
                location = location,
                status=status
            )
            return redirect('complain_list')

        return render(request, 'people_management/complain_create.html', {
            'error': 'All fields are required.'
        })

    return render(request, 'people_management/complain_create.html')


@login_required
def update_complain(request , complain_id):
    complain = get_object_or_404(Complains, id=complain_id, user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        status = request.POST.get('status')

        if title and description and location and status:
            complain.title = title
            complain.description = description
            complain.location = location
            complain.status = status
            complain.save()
            return redirect('complain_list')

        return render(request, 'people_management/update_complain.html', {
            'complain': complain,
            'error': 'All fields are required.'
        })

    return render(request, 'people_management/update_complain.html', {'complain': complain})

@login_required
def delete_complain(request, complain_id):
    complain = get_object_or_404(Complains, id=complain_id, user=request.user)

    if request.method == 'POST':
        complain.delete()
        return redirect('complain_list')

    return render(request, 'people_management/delete_complain.html', {'complain': complain})

    
@login_required
def repair_detail(request, complain_id):
    complain = get_object_or_404(Complains, id=complain_id)
    repair = getattr(complain, 'repair', None)
    return render(request, 'people_management/repair_detail.html', {
        'complain': complain,
        'repair': repair
    })

@login_required
def repair_create(request, complain_id):
    complain = get_object_or_404(Complains, id=complain_id)
    employees = Employee.objects.all()
    tasks = Task.objects.all()
    departments = Department.objects.all()  # Fetch all departments

    if request.method == 'POST':
        assigned_to_id = request.POST.get('assigned_to')
        task_id = request.POST.get('task')
        location = request.POST.get('location')
        notes = request.POST.get('notes')
        department_id = request.POST.get('department') # Get selected department

        assigned_to = get_object_or_404(Employee, id=assigned_to_id) if assigned_to_id else None
        task = get_object_or_404(Task, id=task_id) if task_id else None
        department = get_object_or_404(Department, id=department_id) if department_id else None

        repair = Repair.objects.create(
            complain=complain,
            assigned_to=assigned_to,
            task=task,
            location=location,
            notes=notes,
            department=department  
        )
        return redirect('repair_detail', complain_id=complain.id)
    else:
        context = {
            'complain': complain,
            'employees': employees,
            'tasks': tasks,
            'departments': departments
        }
        return render(request, 'people_management/repair_create.html', context)


@login_required
def repair_update(request, repair_id):
    repair = get_object_or_404(Repair, id=repair_id)
    employees = Employee.objects.all()
    tasks = Task.objects.all()
    departments = Department.objects.all()

    if request.method == 'POST':
        assigned_to_id = request.POST.get('assigned_to')
        task_id = request.POST.get('task')
        location = request.POST.get('location')
        notes = request.POST.get('notes')
        is_completed = request.POST.get('is_completed') is not None
        department_id = request.POST.get('department')

        repair.assigned_to = get_object_or_404(Employee, id=assigned_to_id) if assigned_to_id else None
        repair.task = get_object_or_404(Task, id=task_id) if task_id else None
        repair.location = location
        repair.notes = notes
        repair.is_completed = is_completed
        repair.department = get_object_or_404(Department, id=department_id) if department_id else None

        # 🔥 Set completed_at if marked as completed
        if is_completed and repair.completed_at is None:
            repair.completed_at = timezone.now()
        elif not is_completed:
            repair.completed_at = None  

        repair.save()
        return redirect('repair_update',repair.id)

    context = {
        'repair': repair,
        'employees': employees,
        'tasks': tasks,
        'departments': departments,
    }
    return render(request, 'people_management/repair_update.html', context)


@login_required
def repair_delete(request, repair_id):
    repair = get_object_or_404(Repair, id=repair_id)
    complain_id = repair.complain.id

    if request.method == 'POST':
        repair.delete()
        return redirect('complain_list') 

    return render(request, 'people_management/repair_confirm_delete.html', {
        'repair': repair
    })


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/change_password.html'
    success_url = reverse_lazy('password_change_done')

    def get_success_url(self):
        return str(self.success_url)