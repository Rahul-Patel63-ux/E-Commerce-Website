from django.contrib import admin
from .models import *
# Register your models here.


class AdminRegistrations(admin.ModelAdmin):
    list_display = ('id', 'admin_email')
    list_display_links = ('id', 'admin_email')

class AdminContacts(admin.ModelAdmin):
    list_display = ('id', 'admin_contactus_email')
    list_display_links = ('id', 'admin_contactus_email')

admin.site.register(Admin_registrations,AdminRegistrations)
admin.site.register(AdminContactUs,AdminContacts)
admin.site.register(Admin_Onetime_Profile)
admin.site.register(Gender)
admin.site.register(Nationality)
admin.site.register(Salutation)
admin.site.register(Main_category)
admin.site.register(Sub_category)
admin.site.register(Brand)
# admin.site.register(Product)
admin.site.register(ProductCatalogue)
admin.site.register(ProductCatalogueImages)
admin.site.register(Purchase)
admin.site.register(PurchaseItem)
admin.site.register(PurchasePayments)
admin.site.register(PurchaseInvoice)
admin.site.register(VendorCredit)

# admin.site.register(ProductImages)
# admin.site.register(CategoryType)
admin.site.register(ProductMaterial)
admin.site.register(ProductSize)
admin.site.register(ProductTag)
admin.site.register(ProductPaymentType)
admin.site.register(ProductColor)


admin.site.register(VendorType)
admin.site.register(BankName)
admin.site.register(AccountType)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Area)
admin.site.register(CreateVendor)

#inventory
admin.site.register(InventoryItem)


admin.site.register(TransportType)
admin.site.register(PackingStatus)
admin.site.register(TransportDetails)




# ======== USER MODELS =========================

admin.site.register(Cart)
admin.site.register(Coupon)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(UserRegistration)
admin.site.register(UserProfileSetup)
admin.site.register(Banner)




