from django.db import models
from django.contrib.auth.models import User
from people_management.models import Employee 

class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_days_per_year = models.PositiveIntegerField(default=0, help_text="Maximum days allowed for this leave type per year.")
    is_paid = models.BooleanField(default=True) 

    def __str__(self):
        return self.name

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests', 
                                 help_text="The employee submitting this leave request.")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, 
                                   help_text="The type of leave being requested.")
    start_date = models.DateField(help_text="The first day of the requested leave.")
    end_date = models.DateField(help_text="The last day of the requested leave.")
    
 
    reason = models.TextField(
        blank=False, 
        help_text="Detailed reason for the leave request (min. 20, max. 500 characters)."
    )
    
    
    emergency_contact = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Name and contact number of a person to contact during leave."
    )

    
    work_handover = models.TextField(
        blank=True, 
        null=True, 
        help_text="Details about work delegation or handover arrangements."
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', 
                              help_text="Current status of the leave request.")
    applied_at = models.DateTimeField(auto_now_add=True, 
                                      help_text="Timestamp when the leave request was submitted.")
    reviewed_at = models.DateTimeField(null=True, blank=True, 
                                       help_text="Timestamp when the leave request was reviewed.")
    reviewer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_leaves', 
                                 help_text="The user (manager/admin) who reviewed this leave request.")

    class Meta:
        ordering = ['-applied_at']
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"

    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.leave_type.name} ({self.start_date} to {self.end_date})"


    def get_duration(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError("End date cannot be before the start date.")
        
