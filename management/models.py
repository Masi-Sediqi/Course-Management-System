from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from account.models import *
# Create your models here.

class TotalBalance(models.Model):
    total_income = models.FloatField(default=0)
    total_expenses = models.FloatField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.total_income < 0:
            self.total_income = 0
        if self.total_expenses < 0:
            self.total_expenses = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Income: {self.total_income} | Expenses: {self.total_expenses}"

class FinanceRecord(models.Model):
    TYPE_CHOICES = (
        ('income', 'عاید'),
        ('expense', 'مصرف'),
    )

    date = models.CharField(max_length=14)
    title = models.CharField(max_length=100, blank=True)
    amount = models.FloatField()
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    # Optional generic relation
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    related_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.type.upper()} - {self.amount}"
    
    def is_external(self):
        """Check if this record came from another source (has content_type)"""
        return self.content_type is not None
    
    def is_editable(self):
        """Check if the record can be edited (only if not from external source)"""
        return not self.is_external()
    
    def is_deletable(self):
        """Check if the record can be deleted (only if not from external source)"""
        return not self.is_external()

    
class SystemPermission(models.Model):
    account = models.ForeignKey(Employee, on_delete=models.CASCADE)

    # Students Secions
    add_student = models.BooleanField(default=False, blank=True)
    view_student = models.BooleanField(default=False, blank=True)
    edit_student = models.BooleanField(default=False, blank=True)
    delete_student = models.BooleanField(default=False, blank=True)
    active_deactive_student = models.BooleanField(default=False, blank=True)
    add_registeration_student = models.BooleanField(default=False, blank=True)
    view_registration_student = models.BooleanField(default=False, blank=True)
    delete_registration_student = models.BooleanField(default=False, blank=True)
    edit_registration_student = models.BooleanField(default=False, blank=True)
    add_buybook_student = models.BooleanField(default=False, blank=True)
    view_buybook_student = models.BooleanField(default=False, blank=True)
    edit_buybook_student = models.BooleanField(default=False, blank=True)
    delete_buybook_student = models.BooleanField(default=False, blank=True)
    add_improving_student = models.BooleanField(default=False, blank=True)
    view_improving_student = models.BooleanField(default=False, blank=True)
    edit_improving_student = models.BooleanField(default=False, blank=True)
    delete_improving_student = models.BooleanField(default=False, blank=True)
    add_paid_remain_student = models.BooleanField(default=False, blank=True)
    view_paid_remain_student = models.BooleanField(default=False, blank=True)
    edit_paid_remain_student = models.BooleanField(default=False, blank=True)
    delete_paid_remain_student = models.BooleanField(default=False, blank=True)

    # Teachers
    add_teacher = models.BooleanField(default=False, blank=True)
    view_teacher = models.BooleanField(default=False, blank=True)
    edit_teacher = models.BooleanField(default=False, blank=True)
    delete_teacher = models.BooleanField(default=False, blank=True)
    active_deactive_teacher = models.BooleanField(default=False, blank=True)
    add_paid_salary_teacher = models.BooleanField(default=False, blank=True)
    view_paid_salary_teacher = models.BooleanField(default=False, blank=True)
    edit_paid_salary_teacher = models.BooleanField(default=False, blank=True)
    delete_paid_salary_teacher = models.BooleanField(default=False, blank=True)
    add_loan_teacher = models.BooleanField(default=False, blank=True)
    view_loan_teacher = models.BooleanField(default=False, blank=True)
    edit_loan_teacher = models.BooleanField(default=False, blank=True)
    delete_loan_teacher = models.BooleanField(default=False, blank=True)
    add_attendance_teacher = models.BooleanField(default=False, blank=True)
    view_attendance_teacher = models.BooleanField(default=False, blank=True)
    edit_attendance_teacher = models.BooleanField(default=False, blank=True)
    delete_attendance_teacher = models.BooleanField(default=False, blank=True)

    # Suppliers 
    add_supplier = models.BooleanField(default=False, blank=True)
    view_supplier = models.BooleanField(default=False, blank=True)
    edit_supplier = models.BooleanField(default=False, blank=True)
    delete_supplier = models.BooleanField(default=False, blank=True)
    add_balance_supplier = models.BooleanField(default=False, blank=True)
    paid_money_supplier = models.BooleanField(default=False, blank=True)

    # Library
    add_book = models.BooleanField(default=False, blank=True)
    view_book = models.BooleanField(default=False, blank=True)
    edit_book = models.BooleanField(default=False, blank=True)
    delete_book = models.BooleanField(default=False, blank=True)
    purchase_book = models.BooleanField(default=False, blank=True)

    # Classes 
    add_class = models.BooleanField(default=False, blank=True)
    view_class = models.BooleanField(default=False, blank=True)
    edit_class = models.BooleanField(default=False, blank=True)
    delete_class = models.BooleanField(default=False, blank=True)

    # Income Expenses 
    add_income_expenses = models.BooleanField(default=False, blank=True)
    view_income_expenses = models.BooleanField(default=False, blank=True)
    edit_income_expenses = models.BooleanField(default=False, blank=True)
    delete_income_expenses = models.BooleanField(default=False, blank=True)
    collect_income = models.BooleanField(default=False, blank=True)
    collect_expenses = models.BooleanField(default=False, blank=True)

    # Reports 
    student_report = models.BooleanField(default=False, blank=True)
    teachers_report = models.BooleanField(default=False, blank=True)
    income_expenses_report = models.BooleanField(default=False, blank=True)
    library_report = models.BooleanField(default=False, blank=True)
    supplier_report = models.BooleanField(default=False, blank=True)

    # Settings
    setting = models.BooleanField(default=False, blank=True)

    # History
    history = models.BooleanField(default=False, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)