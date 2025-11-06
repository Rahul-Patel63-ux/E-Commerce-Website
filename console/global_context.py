from  .models import Admin_Onetime_Profile
def global_context(request):
    admin_regno = request.session.get('master_id')
    print(admin_regno)
    context={
        'admin': Admin_Onetime_Profile.objects.filter(admin_registration_id=admin_regno).first()
    }
    print(context)
    return context