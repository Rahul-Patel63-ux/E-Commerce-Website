# from .models import UserProfileSetup
# from console.models import Cart, UserProfileSetup

from console.models import *

def global_data(request):

    context = {}

    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = UserProfileSetup.objects.get(user_id=user_id)
            context['user'] = user
            
            cart_count = Cart.objects.filter(user_id=user.id, status=True).count()
            
            context['cart_count'] = cart_count
            
        except UserProfileSetup.DoesNotExist:
            context['cart_count'] = 0
    else:
        context['cart_count'] = 0
        
    inventory_items = InventoryItem.objects.filter(allocated_quantity__gt=0)
    main_cats = Main_category.objects.all()
    sub_cats = Sub_category.objects.all()
    brands = Brand.objects.all()
    context['inventory_items'] = inventory_items
    context['main_cats'] = main_cats
    context['sub_cats'] =sub_cats
    context['brands'] = brands
    
    
    return context
