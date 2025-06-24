from django.db import models
from django.contrib.auth.models import User
from task_management_system_app.models import Category, Task 


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    default_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    current_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
class Complains(models.Model):
    COMPLAIN_STATUS = [
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, help_text="Enter the location of the issue",null=True, blank=True)
    status = models.CharField(max_length=20, choices=COMPLAIN_STATUS, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Repair(models.Model):
    complain = models.OneToOneField('Complains', on_delete=models.CASCADE, related_name='repair')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)  
    notes = models.TextField(blank=True)
    location = models.CharField(max_length=255, help_text="Enter the location of the issue",null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Repair for: {self.complain.title}"
 