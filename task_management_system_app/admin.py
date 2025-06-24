from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_colored')
    search_fields = ('name',)
    ordering = ('name',)

    @admin.display(description='Name')
    def name_colored(self, obj):
        return format_html(
            '<span class="badge bg-primary">{}</span>', obj.name
        )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'colored_category', 'assigned_to', 'formatted_start_date',
        'formatted_end_date', 'deadline_badge', 'priority_badge', 'status_badge'
    )
    list_filter = ('status', 'priority', 'category', 'assigned_to')
    search_fields = ('name', 'description', 'location', 'organizer')
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'
    autocomplete_fields = ('assigned_to', 'category')

    @admin.display(description='Category')
    def colored_category(self, obj):
        return format_html(
            '<span class="badge bg-info text-dark">{}</span>',
            obj.category.name if obj.category else "—"
        )

    @admin.display(description='Start')
    def formatted_start_date(self, obj):
        return obj.start_date.strftime('%Y-%m-%d')

    @admin.display(description='End')
    def formatted_end_date(self, obj):
        return obj.end_date.strftime('%Y-%m-%d') if obj.end_date else "—"

    @admin.display(description='Deadline')
    def deadline_badge(self, obj):
        if obj.deadline:
            return format_html(
                '<span class="badge bg-danger">{}</span>', obj.deadline.strftime('%Y-%m-%d')
            )
        return "—"

    @admin.display(description='Priority')
    def priority_badge(self, obj):
        color_map = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
        }
        color = color_map.get(obj.priority, 'secondary')
        return format_html(
            '<span class="badge bg-{} text-uppercase">{}</span>',
            color, obj.priority
        )

    @admin.display(description='Status')
    def status_badge(self, obj):
        color_map = {
            'pending': 'secondary',
            'in_progress': 'warning',
            'completed': 'success',
            'cancelled': 'dark'
        }
        color = color_map.get(obj.status, 'light')
        return format_html(
            '<span class="badge bg-{} text-uppercase">{}</span>',
            color, obj.status
        )
