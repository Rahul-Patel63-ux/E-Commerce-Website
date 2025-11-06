

from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.db.models import Sum
from decimal import Decimal

from datetime import datetime, timedelta
from django.utils import timezone



import random

from functools import wraps

from .models import *

from django.views.decorators.cache import never_cache

# from cryptography.fernet import Fernet
from django.http import HttpResponse, JsonResponse

from django.template.loader import render_to_string
from weasyprint import HTML
import os

# master login decorator
def master_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        master_id = request.session.get('master_id')

        if not master_id:
            return redirect('sign-in')

        admin = Admin_registrations.objects.filter(id = master_id).first()
        if not admin:
            del request.session['master_id']
            messages.error(request, "You are not an authorized Admin User!",extra_tags='danger')
            return redirect('sign-in')

        return view_func(request, *args, **kwargs)

    return wrapper



#Registration of the console(admin panel)

def send_email(email, subject, message):
    from_email = "rp797968@gmail.com"
    recipient_list = [f"{email}"]
    send_mail(subject, message, from_email, recipient_list)
def signUp(request):

    if request.method =='POST':
        admin_email = request.POST.get('useremail')
        admin_username = request.POST.get('username')
        admin_password = request.POST.get('password_input')
        admin_confirm_password = request.POST.get('confirm_password_input')
        if admin_password == admin_confirm_password:
            if Admin_registrations.objects.filter(admin_email=admin_email).exists():
                messages.error(request, "Email already exists, Try again!",extra_tags='danger')
                return redirect('signUp')
            else:
                if Admin_registrations.objects.filter(admin_username=admin_username).exists():
                    messages.error(request, " Username already exists, Try again!",extra_tags='danger')
                    return redirect('signUp')
                else:
                    otp = random.randint(1111, 9999)
                    subject = "Ecommerce Store Registration OTP"
                    message = f"This is your OTP: {otp}"
                    send_email(admin_email, subject, message)
                    user_instance=Admin_registrations.objects.create(
                        admin_email=admin_email,
                        admin_username=admin_username,
                        admin_password=admin_password,
                        admin_confirm_password=admin_confirm_password,
                        otp = otp,
                    )
                    # user_instance.save()

                    return redirect('otpPage',user_instance.id)
        else:
            messages.error(request,"Unable to Create an Account" , extra_tags='danger')
            return redirect('signUp')
    else:

        return render(request, 'authentication/sign_up.html')


def otpPage(request,user_id):
    admin_user= get_object_or_404(Admin_registrations,id=user_id)
    if request.method=='POST':
        user_otp = request.POST.get('otp')
        if admin_user.otp==user_otp:
            admin_user.admin_registration_status=True
            admin_user.save()
            messages.error(request, "Sign Up successfully.",extra_tags='success')
            return redirect('sign-in')

        messages.error(request, "Please enter valid OTP",extra_tags='danger')
        return redirect('otpPage', admin_user.id)
    return render(request,'authentication/admin_email_verification_otp.html',{'user_id': admin_user})


# login page
def sign_in(request):
    
    if request.method == "POST":
        admin_email = request.POST.get('emailInput')
        password = request.POST.get('password')
        
        try:
            admin = Admin_registrations.objects.get(admin_email=admin_email)

            if admin:
                if admin.admin_password == password:
                    request.session['master_id'] = admin.id
                    messages.success(request, 'Signin Successfully!',extra_tags='success')
                    if admin.admin_oneTime_profile_status:
                        return redirect('console_dashboard')
                    else:
                        return redirect('oneTimeProfile')

                else:
                    messages.error(request, 'Incorrect password',extra_tags='danger')
            else:
                 messages.error(request, "User not found!",extra_tags='danger')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}",extra_tags='danger')
            return redirect('sign-in')

    return render(request, 'authentication/sign_in.html')

def forgotPassword(request):
    try:
        if request.method == 'POST':
            forgot_password_email = request.POST.get('forgot_password_email')
            admin_exists = Admin_registrations.objects.filter(admin_email=forgot_password_email).first()
            print(admin_exists,'admin')
            if admin_exists:

                subject="Ecommerce store credentials"
                message=f"""
                Your Credentials are below: 
                
                Username: {admin_exists.admin_username} 
                Password: {admin_exists.admin_password}
                """
                send_email(forgot_password_email,subject, message)
                messages.error(request,'Your credentials are sent !',extra_tags='success')
                return redirect('sign-in')
            else:
                messages.error(request,'Please provide registered email.',extra_tags='danger')

    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('forgotPassword')
    return render(request,'authentication/admin_signin_forget_password.html')


def oneTimeProfile(request):
    try:
        admin_regid = request.session.get('master_id')
        admin_details = get_object_or_404(Admin_registrations,id=admin_regid)
        if request.method == 'POST':
            admin_name = request.POST.get('ecom_name')
            admin_phone = request.POST.get('ecom_phone_number')
            admin_gender = request.POST.get('ecom_gender')
            admin_dob= request.POST.get('ecom_dob')
            admin_aadhar = request.POST.get('ecom_aadhaar')
            admin_company_name = request.POST.get('company_name')
            admin_company_regno = request.POST.get('company_regno')
            admin_company_logo = request.FILES.get('company_logo')
            admin_company_banner = request.FILES.get('company_banner')
            admin_company_icon = request.FILES.get('company_icon')
            admin_company_about = request.POST.get('admin_company_about')
            admin_company_summary = request.POST.get('admin_company_summary')
            if Admin_Onetime_Profile.objects.filter(admin_phone=admin_phone).exists():
                messages.error(request, 'Phone number already exists.', extra_tags='danger')
            elif Admin_Onetime_Profile.objects.filter(admin_aadhar=admin_aadhar).exists():
                messages.error(request, 'Aadhar already exists.', extra_tags='danger')
            else:
                Admin_Onetime_Profile.objects.create(
                    admin_registration_id_id=admin_regid,
                    admin_name=admin_name,
                    admin_phone=admin_phone,
                    admin_gender=admin_gender,
                    admin_dob=admin_dob,
                    admin_aadhar=admin_aadhar,
                    admin_company_name=admin_company_name,
                    admin_company_regno=admin_company_regno,
                    admin_company_logo=admin_company_logo,
                    admin_company_banner=admin_company_banner,
                    admin_company_icon=admin_company_icon,
                    admin_company_about=admin_company_about,
                    admin_company_summary=admin_company_summary,
                )
                admin_details.admin_oneTime_profile_status= not admin_details.admin_oneTime_profile_status
                admin_details.save()
                messages.error(request, "Admin One Time Profile created successfully.", extra_tags='success')
            return redirect('console_dashboard')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('oneTimeProfile')
    return render(request,'Admin_onetime_profile/one_time_profile_setup.html')

#Profile views starts here
@master_login_required
def showProfile(request):
    admin_regid = request.session.get('master_id')
    profile_details = get_object_or_404(Admin_Onetime_Profile,admin_registration_id_id=admin_regid)
    email = get_object_or_404(Admin_registrations,id=admin_regid)
    context = {
        'profile': profile_details,
        'email': email
    }
    return render(request,'Profile_page/profile.html',context)

@master_login_required
def edit_profile(request):
    # Fetch the existing profile for the logged-in user
    admin_regid = request.session.get('master_id')
    profile = get_object_or_404(Admin_Onetime_Profile, admin_registration_id=admin_regid)

    if request.method == 'POST':
        # Get form data
        admin_name = request.POST.get('ecom_name')
        admin_phone = request.POST.get('ecom_phone_number')
        admin_gender = request.POST.get('ecom_gender')
        admin_dob = request.POST.get('ecom_dob')
        admin_company_about = request.POST.get('admin_company_about')
        admin_company_summary = request.POST.get('admin_company_summary')

        # Update profile fields
        profile.admin_name = admin_name
        profile.admin_phone = admin_phone
        profile.admin_gender = admin_gender
        profile.admin_dob = admin_dob
        profile.admin_company_about = admin_company_about
        profile.admin_company_summary = admin_company_summary

        # Handle file uploads
        if 'company_logo' in request.FILES:
            profile.admin_company_logo = request.FILES['company_logo']
        if 'company_banner' in request.FILES:
            profile.admin_company_banner = request.FILES['company_banner']
        if 'company_icon' in request.FILES:
            profile.admin_company_icon = request.FILES['company_icon']

        try:
            profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('showProfile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')

    # If GET request or form submission fails, render the profile page with the modal open
    return render(request, 'Profile_page/profile.html', {'profile': profile})

# dashboard of the console (admin panel)


@never_cache
@master_login_required
def consoleDashboard(request):
    if request.session.get('master_id'):
        return render(request,'console_dashboard/dashboard.html')
    else:
        return redirect('sign-in')

# view for E-commerce General Settings
@master_login_required
def consoleGeneralSettings(request):
    return render(request, 'general_settings/console_general_settings.html')

# Sign-out here
@master_login_required
def sign_out(request):
    del request.session['master_id']
    return redirect('sign-in')



#gender

