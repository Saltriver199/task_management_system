'''from django.core.management.base import BaseCommand
from django.utils import timezone
from task_management_system_app.models import Task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from datetime import time, timedelta, datetime

class Command(BaseCommand):
    help = 'Checks tasks for pending/completed status and performs actions based on time'

    def handle(self, *args, **kwargs):
        now = timezone.localtime()
        current_time = now.time()

        print("🕒 Current Time:", current_time)

        admin_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
        print("📧 Admin Emails:", admin_emails)

        if time(10, 0) <= current_time <= time(17, 0):
            pending_tasks = Task.objects.filter(status='pending')
            print("📋 Pending Tasks Count:", pending_tasks.count())
            if pending_tasks.exists():
                subject = '⚠️ Pending Tasks Alert'
                message = "The following tasks are still pending after 4 AM:\n\n"
                for task in pending_tasks:
                    assigned_user = task.assigned_to.username if task.assigned_to else 'Unassigned'
                    message += f"- {task.name} (Assigned to: {assigned_user})\n"
                try:
                    send_mail(subject, message, 'yashpatel342212@gmail.com', admin_emails, fail_silently=False)
                    self.stdout.write(self.style.SUCCESS("✅ Admin notified of pending tasks."))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ Failed to send email: {e}"))

        if time(17, 0) <= current_time <= time(19, 0):
            completed_tasks = Task.objects.filter(status='complete')
            updated_count = 0

            today_date = timezone.localdate()
            tomorrow_date = today_date + timedelta(days=1)

            tz = timezone.get_current_timezone()

            naive_start = datetime.combine(today_date, time(0, 0))
            start_dt = timezone.make_aware(naive_start, tz)

            naive_end = datetime.combine(tomorrow_date, time(7, 0))
            end_dt = timezone.make_aware(naive_end, tz)

            naive_dead = datetime.combine(tomorrow_date, time(7, 30))
            dead_dt = timezone.make_aware(naive_dead, tz)

            for task in completed_tasks:
                print(f"Before reset (Task {task.pk}): start_date={task.start_date}, end_date={task.end_date}, deadline={task.deadline}")
                task.status = 'pending'
                task.start_date = start_dt
                task.end_date = end_dt
                task.deadline = dead_dt
                print(f" After assignment: start_date={task.start_date}, end_date={task.end_date}, deadline={task.deadline}")
                task.save()
                refreshed = Task.objects.get(pk=task.pk)
                print(f" After save: start_date={refreshed.start_date}, end_date={refreshed.end_date}, deadline={refreshed.deadline}")
                updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"🔁 {updated_count} tasks reset. start_date={start_dt}, end_date={end_dt}, deadline={dead_dt}"
            ))'''


from django.core.management.base import BaseCommand
from django.utils import timezone
from task_management_system_app.models import Task
from django.core.mail import send_mail
from django.contrib.auth.models import User
import logging
import pytz

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Resets daily tasks and sends pending task alerts'

    def handle(self, *args, **kwargs):
        ist = pytz.timezone('Asia/Kolkata')
        now = timezone.now().astimezone(ist)
        current_time = now.time()
        today = now.date()

        # Reset daily tasks at midnight
        if current_time.hour == 0:
            daily_tasks = Task.objects.filter(frequency='daily')
            for task in daily_tasks:
                task.reset_timer()
                logger.debug(f"Reset task {task.name}: end_date={task.end_date}")
            self.stdout.write(self.style.SUCCESS(f"Reset {daily_tasks.count()} daily tasks."))

        # Send pending task alerts between 10 AM and 5 PM
        if 10 <= current_time.hour < 17:
            pending_tasks = Task.objects.filter(status='pending')
            if pending_tasks.exists():
                admin_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
                subject = 'Pending Tasks Alert'
                message = "Pending tasks after 10 AM:\n\n"
                for task in pending_tasks:
                    assigned_user = task.assigned_to.username if task.assigned_to else 'Unassigned'
                    message += f"- {task.name} (Assigned to: {assigned_user})\n"
                try:
                    send_mail(subject, message, 'yashpatel342212@gmail.com', admin_emails)
                    self.stdout.write(self.style.SUCCESS("Admin notified of pending tasks."))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed to send email: {e}"))   