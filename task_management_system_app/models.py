from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('suspend', 'Suspend'),
        ('ready', 'Ready'),
        ('complete', 'Complete'),
        ('delete', 'Delete'),
    ]
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=1)
    description = models.TextField(default='')
    location = models.CharField(max_length=255, default='')
    organizer = models.CharField(max_length=100, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    last_reset_date = models.DateField(null=True, blank=True)

    def reset_timer(self):
        ist = pytz.timezone('Asia/Kolkata')
        now = timezone.now().astimezone(ist)
        today = now.date()
        if self.last_reset_date == today:
            return
        
        if self.frequency == 'daily' and self.last_reset_date != today:
            self.start_date = now
            self.end_date = now.replace(hour=21, minute=0, second=0, microsecond=0)
            self.deadline = None
            # self.status = 'pending'
            self.last_reset_date = today
            self.save()

    def get_remaining_time(self):
        if self.frequency != 'daily':
            return None
        ist = pytz.timezone('Asia/Kolkata')
        now = timezone.now().astimezone(ist)
        if self.status == 'complete':
            return timezone.timedelta(seconds=0)
        if self.end_date and now < self.end_date:
            delta = self.end_date - now
            return delta
        return timezone.timedelta(seconds=0)

    def __str__(self):
        return self.name

class EmployeeLogin(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logins')
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} logged in at {self.login_time}"