from django.urls import path
from user import views


urlpatterns = [
     path('', views.dashboard, name="dashboard"),
     path('each-product/<int:pk>', views.each_product, name="each-product"),
     path('product-view/', views.product_view, name="product-view"),
     path('add-to-cart/<int:pk>', views.add_to_cart, name="cart"),
     path('show-cart/', views.show_cart, name="show-cart"),
     path('delete/', views.delete_product, name='delete-product'),
     path('validate-coupon/', views.OrderView.as_view(), name='validate-coupon'),
     path('generate-order/', views.OrderView.as_view(), name='generate-order'),
     path('related-product/', views.related_products, name='related-product'),
     
     # User Authentication
     path('sign-up/', views.sign_up, name='sign-up'),
     path('sign-in/', views.sign_in, name='signIn'),
     path('sign-out/', views.sign_out, name='sign-out'),
     path('forget-password/', views.forget_password, name='forget-pass'),
     path('otp-configration/<int:user_id>', views.otp_page, name='otp'),
     path('otp-configration-2/', views.otp_page_2, name='otp-2'),
     
     # One time Profile Setup
     path('user-profile', views.profile, name='profile'),
     path('profile-setup/', views.one_time_profile_setup, name='onetime-profile'),
     
     # ajax requests
     path('get-states/', views.get_states, name='get_states'),
     path('get-cities/', views.get_cities, name='get_cities'),
     path('get-areas/', views.get_areas, name='get_areas'),
     
     # Connerction
     path('about-us/', views.about_us, name='about-us'),
     path('contact-us/', views.contact_us, name='contact-us'),
     
     # Services
     path('services/', views.services, name='services'),
]

