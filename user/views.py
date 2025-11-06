from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from console.models import *
from django.db.models import Q, Sum
from django.db import transaction 
from django.contrib import messages
from datetime import datetime
from django.views import View
# from .models import UserRegistration, UserProfileSetup
from django.core.mail import send_mail
import random
import requests
import json
from functools import wraps
from collections import Counter

from decimal import Decimal



# session login decorator
def session_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')

        if not user_id:
            return redirect('signIn')

        user = UserRegistration.objects.filter(id = user_id).first()
        if not user:
            del request.session['user_id']
            messages.warning(request, "You are not an authorized User!")
            return redirect('signIn')

        return view_func(request, *args, **kwargs)

    return wrapper

def send_otp_on_email(email, subject, message):
    
    from_email = "rp797968@gmail.com"
    recipient_list = [f"{email}"] # It contain multiple email-address on them we want to send same email.
    send_mail(subject, message, from_email, recipient_list)


# To send OTP on Phone Number (Not implimented)
def send_on_number(number, subject, message):
    api_key = "8c79945a-4ccb-11f0-a562-0200cd936042"
    
    url = f"https://2factor.in/API/V1/{api_key}/ADDON_SERVICES/SEND/TSMS"

    full_message = f"{subject}: {message}"

    payload = {
        "From": "TXTIND",  
        "To": number,
        "Msg": full_message
    }

    headers = {
        'Content-Type': "application/json"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print("2Factor response:", response.text)
        
        if response.status_code == 200:
            return True
        else:
            return False
        
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return redirect('forget-pass')
    
    
def sign_up(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('useremail')
            username = request.POST.get('username')
            password = request.POST.get('password')
            cpassword = request.POST.get('cpass')
            number = request.POST.get('number')
            
            if password == cpassword:
                if UserRegistration.objects.filter(email=email).exists():
                    messages.warning(request, "User already exists!")
                    return redirect('sign-up')
                if UserRegistration.objects.filter(username=username).exists():
                    messages.warning(request, "Username already exists!")
                    return redirect('sign-up')
                
                if UserRegistration.objects.filter(phone_number=number).exists():
                    messages.warning(request, "Phone number already exists!")
                    return redirect('sign-up')
                
                otp = random.randint(1111, 9999)
                subject = "E-Commerce Shopping Registration OTP"
                message = f"Your Regestration OTP is: {otp}"
                send_otp_on_email(email, subject, message)
                
                user = UserRegistration.objects.create(
                    email= email,
                    username= username,
                    password= password,
                    confirm_password= cpassword,
                    phone_number= number,
                    otp= otp
                )
                # messages.success(request, f"Registration Successfully.")
                return redirect('otp-2', user.id)
    except Exception as e:
        print(f"An Error Occured {e}")
    return render(request, 'userAuthentication/sign_up.html')


def sign_in(request):
    
    if request.method == 'POST':
        email = request.POST.get('useremail')
        password = request.POST.get('password')
            
        try:
            user = UserRegistration.objects.get(email= email)
            
            if not user.status:
                messages.warning(request, "Your account is inactive!")
                return redirect('signIn')
            
            if user:
                if user.password == password:
                    request.session['user_id'] = user.id
                    print("dklhsihfiaod", request.session.get('user_id'))
                    request.session['username'] = user.username
                    print("kjfkshsahdsfipao", request.session.get('username'))
                    if not user.onetime_profile_setup:
                        messages.success(request, "Login Successfull.")
                        return redirect('onetime-profile')
                    else:
                        messages.success(request, "Login Successfull.")
                        return redirect('dashboard')
                else:
                    messages.warning(request, 'Incorrect Password!')
            
        except UserRegistration.DoesNotExist:
            messages.warning(request, 'User Not Found!')
    return render(request, 'userAuthentication/sign_in.html')

@session_login_required
def sign_out(request):
    request.session.flush()
    messages.success(request, "Sign Out Successfully.")
    return redirect('dashboard')


def forget_password(request):
    if request.method == 'POST':
        user_credentrial = request.POST.get('forgetpass', '').strip()
       
        try:          
            # email and phone number      
            # user = UserRegistration.objects.filter(
            #     Q(email__iexact=user_credentrial) |
            #     Q(phone_number__iexact=user_credentrial)
            #     ).first()
            
            # if user.email == user_credentrial:
            #     subject = 'E-Commerce Shopping LogIn Credentails'
            #     message = f"Registered Username: {user.username}\nRegistered Password: {user.password}"
            #     send_otp_on_email(user.email , subject, message)
            #     messages.success(request, "Please Check your Email.")
            #     return redirect('signIn')
            # elif user.phone_number == user_credentrial:
            #     subject = 'E-Commerce Shopping LogIn Credentails'
            #     message = f"Registered Username: {user.username}\nRegistered Password: {user.password}"
            #     send_on_number(user.phone_number, subject, message)
            #     messages.success(request, "Please Check your Phone SMS.")
            #     return redirect('signIn')
            
            # only with email
            user = UserRegistration.objects.filter(email__iexact= user_credentrial).first()
            
            if user:
                subject = 'E-Commerce Shopping LogIn Credentails'
                message = f"Registered Username: {user.username}\nRegistered Password: {user.password}"
                send_otp_on_email(user.email , subject, message)
                messages.success(request, "Please Check your Email.")
                return redirect('signIn')
            messages.warning(request, "No user found!")
            return redirect('forget-pass')
        except UserRegistration.DoesNotExist:
            messages.warning(request, "No user found!")
            return redirect('forget-pass')
    return render(request, 'userAuthentication/forget_password.html')

def otp_page(request, user_id):
    
    user  = get_object_or_404(UserRegistration, id=user_id)
    if request.method == "POST":
        digit1 = request.POST.get('digit1')
        digit2 = request.POST.get('digit2')
        digit3 = request.POST.get('digit3')
        digit4 = request.POST.get('digit4')
        
        user_otp = digit1 + digit2 + digit3 + digit4
        
        if user.otp == user_otp:
            user.status = True
            user.save()
            messages.success(request, "Registration Successfull.")
            return redirect('signIn')
        messages.warning(request, "Please enter valid OTP")
        return redirect('otp', user.id)
   
    return render(request, 'userAuthentication/otp_page.html', {'user_id': user.id})


def otp_page_2(request, user_id):
    
    user  = get_object_or_404(UserRegistration, id=user_id)
    print(":;sdjfpasdfhieofpejfo", user.otp, type(user.otp))
    if request.method == "POST":
        digit1 = request.POST.get('digit1')
        digit2 = request.POST.get('digit2')
        digit3 = request.POST.get('digit3')
        digit4 = request.POST.get('digit4')
        
        user_otp = digit1 + digit2 + digit3 + digit4
        print("ojfsfsjfjioofjf", user_otp)
        if user.otp == user_otp:
            user.status = True
            user.save()
            messages.success(request, "Registration Successfull.")
            return redirect('signIn')
        messages.warning(request, "Please enter valid OTP")
        return redirect('otp-2', user.id)
   
    return render(request, 'userAuthentication/otp_page2.html', {'user_id': user.id})

@session_login_required
def profile(request):
    
    user_id = request.session.get('user_id')    
    user = get_object_or_404(UserProfileSetup, user_id=user_id)
    
    if request.method == 'POST':
        image = request.FILES.get('image', '')
        username = request.POST.get('username', '').strip()
        age = request.POST.get('age', '').strip()
        gender = request.POST.get('gender', '').strip()
        country = request.POST.get('country', '').strip()
        state = request.POST.get('state', '').strip()
        city = request.POST.get('city', '').strip()
        area = request.POST.get('area', '').strip()
        address = request.POST.get('address', '').strip()
        
        user.user.username = username
        user.user.save()
        
        if image:
            user.profile_picture = image
        user.age = age
        user.gender = gender
        user.address = address
        user.area_id = area
        user.city_id= city
        user.state_id= state
        user.country_id= country
        user.save()
        messages.success(request, "Profile Updated Successfully.")
    country = Country.objects.all()
    state = State.objects.all()
    city = City.objects.all()
    area = Area.objects.all()
    context ={
        'user': user,
        'countries' : country,
        'states' : state,
        'cities' : city,
        'area' : area
    }
    return render(request, 'profile/user_profile.html', context)
       


def one_time_profile_setup(request):
    
    user_id = request.session.get('user_id')
    user = get_object_or_404(UserRegistration, id= user_id)
    if request.method == 'POST':
        
        image = request.FILES.get('image')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        area = request.POST.get('area')
        address = request.POST.get('address')
        
        UserProfileSetup.objects.create(
                user_id= user_id,
                profile_picture= image,
                age= age, 
                gender= gender, 
                country_id= country,
                state_id = state,
                city_id= city,
                area_id= area,
                address= address
            )
        user.onetime_profile_setup = not user.onetime_profile_setup
        user.save()
        messages.success(request , "Profile created successfully.")
        return redirect('dashboard')
    
    country = Country.objects.all()
    state = State.objects.all()
    city = City.objects.all()
    area = Area.objects.all()
    context ={
        'countries' : country,
        'states' : state,
        'cities' : city,
        'area' : area
    }
    return render(request, 'profile/one_time_profile_setup.html', context)


def dashboard(request):
    try:      
        inventory_items = InventoryItem.objects.filter(allocated_quantity__gt=0).select_related('product').prefetch_related('product__images')
        bannerImages = Banner.objects.filter(status=True).order_by('-id')
        main_cats = Main_category.objects.all()
        sub_cats = Sub_category.objects.all()
        brands = Brand.objects.all()
        
        context = {
                'products': inventory_items,
                'main_cats': main_cats,
                'sub_cats': sub_cats,
                'brands': brands,
                'banners': bannerImages
                # 'images': images,
        }
        return render(request, 'dashboard/dashboard.html', context)
    except Exception as e:
        print(f"An Error Occured : {e}")
        return render(request, 'dashboard/dashboard.html')
    
        
    
def each_product(request, pk):
    try:
        user_id = request.session.get('user_id')
        user = UserProfileSetup.objects.filter( user= user_id) or None
        
        inventory_items = get_object_or_404(InventoryItem, product=pk, allocated_quantity__gt=0)
        admin_profile = get_object_or_404(Admin_Onetime_Profile, admin_registration_id=inventory_items.admin_registration_id)
        product = inventory_items.product
        images = ProductCatalogueImages.objects.filter(product=product)
        purchase = PurchaseItem.objects.filter(id=inventory_items.purchase_item.id).first()
        cart = Cart.objects.filter( user_id=user_id, product=product).first() or None
        sizes = product.product_size_ref.all()
        total_inventory = InventoryItem.objects.filter(product=product).aggregate(total_quantity=Sum('allocated_quantity'))['total_quantity'] or 0
        available_sizes = [
            {
                'size': size,
                'available': total_inventory > 0,
                'quantity': total_inventory
            }
            for size in sizes
        ]

        context = {
            'admin_profile': admin_profile,
            'pro': product,
            'images': images,
            'purchase': purchase,
            'inventory_items': inventory_items,
            'available_sizes': available_sizes,
            'cart': cart
        }

        return render(request, 'dashboard/each_product.html', context)
    
    except Exception as e:
        print(f"An Error Occurred: {e}")
        return render(request, 'dashboard/each_product.html', {'error': str(e)})


def product_view(request):
    try:
        if request.headers.get('HX-Request'):
            query= request.GET.get('query')
            
            main_cat_value = request.GET.getlist('mainCatInput')
            sub_cat_value = request.GET.getlist('subCatInput')
            brand_name = request.GET.getlist('brandInput')
            query_in = Q()
            
            # Search Query
            if query:
                query_in &= Q(
                    # Q(product_brand_ref__brand_name__icontains= query) |
                    Q(product__product_title__icontains= query)
                )
            # Filter Query
            else:
                if main_cat_value and sub_cat_value and brand_name:
                    query_in = Q(
                        Q(product__main_category_ref__main_category__in=main_cat_value) &
                        Q(product__sub_category_ref__sub_category__in=sub_cat_value) &
                        Q(product__product_brand_ref__brand_name__in=brand_name)
                    )
                elif main_cat_value and sub_cat_value:
                    query_in = Q(
                        Q(product__main_category_ref__main_category__in=main_cat_value) &
                        Q(product__sub_category_ref__sub_category__in=sub_cat_value)
                    )
                elif main_cat_value and brand_name:
                    query_in = Q(
                        Q(product__main_category_ref__main_category__in=main_cat_value) &
                        Q(product__product_brand_ref__brand_name__in=brand_name)
                    )
                elif brand_name and sub_cat_value:
                    query_in = Q(
                        Q(product__product_brand_ref__brand_name__in=brand_name) &
                        Q(product__sub_category_ref__sub_category__in=sub_cat_value)
                    )
                elif main_cat_value:
                    query_in &= Q(product__main_category_ref__main_category__in=main_cat_value)
                    
                elif sub_cat_value:
                    query_in &= Q(product__sub_category_ref__sub_category__in=sub_cat_value)
                    
                elif brand_name:
                    query_in &= Q(product__product_brand_ref__brand_name__in=brand_name)
                
            inventory_items = InventoryItem.objects.filter(query_in, allocated_quantity__gt=0).select_related('product').prefetch_related('product__images').order_by('-product__id')
            context = {
                'products': inventory_items,
            }
                
            return render(request, 'dashboard/product_view.html', context)
    except Exception as e:
        print(f"An Error Occured : {e}")
        

def related_products(request):
    """ To filter the products from Modules based on Main Category/Sub Category/Brands """
    main = request.GET.get('main')
    sub = request.GET.get('sub')
    brand = request.GET.get('brand')
    query_in = Q()
    if brand:
        query_in = Q(product__product_brand_ref__brand_name__iexact=brand)
    elif main:
        query_in = Q(product__main_category_ref__main_category__iexact=main)
    elif sub:
        query_in = Q(product__sub_category_ref__sub_category__iexact=sub)
    product = InventoryItem.objects.filter(query_in, allocated_quantity__gt=0).select_related('product').prefetch_related('product__images')
    print('Poooooooooooooo ', product)
    if main:
        categorized_product = {}
        for m in product:
            sub_cat = m.product.sub_category_ref.sub_category
            product_list = []
            if sub_cat not in categorized_product:
                categorized_product[sub_cat]  = []
            
            if not categorized_product[sub_cat]:
                for i in product:
                    if i.product.sub_category_ref.sub_category == sub_cat:
                        product_list.append(i)
                categorized_product[sub_cat] = product_list
        print("rrrrrrrrrrrrrrrrrr --", categorized_product)
        
        context = {
        'categorized_product': categorized_product,
    }
    else:
        context = {
            'product': product,
            'value' : brand or main or sub
        }
    return render(request, 'dashboard/related_products.html', context)
     
@session_login_required
def add_to_cart(request, pk):
    user_id = request.session.get('user_id')
    user = get_object_or_404(UserRegistration, id=user_id)
    try:
        if request.method == "POST":

            # Quantity Increment/Decrement
            qty = request.POST.get('qty')
            print("pppppppppppppp QTY", qty)
            
            if qty:
                cart = get_object_or_404(Cart, id=pk, user=user)
                print("cccccccccccccccc Cart", cart)

                inventory_item = InventoryItem.objects.filter(product=cart.product, allocated_quantity__gt=0, inventory_status=True)
                print("fhoajhadsgohgaj", inventory_item[0].id)

                if int(qty) <= inventory_item[0].allocated_quantity:
                    cart.quantity = qty
                    cart.total_amount = float(qty) * float(inventory_item[0].sale_price)
                    cart.save()
                    return redirect('show-cart')
                else:
                    messages.warning(request, 'Requested quantity exceeds available stock!')
                    return redirect('show-cart')

            # Adding Product for first time
            purchase_item = PurchaseItem.objects.filter(product=pk).last()
            size = request.POST.get('size')
            if not size:
                messages.warning(request, 'Please select a size!')
                return redirect('each-product', purchase_item.product.id)

            if not purchase_item.product.product_size_ref.filter(product_size_short_name=size).exists():
                messages.warning(request, 'Invalid size selected!')
                return redirect('each-product', purchase_item.product.id)

            inventory_item = InventoryItem.objects.filter(product=purchase_item.product,
                                                          allocated_quantity__gt=0, inventory_status=True).first()
            if not inventory_item:
                messages.warning(request, 'Product is out of stock!')
                return redirect('dashboard')

            existing_item = Cart.objects.filter(user=user, product=purchase_item.product, selected_size=size).first()
            if existing_item:
                messages.success(request, 'Product Already Added!👍')

            else:
                unit_price = inventory_item.sale_price
                Cart.objects.create(
                    user=user,
                    selected_size=size,
                    purchaseItem=purchase_item,
                    product=purchase_item.product,
                    quantity=1,
                    amount=unit_price,
                    total_amount=unit_price
                )
                messages.success(request, 'Product Added Successfully!😍')
            return redirect('show-cart')
    except Exception as e:
        print(f"An Error Occurred: {e}")
        return redirect('dashboard')
    
    
@session_login_required
def show_cart(request):
    
    try:
        user_id = request.session.get('user_id')
        user = get_object_or_404(UserRegistration, id=user_id)
        
        cart_products = Cart.objects.filter(user=user,status=True).select_related('product', 'purchaseItem')
        inventory_items = InventoryItem.objects.filter(allocated_quantity__gt=0)        

        countries = Country.objects.all()
        states = State.objects.all()
        cities = City.objects.all()
        area = Area.objects.all()
        number_of_cart_items = cart_products.count()
        context = {
            'inventory_items': inventory_items,
            'cart_products': cart_products,
            'num' : number_of_cart_items,
            'countries': countries,
            'states': states,
            'cities': cities,
            'area': area
        }
        
        return render(request, 'dashboard/add_to_cart.html', context)
    except Exception as e:
        print(f'An Error Occured {e}')
    return render(request, 'dashboard/add_to_cart.html')


@session_login_required
def delete_product(request):
    
    delid = request.GET.get('delid')
    product = get_object_or_404(Cart, id=delid)
    product.delete()
    messages.success(request, 'Product removed Successfully!😕')
    return redirect('show-cart')


def generate_order_id(user):
    today_code = datetime.now().strftime('%y%m%d')
    counter, created = OrderCounter.objects.get_or_create(date_code=today_code)
    order_reg_id = today_code + f"{counter.count:02d}"
    counter.count += 1
    counter.save()
    
    Order.objects.create(
        user=user,
        order_reg_id= order_reg_id,
    )

class OrderView(View):

    coupon_code = 'No Coupon'
    coupon_discount_percent = 0
    
    # Validates coupon code for Order Place
    def validate_coupon(self, request):
        
        user_id = request.session.get('user_id')
        user = get_object_or_404(UserRegistration, id=user_id)
        if request.headers.get('HX-Request'):
            code = request.GET.get('coupon')
            if code:
                try:
                    coupon = Coupon.objects.get(coupon_code=code, user_id=user, status=True)
                    with transaction.atomic():
                        OrderView.coupon_code=coupon.coupon_code

                        OrderView.coupon_discount_percent=coupon.coupon_discount_percent
                        
                        return JsonResponse({
                            "valid": True,
                            'min_purchase': coupon.minimum_purchase_amount,
                            'discount_per': coupon.coupon_discount_percent,
                            'coupon_code': coupon.coupon_code
                        })
                except Coupon.DoesNotExist:
                    return JsonResponse({'valid': False})
                except Exception as e:
                    print(f"An error occurred for coupon: {e}")
                    return JsonResponse({'valid': False})
        return JsonResponse({'valid': False})

    # Post the Order to places
    def post(self, request, *args, **kwargs):
        return self.generate_order(request)
    
    # Store Products to Order Table in DB
    def generate_order(self, request):
        
        """Handles order generation"""
        
        global global_top_product
        
        user_id = request.session.get('user_id')
        user = get_object_or_404(UserRegistration, id= user_id)
        
        # Store the delivery address
        country = request.POST.get('country')
        country = get_object_or_404(Country, id=country)
        
        state = request.POST.get('state')
        state = get_object_or_404(State, id=state)
        
        city = request.POST.get('city')
        city = get_object_or_404(City, id=city)
        
        area = request.POST.get('area')
        area = get_object_or_404(Area, id=area)
        
        address = request.POST.get('address')
        
        # To generate Order if coupon is not applied
        generate_order_id(user= user)

        # Fetch active cart items
        cart = Cart.objects.filter(user=user, status=True).select_related('product', 'purchaseItem')
        if not cart.exists():
            messages.warning(request, "Your cart is empty!")
            return redirect('show-cart')
        titles = []
        qty = []
        price = []
        quantity_mul_price = []
        sub_total = []
        discount = []
        discount_percent = []
 
        for pro in cart:

            inventory_item = InventoryItem.objects.filter(product=pro.product,inventory_status=True).last()

            if pro.quantity > inventory_item.allocated_quantity:
                messages.warning(request, f"Not enough stock for {pro.product.product_title} ({pro.selected_size})!")
                return redirect('show-cart')
            
            titles.append(str(pro.product.product_title))
            qty.append(str(pro.quantity))
            price.append(str(inventory_item.sale_price))
            quantity_mul_price.append(str(inventory_item.sale_price * pro.quantity))

            unit_price = inventory_item.sale_price
            discount_percent_value = inventory_item.discount_percent or Decimal('0')
            discount_amount = (unit_price * discount_percent_value) / Decimal('100')
            total = Decimal(pro.quantity) * (unit_price - discount_amount)

            sub_total.append(str(total))
            discount.append(str(Decimal(pro.quantity) * discount_amount))
            discount_percent.append(str(float(discount_percent_value)))

            # Update inventory
            inventory_item.allocated_quantity -= pro.quantity
            inventory_item.save()


        
        total = sum(Decimal(i) for i in sub_total)
        st = total
        tax = st * Decimal('0.18')

        # Fetch the last order for the user
        order = Order.objects.filter(user_id=user_id).last()
        grand_total = st + tax
        if order.coupon_discount_percent:
            dis = (grand_total * Decimal(order.coupon_discount_percent)) / Decimal('100')
            grand_total = grand_total - dis
            grand_total = f"{grand_total:.2f}"
        else:
            grand_total = f"{grand_total:.2f}"

        with transaction.atomic():

            # Update order details
            order.user = user
            order.order_items = '* '.join(titles)
            order.order_price = '* '.join(price)
            order.quantity_mul_price = '* '.join(quantity_mul_price)
            order.order_quantity = '* '.join(qty)
            order.order_subtotal = '* '.join(sub_total)
            order.order_discount = '* '.join(discount)
            order.order_discount_percent = '* '.join(discount_percent)
            order.grandtotal = grand_total
            order.coupon_code = OrderView.coupon_code or 'No Coupon'
            order.coupon_discount_percent = OrderView.coupon_discount_percent or 0
            order.country = country
            order.state = state
            order.city = city
            order.area = area
            order.address = address
            order.status = True
            order.created_at = datetime.now()

            print("Order Data:", {
                'order_reg_id': order.order_reg_id,
                'order_items': order.order_items,
                'order_price': order.order_price,
                'quantity_mul_price': order.quantity_mul_price,
                'order_quantity': order.order_quantity,
                'order_subtotal': order.order_subtotal,
                'order_discount': order.order_discount,
                'order_discount_percent': order.order_discount_percent,
                'grandtotal': order.grandtotal,
                'status': order.status
            })

            # Add OrderItems creation
            for pro, item_price, item_qty, item_quantity_mul_price in zip(cart, price, qty, quantity_mul_price):
                inventory_item = InventoryItem.objects.filter(product=pro.product, inventory_status=True).last()
                OrderItems.objects.create(
                    order_ref=order,
                    admin_registration=inventory_item.admin_registration_id,
                    product_name=pro.product.product_title,
                    quantity=int(item_qty),
                    price=Decimal(item_price),
                    quantity_mul_price=item_quantity_mul_price,
                    # order_item_created_at=datetime.now()
                )

            order.save()

            cart.delete()
            messages.success(request, "Order Placed Successfully.")

        return redirect('generate-order')

    # Get the Orders from Order Table to Invoice
    def get(self, request, *args, **kwargs):
        """Handles invoice display"""
        if request.GET.get("coupon"):  # Coupon validation (HTMX)
            return self.validate_coupon(request)

        user_id = request.session.get('user_id')
        # Invoice display
        order = Order.objects.filter(user_id= user_id).last()
        title = order.order_items.split("*")
        price = order.order_price.split("*")
        quantity_mul_price = order.quantity_mul_price.split("*")
        qty = order.order_quantity.split("*")
        subtotal = order.order_subtotal.split("*")
        discounted_value = order.order_discount.split("*")
        discount_percent = order.order_discount_percent.split("*")

        items = zip(title, price, quantity_mul_price, qty, subtotal, discounted_value, discount_percent)

        context = {
            'order': order,
            'items': items
        }
        return render(request, 'dashboard/invoice.html', context)
    

def get_states(request):
    country_id = request.GET.get('country_id')
    print(country_id, 'country id')
    states = State.objects.filter(country_ref_id=country_id, state_status=True).values('id', 'state_name')
    print(states, 'states')
    return JsonResponse({'states': list(states)})

def get_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state_ref_id=state_id, city_status=True).values('id', 'city_name')
    return JsonResponse({'cities': list(cities)})


def get_areas(request):
    city_id = request.GET.get('city_id')
    areas = Area.objects.filter(city_ref_id=city_id, area_status=True).values('id', 'area_name')
    return JsonResponse({'areas': list(areas)})


def about_us(request):
    
    return render(request, 'aboutUs/about_us.html')

def contact_us(request):
    
    return render(request, 'contactUs/contact_us.html')

def services(request):
    
    return render(request, 'userServices/services.html')





