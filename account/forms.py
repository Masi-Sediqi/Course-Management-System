from django import forms
from.models import *
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm, SetPasswordForm)







class UserLoginForm(AuthenticationForm):

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '', 'id': 'login-username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': '',
            'name':'password',
            'id': 'password',
        }
    ))


class RegistrationForm(forms.ModelForm):
    name = forms.CharField(label='User Name', min_length=2, max_length=50, help_text='*')
    email = forms.EmailField(max_length=100, help_text="*", error_messages={'required': 'Sorry, Email address is required!'})
    password = forms.CharField(label='Password', help_text="*", widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': '',
            'name':'password',
            'id':'id_password',
            
        }))
    password2 = forms.CharField(label='Confirm Password', help_text="*",  widget=forms.PasswordInput
                (attrs={
            'class': 'form-control',
            'placeholder': '',
            'name':'password',
            'id':'sign_up_id_password',
        }))
                                        

    class Meta:
        model = Employee
        fields = ('name', 'email')
    

    """ def clean_user_name(self):
        user_name = self.cleaned_data['user_name'].lower()
        r = Customer.objects.filter(user_name=user_name)
        if r.count():
            raise forms.ValidationError("Username already exists")
        return user_name """


    def clean_password2(self):
        
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Password dosen't match.")
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if Employee.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Please use another Email address, Email address already exist.')
        return email

        
        """ adding style to sign up form """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': '', 'name': 'email', 'id': 'id_email'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
    



class UserEditForm(forms.ModelForm):

    email = forms.EmailField(
        label='Account email (can not be changed)', max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'email', 'id': 'form-email', 'readonly': 'readonly'}))

    name = forms.CharField(
        label='User Name', min_length=4, max_length=50, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': '', 'id': 'form-lastname'}))


    class Meta:
        model = Employee
        fields = ('email', 'name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True




class PwdResetForm(PasswordResetForm):

    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-control mb-3', 'placeholder': '', 'id': 'form-email'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        u = Employee.objects.filter(email=email)
        if not u:
            raise forms.ValidationError(
                "Unfortunatley Email address dosen't exist!")
        return email

class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-newpass'}))
    new_password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-new-pass2'}))


class ChangeEmployeePasswordForm(forms.Form):
    new_password = forms.CharField(
        label='رمز جدید',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_new_password',
            'placeholder': 'رمز جدید',
        })
    )

    confirm_password = forms.CharField(
        label='تکرار رمز',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_confirm_password',
            'placeholder': 'تکرار رمز',
        })
    )
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        password2 = cleaned_data.get("confirm_password")

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
class UserPermissionAssignForm(forms.Form):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'id': 'permissions-select'}),
        required=False,
    )