
from django.db import models
from ckeditor.fields import RichTextField
from datetime import datetime

from django.utils import timezone

import random
import string


# Create your models here.



class Admin_registrations(models.Model):
    admin_registration_id=models.CharField(max_length=15,unique=True)
    admin_email=models.EmailField()
    admin_username=models.CharField(max_length=100)
    admin_password= models.CharField(max_length=100)
    admin_confirm_password= models.CharField(max_length=100)
    otp = models.CharField(max_length=8, null=True, blank=True)
    admin_registration_status= models.BooleanField(default=False)
    admin_registrations_created_at=models.DateTimeField(default=datetime.now)
    admin_oneTime_profile_status = models.BooleanField(default=False)

    def generate_registration_id(self):
        registration_date=self.admin_registrations_created_at or timezone.now()

        day= registration_date.strftime('%d')
        month=registration_date.strftime('%m')
        year=registration_date.strftime('%y')

        date_start = registration_date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = registration_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        count= Admin_registrations.objects.filter(admin_registrations_created_at__range=(date_start,date_end)).count()+1

        if count< 10:
            count_string= '0'+str(count)
        else:
            count_string=str(count)


        result= 'ECOM'+ str(day) +str(month)+str(year)+count_string

        return result

    def save(self, *args, **kwargs):

        if not self.admin_registration_id:
            self.admin_registration_id = self.generate_registration_id()

            while Admin_registrations.objects.filter(admin_registration_id=self.admin_registration_id).exists():
                self.admin_registration_id = self.generate_registration_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.admin_username} - {self.admin_registration_id}"

class Admin_Onetime_Profile(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.CASCADE, null=True)
    admin_name= models.CharField(max_length=100, null=True, blank=True)
    admin_phone = models.CharField(max_length=15, null=True, blank=True)
    admin_gender= models.CharField(max_length=10, null=True, blank=True)
    admin_dob = models.DateField(null=True)
    admin_aadhar = models.CharField(max_length=15, null=True, blank=True)
    admin_company_name = models.CharField(max_length=100, null=True, blank=True)
    admin_company_regno = models.CharField(max_length=30, null=True, blank=True)
    admin_company_logo = models.ImageField()
    admin_company_banner = models.ImageField()
    admin_company_icon = models.ImageField()
    admin_company_about = RichTextField()
    admin_company_summary = RichTextField()


class AdminContactUs(models.Model):
    admin_registration_id=models.ForeignKey(Admin_registrations,on_delete=models.CASCADE,null=True)
    admin_contactus_email=models.EmailField()
    admin_contactus_phonenumber=models.CharField(max_length=16)
    admin_contactus_address= models.TextField()
    admin_contactus_status= models.BooleanField(default=True)
    admin_contactus_created_at= models.DateTimeField(default=datetime.now)


class Gender(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.CASCADE,null=True)
    gender=models.CharField(max_length=100,blank=False, null=False)
    gender_status=models.BooleanField(default=True)
    gender_created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.gender

class Nationality(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.CASCADE,null=True)
    nationality=models.CharField(max_length=100, blank=False,null=False)
    nationality_status = models.BooleanField(default=True)
    nationality_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.nationality


class Salutation(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.CASCADE,null=True)
    salutation=models.CharField(max_length=100, blank=False, null=False)
    salutation_status = models.BooleanField(default=True)
    salutation_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.salutation


class Main_category(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.CASCADE,null=True)
    main_category=  models.CharField(max_length=100, blank=False, null=False)
    main_category_image= models.ImageField(upload_to='main_category_images/',blank=True, null=False)
    short_name = models.CharField(max_length=100, blank=True, null=True)
    main_category_status=models.BooleanField(default=True)
    main_category_created_at= models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.main_category


class Sub_category(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.CASCADE,null=True)
    main_category= models.ForeignKey(Main_category,on_delete=models.CASCADE,null=True)
    sub_category=models.CharField(max_length=100, blank=False, null=False)
    sub_category_image= models.ImageField(upload_to='sub_category_images/',blank=True, null=False)
    short_name= models.CharField(max_length=100, blank=True, null=True)
    sub_category_status=models.BooleanField(default=True)
    sub_category_created_at= models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.sub_category


