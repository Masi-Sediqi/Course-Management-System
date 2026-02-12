from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import *
from management.models import *
from management.forms import *
from django.contrib import messages
from .models import Employee
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User, Group, Permission
from .models import Employee
import jdatetime
from home.models import *


def account_register(request):
    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.is_agree_policy = True
            user.is_active = False
            user.save()
            login(request, user)
            return redirect('home:dashboard')   
    else:
        registerForm = RegistrationForm()
    return render(request, 'home/auth/sign_up.html', {'form':registerForm})


@login_required
def delete_user(request):
    user = Employee.objects.get(name=request.user)
    user.is_active = False
    user.save()
    logout(request)
    return redirect('Account:delete_confirmation')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(reverse("account:dashboard"))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'Account/user/dashboard/edit_password.html', {
        'form': form
    })


def accounts(request):
    today = jdatetime.date.today()
    today_persian_date = today.strftime("%d/%m/%Y")
    
    referer = request.META.get('HTTP_REFERER',)
    accounts = Employee.objects.all()
    count_accounts = Employee.objects.all().count()
    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.date_in_persian = today_persian_date
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.is_agree_policy = True
            user.is_active = False
            user.save()
            return redirect(referer)
        else:
            messages.error(request, 'لطفا ایمیل و رمز خود را چک نموده دوباره تلاش نمایید')
            return redirect(referer)
    else:
        registerForm = RegistrationForm()
    context = {
        'accounts':accounts,
        'count_accounts':count_accounts,
        'registerForm':registerForm,
    }
    return render(request, 'accounts/users/accounts.html',context)

def delete_account(request , id):
    url = request.META.get('HTTP_REFERER')  # get last URL
    delete_id =get_object_or_404(Employee, id=id)
    delete_id.delete()
    messages.success(request, 'استفاده کننده موفقانه حذف شد')
    return redirect(url)

def activate_employee(request, employee_id):
    url = request.META.get('HTTP_REFERER')  
    if request.method == "GET":
        employee = get_object_or_404(Employee, id=employee_id)
        employee.is_active = True
        employee.is_staff = True
        employee.is_employee = True
        employee.save()
        messages.success(request, "استفاده کننده موفقانه فعال گردید.")
    return redirect(url)  

def diactivate_employee(request, employee_id):
    url = request.META.get('HTTP_REFERER')  # get last URL
    if request.method == "GET":
        employee = get_object_or_404(Employee, id=employee_id)
        employee.is_active = False
        employee.is_staff = False
        employee.is_employee = False
        employee.save()
        messages.success(request, "استفاده کننده موفقانه غیر فعال گردید.")
    return redirect(url)  

def edit_accounts(request,id):
    food_instance = Employee.objects.get(id=id)

    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=food_instance)
        
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات استفاده کننده موفقانه تغییرات شد")
            return redirect('account:accounts')
       
    else:
        form = RegistrationForm(instance=food_instance)
    context = {
        'form':form,
        'food_instance':food_instance,     
    }
    return render(request, "account/users/edit_accounts.html",context)

def change_account_password(request,id):
    employee = get_object_or_404(Employee, id=id)
    if request.method == 'POST':
        form = ChangeEmployeePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['new_password']
            employee.set_password(password) 
            employee.save()
            messages.success(request, 'پسورد موفقانه چنج شد')
            return redirect('account:login')
    else:
        form = ChangeEmployeePasswordForm()

    return render(request, 'account/users/change_employee_password.html', {'form': form, 'employee': employee})

@login_required
def assign_permission_for_user(request, id):
    user = get_object_or_404(Employee, id=id)
    url = request.META.get('HTTP_REFERER', '/')
    
    # Get existing permission or create new with all fields set to False
    permission, created = SystemPermission.objects.get_or_create(
        account=user
    )
    
    if request.method == 'POST':
        form = SystemPermissionForm(request.POST, instance=permission)
        if form.is_valid():
            form.save()
            
            # Count granted permissions
            granted_count = 0
            for field in SystemPermission._meta.get_fields():
                if field.name not in ['id', 'account', 'created_at']:
                    if getattr(permission, field.name):
                        granted_count += 1
            
            SystemLog.objects.create(
                section="کاربران",
                action="تخصیص دسترسی",
                description=f"دسترسی‌های کاربر {user.name} به‌روزرسانی شد. ({granted_count} دسترسی فعال)",
                user=request.user
            )
            
            messages.success(request, 'دسترسی‌ها با موفقیت ذخیره شدند.')
            return redirect(url)
        else:
            messages.error(request, 'خطا در ذخیره‌سازی دسترسی‌ها.')
    else:
        form = SystemPermissionForm(instance=permission)
    
    # Calculate permission statistics for all fields
    total_permissions = 0
    granted_permissions = 0
    
    for field in SystemPermission._meta.get_fields():
        if field.name not in ['id', 'account', 'created_at']:
            total_permissions += 1
            if getattr(permission, field.name):
                granted_permissions += 1
    
    context = {
        'form': form,
        'user': user,
        'permission': permission,
        'granted_permissions': granted_permissions,
        'total_permissions': total_permissions,
        'created': created,
    }
    return render(request, 'account/users/assign_permission.html', context)

def account_more_info(request, id):
    account = Employee.objects.get(id=id)
    context = {
        'account':account
    }
    return render(request, 'account/users/user-info.html', context)