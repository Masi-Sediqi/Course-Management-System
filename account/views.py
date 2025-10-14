from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from .forms import *
from django.contrib import messages
from .models import Employee
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.template.loader import render_to_string
# say to user this is your account ? or no
from django.contrib.auth import update_session_auth_hash
from django.core.mail import EmailMessage
from django.contrib.auth.models import User, Group, Permission
from .models import Employee
import jdatetime
# Create your views here.


def account_register(request):
   # if request.user.is_authenticated:
        #    return redirect('/')
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
    url = request.META.get('HTTP_REFERER')
    user = get_object_or_404(Employee, id=id)

    if request.method == 'POST':
        form = UserPermissionAssignForm(request.POST)
        if form.is_valid():
            permissions = form.cleaned_data['permissions']
            user.user_permissions.set(permissions)
            messages.success(request, 'برای یوزر موفقانه صلاحیت داده شد.')
            return redirect(url)
    else:
        form = UserPermissionAssignForm()
        # Set initial selected permissions for this user
        form.fields['permissions'].initial = user.user_permissions.all()

    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'account/users/assign_perm copy.html', context)