class Brand(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.CASCADE,null=True)
    brand_name= models.CharField(max_length=100, blank=False, null=False)
    brand_logo=models.ImageField(upload_to='brand_images/',blank=False, null=False)
    brand_status=models.BooleanField(default=True)
    brand_created_at= models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.brand_name

# class CategoryType(models.Model):
#     admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
#     category_type = models.CharField(max_length=100,blank=True,null=True)
#     category_type_image = models.ImageField(upload_to='category_type_images/',blank=True, null=True)
#     category_type_status = models.BooleanField(default=True)
#     category_type_created_at= models.DateTimeField(default=datetime.now)
#
#     def __str__(self):
#         return self.category_type

class ProductMaterial(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL,null=True)
    product_material = models.CharField(max_length=100,blank=True, null=True)
    product_type_status = models.BooleanField(default=True)
    product_type_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.product_material

class ProductSize(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL,null=True)
    product_size_name = models.CharField(max_length=100,blank=True, null=True)
    product_size_short_name = models.CharField(max_length=10,blank=True, null=True)
    product_size_status = models.BooleanField(default=True)
    product_size_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.product_size_short_name

class ProductTag(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL,null=True)
    product_tag_name= models.CharField(max_length=100,blank=True, null=True)
    product_tag_status = models.BooleanField(default=True)
    product_tag_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.product_tag_name


class ProductPaymentType(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL,null=True)
    payment_type = models.CharField(max_length=100,blank=True, null=True)
    payment_status = models.BooleanField(default=True)
    payment_type_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.payment_type

class ProductColor(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL,null=True)
    product_color_name = models.CharField(max_length=100,blank=True, null=True)
    product_color_code = models.CharField(max_length=7,blank=True, null=True)
    product_color_status=models.BooleanField(default=True)
    product_color_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.product_color_name

# Transport type model
class TransportType(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL,null=True)
    transport_type = models.CharField(max_length=100,null=True,blank=True)
    transport_status = models.BooleanField(default=True)
    transport_type_created_at = models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.transport_type

#
#
# class Product(models.Model):
#     admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL,null=True)
#     gender_ref= models.ForeignKey(Gender,on_delete=models.SET_NULL,null=True)
#     main_category_ref = models.ForeignKey(Main_category,on_delete=models.SET_NULL, null=True)
#     sub_category_ref = models.ForeignKey(Sub_category,on_delete=models.SET_NULL,null=True)
#     brand_ref = models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True)
#     material_ref = models.ForeignKey(ProductMaterial,on_delete=models.SET_NULL,null=True)
#     color_ref= models.ForeignKey(ProductColor, on_delete=models.SET_NULL,null=True)
#     size_ref = models.ForeignKey(ProductSize, on_delete=models.SET_NULL,null=True)
#     tags_ref = models.ForeignKey(ProductTag,on_delete=models.SET_NULL,null=True)
#     payment_ref=models.ForeignKey(ProductPaymentType, on_delete=models.SET_NULL,null=True)
#     product_title= models.CharField(max_length=100,blank=True, null=True)
#     product_description= models.TextField(blank=True, null=True)
#     product_mrp = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
#     product_selling_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
#     product_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
#     product_stock_quantity = models.DecimalField(max_digits=20, decimal_places=0,blank=True, null=True)
#     product_status= models.BooleanField(default=True)
#     product_created_at= models.DateTimeField(default=datetime.now)
#     product_updated_at = models.DateTimeField(default=datetime.now)
#
#     def __str__(self):
#         return self.product_title
#
# class ProductImages(models.Model):
#     product_ref =models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
#     color_ref = models.ForeignKey(ProductColor,on_delete=models.SET_NULL, null=True)
#     product_image1 = models.ImageField(upload_to='productimages',blank=True, null=True)
#     product_image2 = models.ImageField(upload_to='productimages',blank=True, null=True)
#     product_image3 = models.ImageField(upload_to='productimages',blank=True, null=True)
#     product_image4 = models.ImageField(upload_to='productimages',blank=True, null=True)
#     product_image5 = models.ImageField(upload_to='productimages',blank=True, null=True)
#     product_image_status = models.BooleanField(default=True)
#     product_image_created_at = models.DateTimeField(default=datetime.now)

