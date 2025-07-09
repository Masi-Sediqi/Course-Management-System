from django.contrib import admin
from django.urls import path
from account import views
from django.contrib.auth import views as auth_views
from .forms import (UserLoginForm, PwdResetForm, PwdResetConfirmForm)
from django.contrib.auth.views import LogoutView 
from django.contrib.auth import views as auth_views
from .forms import (UserLoginForm, PwdResetForm, PwdResetConfirmForm)
from django.views.generic import TemplateView


app_name ='account'

urlpatterns = [

    # path('', views.dashboard, name='dashboard'),  
    path('signup/', views.account_register, name='account_register'),
    path('login/', auth_views.LoginView.as_view(template_name='Home/login.html',
                                                form_class=UserLoginForm), name='login'),
    # path('logout/', LogoutView.as_view(next_page='/account/login/'),name='logout'),
    path('logout/', LogoutView.as_view(next_page='/account/login/'),name='logout'),


    # path('logout/', auth_views.LogoutView.as_view(next_page='/Account/login/'), name='logout'),
        # Reset password  login_required(auth_views.LogoutView.as_view())
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="account/user/password_reset_form.html",
                                                                 success_url='password_reset_email_confirm',
                                                                 email_template_name='account/user/password_reset_email.html',
                                                                 form_class=PwdResetForm), name='pwdreset'),
    path('password_reset_confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='account/user/password_reset_confirm.html',
                                                                                                success_url='/account/password_reset_complete/', 
                                                                                                form_class=PwdResetConfirmForm),name="password_reset_confirm"),

    path('password_reset/password_reset_email_confirm', TemplateView.as_view(template_name="account/user/reset_status.html"), name='password_reset_done'),
    path('password_reset_complete/', TemplateView.as_view(template_name="account/user/reset_status.html"), name='password_reset_complete'),
    path('dashboard/password/change/', views.change_password, name='change_password'),
]
