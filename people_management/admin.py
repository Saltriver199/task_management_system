from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Employee, Complains, Repair

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'department', 'email', 'default_category', 'current_task')
    list_filter = ('department', 'default_category')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'email')
    autocomplete_fields = ('user', 'default_category', 'current_task')
    ordering = ('user__username',)


@admin.register(Complains)
class ComplainsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status_badge', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'location', 'user__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    @admin.display(description='Status')
    def status_badge(self, obj):
        color_map = {
            'new': 'secondary',
            'in_progress': 'warning',
            'resolved': 'success',
            'closed': 'dark'
        }
        color = color_map.get(obj.status, 'light')
        return format_html(
            '<span class="badge bg-{} text-uppercase">{}</span>',
            color, obj.get_status_display()
        )


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ('id', 'complain_title', 'assigned_to', 'task', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'assigned_to')
    search_fields = ('complain__title', 'assigned_to__user__username', 'task__title', 'location')
    autocomplete_fields = ('complain', 'assigned_to', 'task')
    ordering = ('-completed_at',)

    @admin.display(description='Complaint')
    def complain_title(self, obj):
        return obj.complain.title
