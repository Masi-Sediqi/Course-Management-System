from django.db import models
import uuid
from django.contrib.auth.models import *
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
# from administration.models import branches
# Create your models here.

# builten custom account manager from django project
class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, name, password, **other_fields)

    def create_user(self, email, name, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, name=name,
                          **other_fields)
        user.set_password(password)
        user.save()
        return user



# Customer model that get the information of the users
class Employee(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    is_employee = models.BooleanField(default=False)
    is_agree_policy = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    date_in_persian = models.CharField(max_length=150)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = "Accounts"
        verbose_name_plural = "Accounts"

    # Fix clashes by adding related_name
    groups = models.ManyToManyField(
        Group,
        related_name='employee_groups',
        blank=True,
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups'),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='employee_permissions',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )

    objects = CustomAccountManager()
    
    def __str__(self):
        return self.name

class Licsanse_check(models.Model):
    password = models.CharField(max_length=1200)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)