from background_task import background
from django.utils import timezone
from datetime import timedelta
from .models import Order


# @background(schedule=timezone.now())
# def set_pending_orders():
#     today = timezone.now().date()
#     yesterday = today - timedelta(days=1)
#     cutoff_time = timezone.datetime.combine(yesterday, timezone.datetime.min.time()) + timedelta(days=1)
#
#     orders_to_update = Order.objects.filter(
#         order_status='new',
#         created_at__lt=cutoff_time
#     )
#
#     updated_count = orders_to_update.update(order_status='pending')
#     print(f'Successfully set {updated_count} orders to Pending')

@background(schedule=timezone.now())
def set_pending_orders():
    orders_to_update = Order.objects.filter(order_status='new')
    updated_count = orders_to_update.update(order_status='pending')
    print(f'Successfully set {updated_count} orders to Pending')