@master_login_required
def gender_data_list(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == "POST":
            new_gender = request.POST.get('gender')
            if Gender.objects.filter(gender=new_gender).exists():
                messages.error(request, "Gender already exists.", extra_tags='danger')
                
            else:
                Gender.objects.create(
                    admin_registration_id_id= admin_regid,
                    gender=new_gender
                )
                messages.error(request, "Gender created successfully", extra_tags='success')

            return redirect('gender-data-list')
    except Exception as e:
        messages.error(request, f"an Error Occured {str(e)}", extra_tags='danger')
        return redirect('gender-data-list')

    return render(request, 'general_settings/gender/genderDataList.html')


@master_login_required
def gender_data_table(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            editid = request.GET.get('editid')            

            if editid:
                gender = Gender.objects.get(id=editid)
                context = {
                    'i': gender
                }
                
                return render(request, 'general_settings/gender/gender_editform.html', context)

            query = request.GET.get('query')
            query_in = Q()
            if query:
                query_in &= Q(
                    Q(gender__icontains=query)
                )
            gender_record = Gender.objects.filter(query_in).order_by('-id')
            print(gender_record)
            paginator = Paginator(gender_record, 10)
            page_number = request.GET.get('page', )
            page_obj = paginator.get_page(page_number)
            context = {
                'gender_records': page_obj
            }
            return render(request, 'general_settings/gender/gender_list_itter.html', context)

    except Exception as e:
        print(e)
        messages.error(request, f"an Error Occured {str(e)}", extra_tags='danger')
        return redirect('gender-data-list')


@master_login_required
def update_gender(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        gender = Gender.objects.get(id=pk)
        if request.method == "POST":
            new_gender = request.POST.get('upgender')
            if Gender.objects.exclude(id=pk).filter(gender=new_gender).exists():
                messages.error(request, 'Gender alreay exists.', extra_tags='danger')
            else:
                gender.admin_registration_id_id = admin_regid
                gender.gender = new_gender
                gender.save()
                messages.error(request, "Gender updated successfully", extra_tags='success')
            return redirect('gender-data-list')
    except Exception as e:
        messages.error(request, f"an Error Occured {str(e)}", extra_tags='danger')
        return redirect('gender-data-list')


@master_login_required
def delete_gender(request):
    try:
        admin_regid = request.session.get('master_id')
        gender_id = request.GET.get('delid')
        gender_delete = Gender.objects.get(id=gender_id)
        gender_delete.delete()
        messages.error(request, "Gender deleted successfully", extra_tags='success')

        return redirect('gender-data-list')
    except Exception as e:
        messages.error(request, f"an Error Occured {str(e)}", extra_tags='danger')
        return redirect('gender-data-list')


@master_login_required
def gender_status_change(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        gender_details = Gender.objects.get(id=pk)

        if request.headers.get("HX-Request"):
            gender_details.gender_status = not gender_details.gender_status
            gender_details.save()

            context = {
                "gender": gender_details,
                "page_name": 'gender'
            }

            return render(request, "general_settings/status_partial/gender_status_partial.html", context)

    except Exception as e:
        messages.error(request, f"an Error Occured {str(e)}", extra_tags='danger')
        return redirect('gender-data-list')

@master_login_required
def consoleMainCategory(request):
    try:
        admin_regid = request.session.get('master_id')

        if request.method =='POST':
            main_category = request.POST.get('category')
            short_name= request.POST.get('short_name')
            main_category_image=request.FILES.get('main_category_image')


            if Main_category.objects.filter(admin_registration_id=admin_regid,main_category=main_category).exists():
                messages.error(request,'Main Category already exists.',extra_tags='danger')
            else:
                Main_category.objects.create(
                    admin_registration_id_id=admin_regid,
                    main_category=main_category,
                    short_name=short_name,
                    main_category_image=main_category_image
                )
                messages.error(request, 'Main Category created successfully.',extra_tags='success')
            return redirect('consoleMainCategory')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request,f"An error occured {str(e)}",extra_tags='danger')
        return redirect('consoleMainCategory')

    return render(request, 'general_settings/main_category/main_category.html')

@master_login_required
def consoleRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        print(admin_regid)
        if request.headers.get('HX-Request'):
            edit_id=request.GET.get('editid')
            if edit_id:
                category= Main_category.objects.get(id=edit_id)
                context={
                    'i': category
                }
                return render(request, 'general_settings/main_category/mainCategoryComponents/mainCategoryEditForm.html', context)

            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &=Q(
                    Q(admin_registration_id__icontains=admin_regid) &
                    Q(main_category__icontains= query)
                )
            category_records=Main_category.objects.filter(query_name).order_by('-id')
            page_number= request.GET.get('page')
            paginator = Paginator(category_records,10)
            page_obj= paginator.get_page(page_number)
            context={
                'category_records': page_obj
            }
            return render(request,'general_settings/main_category/mainCategoryComponents/mainCategoryListData.html', context)

    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}',extra_tags='danger')
        return redirect('consoleMainCategory')

@master_login_required
def categoryStatusChange(request, pk):
    try:
        category_details= get_object_or_404(Main_category,id=pk)
        if request.headers.get('HX-Request'):
            category_details.main_category_status= not category_details.main_category_status
            category_details.save()

            return render(request, "general_settings/main_category/mainCategoryComponents/mainCategoryStatusChange.html", {"category":category_details, "status_page" : "category_page"})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('consoleRenderData')

@master_login_required
def deleteCategory(request, pk):
    try:
        category_delete= get_object_or_404(Main_category,id=pk)
        category_delete.delete()
        messages.error(request,"Main Category deleted successfully.",extra_tags="success")

        return redirect('consoleMainCategory')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('consoleMainCategory')

@master_login_required
def updateCategory(request,pk):
    try:
        category=get_object_or_404(Main_category, id=pk)
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            main_category = request.POST.get('ucategory')
            short_name = request.POST.get('ushort_name')


            if Main_category.objects.exclude(id=pk).filter(main_category=main_category).exists():
                messages.error(request,'Main Category already exists.', extra_tags='danger')

            else:
                category.admin_registration_id_id = admin_regid
                category.main_category= request.POST.get('ucategory')
                category.short_name= request.POST.get('ushort_name')
                if request.FILES.get('umain_category_image'):
                    category.main_category_image = request.FILES.get('umain_category_image')
                else:
                    category.main_category_image = category.main_category_image
                category.save()
                messages.error(request, "Main Category updated successfully.", extra_tags='success')
            return redirect('consoleMainCategory')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an error occured {str(e)}", extra_tags='danger')
        return redirect('consoleMainCategory')



#Main category ends here


#sub Category starts here

@master_login_required
def consoleSubCategory(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            main_category_id =request.POST.get('category')
            sub_category = request.POST.get('subcategory')
            short_name = request.POST.get('short_name')
            sub_category_image=request.FILES.get('sub_category_image')
            main_category= Main_category.objects.get(id=main_category_id, main_category_status=True)
            if Sub_category.objects.filter(admin_registration_id=admin_regid,main_category=main_category, sub_category=sub_category).exists():
                print('Sub category already exists.')
                messages.error(request,'Sub category already exists.', extra_tags='danger')

            else:
                Sub_category.objects.create(
                    admin_registration_id_id=admin_regid,
                    main_category=main_category,
                    sub_category=sub_category,
                    short_name=short_name,
                    sub_category_image=sub_category_image,
                )
                messages.error(request, 'Sub Category created successfully.',extra_tags='success')
            return redirect('consoleSubCategory')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"en error occured {str(e)}", extra_tags='danger')
        return redirect('consoleSubCategory')
    context={
        'main_category' : Main_category.objects.filter(admin_registration_id=admin_regid,main_category_status=True)
    }
    return render(request, 'general_settings/sub_category/subCategory.html',context)

@master_login_required
def subCategoryRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id_variable = request.GET.get('edit_id')
            print(edit_id_variable)
            if edit_id_variable:

                subcategory= Sub_category.objects.get(id=edit_id_variable)
                context={
                    'j':subcategory,
                    'main_category': Main_category.objects.filter(admin_registration_id=admin_regid,main_category_status=True),
                }
                return render(request,'general_settings/sub_category/subcategorycomponents/subcategoryeditform.html',context)
            query = request.GET.get('query')
            query_name= Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name&=Q(
                    Q(sub_category__icontains=query)
                )

            subcategory_records= Sub_category.objects.filter(query_name).order_by('-id')
            page_number=request.GET.get('page')
            paginator = Paginator(subcategory_records,10)
            page_obj= paginator.get_page(page_number)
            context = {
                'subcategory_records': page_obj,
                'main_category': Main_category.objects.filter(admin_registration_id=admin_regid,main_category_status=True),
            }
            return render(request, 'general_settings/sub_category/subcategorycomponents/subcategorylistdata.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('consoleSubCategory')

@master_login_required
def subCategoryStatusChange(request, pk):
    try:
        subcategory_details= get_object_or_404(Sub_category, id=pk)
        if request.headers.get('HX-Request'):
            subcategory_details.sub_category_status= not subcategory_details.sub_category_status
            subcategory_details.save()
            return render(request, 'general_settings/sub_category/subcategorycomponents/subcategorystatuschange.html',{'subcategory':subcategory_details,"status_page":"subcategory_page"})
    except Exception as e:
        print(str(e), " Error")
        messages.error(request, f"An error Occured {str(e)}", extra_tags='danger')
        return redirect('subCategoryRenderData')

@master_login_required
def deleteSubCategory(request,pk):
    try:
        subcategory_details= get_object_or_404(Sub_category, id=pk)
        subcategory_details.delete()
        messages.error(request, 'Sub category deleted successfully', extra_tags='success')
        return redirect('consoleSubCategory')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('consoleSubCategory')

@master_login_required
def updateSubCategory(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        subcategory=get_object_or_404(Sub_category,id=pk)
        if request.method == 'POST':
            main_category_id=request.POST.get('ucategory')
            sub_category = request.POST.get('usubcategory')
            short_name = request.POST.get('ushort_name')
            main_category = get_object_or_404(Main_category, id=main_category_id, main_category_status=True)
            if Sub_category.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,main_category=main_category, sub_category=sub_category).exists():
                print('Sub category already exists.')
                messages.error(request, 'Sub category already exists.', extra_tags='danger')

            else:
                subcategory.admin_registration_id_id=admin_regid
                subcategory.main_category =main_category
                subcategory.sub_category= sub_category
                subcategory.short_name= short_name
                if request.FILES.get('umain_category_image'):
                    subcategory.sub_category_image = request.FILES.get('usub_category_image')
                else:
                    subcategory.sub_category_image = subcategory.sub_category_image

                subcategory.save()
                messages.error(request,'Sub Category updated successfully.', extra_tags='success')

            return redirect('consoleSubCategory')

    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an error occured {str(e)}", extra_tags='danger')
        return redirect('consoleSubCategory')
#sub category ends here

# # Nationality starts here
@master_login_required
def nationality(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            nationality = request.POST.get('nationality')
            if Nationality.objects.filter(admin_registration_id=admin_regid,nationality=nationality).exists():
                messages.error(request, 'Nationality already exists.', extra_tags='danger')
            else:
                Nationality.objects.create(
                    admin_registration_id_id=admin_regid,
                    nationality=nationality
                )
                messages.error(request,"Nationality created successfully.",extra_tags='success')
            return redirect('nationality')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('nationality')

    return render(request, 'general_settings/nationality/nationality.html')

@master_login_required
def nationalityRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id_variable= request.GET.get('editid')
            if edit_id_variable:
                nationality_details=Nationality.objects.get(id=edit_id_variable)
                context={
                    'n': nationality_details,
                }
                return render(request,'general_settings/nationality/nationalitycomponents/nationalitycomponentseditform.html',context)
            query= request.GET.get('query')
            query_name= Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(nationality__icontains= query)
                )
            nationality_records=Nationality.objects.filter(query_name).order_by('-id')
            page_number= request.GET.get('page')
            paginator=Paginator(nationality_records,10)
            page_obj = paginator.get_page(page_number)
            context={
                'nationality_records': page_obj
            }
            return render(request,'general_settings/nationality/nationalitycomponents/nationalitycomponentslistdata.html',context)

    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('nationality')

@master_login_required
def nationalityStatusChange(request, pk):
    try:
        nationality_details= get_object_or_404(Nationality,id=pk)
        if request.headers.get('HX-Request'):
            nationality_details.nationality_status=not nationality_details.nationality_status
            nationality_details.save()
            return render(request,"general_settings/nationality/nationalitycomponents/nationalityComponentStatusChange.html",{"nationality":nationality_details,"status_page": "nationality_page"})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('nationalityRenderData')

@master_login_required
def deleteNationality(request,pk):
    try:
        nationality_delete= get_object_or_404(Nationality,id=pk)
        nationality_delete.delete()
        messages.error(request,"Nationality deleted successfully.", extra_tags="success")
        return redirect('nationality')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('nationality')

@master_login_required
def updateNationality(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        nationality_details= get_object_or_404(Nationality, id=pk)
        if request.method == "POST":
            nationality=request.POST.get('unationality')
            if Nationality.objects.exclude(id=pk).filter(nationality=nationality).exists():
                messages.error(request,'Nationality already exists.', extra_tags='danger')

            else:
                nationality_details.admin_registration_id_id = admin_regid
                nationality_details.nationality=nationality
                nationality_details.save()
                messages.error(request, "Nationality updated successfully.", extra_tags='success')
            return redirect('nationality')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('nationality')

#Nationality ends here

#Contact us starts here
@master_login_required
def generalSettingsContactUs(request):
    try:
        admin_regid=request.session.get('master_id')
        if request.method == 'POST':
            contact_us_email=request.POST.get('contact_us_email')
            contact_us_phone_number = request.POST.get('contact_us_phone_number')
            contact_us_address = request.POST.get('contact_us_address')

            if AdminContactUs.objects.filter(admin_registration_id=admin_regid,admin_contactus_email = contact_us_email).exists():
                messages.error(request,"Email already exists. ", extra_tags='danger')
            elif AdminContactUs.objects.filter(admin_registration_id=admin_regid,admin_contactus_phonenumber=contact_us_phone_number).exists():
                messages.error(request,'Phone number is already exists.',extra_tags='danger')
            else:
                AdminContactUs.objects.create(
                    admin_registration_id_id=admin_regid,
                    admin_contactus_email=contact_us_email,
                    admin_contactus_phonenumber=contact_us_phone_number,
                    admin_contactus_address=contact_us_address,
                )
                messages.error(request, "Contact details created successfully.",extra_tags='success')
            return redirect('generalSettingsContactUs')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request,f"an error occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingsContactUs')
    return render(request, 'general_settings/Contactus/contactus.html')

@master_login_required
def contactUsDataRender(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id= request.GET.get('editid')
            if edit_id:
                contact_details= get_object_or_404(AdminContactUs, id=edit_id)
                context = {
                    'contact': contact_details,
                }
                return render(request,'general_settings/Contactus/contactuscomponents/contactuseditform.html',context)
            query= request.GET.get('query')
            query_name= Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name&=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(admin_contactus_email__icontains=query)
                )
            contact_details=AdminContactUs.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(contact_details, 10)
            page_obj= paginator.get_page(page_number)
            context={
                'contact_us_details': page_obj,
            }
            return render(request,'general_settings/Contactus/contactuscomponents/contactuscomponentlistdata.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}',extra_tags='danger')
        return redirect('generalSettingsContactUs')
@master_login_required
def contactUsStatusChange(request,pk):
    try:
        contact_details=get_object_or_404(AdminContactUs,id=pk)
        if request.headers.get('HX-Request'):
            contact_details.admin_contactus_status= not contact_details.admin_contactus_status
            contact_details.save()
            return render(request,'general_settings/Contactus/contactuscomponents/contactusstatuschange.html',{'contact_us':contact_details,"status_page":"contact_page"})

    except Exception as e:
        print(str(e), " Error")
        messages.error(request, f"An error Occured {str(e)}", extra_tags='danger')
        return redirect('contactUsDataRender')

@master_login_required
def deleteContactUs(request, pk):
    try:
        contact_details= get_object_or_404(AdminContactUs, id=pk)
        contact_details.delete()
        messages.error(request,"Contact Us deleted Successfully.", extra_tags='success')
        return redirect('generalSettingsContactUs')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingsContactUs')

@master_login_required
def updateContactUs(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        contact_details=get_object_or_404(AdminContactUs,id=pk)
        if request.method == "POST":
            contact_email=request.POST.get('ucontact_us_email')
            contact_phonenumber= request.POST.get('ucontact_us_phone_number')
            contact_address = request.POST.get('ucontact_us_address')

            if AdminContactUs.objects.exclude(id=pk).filter(admin_contactus_email=contact_email).exists():
                messages.error(request,'Email already exists.',extra_tags='danger')

            elif AdminContactUs.objects.exclude(id=pk).filter(admin_contactus_phonenumber=contact_phonenumber).exists():
                messages.error(request,'Phone number already exists.',extra_tags='danger')

            else:
                contact_details.admin_registration_id_id=admin_regid
                contact_details.admin_contactus_email=contact_email
                contact_details.admin_contactus_phonenumber=contact_phonenumber
                contact_details.admin_contactus_address=contact_address
                contact_details.save()
                messages.error(request,'Contact Details updates successfully.', extra_tags='success')

            return redirect('generalSettingsContactUs')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingsContactUs')
# Contact us ends here


#Salutation starts here
@master_login_required
def generalSettingsSalutation(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            salutation = request.POST.get('salutation')
            if Salutation.objects.filter(admin_registration_id=admin_regid,salutation=salutation).exists():
                messages.error(request,'Salutation already exists.',extra_tags='danger')

            else:
                Salutation.objects.create(
                    admin_registration_id_id=admin_regid,
                    salutation=salutation,
                )
                messages.error(request,'Salutation created successfully.',extra_tags='success')
            return redirect('generalSettingsSalutation')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingsSalutation')

    return render(request, 'general_settings/salutation/salutation.html')
@master_login_required
def salutationRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id=request.GET.get('editid')
            if edit_id:
                salutation_details = get_object_or_404(Salutation, id=edit_id)
                context= {
                    's': salutation_details,
                }
                return render(request,'general_settings/salutation/salutationcomponents/salutationeditform.html',context)
            query=request.GET.get('query')
            query_name= Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(salutation__icontains=query)
                )

            salutation_records= Salutation.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(salutation_records,10)
            page_obj=paginator.get_page(page_number)
            context= {
                'salutation_records':page_obj,
            }
            return render(request,'general_settings/salutation/salutationcomponents/salutationtablelistdata.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('generalSettingsSalutation')
@master_login_required
def salutationStatusChange(request,pk):
    try:
        salutation_details = get_object_or_404(Salutation, id=pk)
        if request.headers.get('HX-Request'):
            salutation_details.salutation_status = not salutation_details.salutation_status
            salutation_details.save()
            return render(request,'general_settings/salutation/salutationcomponents/salutationstatuschange.html',{"salutation":salutation_details,"status_page":"salutation_page"})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('salutationRenderData')

@master_login_required
def deleteSalutation(request, pk):
    try:
        salutation_delete= get_object_or_404(Salutation, id=pk)
        salutation_delete.delete()
        messages.error(request,'Salutation deleted successfully.',extra_tags='success')
        return redirect('generalSettingsSalutation')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingsSalutation')

@master_login_required
def updateSalutation(request,pk):
    try:
        admin_id = request.session.get('master_id')
        salutation_details = get_object_or_404(Salutation, id=pk)
        if request.method == 'POST':
            salutation = request.POST.get('usalutation')
            if Salutation.objects.exclude(id=pk).filter(salutation=salutation).exists():
                messages.error(request,'Salutation already exists.',extra_tags='success')
            else:
                salutation_details.admin_registration_id_id= admin_id
                salutation_details.salutation=salutation
                salutation_details.save()
                messages.error(request,'Salutation updated successfully.',extra_tags='success')
            return redirect('generalSettingsSalutation')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingsSalutation')

#Salutation ends here

#Brand starts here
@master_login_required
def generalSettingsBrand(request):

    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            brand_name=request.POST.get('brand')
            brand_logo=request.FILES.get('brand_logo')

            if Brand.objects.filter(admin_registration_id=admin_regid,brand_name=brand_name).exists():
                messages.error(request,'Brand already exists.',extra_tags='danger')
            else:
                Brand.objects.create(
                    admin_registration_id_id=admin_regid,
                    brand_name=brand_name,
                    brand_logo=brand_logo,
                )
                messages.error(request, "Brand created successfully.",extra_tags='success')
                return redirect('generalSettingsBrand')

    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request,f"An error occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingsBrand')
    return render(request,'general_settings/brand/brand.html')

@master_login_required
def brandRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                brand=get_object_or_404(Brand, id=edit_id)
                context={
                    'b':brand
                }
                return render(request, "general_settings/brand/brandcomponents/brandcomponentseditform.html",context)
            query= request.GET.get('query')
            query_name=Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &=Q(
                    Q(admin_registration_id__icontains=admin_regid) &
                    Q(brand_name__icontains=query)
                )
            brand_records = Brand.objects.filter(query_name).order_by('-id')
            page_number= request.GET.get('page')
            paginator=Paginator(brand_records,10)
            page_obj = paginator.get_page(page_number)
            context = {
                'brand_records': page_obj,
            }
            return render(request, "general_settings/brand/brandcomponents/brandcomponentslistdata.html",context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}',extra_tags='danger')
        return redirect('generalSettingsBrand')


@master_login_required
def brandStatusChange(request, pk):
    try:
        brand_details = get_object_or_404(Brand, id=pk)
        if request.headers.get('HX-Request'):
            brand_details.brand_status= not brand_details.brand_status
            brand_details.save()

            return render(request,'general_settings/brand/brandcomponents/brandcomponentsstatuschange.html',{"brand":brand_details,'status_page':'brand_page'})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('brandRenderData')

@master_login_required
def deleteBrand(request, pk):
    try:
        brand_delete= get_object_or_404(Brand,id=pk)
        brand_delete.delete()
        messages.error(request,"Brand deleted successfully.",extra_tags='success')
        return redirect('generalSettingsBrand')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingsBrand')

@master_login_required
def updateBrand(request,pk):
    try:
        brand_details = get_object_or_404(Brand,id=pk)
        admin_regid = request.session.get('master_id')
        if request.method == "POST":
            brand_name= request.POST.get('ubrand')
            brand_logo = request.FILES.get('ubrand_logo')

            if Brand.objects.exclude(id=pk).filter(brand_name= brand_name).exists():
                messages.error(request,'Brand already exists.',extra_tags='danger')

            else:
                brand_details.admin_registration_id_id = admin_regid
                brand_details.brand_name = brand_name
                if request.FILES.get('ubrand_logo'):
                    brand_details.brand_logo = request.FILES.get('ubrand_logo')
                else:
                    brand_details.brand_logo =brand_details.brand_logo
                brand_details.save()
                messages.error(request,'Brand updated successfully.',extra_tags='success')
            return redirect('generalSettingsBrand')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingsBrand')

#Brand ends here


#Product material starts here
@master_login_required
def generalSettingsProductMaterial(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            material = request.POST.get('productmaterial')
            if ProductMaterial.objects.filter(admin_registration_id=admin_regid,product_material=material).exists():
                messages.error(request,"Material already exists.",extra_tags='danger')
            else:
                ProductMaterial.objects.create(
                    admin_registration_id_id=admin_regid,
                    product_material=material,
                )
                messages.error(request,"Material created successfully.",extra_tags='success')
            return redirect('generalSettingsProductMaterial')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingsProductMaterial')

    return render(request,'general_settings/productmaterial/productmaterial.html')

@master_login_required
def materialRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                material_detials = ProductMaterial.objects.get(id=edit_id)
                context={
                    'm': material_detials
                }
                return render(request,'general_settings/productmaterial/productmaterialcomponents/productmaterialeditform.html',context)
            query= request.GET.get('query')
            query_name= Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name&=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(product_material__icontains = query)
                )
            material_records=ProductMaterial.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(material_records,10)
            page_obj = paginator.get_page(page_number)
            context = {
                'material_records':page_obj
            }
            return render(request,"general_settings/productmaterial/productmaterialcomponents/productmaterialcomponentslistdata.html",context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('generalSettingsProductMaterial')


@master_login_required
def materialStatusChange(request, pk):
    try:
        material_details = get_object_or_404(ProductMaterial, id=pk)
        if request.headers.get('HX-Request'):
            material_details.product_type_status = not material_details.product_type_status
            material_details.save()
            return render(request,'general_settings/productmaterial/productmaterialcomponents/productmaterialstatuschange.html',{'material':material_details,"status_page":'material_page'})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('materialRenderData')

@master_login_required
def deleteMaterial(request,pk):
    try:
        material_details = get_object_or_404(ProductMaterial, id=pk)
        material_details.delete()
        messages.error(request,"Material deleted successfully",extra_tags='success')
        return redirect('generalSettingsProductMaterial')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingsProductMaterial')


@master_login_required
def updateMaterial(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        material_details = get_object_or_404(ProductMaterial,id=pk)
        if request.method =="POST":
            material = request.POST.get('uproductmaterial')
            if ProductMaterial.objects.exclude(id=pk).filter(product_material=material).exists():
                messages.error(request,'Material already exists.',extra_tags='danger')
            else:
                material_details.admin_registration_id_id = admin_regid
                material_details.product_material=material
                material_details.save()
                messages.error(request,"Material updated successfully." , extra_tags='success')
            return redirect('generalSettingsProductMaterial')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingsProductMaterial')

#Product material ends here


#Product size starts here
@master_login_required
def generalSettingProductSize(request):
    try:
        admin_regid= request.session.get('master_id')
        if request.method == "POST":
            size = request.POST.get('productsize')
            short_name= request.POST.get('productsize_shortname')
            if ProductSize.objects.filter(admin_registration_id=admin_regid,product_size_name=size).exists():
                messages.error(request,'Product size already exists',extra_tags='danger')
            elif ProductSize.objects.filter(admin_registration_id=admin_regid,product_size_short_name=short_name).exists():
                messages.error(request,'Product short name already exists',extra_tags='danger')
            else:
                ProductSize.objects.create(
                    admin_registration_id_id=admin_regid,
                    product_size_name=size,
                    product_size_short_name=short_name,
                )
                messages.error(request,'Product size created successfully.',extra_tags='success')
            return redirect('generalSettingProductSize')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingProductSize')

    return render(request,'general_settings/productsize/productsize.html')

@master_login_required
def sizeRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                size_details = get_object_or_404(ProductSize, id=edit_id)
                context = {
                    'size' : size_details,
                }
                return render(request,'general_settings/productsize/productsizecomponents/productsizecomponentseditform.html',context)
            query = request.GET.get('query')
            query_name= Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name&=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(product_size_name__icontains = query)
                )
            size_records = ProductSize.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator= Paginator(size_records,10)
            page_obj = paginator.get_page(page_number)
            context={
                'size_records': page_obj
            }
            return render(request,'general_settings/productsize/productsizecomponents/productsizecomponentlistdata.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('generalSettingProductSize')

@master_login_required
def sizeStatusChange(request,pk):
    try:
        size_details = get_object_or_404(ProductSize,id=pk)
        if request.headers.get('HX-Request'):
            size_details.product_size_status = not size_details.product_size_status
            size_details.save()
            return render(request,'general_settings/productsize/productsizecomponents/productsizecomponentstatuschange.html',{'size_product':size_details,"status_page":"size_page"})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('sizeRenderData')

@master_login_required
def deleteSize(request,pk):
    try:
        size_details = get_object_or_404(ProductSize,id=pk)
        size_details.delete()
        messages.error(request,"Size deleted successfully.",extra_tags='success')
        return redirect('generalSettingProductSize')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingProductSize')

@master_login_required
def updateSize(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        size_details = get_object_or_404(ProductSize,id=pk)
        if request.method == "POST":
            size_name= request.POST.get('uproductsize')
            size_short_name = request.POST.get('uproductsize_shortname')
            if ProductSize.objects.exclude(id=pk).filter(product_size_name=size_name).exists():
                messages.error(request,'Product Size already exists.',extra_tags='danger')
            elif ProductSize.objects.exclude(id=pk).filter(product_size_short_name=size_short_name).exists():
                messages.error(request,'Short name already exists', extra_tags='danger')
            else:
                size_details.admin_registration_id_id = admin_regid
                size_details.product_size_name = size_name
                size_details.product_size_short_name = size_short_name
                size_details.save()
                messages.error(request,'Product size updated successfully',extra_tags='success')
            return redirect('generalSettingProductSize')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingProductSize')

# Product size ends here

#Product Tag starts here

@master_login_required
def generalSettingsProductTag(request):

    try:
        admin_regid = request.session.get('master_id')
        if request.method =="POST":
            tag = request.POST.get('producttag')

            if ProductTag.objects.filter(admin_registration_id=admin_regid,product_tag_name=tag).exists():
                messages.error(request, 'Tag already exists',extra_tags='danger')
            else:
                ProductTag.objects.create(
                    admin_registration_id_id=admin_regid,
                    product_tag_name=tag,
                )
                messages.error(request,'Product Tag created successfully',extra_tags='success')
            return redirect('generalSettingsProductTag')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingsProductTag')

    return render(request,'general_settings/producttag/producttag.html')

@master_login_required
def tagRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id= request.GET.get('editid')
            if edit_id:
                tag= get_object_or_404(ProductTag,id=edit_id)
                context ={
                    'tag': tag
                }
                return render(request, 'general_settings/producttag/producttagcomponents/producttagcomponentseditform.html',context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name&=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(product_tag_name__icontains=query)
                )
            tag_records= ProductTag.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator= Paginator(tag_records,10)
            page_obj = paginator.get_page(page_number)
            context = {
                'tag_records':page_obj
            }
            return render(request,'general_settings/producttag/producttagcomponents/producttagcomponentslistdata.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('generalSettingsProductTag')

@master_login_required
def tagStatusChange(request,pk):
    try:
        tag_details = get_object_or_404(ProductTag,id=pk)
        if request.headers.get('HX-Request'):
            tag_details.product_tag_status= not tag_details.product_tag_status
            tag_details.save()
            return render(request,'general_settings/producttag/producttagcomponents/producttagcomponentsstatuschange.html',{'tag_status': tag_details,'status_page':'tag_page'})

    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('tagRenderData')


@master_login_required
def deleteTag(request,pk):
    try:
        tag_details = get_object_or_404(ProductTag,id=pk)
        tag_details.delete()
        messages.error(request,"Product Tag deleted successfully", extra_tags='success')
        return redirect('generalSettingsProductTag')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingsProductTag')

@master_login_required
def updateTag(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        tag_details = get_object_or_404(ProductTag, id=pk)
        if request.method == "POST":
            tag = request.POST.get('uproducttag')
            if ProductTag.objects.exclude(id=pk).filter(product_tag_name=tag).exists():
                messages.error(request,"Producrt Tag already exists.",extra_tags='danger')
            else:
                tag_details.admin_registration_id_id = admin_regid
                tag_details.product_tag_name= tag
                tag_details.save()
                messages.error(request,"Product Tag updated successfully.",extra_tags='success')
            return redirect('generalSettingsProductTag')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingsProductTag')
#Product tag ends here


#Product payment type starts here
@master_login_required
def generalSettingProductPaymentType(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == "POST":
            payment_type= request.POST.get('productpaymenttype')
            if ProductPaymentType.objects.filter(admin_registration_id=admin_regid,payment_type=payment_type).exists():
                messages.error(request,"Payment Type already exists",extra_tags='danger')
            else:
                ProductPaymentType.objects.create(
                    admin_registration_id_id=admin_regid,
                    payment_type=payment_type
                )
                messages.error(request,"Payment Type created successfully.",extra_tags='success')
            return redirect('generalSettingProductPaymentType')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingProductPaymentType')
    return render(request,'general_settings/productpaymenttype/productpaymenttype.html')

@master_login_required
def paymentTypeRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id= request.GET.get('editid')
            if edit_id:
                payment_details =get_object_or_404(ProductPaymentType, id=edit_id)
                context ={
                    'payment':payment_details
                }
                return render(request,'general_settings/productpaymenttype/productpaymenttypecomponents/productpaymenttypecomponentseditformhtml.html',context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name&=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(payment_type__icontains=query)
                )

            payment_records = ProductPaymentType.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator =Paginator(payment_records,10)
            page_obj = paginator.get_page(page_number)
            context = {
                'payment_records':page_obj
            }
            return render(request,'general_settings/productpaymenttype/productpaymenttypecomponents/productpaymenttypecomponentslistdata.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('generalSettingProductPaymentType')


@master_login_required
def paymentTypeStatusChange(request,pk):
    try:
        payment_details = get_object_or_404(ProductPaymentType, id=pk)
        if request.headers.get('HX-Request'):
            payment_details.payment_status = not payment_details.payment_status
            payment_details.save()
            return render(request,'general_settings/productpaymenttype/productpaymenttypecomponents/productpaymenttypecomponentsstatuschange.html',{'p':payment_details,'status_page': 'payment_page'})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('paymentTypeRenderData')

@master_login_required
def deletePaymentType(request,pk):
    try:
        payment_delete = get_object_or_404(ProductPaymentType,id=pk)
        payment_delete.delete()
        messages.error(request, "Payment type deleted successfully.",extra_tags='success')
        return redirect('generalSettingProductPaymentType')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingProductPaymentType')

@master_login_required
def updatePaymentType(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        payment_details = get_object_or_404(ProductPaymentType, id=pk)
        if request.method == "POST":
            payment_type = request.POST.get('uproductpaymenttype')
            if ProductPaymentType.objects.exclude(id=pk).filter(payment_type=payment_type).exists():
                messages.error(request,'Payment Type already exists' , extra_tags='danger')

            else:
                payment_details.admin_registration_id_id = admin_regid
                payment_details.payment_type =payment_type
                payment_details.save()
                messages.error(request,"Payment Type updated successfully.",extra_tags='success')
            return redirect('generalSettingProductPaymentType')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingProductPaymentType')

#Product payment type ends here

# Product color starts here
@master_login_required
def generalSettingProductColor(request):
    try:
        admin_regid= request.session.get('master_id')
        if request.method =='POST':
            color_name = request.POST.get('productcolor')
            color_code= request.POST.get('product_color_code')
            if ProductColor.objects.filter(admin_registration_id=admin_regid,product_color_name=color_name).exists():
                messages.error(request,"Color already exists",extra_tags='danger')
            elif ProductColor.objects.filter(admin_registration_id=admin_regid,product_color_code=color_code).exists():
                messages.error(request, "Color already exists", extra_tags='danger')
            else:
                ProductColor.objects.create(
                    admin_registration_id_id=admin_regid,
                    product_color_name=color_name,
                    product_color_code=color_code,
                )
                messages.error(request,'Color created successfully.',extra_tags='success')
            return redirect('generalSettingProductColor')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingProductColor')

    return render(request,'general_settings/productcolor/productcolor.html')

@master_login_required
def colorRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                color_details = get_object_or_404(ProductColor,id=edit_id)
                context={
                    'c':color_details
                }
                return render(request,'general_settings/productcolor/productcolorcomponents/productcolorcomponenteditform.html',context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(product_color_name__icontains=query)
                )
            size_records = ProductColor.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(size_records, 10)
            page_obj = paginator.get_page(page_number)
            context = {
                'color_records': page_obj
            }
            return render(request,'general_settings/productcolor/productcolorcomponents/productcolorcomponentslistdata.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('generalSettingProductColor')

@master_login_required
def colorStatusChange(request,pk):
    try:
        color_details = get_object_or_404(ProductColor,id=pk)
        if request.headers.get('HX-Request'):
            color_details.product_color_status = not color_details.product_color_status
            color_details.save()
            return render(request,'general_settings/productcolor/productcolorcomponents/productcolorcomponentsstatuschange.html',{'color':color_details,'status_page':'color_page'})

    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('colorRenderData')

@master_login_required
def deleteColor(request,pk):
    try:
        color_details = get_object_or_404(ProductColor,id=pk)
        color_details.delete()
        messages.error(request,"Color deleted successfully.",extra_tags='success')
        return redirect('generalSettingProductColor')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('generalSettingProductColor')

@master_login_required
def updateColor(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        color_details = get_object_or_404(ProductColor,id=pk)
        if request.method =='POST':
            color_name = request.POST.get('uproductcolor')
            color_code =request.POST.get('uproduct_color_code')
            if ProductColor.objects.exclude(id=pk).filter(product_color_name=color_name).exists():
                messages.error(request,'Color already exists',extra_tags='danger')
            elif ProductColor.objects.exclude(id=pk).filter(product_color_code=color_code).exists():
                messages.error(request, 'Color already exists', extra_tags='danger')
            else:
                color_details.admin_registration_id_id = admin_regid
                color_details.product_color_name=color_name
                color_details.product_color_code = color_code
                color_details.save()
                messages.error(request,"Color updated successfully",extra_tags='success')
            return redirect('generalSettingProductColor')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('generalSettingProductColor')

#Color ends here



#Product Management
@master_login_required
def consoleProduct(request):
    return render(request,'console_product/console_product.html')
# def consoleProductCreate(request):
#     return render(request,"console_product/console_product_create_form.html")


# def consoleProductCreate(request):
#     # try:
#         admin_regid = request.session.get('master_id')
#         if request.method == 'POST':
#             # Create ProductCatalogue instance
#             product = ProductCatalogue(
#                 admin_registration_id_id=admin_regid,
#                 gender_ref_id=request.POST.get('gender_ref'),
#                 main_category_ref_id=request.POST.get('main_category_ref'),
#                 sub_category_ref_id=request.POST.get('sub_category_ref'),
#                 brand_ref_id=request.POST.get('brand_ref'),
#                 material_ref_id=request.POST.get('material_ref'),
#                 color_ref_id=request.POST.get('color_ref'),
#                 size_ref_id=request.POST.get('size_ref'),
#                 tags_ref_id=request.POST.get('tags_ref'),
#                 payment_ref_id=request.POST.get('payment_ref'),
#                 product_title=request.POST.get('product_title'),
#                 product_description=request.POST.get('product_description'),
#                 product_mrp=request.POST.get('product_mrp'),
#                 product_selling_price=request.POST.get('product_selling_price'),
#                 product_discount_percentage=request.POST.get('product_discount_percentage'),
#                 product_stock_quantity=request.POST.get('product_stock_quantity'),
#                 product_status=request.POST.get('product_status') == 'True',
#                 product_created_at=timezone.now(),
#                 product_updated_at=timezone.now()
#             )
#             product.save()
#
#             # Process multiple image blocks
#             image_color_refs = request.POST.getlist('image_color_ref[]')
#             product_images1 = request.FILES.getlist('product_image1[]')
#             product_images2 = request.FILES.getlist('product_image2[]')
#             product_images3 = request.FILES.getlist('product_image3[]')
#             product_images4 = request.FILES.getlist('product_image4[]')
#             product_images5 = request.FILES.getlist('product_image5[]')
#
#             for i, color_id in enumerate(image_color_refs):
#                 if color_id:  # Only process if color is selected
#                     image_data = {
#                         'product_ref': product,
#                         'color_ref_id': color_id,
#                         'product_image1': product_images1[i] if i < len(product_images1) and product_images1[i] else None,
#                         'product_image2': product_images2[i] if i < len(product_images2) and product_images2[i] else None,
#                         'product_image3': product_images3[i] if i < len(product_images3) and product_images3[i] else None,
#                         'product_image4': product_images4[i] if i < len(product_images4) and product_images4[i] else None,
#                         'product_image5': product_images5[i] if i < len(product_images5) and product_images5[i] else None,
#                     }
#                     ProductImages.objects.create(**image_data)
#
#             return redirect('consoleProduct')
#         context = {
#
#             'genders': Gender.objects.all(),
#             'main_categories': Main_category.objects.all(),
#             'sub_categories': Sub_category.objects.all(),
#             'brands': Brand.objects.all(),
#             'materials': ProductMaterial.objects.all(),
#             'colors': ProductColor.objects.all(),
#             'sizes': ProductSize.objects.all(),
#             'tags': ProductTag.objects.all(),
#             'payment_types': ProductPaymentType.objects.all(),
#         }
#         return render(request, 'console_product/console_product_create_form.html', context)

# def consoleProductCreate(request):
#     try:
#         admin_regid = request.session.get('master_id')
#
#         if request.method == 'POST':
#
#             # Create ProductCatalogue instance
#             product = ProductCatalogue(
#                 admin_registration_id_id=admin_regid,
#                 gender_ref_id=request.POST.get('gender_ref'),
#                 main_category_ref_id=request.POST.get('main_category_ref'),
#                 sub_category_ref_id=request.POST.get('sub_category_ref'),
#                 brand_ref_id=request.POST.get('brand_ref'),
#                 material_ref_id=request.POST.get('material_ref'),
#                 color_ref_id=request.POST.get('color_ref'),
#                 size_ref_id=request.POST.get('size_ref'),
#                 tags_ref_id=request.POST.get('tags_ref'),
#                 payment_ref_id=request.POST.get('payment_ref'),
#                 product_title=request.POST.get('product_title'),
#                 product_description=request.POST.get('product_description'),
#                 product_mrp=request.POST.get('product_mrp'),
#                 product_selling_price=request.POST.get('product_selling_price'),
#                 product_discount_percentage=request.POST.get('product_discount_percentage'),
#                 product_stock_quantity=request.POST.get('product_stock_quantity'),
#                 product_status=True,
#                 product_created_at=timezone.now(),
#                 product_updated_at=timezone.now()
#             )
#             product.save()
#
#             # Process multiple image blocks
#             image_color_refs = request.POST.getlist('image_color_ref[]')
#             product_images1 = request.FILES.getlist('product_image1[]')
#             product_images2 = request.FILES.getlist('product_image2[]')
#             product_images3 = request.FILES.getlist('product_image3[]')
#             product_images4 = request.FILES.getlist('product_image4[]')
#             product_images5 = request.FILES.getlist('product_image5[]')
#
#             if not image_color_refs:
#                 product.delete()  # Rollback product creation
#                 messages.error(request, "At least one image block with a selected color is required.",
#                                extra_tags='danger')
#                 return redirect('consoleProductCreate')
#
#             valid_blocks = False
#             for i, color_id in enumerate(image_color_refs):
#                 if color_id:
#                     # Count non-empty images in the block
#                     images = [
#                         product_images1[i] if i < len(product_images1) and product_images1[i] else None,
#                         product_images2[i] if i < len(product_images2) and product_images2[i] else None,
#                         product_images3[i] if i < len(product_images3) and product_images3[i] else None,
#                         product_images4[i] if i < len(product_images4) and product_images4[i] else None,
#                         product_images5[i] if i < len(product_images5) and product_images5[i] else None
#                     ]
#                     image_count = sum(1 for img in images if img is not None)
#
#                     if image_count < 3:
#                         product.delete()  # Rollback product creation
#                         messages.error(request, f"At least three images are required for color block {i + 1}.",
#                                        extra_tags='danger')
#                         return redirect('consoleProductCreate')
#
#                     image_data = {
#                         'product_ref': product,
#                         'color_ref_id': color_id,
#                         'product_image1': images[0],
#                         'product_image2': images[1],
#                         'product_image3': images[2],
#                         'product_image4': images[3],
#                         'product_image5': images[4],
#                         'product_image_status': True,
#                         'product_image_created_at': timezone.now()
#                     }
#                     ProductImages.objects.create(**image_data)
#                     valid_blocks = True
#
#             if not valid_blocks:
#                 product.delete()  # Rollback product creation
#                 messages.error(request, "At least one valid image block with a color and three images is required.",
#                                extra_tags='danger')
#                 return redirect('consoleProductCreate')
#
#             messages.success(request, "Product created successfully.", extra_tags='success')
#             return redirect('consoleProduct')
#
#         context = {
#             'genders': Gender.objects.filter(gender_status=True),
#             'main_categories': Main_category.objects.filter(main_category_status=True),
#             'sub_categories': Sub_category.objects.filter(sub_category_status=True),
#             'brands': Brand.objects.filter(brand_status=True),
#             'materials': ProductMaterial.objects.filter(product_type_status=True),
#             'colors': ProductColor.objects.filter(product_color_status=True),
#             'sizes': ProductSize.objects.filter(product_size_status=True),
#             'tags': ProductTag.objects.filter(product_tag_status=True),
#             'payment_types': ProductPaymentType.objects.filter(payment_status=True),
#         }
#         return render(request, 'console_product/console_product_create_form.html', context)
#
#     except Exception as e:
#         messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
#         return redirect('consoleProductCreate')

@master_login_required
def consoleProductCreate(request):
#     try:
#         admin_regid = request.session.get('master_id')
#         if request.method == "POST":
#             gender_ref_id = request.POST.get('gender_ref')
#             main_category_ref = request.POST.get('main_category_ref')
#             sub_category_ref = request.POST.get('sub_category_ref')
#             brand_ref= request.POST.get('brand_ref')
#             material_ref = request.POST.get('')
#
        context = {
                    'genders': Gender.objects.filter(gender_status=True),
                    'main_categories': Main_category.objects.filter(main_category_status=True),
                    'sub_categories': Sub_category.objects.filter(sub_category_status=True),
                    'brands': Brand.objects.filter(brand_status=True),
                    'materials': ProductMaterial.objects.filter(product_type_status=True),
                    'colors': ProductColor.objects.filter(product_color_status=True),
                    'sizes': ProductSize.objects.filter(product_size_status=True),
                    'tags': ProductTag.objects.filter(product_tag_status=True),
                    'payment_types': ProductPaymentType.objects.filter(payment_status=True),
                }
#
        return render(request, 'console_product/console_product_create_form.html', context)
#
#     except Exception as e:
#         print(f"error:{str(e)}")
#         messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
#         return redirect('consoleProductCreate')


#vendor management starts here

#vendor type starts here
@master_login_required
def vendorType(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            vendor_type= request.POST.get('vendortype')
            if VendorType.objects.filter(admin_registration_id=admin_regid,vendor_type=vendor_type).exists():
                messages.error(request,'Vendor Type already exists.',extra_tags='danger')
            else:
                VendorType.objects.create(
                    admin_registration_id_id=admin_regid,
                    vendor_type=vendor_type,
                )
                messages.error(request,'Vendor type created successfully.',extra_tags='success')
            return redirect('vendorType')

    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('vendorType')

    return render(request,'general_settings/vendor_management/vendor_type/vendor_type.html')

@master_login_required
def vendorTypeRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id=request.GET.get('editid')
            if edit_id:
                vendor_details = get_object_or_404(VendorType, id=edit_id)
                context ={
                    'v':vendor_details
                }
                return render(request,'general_settings/vendor_management/vendor_type/vendor_type_components/vendor_type_components_update_form.html',context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(vendor_type__icontains = query)
                )
            vendor = VendorType.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(vendor,10)
            page_obj=paginator.get_page(page_number)
            context={
                'vendortype_records': page_obj
            }
            return render(request,'general_settings/vendor_management/vendor_type/vendor_type_components/vendor_type_component_list_data.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('vendorType')

@master_login_required
def vendorStatusChange(request,pk):
    try:
        vendor_details = get_object_or_404(VendorType, id=pk)
        if request.headers.get('HX-Request'):
            vendor_details.vendor_status = not vendor_details.vendor_status
            vendor_details.save()
            return render(request,'general_settings/vendor_management/vendor_type/vendor_type_components/vendortype_status_change.html',{'vendor':vendor_details, 'status_page':'vendor_page'})

    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('vendorTypeRenderData')

@master_login_required
def deleteVendorType(request, pk):
    try:
        vendor_details = get_object_or_404(VendorType,id=pk)
        vendor_details.delete()
        messages.error(request,'Vendor Type deleted successfully', extra_tags='success')
        return redirect('vendorType')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('vendorType')

@master_login_required
def updateVendorType(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        vendor_details = get_object_or_404(VendorType, id=pk)
        if request.method == 'POST':
            vendor = request.POST.get('uvendortype')
            if VendorType.objects.exclude(id=pk).filter(vendor_type=vendor).exists():
                messages.error(request, 'Vendor type already exists.',extra_tags='danger')

            else:
                vendor_details.admin_registration_id_id = admin_regid
                vendor_details.vendor_type=vendor
                vendor_details.save()
                messages.error(request, 'Vendor updated successfully.', extra_tags='success')

            return redirect('vendorType')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('vendorType')


#vendor type ends here

#vendor management ends here

#console Vendor management starts here
@master_login_required
def vendorManagement(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == "POST":
            company_name = request.POST.get('vendor_company_name')
            company_url = request.POST.get('vendor_company_url')
            vendor_aadhaar=request.POST.get('vendor_aadhaar')
            vendor_tan = request.POST.get('vendor_tan_number')
            vendor_gst = request.POST.get('vendor_gst_number')
            vendor_type_id = request.POST.get('vendor_type')
            vendor_name = request.POST.get('vendor_name')
            vendor_phone_number = request.POST.get('vendor_phonenumber')
            vendor_alt_phone_number = request.POST.get('vendor_alt_phonenumber')
            vendor_email = request.POST.get('vendor_email')
            vendor_poc = request.POST.get('vendor_poc_name')
            vendor_poc_phone_number = request.POST.get('vendor_poc_phonenumber')
            vendor_country_id = request.POST.get('vendor_country')
            vendor_state_id = request.POST.get('vendor_state')
            vendor_city_id = request.POST.get('vendor_city')
            vendor_area_id = request.POST.get('vendor_area')
            vendor_address = request.POST.get('vendor_address')
            vendor_acc_number = request.POST.get('vendor_account_number')
            vendor_ifsc_code = request.POST.get('vendor_ifsc_code')
            vendor_bank_name_id = request.POST.get('vendor_bank_name')
            vendor_bank_branch = request.POST.get('vendor_bank_branch')
            vendor_account_type_id = request.POST.get('vendor_bank_acc_type')
            vendor_company_logo= request.FILES.get('vendor_company_logo')
            vendor_description = request.POST.get('vendor_description')


            if CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_company_name=company_name).exists():
                messages.error(request,'Company Name already exists',extra_tags='danger')
            elif CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_company_url=company_url).exists():
                messages.error(request,'Company Url already exists',extra_tags='danger')
            elif CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_aadhaar=vendor_aadhaar).exists():
                messages.error(request, 'Vendor Aadhaar already exists', extra_tags='danger')
            elif CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_tan_number=vendor_tan).exists():
                messages.error(request, 'Vendor TAN already exists', extra_tags='danger')
            elif CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_gst_number=vendor_gst).exists():
                messages.error(request, 'Vendor GST already exists', extra_tags='danger')
            elif CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_phone_number=vendor_phone_number).exists():
                messages.error(request, 'Vendor phone number already exists', extra_tags='danger')
            elif CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_email=vendor_email).exists():
                messages.error(request, 'Vendor email already exists', extra_tags='danger')
            elif CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_poc_phone=vendor_poc_phone_number).exists():
                messages.error(request, 'POC phone number already exists', extra_tags='danger')
            elif CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_account_number=vendor_acc_number).exists():
                messages.error(request, 'Vendor account number already exists', extra_tags='danger')
            else:
                # Fetch reference objects
                vendor_type = get_object_or_404(VendorType, id=vendor_type_id)
                vendor_country = get_object_or_404(Country, id=vendor_country_id)
                vendor_state = get_object_or_404(State, id=vendor_state_id, country_ref=vendor_country)
                vendor_city = get_object_or_404(City, id=vendor_city_id, state_ref=vendor_state)
                vendor_area = get_object_or_404(Area, id=vendor_area_id, city_ref=vendor_city)
                vendor_bank = get_object_or_404(BankName, id=vendor_bank_name_id)
                vendor_account_type = get_object_or_404(AccountType, id=vendor_account_type_id)

                # Create vendor
                vendor = CreateVendor.objects.create(
                    admin_registration_id_id=admin_regid,
                    vendor_company_name=company_name,
                    vendor_company_url=company_url,
                    vendor_aadhaar=vendor_aadhaar,
                    vendor_tan_number=vendor_tan,
                    vendor_gst_number=vendor_gst,
                    vendor_type_ref=vendor_type,
                    vendor_name=vendor_name,
                    vendor_phone_number=vendor_phone_number,
                    vendor_alt_number=vendor_alt_phone_number,
                    vendor_email=vendor_email,
                    vendor_poc=vendor_poc,
                    vendor_poc_phone=vendor_poc_phone_number,
                    vendor_country_ref=vendor_country,
                    vendor_state_ref=vendor_state,
                    vendor_city_ref=vendor_city,
                    vendor_area_ref=vendor_area,
                    vendor_address=vendor_address,
                    vendor_account_number=vendor_acc_number,
                    vendor_ifsc_code=vendor_ifsc_code,
                    vendor_bank_ref=vendor_bank,
                    vendor_bank_branch=vendor_bank_branch,
                    vendor_account_type=vendor_account_type,
                    vendor_company_logo=vendor_company_logo,
                    vendor_description=vendor_description,
                )
                messages.success(request, 'Vendor created successfully.', extra_tags='success')
                return redirect('vendorManagement')


        context = {
            'vendor_types': VendorType.objects.filter(admin_registration_id=admin_regid,vendor_status=True),
            'countries': Country.objects.filter(admin_registration_id=admin_regid,country_status=True),
            'states': State.objects.filter(admin_registration_id=admin_regid,state_status=True),
            'cities': City.objects.filter(admin_registration_id=admin_regid,city_status=True),
            'areas': Area.objects.filter(admin_registration_id=admin_regid,area_status=True),
            'banks': BankName.objects.filter(admin_registration_id=admin_regid,bank_status=True),
            'account_types': AccountType.objects.filter(admin_registration_id=admin_regid,account_type_status=True),
        }
        return render(request, 'console_vendor_management/console_vendor_management.html', context)

    except Exception as e:
        print(f"Error: {str(e)}")
        messages.error(request, "An error occurred while processing your request.", extra_tags='danger')
        return redirect('vendorManagement')

@master_login_required
def vendorDataRender(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id=request.GET.get('editid')
            show_id= request.GET.get('showid')
            if edit_id:
                vendor_details= get_object_or_404(CreateVendor,id=edit_id)
                context ={
                    'v':vendor_details,
                    'vendor_types': VendorType.objects.filter(admin_registration_id=admin_regid,vendor_status=True),
                    'countries': Country.objects.filter(admin_registration_id=admin_regid,country_status=True),
                    'states': State.objects.filter(admin_registration_id=admin_regid,state_status=True),
                    'cities': City.objects.filter(admin_registration_id=admin_regid,city_status=True),
                    'areas': Area.objects.filter(admin_registration_id=admin_regid,area_status=True),
                    'banks': BankName.objects.filter(admin_registration_id=admin_regid,bank_status=True),
                    'account_types': AccountType.objects.filter(admin_registration_id=admin_regid,account_type_status=True),
                }
                return render(request,'console_vendor_management/console_vendor_management_components/console_vendor_management_edit_form.html',context)
            if show_id:
                vendor_details = get_object_or_404(CreateVendor, id=show_id)
                context = {
                    'v': vendor_details,
                }
                return render(request,'console_vendor_management/console_vendor_management_components/console_vendor_management_show_data.html',context)

            query = request.GET.get('query')
            vendor_type = request.GET.get('vendor_type')
            cities= request.GET.get('city')
            created_date = request.GET.get('created_date')
            query_filter =Q(admin_registration_id__id__icontains=admin_regid)
            if vendor_type:
                query_filter &=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(vendor_type_ref__id = vendor_type))

            if cities:
                query_filter &= Q(
                        Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(vendor_city_ref__id=cities))



            if query:
                query_filter &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(vendor_company_name__icontains=query))



            vendor_details = CreateVendor.objects.filter(query_filter).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(vendor_details, 10)
            page_obj = paginator.get_page(page_number)
            context = {
                'vendor_details': page_obj,
                'cities': City.objects.filter(admin_registration_id=admin_regid,city_status=True),
                'vendor_types': VendorType.objects.filter(admin_registration_id=admin_regid,vendor_status=True),
            }
            return render(request,'console_vendor_management/console_vendor_management_components/console_vendor_management_list_data.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}',extra_tags='danger')
        return redirect('vendorManagement')

@master_login_required

def vendorStatusChange(request,pk):
    try:
        vendor_details= get_object_or_404(CreateVendor,id=pk)
        if request.headers.get('HX-Request'):
            vendor_details.vendor_status = not vendor_details.vendor_status
            vendor_details.save()
            return render(request,'console_vendor_management/console_vendor_management_components/console_vendor_management_status_change.html',{"vendor": vendor_details, "status_page": "vendor_page"})
    except Exception as e:
        print(str(e), " Error")
        messages.error(request, f"An error Occured {str(e)}", extra_tags='danger')
        return redirect('vendorManagement')





@master_login_required
def deleteVendor(request,pk):
    try:
        vendor_details = get_object_or_404(CreateVendor,id=pk)
        vendor_details.delete()
        messages.error(request,'Vendor deleted successfully',extra_tags='success')
        return redirect('vendorManagement')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('vendorManagement')

@master_login_required
def updateVender(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        vendor=get_object_or_404(CreateVendor,id=pk)
        if request.method == "POST":
            company_name = request.POST.get('uvendor_company_name')
            company_url = request.POST.get('uvendor_company_url')
            vendor_aadhaar = request.POST.get('uvendor_aadhaar')
            vendor_tan = request.POST.get('uvendor_tan_number')
            vendor_gst = request.POST.get('uvendor_gst_number')
            vendor_type_id = request.POST.get('uvendor_type')
            vendor_name = request.POST.get('uvendor_name')
            vendor_phone_number = request.POST.get('uvendor_phonenumber')
            vendor_alt_phone_number = request.POST.get('uvendor_alt_phonenumber')
            vendor_email = request.POST.get('uvendor_email')
            vendor_poc = request.POST.get('uvendor_poc_name')
            vendor_poc_phone_number = request.POST.get('uvendor_poc_phonenumber')
            vendor_country_id = request.POST.get('uvendor_country')
            vendor_state_id = request.POST.get('uvendor_state')
            vendor_city_id = request.POST.get('uvendor_city')
            vendor_area_id = request.POST.get('uvendor_area')
            vendor_address = request.POST.get('uvendor_address')
            vendor_acc_number = request.POST.get('uvendor_account_number')
            vendor_ifsc_code = request.POST.get('uvendor_ifsc_code')
            vendor_bank_name_id = request.POST.get('uvendor_bank_name')
            vendor_bank_branch = request.POST.get('uvendor_bank_branch')
            vendor_account_type_id = request.POST.get('uvendor_bank_acc_type')
            vendor_company_logo = request.FILES.get('uvendor_company_logo')
            vendor_description = request.POST.get('uvendor_description')

            vendor_type = get_object_or_404(VendorType, id=vendor_type_id)
            vendor_country = get_object_or_404(Country, id=vendor_country_id)
            vendor_state = get_object_or_404(State, id=vendor_state_id, country_ref=vendor_country)
            vendor_city = get_object_or_404(City, id=vendor_city_id, state_ref=vendor_state)
            vendor_area = get_object_or_404(Area, id=vendor_area_id, city_ref=vendor_city)
            vendor_bank = get_object_or_404(BankName, id=vendor_bank_name_id)
            vendor_account_type = get_object_or_404(AccountType, id=vendor_account_type_id)

            if CreateVendor.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,vendor_company_name=company_name).exists():
                messages.error(request, 'Company Name already exists', extra_tags='danger')
            elif CreateVendor.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,vendor_company_url=company_url).exists():
                messages.error(request, 'Company Url already exists', extra_tags='danger')
            elif CreateVendor.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,vendor_aadhaar=vendor_aadhaar).exists():
                messages.error(request, 'Vendor Aadhaar already exists', extra_tags='danger')
            elif CreateVendor.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,vendor_tan_number=vendor_tan).exists():
                messages.error(request, 'Vendor TAN already exists', extra_tags='danger')
            elif CreateVendor.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,vendor_gst_number=vendor_gst).exists():
                messages.error(request, 'Vendor GST already exists', extra_tags='danger')
            elif CreateVendor.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,vendor_phone_number=vendor_phone_number).exists():
                messages.error(request, 'Vendor phone number already exists', extra_tags='danger')
            elif CreateVendor.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,vendor_email=vendor_email).exists():
                messages.error(request, 'Vendor email already exists', extra_tags='danger')
            elif CreateVendor.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,vendor_poc_phone=vendor_poc_phone_number).exists():
                messages.error(request, 'POC phone number already exists', extra_tags='danger')
            elif CreateVendor.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,vendor_account_number=vendor_acc_number).exists():
                messages.error(request, 'Vendor account number already exists', extra_tags='danger')
            else:



                # Update the existing vendor object
                vendor.admin_registration_id_id = admin_regid
                vendor.vendor_company_name = company_name
                vendor.vendor_company_url = company_url
                vendor.vendor_aadhaar = vendor_aadhaar
                vendor.vendor_tan_number = vendor_tan
                vendor.vendor_gst_number = vendor_gst
                vendor.vendor_type_ref = vendor_type
                vendor.vendor_name = vendor_name
                vendor.vendor_phone_number = vendor_phone_number
                vendor.vendor_alt_number = vendor_alt_phone_number
                vendor.vendor_email = vendor_email
                vendor.vendor_poc = vendor_poc
                vendor.vendor_poc_phone = vendor_poc_phone_number
                vendor.vendor_country_ref = vendor_country
                vendor.vendor_state_ref = vendor_state
                vendor.vendor_city_ref = vendor_city
                vendor.vendor_area_ref = vendor_area
                vendor.vendor_address = vendor_address
                vendor.vendor_account_number = vendor_acc_number
                vendor.vendor_ifsc_code = vendor_ifsc_code
                vendor.vendor_bank_ref = vendor_bank
                vendor.vendor_bank_branch = vendor_bank_branch
                vendor.vendor_account_type = vendor_account_type
                if vendor_company_logo:
                    vendor.vendor_company_logo = vendor_company_logo
                vendor.vendor_description = vendor_description
                vendor.save()

                messages.error(request, 'Vendor updated successfully.', extra_tags='success')
            return redirect('vendorManagement')




    except Exception as e:
        print(f"Error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('vendorManagement')

@master_login_required
def get_states(request):
    print('called')
    country_id = request.GET.get('country_id')
    print(country_id, 'country id')
    states = State.objects.filter(country_ref_id=country_id, state_status=True).values('id', 'state_name')
    print(states, 'states')
    return JsonResponse({'states': list(states)})
@master_login_required
def get_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state_ref_id=state_id, city_status=True).values('id', 'city_name')
    return JsonResponse({'cities': list(cities)})
@master_login_required
def get_areas(request):
    city_id = request.GET.get('city_id')
    areas = Area.objects.filter(city_ref_id=city_id, area_status=True).values('id', 'area_name')
    return JsonResponse({'areas': list(areas)})

# def get_states(request, country_id):
#     try:
#         country = Country.objects.get(id=country_id, country_status=True)
#         states = State.objects.filter(country_ref=country, state_status=True).order_by('state_name')
#         state_list = [{'id': state.id, 'name': state.state_name} for state in states]
#         return JsonResponse({'states': state_list})
#     except Country.DoesNotExist:
#         return JsonResponse({'states': []}, status=404)
#
# def get_cities(request, state_id):
#     try:
#         state = State.objects.get(id=state_id, state_status=True)
#         cities = City.objects.filter(state_ref=state, city_status=True).order_by('city_name')
#         city_list = [{'id': city.id, 'name': city.city_name} for city in cities]
#         return JsonResponse({'city': city_list})
#     except State.DoesNotExist:
#         return JsonResponse({'city': []}, status=404)
#Console vendor management ends here

# Location starts here

#COuntry starts here
@master_login_required
def vendorCountry(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            country = request.POST.get('country')
            if Country.objects.filter(admin_registration_id=admin_regid,country_name=country).exists():
                messages.error(request,'Country already exists.',extra_tags='danger')
            else:
                Country.objects.create(
                    admin_registration_id_id=admin_regid,
                    country_name=country
                )
                messages.error(request,'Country created successfully.',extra_tags='success')
            return redirect('vendorCountry')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('vendorCountry')

    return render(request,'general_settings/locations/country/country.html')


@master_login_required
def countryRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                country_details = get_object_or_404(Country, id=edit_id)
                context ={
                    'c':country_details
                }
                return render(request,'general_settings/locations/country/country_components/country_edit_form.html',context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(country_name__icontains = query)
                )
            country_details = Country.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator= Paginator(country_details,10)
            page_obj = paginator.get_page(page_number)
            context = {
                'country_records':page_obj
            }
            return render(request,'general_settings/locations/country/country_components/country_list_data.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('vendorCountry')


@master_login_required
def countryStatusChange(request,pk):
    try:
        country_details = get_object_or_404(Country,id=pk)
        if request.headers.get('HX-Request'):
            country_details.country_status = not country_details.country_status
            country_details.save()
            return render(request,'general_settings/locations/country/country_components/country_status_change.html', {'country':country_details,'status_page':'country_page'})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('countryRenderData')

@master_login_required
def deleteCountry(request,pk):
    try:
        country_delete= get_object_or_404(Country,id=pk)
        country_delete.delete()
        messages.error(request, "Country deleted successfully.",extra_tags='success')
        return redirect('vendorCountry')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('vendorCountry')

@master_login_required
def updateCountry(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        country_details = get_object_or_404(Country, id=pk)
        if request.method == 'POST':
            country = request.POST.get('ucountry')
            if Country.objects.exclude(id=pk).filter(country_name=country).exists():
                messages.error(request,'Country already exists.',extra_tags='danger')
            else:
                country_details.admin_registration_id_id = admin_regid
                country_details.country_name = country
                country_details.save()
                messages.error(request,'Country Updated successfully.',extra_tags='success')
            return redirect('vendorCountry')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('vendorCountry')

#state starts here
@master_login_required
def vendorState(request):
    try:

        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            state = request.POST.get('state')
            country_id = request.POST.get('country')
            country = Country.objects.get(admin_registration_id=admin_regid,id=country_id,country_status=True)

            if State.objects.filter(admin_registration_id=admin_regid,country_ref=country,state_name=state).exists():
                messages.error(request,'State already exists.',extra_tags='danger')
            else:
                State.objects.create(
                    admin_registration_id_id=admin_regid,
                    country_ref = country,
                    state_name=state
                )
                messages.error(request,'state created successfully.',extra_tags='success')
            return redirect('vendorState')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('vendorState')
    context={
        'country':Country.objects.filter(admin_registration_id=admin_regid,country_status=True)
    }

    return render(request,'general_settings/locations/state/state.html',context)

@master_login_required
def stateRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                state_details = get_object_or_404(State, id=edit_id)
                context ={
                    's':state_details,
                    'country': Country.objects.filter(admin_registration_id=admin_regid,country_status=True)
                }
                return render(request,'general_settings/locations/state/state_components/state_edit_form.html',context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &=Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(state_name__icontains = query)
                )
            state_details = State.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator= Paginator(state_details,10)
            page_obj = paginator.get_page(page_number)
            context = {
                'state_records':page_obj
            }
            return render(request,'general_settings/locations/state/state_components/state_components_list_data.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('vendorState')

@master_login_required
def stateStatusChange(request,pk):
    try:
        state_details = get_object_or_404(State,id=pk)
        if request.headers.get('HX-Request'):
            state_details.state_status = not state_details.state_status
            state_details.save()
            return render(request,'general_settings/locations/state/state_components/state_components_status_change.html', {'state':state_details,'status_page':'state_page'})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('stateRenderData')

def deleteState(request,pk):
    try:
        state_delete = get_object_or_404(State, id=pk)
        state_delete.delete()
        messages.error(request,"State deleted successfully.",extra_tags='success')
        return redirect('vendorState')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('vendorState')

def updateState(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        state_details = get_object_or_404(State,id=pk)
        if request.method == 'POST':
            country_id = request.POST.get('ucountry')
            state = request.POST.get('ustate')
            country = get_object_or_404(Country, id=country_id)
            if State.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,country_ref=country,state_name=state).exists():
                messages.error(request, 'State already exists.',extra_tags='danger')
            else:
                state_details.admin_registration_id_id=admin_regid
                state_details.country_ref=country
                state_details.state_name=state

                state_details.save()
                messages.error(request,'State updated successfully.',extra_tags='success')
            return redirect('vendorState')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an error occured {str(e)}", extra_tags='danger')
        return redirect('vendorState')
#State ends here



#state ends here

#city starts here

@master_login_required
def vendorCity(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            city = request.POST.get('city')
            country_id = request.POST.get('country')
            state_id = request.POST.get('state')
            country = Country.objects.get(admin_registration_id=admin_regid, id=country_id, country_status=True)
            state = State.objects.get(admin_registration_id=admin_regid, id=state_id, state_status=True,
                                      country_ref=country)

            if City.objects.filter(admin_registration_id=admin_regid, country_ref=country, state_ref=state,
                                   city_name=city).exists():
                messages.error(request, 'City already exists.', extra_tags='danger')
            else:
                City.objects.create(
                    admin_registration_id_id=admin_regid,
                    country_ref=country,
                    state_ref=state,
                    city_name=city
                )
                messages.error(request, 'City created successfully.', extra_tags='success')
            return redirect('vendorCity')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('vendorCity')

    context = {
        'country': Country.objects.filter(admin_registration_id=admin_regid, country_status=True),
        'state': State.objects.filter(admin_registration_id=admin_regid, state_status=True)
    }
    return render(request, 'general_settings/locations/city/city.html', context)


@master_login_required
def cityRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                city_details = get_object_or_404(City, id=edit_id)
                context = {
                    's': city_details,
                    'country': Country.objects.filter(admin_registration_id=admin_regid, country_status=True),
                    'state': State.objects.filter(admin_registration_id=admin_regid, state_status=True,
                                                  country_ref=city_details.country_ref)
                }
                return render(request, 'general_settings/locations/city/city_components/city_components_edit_form.html',
                              context)

            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(city_name__icontains=query)
                )
            city_details = City.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(city_details, 10)
            page_obj = paginator.get_page(page_number)
            context = {
                'city_records': page_obj
            }
            return render(request, 'general_settings/locations/city/city_components/city_components_list_data.html',
                          context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f'Error occurred {str(e)}', extra_tags='danger')
        return redirect('vendorCity')


@master_login_required
def cityStatusChange(request, pk):
    try:
        city_details = get_object_or_404(City, id=pk)
        if request.headers.get('HX-Request'):
            city_details.city_status = not city_details.city_status
            city_details.save()
            return render(request, 'general_settings/locations/city/city_components/city_components_status_change.html',
                          {'city': city_details, 'status_page': 'city_page'})
    except Exception as e:
        print(str(e), " Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('cityRenderData')


@master_login_required
def deleteCity(request, pk):
    try:
        city_delete = get_object_or_404(City, id=pk)
        city_delete.delete()
        messages.error(request, "City deleted successfully.", extra_tags='success')
        return redirect('vendorCity')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('vendorCity')


@master_login_required
def updateCity(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        city_details = get_object_or_404(City, id=pk)
        if request.method == 'POST':
            country_id = request.POST.get('ucountry')
            state_id = request.POST.get('ustate')
            city = request.POST.get('ucity')
            country = get_object_or_404(Country, id=country_id)
            state = get_object_or_404(State, id=state_id, country_ref=country)

            if City.objects.exclude(id=pk).filter(admin_registration_id=admin_regid, country_ref=country,
                                                  state_ref=state, city_name=city).exists():
                messages.error(request, 'City already exists.', extra_tags='danger')
            else:
                city_details.admin_registration_id_id = admin_regid
                city_details.country_ref = country
                city_details.state_ref = state
                city_details.city_name = city
                city_details.save()
                messages.error(request, 'City updated successfully.', extra_tags='success')
            return redirect('vendorCity')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('vendorCity')

#get states accordig to country in city
@master_login_required
def get_states_by_country(request):
    try:
        country_id = request.GET.get('country_id')
        states = State.objects.filter(country_ref_id=country_id, state_status=True).values('id', 'state_name')
        return JsonResponse({'states': list(states)})
    except Exception as e:
        print(f"error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
#City ends here


#Area starts here
@master_login_required
def vendorArea(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            area = request.POST.get('area')
            country_id = request.POST.get('country')
            state_id = request.POST.get('state')
            city_id = request.POST.get('city')
            country = Country.objects.get(admin_registration_id=admin_regid, id=country_id, country_status=True)
            state = State.objects.get(admin_registration_id=admin_regid, id=state_id, state_status=True, country_ref=country)
            city = City.objects.get(admin_registration_id=admin_regid, id=city_id, city_status=True, state_ref=state, country_ref=country)

            if Area.objects.filter(admin_registration_id=admin_regid, country_ref=country, state_ref=state, city_ref=city, area_name=area).exists():
                messages.error(request, 'Area already exists.', extra_tags='danger')
            else:
                Area.objects.create(
                    admin_registration_id_id=admin_regid,
                    country_ref=country,
                    state_ref=state,
                    city_ref=city,
                    area_name=area
                )
                messages.error(request, 'Area created successfully.', extra_tags='success')
            return redirect('vendorArea')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('vendorArea')

    context = {
        'country': Country.objects.filter(admin_registration_id=admin_regid, country_status=True),
        'state': State.objects.filter(admin_registration_id=admin_regid, state_status=True),
        'city': City.objects.filter(admin_registration_id=admin_regid, city_status=True)
    }
    return render(request, 'general_settings/locations/area/area.html', context)

@master_login_required
def areaRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                area_details = get_object_or_404(Area, id=edit_id)
                context = {
                    's': area_details,
                    'country': Country.objects.filter(admin_registration_id=admin_regid, country_status=True),
                    'state': State.objects.filter(admin_registration_id=admin_regid, state_status=True, country_ref=area_details.country_ref),
                    'city': City.objects.filter(admin_registration_id=admin_regid, city_status=True, state_ref=area_details.state_ref)
                }
                return render(request, 'general_settings/locations/area/area_components/area_components_edit_form.html', context)

            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(area_name__icontains=query)
                )
            area_details = Area.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(area_details, 10)
            page_obj = paginator.get_page(page_number)
            context = {
                'area_records': page_obj
            }
            return render(request, 'general_settings/locations/area/area_components/area_components_list_data.html', context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f'Error occurred {str(e)}', extra_tags='danger')
        return redirect('vendorArea')

@master_login_required
def areaStatusChange(request, pk):
    try:
        area_details = get_object_or_404(Area, id=pk)
        if request.headers.get('HX-Request'):
            area_details.area_status = not area_details.area_status
            area_details.save()
            return render(request, 'general_settings/locations/area/area_components/area_components_status_change.html',
                          {'area': area_details, 'status_page': 'area_page'})
    except Exception as e:
        print(str(e), " Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('areaRenderData')

@master_login_required
def deleteArea(request, pk):
    try:
        area_delete = get_object_or_404(Area, id=pk)
        area_delete.delete()
        messages.error(request, "Area deleted successfully.", extra_tags='success')
        return redirect('vendorArea')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('vendorArea')

@master_login_required
def updateArea(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        area_details = get_object_or_404(Area, id=pk)
        if request.method == 'POST':
            country_id = request.POST.get('ucountry')
            state_id = request.POST.get('ustate')
            city_id = request.POST.get('ucity')
            area = request.POST.get('uarea')
            country = get_object_or_404(Country, id=country_id)
            state = get_object_or_404(State, id=state_id, country_ref=country)
            city = get_object_or_404(City, id=city_id, state_ref=state, country_ref=country)

            if Area.objects.exclude(id=pk).filter(admin_registration_id=admin_regid, country_ref=country, state_ref=state, city_ref=city, area_name=area).exists():
                messages.error(request, 'Area already exists.', extra_tags='danger')
            else:
                area_details.admin_registration_id_id = admin_regid
                area_details.country_ref = country
                area_details.state_ref = state
                area_details.city_ref = city
                area_details.area_name = area
                area_details.save()
                messages.error(request, 'Area updated successfully.', extra_tags='success')
            return redirect('vendorArea')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('vendorArea')

@master_login_required
def get_cities_by_state(request):
    try:
        state_id = request.GET.get('state_id')
        cities = City.objects.filter(state_ref_id=state_id, city_status=True).values('id', 'city_name')
        return JsonResponse({'cities': list(cities)})
    except Exception as e:
        print(f"error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
#Area ends here


# Location ends here
#account Type starts here
@master_login_required
def accountType(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            account_type = request.POST.get('accounttype')
            if AccountType.objects.filter(admin_registration_id=admin_regid,account_type=account_type).exists():
                messages.error(request,'Account type already exists.',extra_tags='danger')

            else:
                AccountType.objects.create(
                    admin_registration_id_id=admin_regid,
                    account_type=account_type,
                )
                messages.error(request,"Account Type created successfully.",extra_tags='success')

            return redirect('accountType')
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('accountType')
    return render(request,'general_settings/financeandaccounts/accounttype/accounttype.html')

@master_login_required
def accountTypeRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                account_details= get_object_or_404(AccountType,id=edit_id)
                context ={
                    'a':account_details
                }
                return render(request,'general_settings/financeandaccounts/accounttype/account_type_components/account_type_edit_form.html',context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(account_type__icontains = query)
                )
            account_records = AccountType.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(account_records,10)
            page_obj = paginator.get_page(page_number)
            context={
                'account_records': page_obj
            }
            return render(request, 'general_settings/financeandaccounts/accounttype/account_type_components/account_type_components_list_data.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('accountType')

@master_login_required
def accountStatusChange(request,pk):
    try:
        account_details = get_object_or_404(AccountType,id=pk)
        if request.headers.get('HX-Request'):
            account_details.account_type_status = not account_details.account_type_status
            account_details.save()
            return render(request,'general_settings/financeandaccounts/accounttype/account_type_components/account_type_status_change.html',{'account':account_details,'status_page':'account_page'})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('accountTypeRenderData')

@master_login_required
def accountTypeDelete(request,pk):
    try:
        account_delete = get_object_or_404(AccountType,id=pk)
        account_delete.delete()
        messages.error(request,'Account type deleted successfully.',extra_tags='success')
        return redirect('accountType')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('accountType')

@master_login_required
def accountTypeUpdate(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        account_details = get_object_or_404(AccountType,id=pk)
        if request.method =='POST':
            account_type = request.POST.get('uaccounttype')
            if AccountType.objects.exclude(id=pk).filter(account_type=account_type).exists():
                messages.error(request,"Account type already exists.", extra_tags='danger')

            else:
                account_details.admin_registration_id_id = admin_regid
                account_details.account_type=account_type
                account_details.save()
                messages.error(request,'Account type updated successfully.',extra_tags='success')
            return redirect('accountType')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('accountType')

#account Type ends here


#bank name starts here
@master_login_required
def bankName(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            bank_name = request.POST.get('bankname')
            if BankName.objects.filter(admin_registration_id=admin_regid,bank_name=bank_name).exists():
                messages.error(request,'Bank already exists.', extra_tags='danger')
            else:
                BankName.objects.create(
                    admin_registration_id_id=admin_regid,
                    bank_name= bank_name,
                )
                messages.error(request,'Bank created successfully.')
            return redirect('bankName')

    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f"An error occured {str(e)}", extra_tags='danger')
        return redirect('bankName')
    return render(request,'general_settings/financeandaccounts/bank_names/bank_name.html')

@master_login_required
def bankNameRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                bank_details = get_object_or_404(BankName,id=edit_id)
                context= {
                    'b': bank_details
                }
                return render(request, 'general_settings/financeandaccounts/bank_names/bank_name_components/bank_name_edit_form.html',context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name&= Q(
                    Q(admin_registration_id__id__icontains=admin_regid)&
                    Q(bank_name__icontains=query)

                )
            bank_records = BankName.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(bank_records,10)
            page_obj = paginator.get_page(page_number)
            context ={
                'bank_records': page_obj
            }
            return render(request,'general_settings/financeandaccounts/bank_names/bank_name_components/bank_name_components_list_data.html',context)

    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('bankName')

@master_login_required
def bankStatusChange(request,pk):
    try:
        bank_details = get_object_or_404(BankName,id=pk)
        if request.headers.get('HX-Request'):
            bank_details.bank_status = not bank_details.bank_status
            bank_details.save()
            return render(request,'general_settings/financeandaccounts/bank_names/bank_name_components/bank_name_components_status_change.html',{'bank':bank_details,'status_page':'bank_page'})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('bankNameRenderData')

@master_login_required
def bankDelete(request,pk):
    try:
        bank_delete = get_object_or_404(BankName, id=pk)
        bank_delete.delete()
        messages.error(request, "Bank deleted successfully.", extra_tags="success")
        return redirect('bankName')
    except Exception as e:
        print(str(e),"Error")
        messages.error(request,f"an Error Occured {str(e)}",extra_tags='danger')
        return redirect('bankName')

@master_login_required
def bankUpdate(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        bank_details = get_object_or_404(BankName,id=pk)
        if request.method == "POST":
            bank_name = request.POST.get('ubankname')
            if BankName.objects.exclude(id=pk).filter(bank_name = bank_name).exists():
                messages.error(request,'Bank name already exists.',extra_tags='danger')

            else:
                bank_details.admin_registration_id_id = admin_regid
                bank_details.bank_name= bank_name
                bank_details.save()
                messages.error(request,'Bank updated successfully.',extra_tags='success')
            return redirect('bankName')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('bankName')
#bank name ends here


# Transport Type start here
@master_login_required
def transportType(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            transport_type = request.POST.get('transport_type')
            if TransportType.objects.filter(admin_registration_id=admin_regid, transport_type=transport_type).exists():
                messages.error(request, 'Transport Type already exists.', extra_tags='danger')
            else:
                TransportType.objects.create(
                    admin_registration_id_id=admin_regid,
                    transport_type=transport_type
                )
                messages.error(request, "Transport Type created successfully.", extra_tags='success')
            return redirect('transportType')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('transportType')
    return render(request, 'general_settings/console_transport_type/transport_type.html')

@master_login_required
def transportTypeRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id_variable = request.GET.get('editid')
            if edit_id_variable:
                transport_type_details = TransportType.objects.get(id=edit_id_variable)
                context = {
                    't': transport_type_details,
                }
                return render(request, 'general_settings/console_transport_type/transport_type_components/transport_type_edit_form.html', context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(transport_type__icontains=query)
                )
            transport_type_records = TransportType.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(transport_type_records, 10)
            page_obj = paginator.get_page(page_number)
            context = {
                'transport_type_records': page_obj
            }
            return render(request, 'general_settings/console_transport_type/transport_type_components/transport_type_list_data.html', context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f'Error occurred: {str(e)}', extra_tags='danger')
        return redirect('transportType')

@master_login_required
def transportTypeStatusChange(request, pk):
    try:
        transport_type_details = get_object_or_404(TransportType, id=pk)
        if request.headers.get('HX-Request'):
            transport_type_details.transport_status = not transport_type_details.transport_status
            transport_type_details.save()
            return render(request, "general_settings/console_transport_type/transport_type_components/transport_form_status_change.html",
                          {"transport_type": transport_type_details, "status_page": "transport_type_page"})
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('transportTypeRenderData')

@master_login_required
def deleteTransportType(request, pk):
    try:
        transport_type_delete = get_object_or_404(TransportType, id=pk)
        transport_type_delete.delete()
        messages.error(request, "Transport Type deleted successfully.", extra_tags="success")
        return redirect('transportType')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('transportType')

@master_login_required
def updateTransportType(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        transport_type_details = get_object_or_404(TransportType, id=pk)
        if request.method == "POST":
            transport_type = request.POST.get('utransport_type')
            if TransportType.objects.exclude(id=pk).filter(transport_type=transport_type).exists():
                messages.error(request, 'Transport Type already exists.', extra_tags='danger')
            else:
                transport_type_details.admin_registration_id_id = admin_regid
                transport_type_details.transport_type = transport_type
                transport_type_details.save()
                messages.error(request, "Transport Type updated successfully.", extra_tags='success')
            return redirect('transportType')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('transportType')
#Transport ends here


# ity Catalogue starts here
@master_login_required
def productCatalogue(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            main_category_id = request.POST.get('product_category')
            sub_category_id = request.POST.get('product_subcategory')
            brand_id = request.POST.get('product_brand')
            product_color_id = request.POST.get('product_color')
            product_size_id = request.POST.getlist('product_size[]')
            product_material_id = request.POST.get('product_material')
            # product_mrp = request.POST.get('product_catalogue_mrp')
            # product_discount_percent = request.POST.get('product_discount_percent')
            product_title = request.POST.get('product_catalogue_title')
            product_description = request.POST.get('product_description')
            product_images = request.FILES.getlist('product_images')
            main_category = get_object_or_404(Main_category, id=main_category_id)
            sub_category = get_object_or_404(Sub_category, id=sub_category_id)
            brand= get_object_or_404(Brand, id=brand_id)
            color= get_object_or_404(ProductColor,id=product_color_id)
            material=get_object_or_404(ProductMaterial,id=product_material_id)


            # Validate number of images
            if len(product_images) < 3:
                messages.error(request, "Please upload at least 3 images.", extra_tags='danger')
                return redirect('productCatalogue')
            if len(product_images) > 5:
                messages.error(request, "You can upload a maximum of 5 images.", extra_tags='danger')
                return redirect('productCatalogue')
            if not product_size_id:
                messages.error(request, "Please select at least one size.", extra_tags='danger')
                return redirect('productCatalogue')

            # Validate MRP and discount percent
            # if not product_mrp or float(product_mrp) <= 0:
            #     messages.error(request, "Please enter a valid MRP greater than 0.", extra_tags='danger')
            #     return redirect('productCatalogue')
            # if product_discount_percent and (
            #         float(product_discount_percent) < 0 or float(product_discount_percent) > 100):
            #     messages.error(request, "Discount percent must be between 0 and 100.", extra_tags='danger')
            #     return redirect('productCatalogue')

            if ProductCatalogue.objects.filter(admin_registration_id=admin_regid,main_category_ref=main_category,sub_category_ref=sub_category,product_title=product_title).exists():
                messages.error(request, "Product already exists.",extra_tags='danger')

            else:
                product=ProductCatalogue.objects.create(
                    admin_registration_id_id=admin_regid,
                    main_category_ref=main_category,
                    sub_category_ref=sub_category,
                    product_brand_ref=brand,
                    product_color_ref=color,
                    product_material=material,
                    # product_mrp=product_mrp,
                    # product_discount_percent=product_discount_percent,
                    product_title=product_title,
                    product_description = product_description,

                )
                #sizes
                for size_id in product_size_id:
                    size=get_object_or_404(ProductSize,id=size_id)
                    product.product_size_ref.add(size)

                for image in product_images:
                    ProductCatalogueImages.objects.create(product=product, image=image)
                messages.success(request, 'Product created successfully.', extra_tags='success')
            return redirect('productCatalogue')

    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"en error occured {str(e)}", extra_tags='danger')
        return redirect('productCatalogue')
    context={
        'main_category': Main_category.objects.filter(admin_registration_id=admin_regid,main_category_status=True),
        'sub_category': Sub_category.objects.filter(admin_registration_id=admin_regid,sub_category_status=True),
        'brand':Brand.objects.filter(admin_registration_id=admin_regid,brand_status=True),
        'color':ProductColor.objects.filter(admin_registration_id=admin_regid,product_color_status=True),
        'size':ProductSize.objects.filter(admin_registration_id=admin_regid,product_size_status=True),
        'material':ProductMaterial.objects.filter(admin_registration_id=admin_regid,product_type_status=True),
    }
    return render(request,'console_product_catalogue/product_catalogue.html',context)

@master_login_required
def productcatalogueRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            show_id=request.GET.get('showid')
            if show_id:
                product_details = get_object_or_404(ProductCatalogue,id=show_id)
                product_images = ProductCatalogueImages.objects.filter(admin_registration_id=admin_regid,product=product_details)
                context={
                    'product':product_details,
                    'product_images': product_images
                }
                return render(request,'console_product_catalogue/product_catalogue_components/product_catalogue_show_product.html',context)
            edit_id= request.GET.get('editid')
            if edit_id:
                product_details = get_object_or_404(ProductCatalogue,id=edit_id)
                context={
                    'p':product_details,
                    'main_category': Main_category.objects.filter(admin_registration_id=admin_regid,main_category_status=True),
                    'sub_category':Sub_category.objects.filter(admin_registration_id=admin_regid,sub_category_status=True),
                    'brand': Brand.objects.filter(admin_registration_id=admin_regid,brand_status=True),
                    'color': ProductColor.objects.filter(admin_registration_id=admin_regid,product_color_status=True),
                    'size': ProductSize.objects.filter(admin_registration_id=admin_regid,product_size_status=True),
                    'material': ProductMaterial.objects.filter(admin_registration_id=admin_regid,product_type_status=True),
                }
                return render(request,'console_product_catalogue/product_catalogue_components/product_catalogue_components_edit_form.html',context)
            query = request.GET.get('query')
            query_name =Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &=Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(product_title__icontains= query)
                )
            product_details = ProductCatalogue.objects.filter(query_name).order_by('-id')
            page_number=request.GET.get('page')
            paginator = Paginator(product_details,10)
            page_obj = paginator.get_page(page_number)
            context={
                'product_records': page_obj,
                'main_category': Main_category.objects.filter(admin_registration_id=admin_regid,main_category_status=True),
                'sub_category': Sub_category.objects.filter(admin_registration_id=admin_regid,sub_category_status=True),
            }
            return render(request,'console_product_catalogue/product_catalogue_components/product_catalogue_components_list_data.html',context)
    except Exception as e:
        print(f"error:{str(e)}")
        messages.error(request, f'Error occured {str(e)}', extra_tags='danger')
        return redirect('productCatalogue')


@master_login_required
def productcatalogueStatusChange(request,pk):
    try:
        product_details= get_object_or_404(ProductCatalogue,id=pk)
        if request.headers.get('HX-Request'):
            product_details.product_catalogue_status=not product_details.product_catalogue_status
            product_details.save()
            return render(request,"console_product_catalogue/product_catalogue_components/product_catalogue_components_status_change.html",{"product":product_details,"status_page": "product_page"})
    except Exception as e:
        print(str(e)," Error")
        messages.error(request, f"An error Occured {str(e)}",extra_tags='danger')
        return redirect('productcatalogueRenderData')

@master_login_required
def deleteProductCatalogue(request,pk):
    try:
        product_delete = get_object_or_404(ProductCatalogue, id=pk)
        product_delete.delete()
        messages.error(request, "Product deleted successfully.", extra_tags="success")
        return redirect('productCatalogue')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an Error Occured {str(e)}", extra_tags='danger')
        return redirect('productCatalogue')

@master_login_required
def updateProductCatalogue(request,pk):
    try:
        admin_regid = request.session.get('master_id')
        product_catalogue = get_object_or_404(ProductCatalogue,id=pk)
        if request.method == 'POST':
            main_category_id= request.POST.get('uproduct_category')
            sub_category_id = request.POST.get('uproduct_subcategory')
            brand_id = request.POST.get('uproduct_brand')
            product_color_id = request.POST.get('uproduct_color')
            product_size_id = request.POST.getlist('uproduct_size[]')
            product_material_id = request.POST.get('uproduct_material')
            # product_mrp = request.POST.get('uproduct_catalogue_mrp')
            # product_discount_percent = request.POST.get('uproduct_discount_percent')
            product_title = request.POST.get('uproduct_catalogue_title')
            product_description = request.POST.get('uproduct_description')
            product_images = request.FILES.getlist('uproduct_images')
            main_category= get_object_or_404(Main_category,id=main_category_id,main_category_status=True)
            sub_category= get_object_or_404(Sub_category,id=sub_category_id, sub_category_status=True)
            brand = get_object_or_404(Brand, id=brand_id,brand_status=True)
            color = get_object_or_404(ProductColor, id=product_color_id,product_color_status=True)
            material = get_object_or_404(ProductMaterial, id=product_material_id,product_type_status=True)
            # Validate MRP and discount percent
            # if not product_mrp or float(product_mrp) <= 0:
            #     messages.error(request, "Please enter a valid MRP greater than 0.", extra_tags='danger')
            #     return redirect('productCatalogue')
            # if product_discount_percent and (
            #         float(product_discount_percent) < 0 or float(product_discount_percent) > 100):
            #     messages.error(request, "Discount percent must be between 0 and 100.", extra_tags='danger')
            #     return redirect('productCatalogue')


            if ProductCatalogue.objects.exclude(id=pk).filter(admin_registration_id=admin_regid,main_category_ref=main_category,sub_category_ref=sub_category,product_title=product_title).exists():
                messages.error(request,'Product already exists',extra_tags='danger')

            # if not product_size_id:
            #     messages.error(request, 'Please select at least one size.', extra_tags='danger')
            #     return redirect('productCatalogue')

            # # Validate images if provided
            # if product_images:
            #     if len(product_images) < 3:
            #         messages.error(request, 'Please upload at least 3 images.', extra_tags='danger')
            #         return redirect('productCatalogue')
            #     if len(product_images) > 5:
            #         messages.error(request, 'You can upload a maximum of 5 images.', extra_tags='danger')
            #         return redirect('productCatalogue')

            product_catalogue.admin_registration_id_id = admin_regid

            product_catalogue.main_category_ref = main_category

            product_catalogue.sub_category_ref = sub_category

            product_catalogue.product_brand_ref = brand

            product_catalogue.product_color_ref = color

            product_catalogue.product_material = material

            # product_catalogue.product_mrp = product_mrp
            # product_catalogue.product_discount_percent = product_discount_percent

            product_catalogue.product_title = product_title

            product_catalogue.product_description = product_description

            product_catalogue.save()
            # Update sizes (clear existing and add new ones)
            if product_size_id:
                product_catalogue.product_size_ref.clear()
                for size_id in product_size_id:
                    size = get_object_or_404(ProductSize, id=size_id, product_size_status=True)
                    product_catalogue.product_size_ref.add(size)

            # Update images if provided
            if product_images:
                # Delete existing images
                ProductCatalogueImages.objects.filter(product=product_catalogue).delete()
                # Add new images
                for image in product_images:
                    ProductCatalogueImages.objects.create(product=product_catalogue, image=image)

            messages.success(request, 'Product updated successfully.', extra_tags='success')
            return redirect('productCatalogue')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"an error occured {str(e)}", extra_tags='danger')
        return redirect('productCatalogue')

@master_login_required
def showProductCatalogue(request,pk):
    admin_regid = request.session.get('master_id')
    product_details = ProductCatalogue.objects.filter(admin_registration_id=admin_regid,id=pk).first()
    product_images = ProductCatalogueImages.objects.filter(product=product_details)
    purchase_items = PurchaseItem.objects.filter(admin_registration_id=admin_regid,product=product_details, purchase_item_status=True)
    total_quantity = purchase_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    latest_mrp = purchase_items.order_by('-purchase_item_created_at').values('mrp').first()['mrp'] if purchase_items.exists() else None

    context={
        'product':product_details,
        'product_images': product_images,
        'purchase_items': purchase_items,
        'total_quantity': total_quantity,
        'latest_mrp': latest_mrp,
    }
    return render(request,'console_product_catalogue/console_product_catalogue_show_product.html',context)


#getting subcategory values according to main category
@master_login_required
def get_subcategories(request):
    main_category_id = request.GET.get('main_category_id')
    subcategories = Sub_category.objects.filter(main_category_id=main_category_id, sub_category_status=True).values('id', 'sub_category')
    return JsonResponse({'subcategories': list(subcategories)})

# Product Catalogue ends here


#Purchase Management starts here
@master_login_required
def viewAllPurchasesTable(request):
    return render(request,'console_product_purchase_management/product_all_purchases.html')
#Create purchase starts here

@master_login_required
def purchaseManagement(request):
    admin_regid = request.session.get('master_id')
    vendor_details = CreateVendor.objects.filter(admin_registration_id=admin_regid,vendor_status=True)
    products = ProductCatalogue.objects.filter(admin_registration_id=admin_regid)
    payment_types = ProductPaymentType.objects.filter(admin_registration_id=admin_regid,payment_status=True)
    account_type = AccountType.objects.filter(account_type_status=True, admin_registration_id=admin_regid)

    try:
        if request.method == 'POST':
            vendor_id = request.POST.get('purchase_vendor')
            payment_type_id = request.POST.get('payment_type')
            grand_total = request.POST.get('grand_total')
            advance_amount = request.POST.get('advance_amount')
            pending_amount = request.POST.get('pending_amount')
            credit_amount = request.POST.get('credit_amount')
            use_credit = request.POST.get('use_credit') == 'true'
            print('Helloe', vendor_id)



            product_ids = request.POST.getlist('product[]')
            quantities = request.POST.getlist('quantity[]')
            mrps = request.POST.getlist('mrp[]')
            purchase_prices = request.POST.getlist('purchase_price[]')
            cgsts = request.POST.getlist('cgst[]')
            sgsts = request.POST.getlist('sgst[]')
            total= request.POST.getlist('total[]')
            total_with_gst = request.POST.getlist('total_with_gst[]')
            if not vendor_id or not payment_type_id:
                messages.error(request, "Vendor and payment type are required.", extra_tags='danger')
                return redirect('purchaseManagement')

            vendor = CreateVendor.objects.get(admin_registration_id=admin_regid, id=vendor_id, vendor_status=True)
            payment_type = ProductPaymentType.objects.get(admin_registration_id=admin_regid, id=payment_type_id,payment_status=True)

            # Convert amounts to Decimal
            grand_total = Decimal(grand_total) if grand_total else None
            advance_amount = Decimal(advance_amount) if advance_amount else None
            pending_amount = Decimal(pending_amount) if pending_amount else None
            credit_amount = Decimal(credit_amount) if credit_amount else Decimal('0')

            # Handle credit amount application
            vendor_credit, created = VendorCredit.objects.get_or_create(
                admin_registration_id_id=admin_regid,
                vendor=vendor,
                defaults={'credit_amount': Decimal('0')}
            )

            if use_credit and vendor_credit.credit_amount > 0:
                # Apply credit to advance_amount, up to grand_total
                credit_to_use = min(vendor_credit.credit_amount, grand_total)
                advance_amount = (advance_amount or Decimal('0')) + credit_to_use
                vendor_credit.credit_amount -= credit_to_use
                vendor_credit.save()
                pending_amount = grand_total - advance_amount

            # vendor = CreateVendor.objects.get(admin_registration_id=admin_regid,id=vendor_id, vendor_status=True)
            # payment_type = ProductPaymentType.objects.get(admin_registration_id=admin_regid,id=payment_type_id, payment_status=True)
            purchase_data = {
                'admin_registration_id_id': admin_regid,
                'vendor': vendor,
                'payment_type': payment_type,
                'grand_total': float(grand_total) if grand_total else None,
                'advance_amount': float(advance_amount) if advance_amount else None,
                'pending_amount': float(pending_amount) if pending_amount else None,
            }
            invoice_data = {
                'admin_registration_id_id': admin_regid,
                'vendor': vendor,

                'grand_total': float(grand_total) if grand_total else None,
                'advance_amount': float(advance_amount) if advance_amount else None,
                'pending_amount': float(pending_amount) if pending_amount else None,
            }
            payment_data = {
                'vendor': vendor,
                'payment_type': payment_type,
                'grand_total': float(grand_total) if grand_total else None,
                'advance_amount': float(advance_amount) if advance_amount else None,
                'pending_amount': float(pending_amount) if pending_amount else None,
            }

            payment_type_str = payment_type.payment_type.lower().replace(' ', '_')
            if payment_type_str == 'cash':
                purchase_data['cash_amount'] = float(request.POST.get('cash_amount')) if request.POST.get(
                    'cash_amount') else None
            elif payment_type_str == 'upi':
                purchase_data['upi_id'] = request.POST.get('upi_id')
                purchase_data['upi_transaction_id'] = request.POST.get('upi_transaction_id')
            elif payment_type_str == 'upi_cash':
                purchase_data['upi_cash_amount'] = float(request.POST.get('upi_cash_amount')) if request.POST.get(
                    'upi_cash_amount') else None
                purchase_data['upi_amount'] = float(request.POST.get('upi_amount')) if request.POST.get(
                    'upi_amount') else None
                purchase_data['upi_cash_transaction_id'] = request.POST.get('upi_cash_transaction_id')
            elif payment_type_str == 'net_banking':
                purchase_data['account_type'] = request.POST.get('account_type')
                purchase_data['bank_name'] = request.POST.get('bank_name')
                purchase_data['account_number'] = request.POST.get('account_number')
                purchase_data['netbanking_transaction_id'] = request.POST.get('netbanking_transaction_id')
            elif payment_type_str == 'cheque':
                purchase_data['cheque_number'] = request.POST.get('cheque_number')

            # Create Purchase instance
            purchase = Purchase.objects.create(**purchase_data)

            # Create PurchaseInvoice instance
            invoice_data['purchase_ref'] = purchase
            purchase_invoice = PurchaseInvoice.objects.create(**invoice_data)

            # Create PurchasePayments instance
            payment_data['invoice_ref'] = purchase_invoice
            payment_data['purchase_ref'] = purchase
            PurchasePayments.objects.create(**payment_data)


            if credit_amount > 0:
                vendor_credit, created = VendorCredit.objects.get_or_create(
                    admin_registration_id_id=admin_regid,
                    vendor=vendor,
                    defaults={'credit_amount': float(credit_amount)}
                )
                if not created:
                    vendor_credit.credit_amount += float(credit_amount)
                    vendor_credit.save()

            if pending_amount == 0:
                status=True
            else:
                status=False


            for i in range(len(product_ids)):
                product = ProductCatalogue.objects.get(admin_registration_id=admin_regid,id=product_ids[i])
                PurchaseItem.objects.create(
                    admin_registration_id_id=admin_regid,
                    purchase=purchase,
                    product=product,
                    quantity=int(quantities[i]),
                    mrp=float(mrps[i]),
                    purchase_price=float(purchase_prices[i]),
                    cgst=float(cgsts[i]),
                    sgst=float(sgsts[i]),
                    total_amount=float(total[i]),
                    total_amount_with_gst=float(total_with_gst[i]),
                    purchase_item_status=status,
                )


            messages.error(request, "Purchase saved successfully!",extra_tags='success')
            return redirect('viewAllPurchasesTable')

    except Exception as e:
        messages.error(request, f"Error saving purchase: {str(e)}",extra_tags='danger')
        return redirect('purchaseManagement')



    context = {
        'vendor': vendor_details,
        'products': products,
        'payment_types': payment_types,
        'account_types':account_type,
    }
    return render(request, 'console_product_purchase_management/product_purchase_management.html', context)
#create purchase ends here

#create render view starts here
@master_login_required
def purchaseRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if not admin_regid:
            messages.error(request, "Session expired. Please log in again.", extra_tags='danger')
            return redirect('sign-in')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                # Render edit form for a specific PurchaseItem
                purchase_invoice = get_object_or_404(PurchaseInvoice, id=edit_id)
                vendors = CreateVendor.objects.filter(vendor_status=True)
                products = ProductCatalogue.objects.filter(product_catalogue_status=True)
                payment_types = ProductPaymentType.objects.filter(admin_registration_id=admin_regid,payment_status=True)
                purchase_payments=PurchasePayments.objects.filter(invoice_ref__id=purchase_invoice.id)
                account_type=AccountType.objects.filter(account_type_status=True,admin_registration_id=admin_regid)
                context ={
                    'item': purchase_invoice,
                    'vendors': vendors,
                    'products': products,
                    'purchase_payments':purchase_payments,
                    'payment_types':payment_types,
                    'account_types':account_type,
                }
                return render(request, 'console_product_purchase_management/product_purchase_components/product_purchase_edit_form.html', context)

            # Render table data
            query = request.GET.get('query')
            query_filter = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_filter &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(vendor__vendor_name__icontains=query)
                )
            purchases = PurchaseInvoice.objects.filter(query_filter).select_related('vendor', 'purchase_ref', 'purchase_ref__payment_type').prefetch_related('purchase_ref__items','purchasepayments_set').annotate(
                num_products=Count('purchase_ref__items'),
                total_quantity=Sum('purchase_ref__items__quantity'),
                total_gst=Sum('purchase_ref__items__cgst') + Sum('purchase_ref__items__sgst')
            ).distinct().order_by('-id')
            vendor_ids=[]
            for purchase in purchases:
                vendor_ids.append(purchase.vendor.id)

            vendor_credits = VendorCredit.objects.filter(
                admin_registration_id_id=admin_regid,
                vendor__id__in=vendor_ids
            ).select_related('vendor')
            credit_map={}
            for credit in vendor_credits:
                credit_map={credit.vendor.id:credit.credit_amount}



            page_number = request.GET.get('page')
            paginator = Paginator(purchases, 10)
            page_obj = paginator.get_page(page_number)
            context = {

                'purchases': page_obj,
                'credit_map': credit_map,
            }
            return render(request, 'console_product_purchase_management/product_purchase_components/product_purchase_list_data.html', context)

    except Exception as e:
        print(f"Error: {str(e)}")
        messages.error(request, f"Error occurred: {str(e)}", extra_tags='danger')
        return redirect('viewAllPurchasesTable')

@master_login_required
def view_purchase_invoice(request, invoice_id):
    try:
        invoice = get_object_or_404(PurchaseInvoice, id=invoice_id, admin_registration_id=request.session.get('master_id'))
        # Fetch admin profile and contact details
        admin_profile = Admin_Onetime_Profile.objects.filter(
            admin_registration_id=invoice.admin_registration_id
        ).first()
        admin_contact = AdminContactUs.objects.filter(
            admin_registration_id=invoice.admin_registration_id,
            admin_contactus_status=True
        ).first()
        # Calculate totals for CGST, SGST, Total Amount, and Total Amount with GST
        totals = invoice.purchase_ref.items.aggregate(
            total_quantity=Sum('quantity'),
            total_cgst=Sum('cgst'),
            total_sgst=Sum('sgst'),
            total_amount=Sum('total_amount'),
            total_amount_with_gst=Sum('total_amount_with_gst')
        )

        context = {

            'invoice': invoice,
            'admin_profile': admin_profile,
            'admin_contact': admin_contact,
            'totals':totals
        }
        return render(request, 'console_product_purchase_management/product_purchase_invoice.html', context)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=400)
@master_login_required
def purchaseItemStatusChange(request, item_id):
    try:
        item = get_object_or_404(PurchaseItem, id=item_id)
        if request.headers.get('HX-Request'):
            item.purchase_item_status = not item.purchase_item_status
            item.save()
            context = {
                'item': item,
                'status_page':'purchase_status',
            }
            return render(request, 'console_product_purchase_management/product_purchase_components/product_purchase_status_change.html', context)
    except Exception as e:
        messages.error(request, f"Error: {str(e)}", extra_tags='danger')
    return HttpResponse(status=400)

# def deletePurchaseItem(request, item_id):
#     try:
#         item = get_object_or_404(PurchaseItem, id=item_id)
#         item.delete()
#         messages.error(request, "Purchase item deleted successfully!", extra_tags='success')
#     except Exception as e:
#         messages.error(request, f"Error: {str(e)}", extra_tags='danger')
#     return redirect('viewAllPurchasesTable')
@master_login_required
def deletePurchase(request, invoice_id):
    try:
        purchase_invoice = get_object_or_404(PurchaseInvoice, id=invoice_id)
        admin_regid = request.session.get('master_id')
        purchase_payment = PurchasePayments.objects.filter(invoice_ref=purchase_invoice).first()
        if purchase_payment and purchase_payment.pending_amount == 0:
            messages.error(request, 'Purchase cannot be deleted as it is fully paid!', extra_tags='danger')
        else:
            # Update vendor credit if advance amount exists
            if purchase_payment and purchase_payment.advance_amount and purchase_payment.advance_amount > 0:
                vendor_credit, created = VendorCredit.objects.get_or_create(
                    admin_registration_id_id=admin_regid,
                    vendor=purchase_invoice.vendor,
                    defaults={'credit_amount': purchase_payment.advance_amount}
                )
                if not created:
                    vendor_credit.credit_amount += purchase_payment.advance_amount
                    vendor_credit.save()
            # Delete related objects
            purchase_invoice.purchase_ref.delete()  # Cascades to PurchaseItem
            purchase_invoice.delete()  # Cascades to PurchasePayments
            messages.success(request, "Purchase deleted successfully!", extra_tags='success')
    except Exception as e:
        messages.error(request, f"Error deleting purchase: {str(e)}", extra_tags='danger')
    return redirect('viewAllPurchasesTable')
    # try:
    #
    #     item = get_object_or_404(PurchaseItem, id=item_id)
    #     purchase = item.purchase
    #     admin_regid = request.session.get('master_id')
    #     purchase_details = get_object_or_404(Purchase,id=purchase.id)
    #     if purchase_details.pending_amount == 0:
    #         messages.error(request, 'Product can not be deleted!',extra_tags='danger')
    #     else:
    #
    #         # Update grand total by subtracting the deleted item's total_amount_with_gst
    #         purchase_details.grand_total = (purchase_details.grand_total) - item.total_amount_with_gst
    #
    #         # Calculate new pending amount and potential credit
    #         if purchase_details.grand_total < (purchase_details.advance_amount):
    #             credit_amount = (purchase_details.advance_amount) - purchase_details.grand_total
    #             vendor_credit, created = VendorCredit.objects.get_or_create(
    #                 admin_registration_id_id=admin_regid,
    #                 vendor=purchase_details.vendor,
    #                 defaults={'credit_amount': credit_amount}
    #             )
    #             if not created:
    #                 vendor_credit.credit_amount += credit_amount
    #                 vendor_credit.save()
    #             purchase_details.pending_amount = 0
    #         else:
    #             purchase_details.pending_amount = purchase_details.grand_total - (purchase_details.advance_amount or 0)
    #
    #         purchase_details.save()
    #         item.delete()
    #         remaining_items = purchase.items.all()
    #         status = (purchase_details.pending_amount == 0)
    #         for remaining_item in remaining_items:
    #             remaining_item.purchase_item_status = status
    #             remaining_item.save()
    #
    #
    #
    #         # Check if the purchase has any remaining items
    #         if purchase.items.count() == 0:
    #
    #             # Delete the purchase
    #             purchase.delete()
    #             messages.success(request, "Purchase item and purchase  deleted successfully!",extra_tags='success')
    #         else:
    #             messages.success(request, "Purchase item deleted successfully!", extra_tags='success')
    #
    # except Exception as e:
    #     messages.error(request, f"Error deleting purchase item: {str(e)}", extra_tags='danger')
    #
    # return redirect('viewAllPurchasesTable')

@master_login_required
def editPurchase(request, invoice_id):
    admin_regid = request.session.get('master_id')
    invoice = get_object_or_404(PurchaseInvoice, id=invoice_id, admin_registration_id=admin_regid)
    payment_types = ProductPaymentType.objects.filter(admin_registration_id=admin_regid, payment_status=True)
    purchase_payments = PurchasePayments.objects.filter(invoice_ref=invoice)
    if request.method == 'POST':
        try:
            payment_type_id = request.POST.get('payment_type')
            installment_amount = Decimal(request.POST.get('installment_amount'))
            payment_type = get_object_or_404(ProductPaymentType, id=payment_type_id, admin_registration_id=admin_regid)

            # Validate installment amount
            if not installment_amount or float(installment_amount) <= 0:
                messages.error(request, "Installment amount must be greater than 0.", extra_tags='danger')
                return redirect('viewAllPurchasesTable')

            installment_amount = Decimal(request.POST.get('installment_amount'))
            if installment_amount > invoice.pending_amount:
                messages.error(request, "Installment amount cannot exceed pending amount.", extra_tags='danger')
                return redirect('viewAllPurchasesTable')

            # Prepare payment data
            payment_data = {
                'invoice_ref': invoice,
                'purchase_ref': invoice.purchase_ref,
                'vendor': invoice.vendor,
                'payment_type': payment_type,
                'advance_amount': installment_amount,
                'grand_total': invoice.grand_total,
                'pending_amount': invoice.pending_amount - installment_amount,
            }

            payment_type_str = payment_type.payment_type.lower().replace(' ', '_')
            if payment_type_str == 'cash':
                payment_data['cash_amount'] = float(request.POST.get('cash_amount')) if request.POST.get('cash_amount') else None
            elif payment_type_str == 'upi':
                payment_data['upi_id'] = request.POST.get('upi_id')
                payment_data['upi_transaction_id'] = request.POST.get('upi_transaction_id')
            elif payment_type_str == 'upi_cash':
                payment_data['upi_cash_amount'] = float(request.POST.get('upi_cash_amount')) if request.POST.get('upi_cash_amount') else None
                payment_data['upi_amount'] = float(request.POST.get('upi_amount')) if request.POST.get('upi_amount') else None
                payment_data['upi_cash_transaction_id'] = request.POST.get('upi_cash_transaction_id')
            elif payment_type_str == 'net_banking':
                payment_data['account_type'] = request.POST.get('account_type')
                payment_data['bank_name'] = request.POST.get('bank_name')
                payment_data['account_number'] = request.POST.get('account_number')
                payment_data['netbanking_transaction_id'] = request.POST.get('netbanking_transaction_id')
            elif payment_type_str == 'cheque':
                payment_data['cheque_number'] = request.POST.get('cheque_number')

            # Create new payment installment
            PurchasePayments.objects.create(**payment_data)

            # Update Purchase and PurchaseInvoice
            invoice.advance_amount = (invoice.advance_amount or Decimal('0')) + installment_amount
            invoice.pending_amount = invoice.pending_amount - installment_amount
            invoice.purchase_ref.advance_amount = invoice.advance_amount
            invoice.purchase_ref.pending_amount = invoice.pending_amount
            invoice.purchase_ref.purchase_status = invoice.pending_amount == Decimal('0')
            invoice.save()
            invoice.purchase_ref.save()



            # Update PurchaseItems status
            for item in invoice.purchase_ref.items.all():
                item.purchase_item_status = invoice.purchase_ref.purchase_status
                item.save()

            # Update VendorCredit if necessary
                # Update VendorCredit if necessary
                vendor_credit, created = VendorCredit.objects.get_or_create(
                    admin_registration_id_id=admin_regid,
                    vendor=invoice.vendor,
                    defaults={'credit_amount': Decimal('0')}
                )
                if invoice.pending_amount < Decimal('0'):
                    vendor_credit.credit_amount += abs(invoice.pending_amount)
                    vendor_credit.save()
                    invoice.pending_amount = Decimal('0')
                    invoice.purchase_ref.pending_amount = Decimal('0')
                    invoice.save()
                    invoice.purchase_ref.save()

            messages.success(request, "Payment installment added successfully.", extra_tags='success')
            return redirect('viewAllPurchasesTable')

        except Exception as e:
            messages.error(request, f"Error adding payment installment: {str(e)}", extra_tags='danger')
            return redirect('viewAllPurchasesTable')

    # context = {
    #     'invoice': invoice,
    #     'payment_types': payment_types,
    # }
    # return render(request, 'console_product_purchase_management/purchasecomponents/product_purchase_edit_form.html', context)

#Create render view ends here
@master_login_required
def get_vendor_details(request):
    vendor_id= request.GET.get('vendor_id')
    if vendor_id:
        try:
            vendor= CreateVendor.objects.get(id=vendor_id, vendor_status=True)
            vendor_credit, created = VendorCredit.objects.get_or_create(
                admin_registration_id_id=request.session.get('master_id'),
                vendor=vendor,
                defaults={'credit_amount': Decimal('0')}
            )
            if vendor.vendor_type_ref:
                vendor_type = vendor.vendor_type_ref.vendor_type
            else:
                vendor_type=''
            data = {
                'success': True,
                'vendor_name': vendor.vendor_name,
                'vendor_phone_number': vendor.vendor_phone_number,
                'vendor_email': vendor.vendor_email,
                'vendor_aadhaar': vendor.vendor_aadhaar,
                'vendor_company_url': vendor.vendor_company_url,
                'vendor_type': vendor_type,
                'credit_amount': str(vendor_credit.credit_amount)
            }
        except CreateVendor.DoesNotExist:
            data = {'success': False}
    else:
        data = {'success': False}
    return JsonResponse(data)





@master_login_required
def get_mrp(request, product_id):
    product = get_object_or_404(ProductCatalogue, id=product_id)
    return JsonResponse({'mrp': str(product.product_mrp)})

#converting invoice to Pdf
#
# def generate_invoice_pdf(request, invoice_id):
#     # Fetch your invoice object (adjust based on your model)
#     invoice = get_object_or_404(PurchaseInvoice, invoice_id=invoice_id)
#     admin_profile = invoice.admin_profile  # Adjust based on your models
#     admin_contact = invoice.admin_contact  # Adjust based on your models
#     totals = invoice.totals  # Adjust based on your totals calculation
#
#     # Render the HTML template
#     html_string = render_to_string('console_product_purchase_management/invoice_pdf_convert/purchase_invoice_convert_pdf.html', {
#         'invoice': invoice,
#         'admin_profile': admin_profile,
#         'admin_contact': admin_contact,
#         'totals': totals,
#         'request': request,  # Pass request for absolute_url filter
#     })
#
#     # Generate PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_id}.pdf"'
#
#     # Use WeasyPrint to convert HTML to PDF
#     HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
#
#     return response
#
@master_login_required
def generate_invoice_pdf(request, invoice_id):
    # Fetch the invoice object
    invoice = get_object_or_404(PurchaseInvoice, invoice_id=invoice_id,
                                admin_registration_id=request.session.get('master_id'))

    # Fetch admin profile and contact details
    admin_profile = Admin_Onetime_Profile.objects.filter(
        admin_registration_id=invoice.admin_registration_id
    ).first()
    admin_contact = AdminContactUs.objects.filter(
        admin_registration_id=invoice.admin_registration_id,
        admin_contactus_status=True
    ).first()

    # Calculate totals for CGST, SGST, Total Amount, and Total Amount with GST
    totals = invoice.purchase_ref.items.aggregate(
        total_quantity=Sum('quantity'),
        total_cgst=Sum('cgst'),
        total_sgst=Sum('sgst'),
        total_amount=Sum('total_amount'),
        total_amount_with_gst=Sum('total_amount_with_gst')
    )

    # Render the HTML template
    html_string = render_to_string(
        'console_product_purchase_management/invoice_pdf_convert/purchase_invoice_convert_pdf.html', {
            'invoice': invoice,
            'admin_profile': admin_profile,
            'admin_contact': admin_contact,
            'totals': totals,
            'request': request,  # Pass request for absolute_url filter
        })

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_id}.pdf"'

    # Use WeasyPrint to convert HTML to PDF
    HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)

    return response
#Purchase Management ends here

#Upi Details starts here

@master_login_required
def vendorUpi(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            upi_accountant = request.POST.get('upi_accountant')
            upi_name = request.POST.get('upi_name')
            upi_id = request.POST.get('upi_id')
            upi_phonenumber = request.POST.get('upi_phonenumber')
            upi_qr_image = request.FILES.get('upi_qr_image')

            if Upi.objects.filter(admin_registration_id=admin_regid, upi_id=upi_id).exists():
                messages.error(request, 'UPI ID already exists.', extra_tags='danger')
            else:
                Upi.objects.create(
                    admin_registration_id_id=admin_regid,
                    upi_accountant=upi_accountant,
                    upi_name=upi_name,
                    upi_id=upi_id,
                    upi_phonenumber=upi_phonenumber,
                    upi_qr_image=upi_qr_image
                )
                messages.error(request, 'UPI details created successfully.', extra_tags='success')
            return redirect('vendorUpi')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('vendorUpi')

    context = {
        'upi_records': Upi.objects.filter(admin_registration_id=admin_regid, upi_status=True)
    }
    return render(request, 'general_settings/financeandaccounts/upi_details/upi_details.html', context)

@master_login_required
def upiRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                upi_details = get_object_or_404(Upi, id=edit_id)
                context = {
                    's': upi_details,
                }
                return render(request, 'general_settings/financeandaccounts/upi_details/upi_components/upi_components_edit_form.html', context)

            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    (Q(upi_name__icontains=query) | Q(upi_id__icontains=query))
                )
            upi_details = Upi.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(upi_details, 10)
            page_obj = paginator.get_page(page_number)
            context = {
                'upi_records': page_obj
            }
            return render(request, 'general_settings/financeandaccounts/upi_details/upi_components/upi_components_list_data.html', context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f'Error occurred {str(e)}', extra_tags='danger')
        return redirect('vendorUpi')

@master_login_required
def upiStatusChange(request, pk):
    try:
        upi_details = get_object_or_404(Upi, id=pk)
        if request.headers.get('HX-Request'):
            upi_details.upi_status = not upi_details.upi_status
            upi_details.save()
            return render(request, 'general_settings/financeandaccounts/upi_details/upi_components/upi_components_status_change.html',{'upi': upi_details, 'status_page': 'upi_page'})
    except Exception as e:
        print(str(e), " Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('upiRenderData')

@master_login_required
def deleteUpi(request, pk):
    try:
        upi_delete = get_object_or_404(Upi, id=pk)
        upi_delete.delete()
        messages.error(request, "UPI details deleted successfully.", extra_tags='success')
        return redirect('vendorUpi')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('vendorUpi')

@master_login_required
def updateUpi(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        upi_details = get_object_or_404(Upi, id=pk)
        if request.method == 'POST':
            upi_accountant = request.POST.get('uupi_accountant')
            upi_name = request.POST.get('uupi_name')
            upi_id = request.POST.get('uupi_id')
            upi_phonenumber = request.POST.get('uupi_phonenumber')
            upi_qr_image = request.FILES.get('uupi_qr_image')

            if Upi.objects.exclude(id=pk).filter(admin_registration_id=admin_regid, upi_id=upi_id).exists():
                messages.error(request, 'UPI ID already exists.', extra_tags='danger')
            else:
                upi_details.upi_accountant = upi_accountant
                upi_details.upi_name = upi_name
                upi_details.upi_id = upi_id
                upi_details.upi_phonenumber = upi_phonenumber
                if upi_qr_image:
                    upi_details.upi_qr_image = upi_qr_image
                upi_details.save()
                messages.error(request, 'UPI details updated successfully.', extra_tags='success')
            return redirect('vendorUpi')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('vendorUpi')
#upi details ends here

#Account details starts here

@master_login_required
def accountDetail(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            account_type_id = request.POST.get('account_type')
            bank_name_id = request.POST.get('bank_name')
            bank_branch = request.POST.get('bank_branch')
            account_number = request.POST.get('account_number')
            ifsc_code = request.POST.get('ifsc_code')
            bank_holder = request.POST.get('bank_holder')

            account_type = AccountType.objects.get(admin_registration_id=admin_regid, id=account_type_id, account_type_status=True)
            bank_name = BankName.objects.get(admin_registration_id=admin_regid, id=bank_name_id, bank_status=True)

            if AccountDetail.objects.filter(admin_registration_id=admin_regid, account_number=account_number).exists():
                messages.error(request, 'Account number already exists.', extra_tags='danger')
            else:
                AccountDetail.objects.create(
                    admin_registration_id_id=admin_regid,
                    account_type_id=account_type,
                    bank_name_id=bank_name,
                    bank_branch=bank_branch,
                    account_number=account_number,
                    ifsc_code=ifsc_code,
                    bank_holder=bank_holder
                )
                messages.error(request, 'Account details created successfully.', extra_tags='success')
            return redirect('accountDetail')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('accountDetail')

    context = {
        'account_types': AccountType.objects.filter(admin_registration_id=admin_regid, account_type_status=True),
        'bank_names': BankName.objects.filter(admin_registration_id=admin_regid, bank_status=True),
    }
    return render(request, 'general_settings/financeandaccounts/account_details/account_details.html', context)

@master_login_required
def accountDetailRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                account_detail = get_object_or_404(AccountDetail, id=edit_id)
                context = {
                    's': account_detail,
                    'account_types': AccountType.objects.filter(admin_registration_id=admin_regid, account_type_status=True),
                    'bank_names': BankName.objects.filter(admin_registration_id=admin_regid, bank_status=True),
                }
                return render(request, 'general_settings/financeandaccounts/account_details/account_details_components/account_details_edit_form.html', context)

            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    (Q(bank_holder__icontains=query) | Q(account_number__icontains=query) | Q(account_type_id__account_type__icontains=query) | Q(bank_name_id__bank_name__icontains=query))
                )
            account_details = AccountDetail.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(account_details, 1)
            page_obj = paginator.get_page(page_number)
            context = {
                'account_detail_records': page_obj
            }
            return render(request, 'general_settings/financeandaccounts/account_details/account_details_components/account_details_list_data.html', context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f'Error occurred {str(e)}', extra_tags='danger')
        return redirect('accountDetail')

@master_login_required
def accountDetailStatusChange(request, pk):
    try:
        account_detail = get_object_or_404(AccountDetail, id=pk)
        if request.headers.get('HX-Request'):
            account_detail.account_status = not account_detail.account_status
            account_detail.save()
            return render(request, 'general_settings/financeandaccounts/account_details/account_details_components/account_details_status_change.html',{'account_detail': account_detail, 'status_page': 'account_detail_page'})
    except Exception as e:
        print(str(e), " Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('accountDetailRenderData')

@master_login_required
def deleteAccountDetail(request, pk):
    try:
        account_detail = get_object_or_404(AccountDetail, id=pk)
        account_detail.delete()
        messages.error(request, "Account details deleted successfully.", extra_tags='success')
        return redirect('accountDetail')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('accountDetail')

@master_login_required
def updateAccountDetail(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        account_detail = get_object_or_404(AccountDetail, id=pk)
        if request.method == 'POST':
            account_type_id = request.POST.get('uaccount_type')
            bank_name_id = request.POST.get('ubank_name')
            bank_branch = request.POST.get('ubank_branch')
            account_number = request.POST.get('uaccount_number')
            ifsc_code = request.POST.get('uifsc_code')
            bank_holder = request.POST.get('ubank_holder')

            account_type = get_object_or_404(AccountType, id=account_type_id)
            bank_name = get_object_or_404(BankName, id=bank_name_id)

            if AccountDetail.objects.exclude(id=pk).filter(admin_registration_id=admin_regid, account_number=account_number).exists():
                messages.error(request, 'Account number already exists.', extra_tags='danger')
            else:
                account_detail.account_type_id = account_type
                account_detail.bank_name_id = bank_name
                account_detail.bank_branch = bank_branch
                account_detail.account_number = account_number
                account_detail.ifsc_code = ifsc_code
                account_detail.bank_holder = bank_holder
                account_detail.save()
                messages.error(request, 'Account details updated successfully.', extra_tags='success')
            return redirect('accountDetail')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('accountDetail')
#account details ends here



#stock management starts here

def stockManagementListProducts(request):
    admin_regid = request.session.get('master_id')
    purchase_items = PurchaseItem.objects.filter(admin_registration_id__id=admin_regid)
    in_stock = 0
    out_of_stock = 0
    total_amount = 0
    total_including_gst = 0
    for purchase_item in purchase_items:
        if purchase_item.quantity > 0:
            in_stock += 1
            total_amount += purchase_item.total_amount
            total_including_gst += purchase_item.total_amount_with_gst
        else:
            out_of_stock += 1
    context={
        'in_stock':in_stock,
        'out_of_stock': out_of_stock,
        'total_amount': total_amount,
        'total_inc_gst': total_including_gst,
    }

    return render(request,'console_stock_management/console_stock_management_product_list.html',context)

def stockManagementRenderData(request):
    admin_regid = request.session.get('master_id')
    try:
        if request.headers.get('HX-Request'):
            purchase_item_id = request.GET.get('showid')
            print(purchase_item_id)
            if purchase_item_id:
                print(request.GET, request.headers)
                print(purchase_item_id)
                purchase_item_details = get_object_or_404(PurchaseItem,id=purchase_item_id,admin_registration_id__id=admin_regid)
                context={
                    'i': purchase_item_details
                }
                return render(request,'console_stock_management/console_inventory/console_inventory_form.html',context)


            query = request.GET.get('query')
            query_filter = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_filter &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(product__product_title__icontains=query)
                )

            purchase_items = PurchaseItem.objects.filter(query_filter).select_related('product').order_by('product__product_title','purchase_item_created_at')

            # Create a dictionary to group purchase items by product

            product_purchases = {}
            for item in purchase_items:
                product = item.product
                if product not in product_purchases:
                    product_purchases[product] = {'items': [], 'total_remaining': 0, 'total_quantity': 0}
                product_purchases[product]['items'].append(item)
                product_purchases[product]['total_remaining'] += item.remaining_quantity
                product_purchases[product]['total_quantity'] += item.quantity
            context = {
                'product_purchases': product_purchases,
            }

            return render(request,'console_stock_management/console_stock_management_components/console_stock_management_search_results.html',context)
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('stockManagementListProducts')

def stockManagementInventory(request,pk):
    admin_regid = request.session.get('master_id')
    purchase_item = get_object_or_404(PurchaseItem,id=pk,admin_registration_id=admin_regid)
    try:
        if request.method == 'POST':
            allocated_quantity = int(request.POST.get('allocated_quantity'))
            sale_price = float(request.POST.get('sale_price'))
            discount_percent = float(request.POST.get('discount_percent'))
            selling_price = float(request.POST.get('selling_price'))

            if allocated_quantity > purchase_item.remaining_quantity:
                messages.error(request,'Allocated quantity exceeds available quantity.',extra_tags='danger')
                return redirect('stockManagementListProducts')
            else:


                # Create inventory item
                InventoryItem.objects.create(
                    admin_registration_id=purchase_item.admin_registration_id,
                    purchase_item=purchase_item,
                    product=purchase_item.product,
                    allocated_quantity=allocated_quantity,
                    sale_price=sale_price,
                    discount_percent=discount_percent,
                    selling_price=selling_price
                )

                # Update purchase item quantity
                purchase_item.remaining_quantity -= allocated_quantity
                purchase_item.save()

                # Return a success message
                messages.error(request,'Successfully added to inventory',extra_tags='success')
                return redirect('stockManagementListProducts')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('stockManagementListProducts')

#stock management ends here

#order management starts here

def consoleOrderManagement(request):
    admin_id= request.session.get('master_id')
    total_orders=OrderItems.objects.filter(admin_registration__id=admin_id).count()
    print(total_orders)
    # total_orders = Order.objects.count()
    today = timezone.now().date()
    # new_orders = Order.objects.filter(order_status='new').count()
    new_orders = OrderItems.objects.filter(admin_registration__id=admin_id,order_item_status='new').count()

    # accepted_orders = Order.objects.filter(order_status='accept').count()
    accepted_orders = OrderItems.objects.filter(admin_registration__id=admin_id,order_item_status='accept').count()

    # rejected_orders = Order.objects.filter(order_status='reject').count()
    rejected_orders = OrderItems.objects.filter(admin_registration__id=admin_id,order_item_status='reject').count()

    # pending_orders = Order.objects.filter(order_status='pending').count()
    pending_orders = OrderItems.objects.filter(admin_registration=admin_id,order_item_status='pending').count()

    # today_orders = Order.objects.filter(created_at__date=today).count()
    today_orders = OrderItems.objects.filter(admin_registration=admin_id,order_item_created_at__date=today).count()

    yesterday = today - timedelta(days=1)
    yesterday_orders = OrderItems.objects.filter(admin_registration=admin_id,order_item_created_at__date=yesterday).count()
    last_week = today - timedelta(days=7)
    last_week_orders = OrderItems.objects.filter(admin_registration=admin_id,order_item_created_at__gte=last_week).count()

    my_orders = new_orders + accepted_orders
    print(my_orders)

    context={
        'total_orders': total_orders,
        'new_orders': new_orders,
        'accepted_orders': accepted_orders,
        'rejected_orders': rejected_orders,
        'pending_orders': pending_orders,
        'today_orders': today_orders,
        'yesterday_orders': yesterday_orders,
        'last_week_orders': last_week_orders,
        'my_orders': my_orders,
    }
    return render(request, 'console_order_management/console_order_management.html', context)

def myOrdersView(request):
    admin_regid = request.session.get('master_id')
    try:
        if request.headers.get('HX-Request'):


            return render(request, 'console_order_management/console_order_management_components/order_management_my orders.html')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('consoleOrderManagement')

def myOrderViewRenderData(request):
    admin_regid = request.session.get('master_id')
    try:
        if request.headers.get('HX-Request'):
            order_edit_id= request.GET.get('editid')
            if order_edit_id:
                order_details = get_object_or_404(OrderItems,id=order_edit_id)
                context = {
                    'orders':order_details
                }
                return render(request,'console_order_management/console_order_management_components/order_management_order_status_form.html',context)
            search_query = request.GET.get('search_query', '')
            text_query = request.GET.get('text_query', '')  # Text search from input
            # status_filter = request.GET.get('status', '')  # Status filter (accept, reject, pending)

            # orders = Order.objects.select_related('user').order_by('-created_at')
            # Filter orders for 'new' or 'accept' status
            # orders = Order.objects.select_related('user').filter(order_status__in=['new', 'accept']).order_by('-created_at')
            # Filter OrderItems for the specific admin and order status 'new' or 'accept'
            orders = OrderItems.objects.select_related('order_ref__user').filter(
                admin_registration_id=admin_regid,
                order_item_status__in=['new', 'accept']
            ).order_by('-order_ref__created_at')

            today = timezone.now().date()
            if search_query == 'today':
                orders = orders.filter(order_ref__created_at__date=today)
            elif search_query == 'yesterday':
                yesterday = today - timedelta(days=1)
                orders = orders.filter(order_ref__created_at__date=yesterday)
            elif search_query == 'last_week':
                last_week = today - timedelta(days=7)
                orders = orders.filter(order_ref__created_at__gte=last_week)

            # Apply text-based search filter
            if text_query:
                orders = orders.filter(
                    Q(order_item_reg_id__icontains=text_query) |
                    Q(order_ref__order_reg_id__icontains=text_query) |
                    Q(order_ref__user__username__icontains=text_query) |
                    Q(product_name__icontains=text_query)
                )

            # # Apply status filter
            # if status_filter == 'accepted':
            #     orders = orders.filter(order_status='accept')
            # elif status_filter == 'rejected':
            #     orders = orders.filter(order_status='reject')
            # elif status_filter == 'pending':
            #     orders = orders.filter(order_status='pending')
            page = request.GET.get('page')
            paginator = Paginator(orders, 10)  # 10 orders per page
            page_obj = paginator.get_page(page)

            context={
                'orders': page_obj,
                'page_obj': page_obj,
                'search_query': search_query,
                'text_query': text_query,
                # 'status_filter': status_filter
            }

            return render(request,'console_order_management/console_order_management_components/order_management_my_orders_partials/order_management_my_order_partial.html',context)

    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('myOrdersView')


def update_order_status(request, order_id):
    admin_regid = request.session.get('master_id')

    # Restrict to POST requests for updates
    if request.method != 'POST':
        messages.error(request, "Method not allowed", extra_tags='danger')
        return redirect('consoleOrderManagement')

    try:
        order = get_object_or_404(OrderItems, id=order_id)
        new_status = request.POST.get('order_status')
        rejection_reason = request.POST.get('rejection_reason', '')

        # Validate status
        if new_status not in ['new', 'accept', 'reject', 'pending']:
            messages.error(request, 'Please select a valid status.', extra_tags='danger')
            return redirect('consoleOrderManagement')

        # Validate rejection reason if status is 'reject'
        if new_status == 'reject' and not rejection_reason.strip():
            messages.error(request, 'Please enter a reason for the rejection.', extra_tags='danger')
            return redirect('consoleOrderManagement')

        # Update order
        order.order_item_status = new_status
        order.rejection_reason = rejection_reason if new_status == 'reject' else None
        order.save()
        # Create or update PackingStatus when order_status is 'accept'
        if new_status == 'accept':
            admin = get_object_or_404(Admin_registrations, id=admin_regid)
            PackingStatus.objects.get_or_create(
                admin_registration_id=admin,
                order_ref=order,
                defaults={'packing_status': 'yet_to_pack', 'packing_created_at': datetime.now()}
            )

        # Send email if order is rejected
        if new_status == 'reject':
            admin_details = get_object_or_404(Admin_Onetime_Profile, admin_registration_id_id=admin_regid)
            print("admin details are :",admin_details)
            subject = f"Order {order.order_item_reg_id} from {admin_details.admin_company_name} Cancelled"
            message = (
                f"Dear {order.order_ref.user.username},\n\n"
                f"Your order with Id  {order.order_item_reg_id} has been cancelled.Due to the below reason. \n\n"
                f"Product details : {order.product_name}\n\n"
                f"Reason: {rejection_reason}\n\n"
                f"Thank you,\n{admin_details.admin_company_name}"
            )
            recipient_email = order.order_ref.user.email
            send_email(recipient_email, subject, message)

        messages.success(request, 'Status updated successfully.', extra_tags='success')
        return redirect('consoleOrderManagement')

    except (Order.DoesNotExist, Admin_Onetime_Profile.DoesNotExist) as e:
        messages.error(request, f"Error updating order: {str(e)}", extra_tags='danger')
        return redirect('consoleOrderManagement')
    except Exception as e:
        print(str(e), "Error")  # Log for debugging
        messages.error(request, f"An unexpected error occurred: {str(e)}", extra_tags='danger')
        return redirect('consoleOrderManagement')
    # admin_regid = request.session.get('master_id')
    # try:
    #     if request.headers.get('HX-Request'):
    #         order = get_object_or_404(Order, id=order_id)
    #         new_status = request.POST.get('order_status')
    #         rejection_reason = request.POST.get('rejection_reason', '')
    #         if new_status not in ['new', 'accept', 'reject', 'pending']:
    #             messages.error(request,'Please select valid status.',extra_tags='danger')
    #             return redirect('consoleOrderManagement')
    #         if new_status == 'reject' and not rejection_reason.strip():
    #             messages.error(request,'Please enter a reason for the rejection.',extra_tags='danger')
    #
    #         order.order_status = new_status
    #         if new_status == 'reject':
    #             order.rejection_reason = rejection_reason
    #         else:
    #             order.rejection_reason = None  # Clear rejection reason for non-reject statuses
    #         order.save()
    #
    #         # Send email if order is cancelled
    #         admin_details = get_object_or_404(Admin_Onetime_Profile,id=admin_regid)
    #         if new_status == 'reject':
    #             subject = f"Order {order.order_reg_id} Cancelled"
    #             message = f"Dear {order.user.username},\n\nYour order {order.order_reg_id} has been cancelled.\nReason: {rejection_reason}\n\nThank you,\n{admin_details.admin_company_name}"
    #
    #             recipient_list = [order.user.email]
    #             send_email(recipient_list, subject, message)
    #
    #         messages.error(request, 'Status updated successfully.',extra_tags='success')
    #
    #         return redirect('consoleOrderManagement')
    # except Exception as e:
    #     print(str(e), "Error")
    #     messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
    #     return redirect('consoleOrderManagement')

def pendingOrdersView(request):
    try:
        if request.headers.get('HX-Request'):


            return render(request, 'console_order_management/console_order_management_pending_orders/console_order_management_pending_orders.html')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('consoleOrderManagement')

def pendingOrdersRenderData(request):
    try:
        if request.headers.get('HX-Request'):
            order_edit_id= request.GET.get('editid')
            if order_edit_id:
                order_details = get_object_or_404(OrderItems,id=order_edit_id)
                context = {
                    'orders':order_details
                }
                return render(request,'console_order_management/console_order_management_components/order_management_order_status_form.html',context)
            # search_query = request.GET.get('search_query', '')
            # text_query = request.GET.get('text_query', '')  # Text search from input
            # status_filter = request.GET.get('status', '')  # Status filter (accept, reject, pending)

            # Filter orders for 'pending' status
            # Filter OrderItems for 'pending' status
            orders = OrderItems.objects.select_related('order_ref__user').filter(
                order_item_status='pending'
            ).order_by('-order_ref__created_at')

            # today = timezone.now().date()
            # if search_query == 'today':
            #     orders = orders.filter(created_at__date=today)
            # elif search_query == 'yesterday':
            #     yesterday = today - timedelta(days=1)
            #     orders = orders.filter(created_at__date=yesterday)
            # elif search_query == 'last_week':
            #     last_week = today - timedelta(days=7)
            #     orders = orders.filter(created_at__gte=last_week)
            #
            # # Apply text-based search filter
            # if text_query:
            #     orders = orders.filter(
            #         Q(order_reg_id__icontains=text_query) |
            #         Q(user__username__icontains=text_query) |
            #         Q(order_items__icontains=text_query)
            #     )

            # # Apply status filter
            # if status_filter == 'accepted':
            #     orders = orders.filter(order_status='accept')
            # elif status_filter == 'rejected':
            #     orders = orders.filter(order_status='reject')
            # elif status_filter == 'pending':
            #     orders = orders.filter(order_status='pending')
            page = request.GET.get('page')
            paginator = Paginator(orders, 10)  # 10 orders per page
            page_obj = paginator.get_page(page)

            context={
                'orders': page_obj,
                'page_obj': page_obj,
                # 'search_query': search_query,
                # 'text_query': text_query,
                # 'status_filter': status_filter
            }

            return render(request,'console_order_management/console_order_management_pending_orders/console_order_management_pending_orders_components/order_management_pending_orders_partial.html',context)

    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('pendingOrdersView')


#cancel Orders

def cancelOrdersView(request):
    try:
        if request.headers.get('HX-Request'):


            return render(request, 'console_order_management/console_order_management_cancel_orders/console_order_management_cancel_orders.html')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('consoleOrderManagement')

def cancelOrdersRenderData(request):
    try:
        if request.headers.get('HX-Request'):
            order_edit_id= request.GET.get('editid')
            if order_edit_id:
                order_details = get_object_or_404(OrderItems,id=order_edit_id)
                context = {
                    'orders':order_details
                }
                return render(request,'console_order_management/console_order_management_components/order_management_order_status_form.html',context)
            # search_query = request.GET.get('search_query', '')
            # text_query = request.GET.get('text_query', '')  # Text search from input
            # status_filter = request.GET.get('status', '')  # Status filter (accept, reject, pending)

            # orders = Order.objects.select_related('user').filter(order_status='reject').order_by('-created_at')
            # Filter OrderItems for 'reject' status
            orders = OrderItems.objects.select_related('order_ref__user').filter(
                order_item_status='reject'
            ).order_by('-order_ref__created_at')
            # today = timezone.now().date()
            # if search_query == 'today':
            #     orders = orders.filter(created_at__date=today)
            # elif search_query == 'yesterday':
            #     yesterday = today - timedelta(days=1)
            #     orders = orders.filter(created_at__date=yesterday)
            # elif search_query == 'last_week':
            #     last_week = today - timedelta(days=7)
            #     orders = orders.filter(created_at__gte=last_week)
            #
            # # Apply text-based search filter
            # if text_query:
            #     orders = orders.filter(
            #         Q(order_reg_id__icontains=text_query) |
            #         Q(user__username__icontains=text_query) |
            #         Q(order_items__icontains=text_query)
            #     )

            # # Apply status filter
            # if status_filter == 'accepted':
            #     orders = orders.filter(order_status='accept')
            # elif status_filter == 'rejected':
            #     orders = orders.filter(order_status='reject')
            # elif status_filter == 'pending':
            #     orders = orders.filter(order_status='pending')
            page = request.GET.get('page')
            paginator = Paginator(orders, 10)  # 10 orders per page
            page_obj = paginator.get_page(page)

            context={
                'orders': page_obj,
                'page_obj': page_obj,
                # 'search_query': search_query,
                # 'text_query': text_query,
                # 'status_filter': status_filter
            }

            return render(request,'console_order_management/console_order_management_cancel_orders/console_order_management_cancel_orders_partials/console_order_management_cancel_orders_partial.html',context)

    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('cancelOrdersView')

def view_order_details(request, order_id):
    try:
        order = get_object_or_404(OrderItems, id=order_id)
        # Parse order_items and related fields (assuming comma-separated strings)
        # items = order.order_items.split(", ") if order.order_items else []
        # prices = order.order_price.split(", ") if order.order_price else []
        # selling_prices = order.quantity_mul_price.split(", ") if order.quantity_mul_price else []
        # quantities = order.order_quantity.split(", ") if order.order_quantity else []
        # subtotals = order.order_subtotal.split(", ") if order.order_subtotal else []
        # discounts = order.order_discount.split(", ") if order.order_discount else []

        # Combine items into a list of dictionaries
        # order_items = [
        #     {
        #         'product': items[i] if i < len(items) else "N/A",
        #         'price': prices[i] if i < len(prices) else "N/A",
        #         'selling_price': selling_prices[i] if i < len(selling_prices) else "N/A",
        #         'quantity': quantities[i] if i < len(quantities) else "N/A",
        #         'subtotal': subtotals[i] if i < len(subtotals) else "N/A",
        #         'discount': discounts[i] if i < len(discounts) else "N/A",
        #         'total': (
        #             float(quantities[i]) * float(selling_prices[i]) - float(discounts[i])
        #             if i < len(quantities) and i < len(selling_prices) and discounts[i] != "N/A"
        #                and quantities[i] != "N/A" and selling_prices[i] != "N/A"
        #             else "N/A"
        #         )
        #     } for i in
        #     range(max(len(items), len(prices), len(selling_prices), len(quantities), len(subtotals), len(discounts)))
        # ]




        context = {
            'order': order,
            # 'order_items': order_items
        }
        return render(request, 'console_order_management/console_order_managment_order_details/order_management_show_order_details.html', context)
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('consoleOrderManagement')

#Order management ends here


#packing management starts here

def packingManagementView(request):
    try:
        admin_regid = request.session.get('master_id')
        packed_orders = PackingStatus.objects.filter(
            admin_registration_id=admin_regid,
            packing_status='packed',
            order_ref__order_item_status='accept'
        ).count()
        yet_to_pack_orders = PackingStatus.objects.filter(
            admin_registration_id=admin_regid,
            packing_status='yet_to_pack',
            order_ref__order_item_status='accept'
        ).count()
        total_orders = packed_orders + yet_to_pack_orders
        packed_percentage = (packed_orders / total_orders * 100) if total_orders > 0 else 0

        context = {
            'packed_orders': packed_orders,
            'yet_to_pack_orders': yet_to_pack_orders,
            'packed_percentage': round(packed_percentage, 1),
            'total_orders': total_orders,
        }
        return render(request, 'console_packing_management/console_packing_management.html', context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('packingManagementView')


def packingManagementPackedView(request):
    try:
        if request.headers.get('HX-Request'):


            return render(request, 'console_packing_management/console_packing_management_packed/packing_managment_packed.html')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('packingManagementView')


@master_login_required
def packingManagementPackedRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id = request.GET.get('editid')
            if edit_id:
                order = get_object_or_404(OrderItems, id=edit_id)
                transport_types = TransportType.objects.all()
                context = {
                    'o': order,
                    'transport_types': transport_types
                }
                return render(request, 'console_packing_management/transport_details/transport_details_form.html', context)



            text_query = request.GET.get('query', '')


            packing_orders = PackingStatus.objects.filter(
                admin_registration_id=admin_regid,
                packing_status='packed',
                order_ref__order_item_status='accept'
            ).order_by('-order_ref__order_item_created_at')
            if text_query:
                packing_orders = packing_orders.filter(
                    Q(order_ref__order_item_reg_id__icontains=text_query)
                )

            page = request.GET.get('page')
            paginator = Paginator(packing_orders, 10)  # 10 orders per page
            page_obj = paginator.get_page(page)

            context = {
                'orders': page_obj,
                'page_obj': page_obj,
                # 'transport_details': TransportDetails.objects.filter(order_ref__id=edit_id),
                'text_query': text_query,
            }
            return render(request, 'console_packing_management/console_packing_management_packed/packing_management_packed_partials/packing_management_packed_partials.html', context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('packingManagementPackedView')


def packingManagementYetToPackView(request):
    try:
        if request.headers.get('HX-Request'):


            return render(request, 'console_packing_management/console_packing_managment_yettopack/packing_management_yet_to_pack.html')
    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('packingManagementView')


def packingManagementYettopackRenderData(request):
    try:
        if request.headers.get('HX-Request'):
            admin_regid = request.session.get('master_id')
            packing_status_edit_id = request.GET.get('editid')
            if packing_status_edit_id:
                packing_status_details = get_object_or_404(PackingStatus, id=packing_status_edit_id)
                context = {
                    'packing_status': packing_status_details
                }
                return render(request,'console_packing_management/console_status_update_form/packing_management_status_update_form.html',context)

            text_query = request.GET.get('query', '')
            packing_orders = PackingStatus.objects.filter(
                admin_registration_id=admin_regid,
                packing_status='yet_to_pack',
                order_ref__order_item_status='accept'
            ).order_by('-order_ref__order_item_created_at')

            if text_query:
                packing_orders = packing_orders.filter(
                    Q(order_ref__order_item_reg_id__icontains=text_query)
                )
            page = request.GET.get('page')
            paginator = Paginator(packing_orders, 10)  # 10 orders per page
            page_obj = paginator.get_page(page)

            context = {
                'orders': page_obj,
                'page_obj': page_obj,
                'text_query': text_query,
            }
            return render(request,
                          'console_packing_management/console_packing_managment_yettopack/packing_management_yettopack_partials/packing_management_yettopack_partials.html',
                          context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('packingManagementYetToPackView')


    # try:
    #     if request.headers.get('HX-Request'):
    #
    #         # orders = Order.objects.select_related('user').filter(order_status='accept').order_by('-created_at')
    #         packing_orders = PackingStatus.objects.filter(order_ref__order_status='accept').order_by('-order_ref__created_at')
    #         page = request.GET.get('page')
    #         paginator = Paginator(packing_orders, 10)  # 10 orders per page
    #         page_obj = paginator.get_page(page)
    #
    #         context={
    #             'orders':page_obj,
    #             'page_obj':page_obj,
    #         }
    #         return render(request,'console_packing_management/console_packing_managment_yettopack/packing_management_yettopack_partials/packing_management_yettopack_partials.html',context)
    #
    # except Exception as e:
    #     print(str(e), "Error")
    #     messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
    #     return redirect('packingManagementYetToPackView')


@master_login_required
def packingManagementStatusChange(request, packing_status_id):
    try:
        if request.method == 'POST':
            packing_status = get_object_or_404(PackingStatus, id=packing_status_id)
            new_status = request.POST.get('packing_status')
            if new_status not in ['packed', 'yet_to_pack']:
                messages.error(request, 'Invalid packing status.', extra_tags='danger')
                return redirect('packingManagementView')
            packing_status.packing_status = new_status
            packing_status.save()
            messages.success(request, 'Packing status updated successfully.', extra_tags='success')
            return redirect('packingManagementView')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('packingManagementView')


@master_login_required
def packingOrderDetails(request, order_id):
    try:
        if request.headers.get('HX-Request'):
            order = get_object_or_404(OrderItems, id=order_id)
            context = {
                'order': order
            }
            return render(request, 'console_packing_management/console_packing_managenement_order_details/console_packing_management_order_details.html', context)
    except Exception as e:
        print(f"Error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('packingManagementView')

@master_login_required
def packingOrderDetailsPDF(request, order_id):
    admin_regno = request.session.get('master_id')
    try:
        order = get_object_or_404(OrderItems, id=order_id)
        context = {
            'order': order,
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'admin': Admin_Onetime_Profile.objects.filter(admin_registration_id=admin_regno).first()
        }
        html_string = render_to_string('console_packing_management/packing_management_order_details_pdf/packing_management_order_details_pdf.html', context)
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order.order_item_reg_id}_details.pdf"'
        response.write(pdf_file)
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        messages.error(request, f"An error occurred while generating PDF: {str(e)}", extra_tags='danger')
        return redirect('packingManagementView')


@master_login_required
def viewTransportDetails(request, order_id):
    try:
        order = get_object_or_404(OrderItems, id=order_id)
        transport_detail = TransportDetails.objects.filter(order_ref=order).first()
        context = {
            'transport_detail': transport_detail
        }
        return render(request, 'console_packing_management/transport_details/transport_details_show.html', context)
    except Exception as e:
        print(f"Error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('packingManagementView')


def transportDetailsForm(request, order_id):
    try:

        if request.method == 'POST':
            order = get_object_or_404(OrderItems, id=order_id)
            transport_type_id = request.POST.get('transport_type')
            delivery_date = request.POST.get('delivery_date')

            transport_type = get_object_or_404(TransportType, id=transport_type_id)
            if TransportDetails.objects.filter(order_ref = order).exists():
                messages.error(request,'Transportation already selected.',extra_tags='danger')
            else:

                TransportDetails.objects.create(
                    order_ref=order,
                    transport_type=transport_type,
                    delivery_date=delivery_date,
                )

                messages.success(request, 'Transport details added successfully.', extra_tags='success')
            # if request.headers.get('HX-Request'):
            #     admin_regid = request.session.get('master_id')
            #     packing_orders = PackingStatus.objects.filter(
            #         admin_registration_id=admin_regid,
            #         packing_status='packed',
            #         order_ref__order_status='accept'
            #     ).order_by('-order_ref__created_at')
            #     paginator = Paginator(packing_orders, 10)
            #     page = request.GET.get('page', 1)
            #     page_obj = paginator.get_page(page)
            #     context = {
            #         'orders': page_obj,
            #         'page_obj': page_obj,
            #         'text_query': '',
            #     }
            #     return render(request, 'console_packing_management/console_packing_management_packed/packing_management_packed_partials/packing_management_packed_partials.html', context)
            return redirect('packingManagementView')
        # else:  # GET request
        #     order = get_object_or_404(Order, id=order_id)
        #     transport_types = TransportType.objects.all()
        #     context = {
        #         'o': order,
        #         'transport_types': transport_types
        #     }
        #     return render(request, 'console_packing_management/transport_details/transport_details_form.html', context)
    except Exception as e:
        print(f"Error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('packingManagementView')



# def transportDetailsForm(request,order_id):
#     try:
#         # if request.headers.get('HX-Request'):
#         if request.method == 'POST':
#         #     order_id = request.GET.get('order_id')
#         #     order = get_object_or_404(Order, id=order_id)
#         #     transport_types = TransportType.objects.all()
#         #     context = {
#         #         'order': order,
#         #         'transport_types': transport_types
#         #     }
#         #     return render(request, 'console_packing_management/transport_details/transport_details_form.html', context)
#         # elif request.method == 'POST':
#             order_id = request.POST.get('order_id')
#             transport_type_id = request.POST.get('transport_type')
#             delivery_date = request.POST.get('delivery_date')
#
#
#             order = get_object_or_404(Order, id=order_id)
#             transport_type = get_object_or_404(TransportType, id=transport_type_id)
#
#             TransportDetails.objects.create(
#                 order_ref=order,
#                 transport_type=transport_type,
#                 delivery_date=delivery_date,
#             )
#
#             messages.success(request, 'Transport details added successfully.', extra_tags='success')
#             # admin_regid = request.session.get('master_id')
#             # packing_orders = PackingStatus.objects.filter(
#             #     admin_registration_id=admin_regid,
#             #     packing_status='packed',
#             #     order_ref__order_status='accept'
#             # ).order_by('-order_ref__created_at')
#             # paginator = Paginator(packing_orders, 10)
#             # page = request.GET.get('page', 1)
#             # page_obj = paginator.get_page(page)
#
#             # context = {
#             #     'orders': page_obj,
#             #     'page_obj': page_obj,
#             #     'text_query': '',
#             # }
#             return redirect('packingManagementPackedView')
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
#         return redirect('packingManagementPackedView')

# Packing management ends here

# finance and accounts starts here

def financeAndAccountsShow(request):
    return render(request, 'finance_and_accounts/finance_and_accounts_main_page.html')


#accepted orders in finance and accounts
def acceptedOrderViewRenderData(request):
    admin_regid = request.session.get('master_id')
    try:
        if request.headers.get('HX-Request'):
            order_edit_id= request.GET.get('editid')
            if order_edit_id:
                order_details = get_object_or_404(Order,id=order_edit_id)
                context = {
                    'orders':order_details
                }
                return render(request,'console_order_management/console_order_management_components/order_management_order_status_form.html',context)
            search_query = request.GET.get('search_query', '')
            text_query = request.GET.get('text_query', '')  # Text search from input
            # status_filter = request.GET.get('status', '')  # Status filter (accept, reject, pending)

            # orders = Order.objects.select_related('user').order_by('-created_at')
            # Filter orders for 'new' or 'accept' status
            orders = Order.objects.select_related('user').filter(order_status__in=['accept']).order_by('-created_at')

            today = timezone.now().date()
            if search_query == 'today':
                orders = orders.filter(created_at__date=today)
            elif search_query == 'yesterday':
                yesterday = today - timedelta(days=1)
                orders = orders.filter(created_at__date=yesterday)
            elif search_query == 'last_week':
                last_week = today - timedelta(days=7)
                orders = orders.filter(created_at__gte=last_week)

            # Apply text-based search filter
            if text_query:
                orders = orders.filter(
                    Q(order_reg_id__icontains=text_query) |
                    Q(user__username__icontains=text_query) |
                    Q(order_items__icontains=text_query)
                )

            # # Apply status filter
            # if status_filter == 'accepted':
            #     orders = orders.filter(order_status='accept')
            # elif status_filter == 'rejected':
            #     orders = orders.filter(order_status='reject')
            # elif status_filter == 'pending':
            #     orders = orders.filter(order_status='pending')
            page = request.GET.get('page')
            paginator = Paginator(orders, 10)  # 10 orders per page
            page_obj = paginator.get_page(page)

            context={
                'orders': page_obj,
                'page_obj': page_obj,
                'search_query': search_query,
                'text_query': text_query,
                # 'status_filter': status_filter
            }

            return render(request,'console/templates/finance_and_accounts/finance_accounts_order_table/accepted_orders.html',context)

    except Exception as e:
        print(str(e), "Error")
        messages.error(request, f"An error occurred {str(e)}", extra_tags='danger')
        return redirect('myOrdersView')



# profit and lose
def profitAndLose(request):
    return render(request, 'finance_and_accounts/profit_and_lose/profit_and_lose.html')

def reports(request):
    return render(request, 'finance_and_accounts/reports/reports.html')


def expenses(request):
    return render(request, 'finance_and_accounts/expenses/expenses.html')


def refund(request):
    return render(request, 'finance_and_accounts/refund/refund.html')
#finance and accounts ends here

# banner views starts here


@master_login_required
def banner(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            title = request.POST.get('title')
            banner_picture = request.FILES.get('banner_picture')
            if Banner.objects.filter(admin_registration_id=admin_regid, title=title).exists():
                messages.error(request, 'Banner title already exists.', extra_tags='danger')
            else:
                Banner.objects.create(
                    admin_registration_id_id=admin_regid,
                    title=title,
                    banner_picture=banner_picture,
                    status=True,
                    created_at=datetime.now()
                )
                messages.error(request, "Banner created successfully.", extra_tags='success')
            return redirect('banner')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('banner')

    return render(request, 'general_settings/site_management/banners/banners.html')

@master_login_required
def bannerRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id_variable = request.GET.get('editid')
            if edit_id_variable:
                banner_details = Banner.objects.get(id=edit_id_variable)
                context = {
                    'b': banner_details,
                }
                return render(request, 'general_settings/site_management/banners/banners_components/banners_components_form_edit.html', context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(title__icontains=query)
                )
            banner_records = Banner.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(banner_records, 10)
            page_obj = paginator.get_page(page_number)
            context = {
                'banner_records': page_obj
            }
            return render(request, 'general_settings/site_management/banners/banners_components/banners_components_list_data.html', context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"Error occurred: {str(e)}", extra_tags='danger')
        return redirect('banner')

@master_login_required
def bannerStatusChange(request, pk):
    try:
        banner_details = get_object_or_404(Banner, id=pk)
        if request.headers.get('HX-Request'):
            banner_details.status = not banner_details.status
            banner_details.save()
            return render(request, "general_settings/site_management/banners/banners_components/banners_components_status_change.html", {"banner": banner_details, "status_page": "banner_page"})
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('bannerRenderData')

@master_login_required
def deleteBanner(request, pk):
    try:
        banner_delete = get_object_or_404(Banner, id=pk)
        banner_delete.delete()
        messages.error(request, "Banner deleted successfully.", extra_tags="success")
        return redirect('banner')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('banner')

@master_login_required
def updateBanner(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        banner_details = get_object_or_404(Banner, id=pk)
        if request.method == "POST":
            title = request.POST.get('utitle')
            banner_picture = request.FILES.get('ubanner_picture')
            if Banner.objects.exclude(id=pk).filter(title=title).exists():
                messages.error(request, 'Banner title already exists.', extra_tags='danger')
            else:
                banner_details.admin_registration_id_id = admin_regid
                banner_details.title = title
                if banner_picture:
                    banner_details.banner_picture = banner_picture
                banner_details.save()
                messages.error(request, "Banner updated successfully.", extra_tags='success')
            return redirect('banner')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('banner')
# banner views ends here

# Services views starts here


@master_login_required
def services(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.method == 'POST':
            service_title = request.POST.get('service_title')
            content = request.POST.get('content')
            image = request.FILES.get('image')
            if Services.objects.filter(admin_registration_id=admin_regid, service_title=service_title).exists():
                messages.error(request, 'Service title already exists.', extra_tags='danger')
            else:
                Services.objects.create(
                    admin_registration_id_id=admin_regid,
                    service_title=service_title,
                    content=content,
                    image=image,
                    status=True,
                    created_at=datetime.now()
                )
                messages.success(request, "Service created successfully.", extra_tags='success')
            return redirect('services')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('services')

    return render(request, 'general_settings/site_management/services/services.html')

@master_login_required
def servicesRenderData(request):
    try:
        admin_regid = request.session.get('master_id')
        if request.headers.get('HX-Request'):
            edit_id_variable = request.GET.get('editid')
            if edit_id_variable:
                service_details = Services.objects.get(id=edit_id_variable)
                context = {
                    's': service_details,
                }
                return render(request, 'general_settings/site_management/services/services_components/services_components_edit_form.html', context)
            query = request.GET.get('query')
            query_name = Q(admin_registration_id__id__icontains=admin_regid)
            if query:
                query_name &= Q(
                    Q(admin_registration_id__id__icontains=admin_regid) &
                    Q(service_title__icontains=query)
                )
            service_records = Services.objects.filter(query_name).order_by('-id')
            page_number = request.GET.get('page')
            paginator = Paginator(service_records, 10)
            page_obj = paginator.get_page(page_number)
            context = {
                'service_records': page_obj
            }
            return render(request, 'general_settings/site_management/services/services_components/services_components_list_data.html', context)
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"Error occurred: {str(e)}", extra_tags='danger')
        return redirect('services')

@master_login_required
def servicesStatusChange(request, pk):
    try:
        service_details = get_object_or_404(Services, id=pk)
        if request.headers.get('HX-Request'):
            service_details.status = not service_details.status
            service_details.save()
            return render(request, "general_settings/site_management/services/services_components/services_components_status_change.html", {"service": service_details, "status_page": "services_page"})
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('servicesRenderData')

@master_login_required
def deleteServices(request, pk):
    try:
        service_delete = get_object_or_404(Services, id=pk)
        service_delete.delete()
        messages.success(request, "Service deleted successfully.", extra_tags="success")
        return redirect('services')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('services')

@master_login_required
def updateServices(request, pk):
    try:
        admin_regid = request.session.get('master_id')
        service_details = get_object_or_404(Services, id=pk)
        if request.method == "POST":
            service_title = request.POST.get('uservice_title')
            content = request.POST.get('ucontent')
            image = request.FILES.get('uimage')
            if Services.objects.exclude(id=pk).filter(service_title=service_title).exists():
                messages.error(request, 'Service title already exists.', extra_tags='danger')
            else:
                service_details.admin_registration_id_id = admin_regid
                service_details.service_title = service_title
                service_details.content = content
                if image:
                    service_details.image = image
                service_details.save()
                messages.success(request, "Service updated successfully.", extra_tags='success')
            return redirect('services')
    except Exception as e:
        print(f"error: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}", extra_tags='danger')
        return redirect('services')
# Services views ends here