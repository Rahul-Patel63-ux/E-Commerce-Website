# from django.core.management.base import BaseCommand
# from background_task.models import Task
# from console.tasks import set_pending_orders
#
# from django.utils import timezone
#
# from datetime import timedelta
#
# class Command(BaseCommand):
#     help = 'Schedules the set_pending_orders task to run daily at 12:01 AM'
#
#     def handle(self, *args, **kwargs):
#         # Schedule the task to run daily at 12:01 AM
#         schedule_time = timezone.now() + timedelta(seconds=60)
#         set_pending_orders(repeat=Task.DAILY, repeat_until=None, schedule=schedule_time)
#         self.stdout.write(self.style.SUCCESS('Successfully scheduled set_pending_orders task'))

from django.core.management.base import BaseCommand
from background_task.models import Task
from console.tasks import set_pending_orders
from django.utils import timezone
from datetime import timedelta, datetime

class Command(BaseCommand):
    help = 'Schedules the set_pending_orders task to run daily at 12:01 AM IST'

    def handle(self, *args, **kwargs):
        # Get current time in IST
        now = timezone.now()
        # Set schedule for 12:01 AM IST of the next day
        schedule_time = now.replace(hour=0, minute=1, second=0, microsecond=0)
        if now.hour >= 0 and now.minute >= 1:
            schedule_time += timedelta(days=1)
        set_pending_orders(repeat=Task.DAILY, repeat_until=None, schedule=schedule_time)
        self.stdout.write(self.style.SUCCESS(f'Successfully scheduled set_pending_orders task for {schedule_time} and daily thereafter'))