class VendorType(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    vendor_type = models.CharField(max_length=100,blank=True, null=True)
    vendor_status = models.BooleanField(default=True)
    vendor_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.vendor_type


#finance models

class BankName(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    bank_name = models.CharField(max_length=100,blank=True,null=True)
    bank_status = models.BooleanField(default=True)
    bank_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.bank_name

class AccountType(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    account_type = models.CharField(max_length=100,blank=True, null=True)
    account_type_status = models.BooleanField(default=True)
    account_type_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.account_type



class Country(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True)
    country_status = models.BooleanField(default=True)
    country_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.country_name

class State(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    country_ref = models.ForeignKey(Country, on_delete=models.CASCADE)
    state_name = models.CharField(max_length=100, null=True, blank=True)
    state_status = models.BooleanField(default=True)
    state_created_at = models.DateTimeField(default=datetime.now)


    def __str__(self):
        return self.state_name

class City(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    country_ref = models.ForeignKey(Country,on_delete=models.CASCADE)
    state_ref = models.ForeignKey(State,on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100, null=True, blank=True)
    city_status = models.BooleanField(default=True)
    city_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.city_name


class Area(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    country_ref = models.ForeignKey(Country, on_delete=models.CASCADE)
    state_ref = models.ForeignKey(State, on_delete=models.CASCADE)
    city_ref = models.ForeignKey(City,on_delete=models.CASCADE)
    area_name = models.CharField(max_length=100, null=True, blank=True)
    area_status = models.BooleanField(default=True)
    area_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.area_name

class CreateVendor(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    vendor_company_name = models.CharField(max_length=100, blank=True, null=True)
    vendor_company_url = models.URLField(max_length=100,blank=True, null=True)
    vendor_aadhaar = models.CharField(max_length=12, unique=True, blank=True, null=True)
    vendor_tan_number = models.CharField(max_length=20,unique=True, blank=True, null=True)
    vendor_gst_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    vendor_type_ref = models.ForeignKey(VendorType, on_delete=models.SET_NULL, null=True)
    vendor_name = models.CharField(max_length=100, null=True, blank=True)
    vendor_phone_number = models.CharField(max_length=15, null=True, blank=True)
    vendor_alt_number = models.CharField(max_length=15, null=True, blank=True)
    vendor_email = models.EmailField(null=True, blank=True)
    vendor_poc = models.CharField(max_length=100, null=True, blank=True)
    vendor_poc_phone = models.CharField(max_length=15, null=True, blank=True)

    vendor_country_ref = models.ForeignKey(Country,on_delete=models.SET_NULL, null=True)
    vendor_state_ref = models.ForeignKey(State,on_delete=models.SET_NULL, null=True)
    vendor_city_ref = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    vendor_area_ref = models.ForeignKey(Area,on_delete=models.SET_NULL,null=True)
    vendor_address = models.TextField(null=True,blank=True)
    vendor_account_number = models.CharField(max_length=20, null=True, blank=True)
    vendor_ifsc_code = models.CharField(max_length=15, null=True, blank=True)
    vendor_bank_ref = models.ForeignKey(BankName, on_delete=models.SET_NULL, null=True)
    vendor_bank_branch = models.CharField(max_length=100, null=True, blank=True)
    vendor_account_type = models.ForeignKey(AccountType, on_delete=models.SET_NULL, null=True)
    vendor_company_logo = models.ImageField(blank=True, null=True)
    vendor_description = RichTextField()
    vendor_status=models.BooleanField(default=True)
    vendor_created_at= models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.vendor_name


#Product Catelogue models

class ProductCatalogue(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    vendor_ref = models.ForeignKey(CreateVendor, on_delete=models.CASCADE)
    main_category_ref = models.ForeignKey(Main_category, on_delete=models.SET_NULL, null=True)
    sub_category_ref = models.ForeignKey(Sub_category, on_delete=models.SET_NULL, null=True)
    product_brand_ref = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    product_color_ref = models.ForeignKey(ProductColor, on_delete=models.SET_NULL, null=True)
    product_size_ref = models.ManyToManyField(ProductSize)
    product_tag_ref = models.ForeignKey(ProductTag,on_delete=models.SET_NULL, null=True)
    product_material= models.ForeignKey(ProductMaterial,on_delete=models.SET_NULL,null=True)
    # product_stock_quantity = models.DecimalField(max_digits=10,decimal_places=0, null=True, blank=True)
    # product_mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_title = models.CharField(max_length=255,null=True, blank=True)
    # product_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    product_description = RichTextField()
    product_catalogue_status = models.BooleanField(default=False)
    product_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.product_title

class ProductCatalogueImages(models.Model):
    product = models.ForeignKey(ProductCatalogue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='productcatalogue_images', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.product_title}"
#Purchase models
class VendorCredit(models.Model):
    admin_registration_id = models.ForeignKey('Admin_registrations', on_delete=models.SET_NULL, null=True)
    vendor = models.ForeignKey('CreateVendor', on_delete=models.CASCADE, related_name='credits')
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Credit for {self.vendor.vendor_company_name}: {self.credit_amount}"

class Purchase(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    vendor = models.ForeignKey(CreateVendor, on_delete=models.CASCADE)
    purchase_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)
    payment_type = models.ForeignKey(ProductPaymentType, on_delete=models.SET_NULL, null=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    upi_id = models.CharField(max_length=100, null=True, blank=True)
    upi_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    upi_cash_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    upi_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    upi_cash_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    account_type = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)
    netbanking_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    cheque_number = models.CharField(max_length=20, null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     # Update purchase_status based on the related PurchaseInvoice's pending_amount
    #     try:
    #         purchase_invoice = PurchaseInvoice.objects.get(purchase_ref=self)
    #         self.purchase_status = purchase_invoice.pending_amount == 0.00
    #     except PurchaseInvoice.DoesNotExist:
    #         # If no PurchaseInvoice exists, default to False (or handle as needed)
    #         self.purchase_status = False
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchase {self.id} - {self.vendor.vendor_name}"

class PurchaseInvoice(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    invoice_id = models.CharField(max_length=30, unique=True, editable=False)
    purchase_ref = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    vendor = models.ForeignKey(CreateVendor, on_delete=models.CASCADE)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def generate_invoice_id(self):
        # Get current date in YYYYMMDD format
        date_str = timezone.now().strftime('%Y%m%d')
        # Generate a 4-character random string (alphanumeric)
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        # Combine prefix, date, and random string
        invoice_id = f'INV-{date_str}-{random_str}'
        # Ensure uniqueness
        while PurchaseInvoice.objects.filter(invoice_id=invoice_id).exists():
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            invoice_id = f'INV-{date_str}-{random_str}'
        return invoice_id

    def save(self, *args, **kwargs):
        # Generate invoice_id only if it's a new instance (not updating an existing one)
        if not self.invoice_id:
            self.invoice_id = self.generate_invoice_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_id

class PurchaseItem(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.SET_NULL, null=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductCatalogue, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    remaining_quantity=models.PositiveIntegerField()
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    cgst = models.DecimalField(max_digits=5, decimal_places=2)
    sgst = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount=models.DecimalField(max_digits=10, decimal_places=2)
    total_amount_with_gst=models.DecimalField(max_digits=10,decimal_places=2)
    purchase_item_status=models.BooleanField(default=True)
    purchase_item_created_at=models.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        # If this is a new instance (not yet saved to the database)
        if not self.pk:
            # Set remaining_quantity to quantity if not explicitly provided
            if self.remaining_quantity is None:
                self.remaining_quantity = self.quantity
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.product.product_title} - {self.quantity}"

class PurchasePayments(models.Model):
    invoice_ref = models.ForeignKey(PurchaseInvoice,on_delete=models.SET_NULL,null=True)
    purchase_ref = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    vendor = models.ForeignKey(CreateVendor, on_delete=models.CASCADE)
    payment_type = models.ForeignKey(ProductPaymentType, on_delete=models.SET_NULL, null=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    upi_id = models.CharField(max_length=100, null=True, blank=True)
    upi_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    upi_cash_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    upi_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    upi_cash_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    account_type = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)
    netbanking_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    cheque_number = models.CharField(max_length=20, null=True, blank=True)
    purchase_payment_status= models.BooleanField(default=True)
    purchase_created_at = models.DateTimeField(default=datetime.now)



class Upi(models.Model):
    admin_registration_id = models.ForeignKey('Admin_registrations', on_delete=models.SET_NULL, null=True)
    upi_accountant = models.CharField(max_length=100, null=True, blank=True)
    upi_name = models.CharField(max_length=100, null=True, blank=True)
    upi_id = models.CharField(max_length=100, null=True, blank=True)
    upi_phonenumber = models.CharField(max_length=15, null=True, blank=True)
    upi_qr_image = models.ImageField(upload_to='upi_qr_images', null=True, blank=True)
    upi_status = models.BooleanField(default=True)
    upi_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.upi_name} ({self.upi_id})"

class AccountDetail(models.Model):
    admin_registration_id = models.ForeignKey('Admin_registrations', on_delete=models.SET_NULL, null=True)
    account_type_id = models.ForeignKey(AccountType, on_delete=models.CASCADE, null=True)
    bank_name_id = models.ForeignKey(BankName, on_delete=models.CASCADE)
    bank_branch = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    ifsc_code = models.CharField(max_length=11, null=True)
    bank_holder = models.CharField(max_length=100, null=True, blank=True)
    account_status = models.BooleanField(default=True)
    account_detail_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.bank_holder} ({self.account_number})"


#inventory modals

class InventoryItem(models.Model):
    admin_registration_id = models.ForeignKey('Admin_registrations', on_delete=models.SET_NULL, null=True)
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductCatalogue, on_delete=models.CASCADE)
    allocated_quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product.product_title} - {self.allocated_quantity}"


# ========================================= USER MODULES ============================================

# User Registration
class UserRegistration(models.Model):

    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(max_length=64, blank=True, null=True)
    password = models.CharField(max_length= 128, null=False, blank=False)
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    confirm_password = models.CharField(max_length= 128, null=False, blank=False)
    otp = models.CharField(max_length=8, null=True, blank=True)
    status = models.BooleanField(default=False)
    onetime_profile_setup = models.BooleanField(default=False)
    crated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# User One time Profile Setup
class UserProfileSetup(models.Model):

    user = models.ForeignKey('UserRegistration', on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='user/userProfilePicture', null=True, blank=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=16, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    address = models.TextField(max_length=128, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    user = models.ForeignKey('UserRegistration', on_delete= models.CASCADE, null=True)
    coupon_name = models.CharField(max_length=32, null=True, blank=True)
    coupon_code = models.CharField(max_length=16, null=True, blank=True)
    minimum_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coupon_discount_percent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.coupon_code}   -   {self.user}"


class Cart(models.Model):
    user = models.ForeignKey('UserRegistration', on_delete=models.CASCADE, null=True)
    purchaseItem = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(ProductCatalogue, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Undiscounted unit price
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Discounted total
    gst = models.FloatField(default=18.0, null=True, blank=True)
    # To store the selected Size
    selected_size = models.CharField(max_length=20, null=True, blank=True)
    # To store color (for future purpose if needed)
    # selected_colors = models.CharField(max_length=20, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.product.product_title

class OrderCounter(models.Model):
    date_code = models.CharField(max_length=8, unique=True)
    count = models.IntegerField(default=1)
    

class Order(models.Model):
    order_status_choices = [
        ('new', 'New'),
        ('accept','Accept'),
        ('reject','Cancel'),
        ('pending', 'Pending'),
    ]
    # admin_registration_id = models.ForeignKey('Admin_registrations', on_delete=models.SET_NULL, null=True)
    # user = models.ForeignKey(UserRegistration, on_delete= models.CASCADE, null=True)
    user = models.ForeignKey('UserRegistration', on_delete=models.CASCADE, null=True)
    order_reg_id = models.CharField(max_length=16, null=True, blank=True, unique=True)
    order_items = models.TextField(max_length=128, null=True)
    order_price = models.TextField(max_length=128, null=True)
    quantity_mul_price = models.TextField(max_length=128, null=True)
    order_quantity = models.TextField(max_length=128, null=True)
    order_subtotal = models.TextField(max_length=128, null=True)
    order_discount = models.TextField(max_length=128, null=True)
    order_discount_percent = models.TextField(null=True)
    coupon_code = models.CharField(max_length=16, null=True, blank=True)
    coupon_discount_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grandtotal = models.CharField(max_length=10, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    address = models.TextField(null=True)
    status = models.BooleanField(default=True)
    order_status =models.CharField(max_length=10,choices=order_status_choices, default='new')
    rejection_reason = models.TextField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.order_reg_id}"


class OrderItems(models.Model):
    order_item_status_choices = [
        ('new', 'New'),
        ('accept', 'Accept'),
        ('reject', 'Cancel'),
        ('pending', 'Pending'),
    ]
    admin_registration = models.ForeignKey('Admin_registrations', on_delete=models.SET_NULL, null=True, blank=True)

    order_item_reg_id = models.CharField(max_length=16, null=True, blank=True, unique=True)
    order_ref = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=128)
    # inventory_item = models.ForeignKey(InventoryItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_mul_price = models.TextField(max_length=128, null=True)
    status = models.BooleanField(default=True)
    order_item_status = models.CharField(max_length=10, choices=order_item_status_choices, default='new')
    rejection_reason = models.TextField(max_length=200, null=True, blank=True)
    order_item_created_at = models.DateTimeField(default=datetime.now)

    def generate_order_item_id(self):
        order_item_date = self.order_item_created_at or timezone.now()

        day= order_item_date.strftime('%d')
        month= order_item_date.strftime('%m')
        year= order_item_date.strftime('%y')

        date_start = order_item_date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = order_item_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        count= OrderItems.objects.filter(order_item_created_at__range=(date_start,date_end)).count()+1

        if count< 10:
            count_string = '0'+str(count)

        else:
            count_string = str(count)

        result = 'ORD-ITEM'+ str(day) + str(month) + str(year) + count_string

        return result
    def save(self, *args, **kwargs):
        if not self.order_item_reg_id:
            self.order_item_reg_id = self.generate_order_item_id()

            while OrderItems.objects.filter(order_item_reg_id= self.order_item_reg_id).exists():
                self.order_item_reg_id = self.generate_order_item_id()
        # if self.inventory_item:
        #     self.admin_registration_id = self.inventory_item.admin_registration_id


        super().save(*args,**kwargs)


    def __str__(self):
        return f"{self.order_ref.order_reg_id} - {self.product_name}"




# Packing model starts here

class PackingStatus(models.Model):
    packing_status_choice = [
        ('packed','Packed'),
        ('yet_to_pack','Yet To Pack')
    ]

    admin_registration_id = models.ForeignKey('Admin_registrations', on_delete=models.SET_NULL, null=True)
    order_ref = models.ForeignKey(OrderItems,on_delete=models.SET_NULL,null=True)
    packing_status = models.CharField(max_length=15,choices=packing_status_choice, default='yet_to_pack')
    packing_created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.packing_status


#Packing ends here


class Banner(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    banner_picture = models.ImageField(upload_to='AdvertisementBanner', null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateField(default=datetime.now)

    def __self__(self):
        return f"{self.title}" or f"{self.id}"

class Services(models.Model):
    admin_registration_id = models.ForeignKey(Admin_registrations, on_delete=models.CASCADE, null=True)
    service_title =models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='services', null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateField(default=datetime.now)
    def __str__(self):
        return self.service_title


class TransportDetails(models.Model):
    # STATUS_CHOICES = [
    #     ('Scheduled', 'Scheduled'),
    #     ('In Transit', 'In Transit'),
    #     ('Delivered', 'Delivered'),
    # ]

    order_ref = models.ForeignKey(OrderItems, on_delete=models.CASCADE, related_name='transport_details')
    transport_type = models.ForeignKey(TransportType, on_delete=models.CASCADE)
    delivery_date = models.DateField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transport for {self.order_ref.order_item_reg_id} - {self.delivery_date}"


