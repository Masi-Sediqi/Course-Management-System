from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegistrationForm, UserEditForm
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

