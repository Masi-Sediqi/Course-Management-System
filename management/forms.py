from django import forms
from .models import *
from jalali_date.widgets import AdminJalaliDateWidget
from .models import SystemPermission

class FinanceRecordForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "تاریخ", "id": "datepicker3",'class': 'form-control' }))

    class Meta:
        model = FinanceRecord
        fields = ["amount","description","date","type","title"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["amount"].widget.attrs.update(
        {"class": "form-control", "placeholder": "100"}
        )
        self.fields["type"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["title"].widget.attrs.update(
        {"class": "form-control", "placeholder": "خرید نان"}
        )

class SystemPermissionForm(forms.ModelForm):
    class Meta:
        model = SystemPermission
        exclude = ['account', 'created_at']
        widgets = {
            field: forms.CheckboxInput(attrs={'class': 'form-check-input permission-checkbox'})
            for field in [
                # Students
                'add_student', 'view_student', 'edit_student', 'delete_student', 'active_deactive_student',
                'add_registeration_student', 'view_registration_student', 'edit_registration_student', 'delete_registration_student',
                'add_buybook_student', 'view_buybook_student', 'edit_buybook_student', 'delete_buybook_student',
                'add_improving_student', 'view_improving_student', 'edit_improving_student', 'delete_improving_student',
                'add_paid_remain_student', 'view_paid_remain_student', 'edit_paid_remain_student', 'delete_paid_remain_student',
                
                # Teachers
                'add_teacher', 'view_teacher', 'edit_teacher', 'delete_teacher', 'active_deactive_teacher',
                'add_paid_salary_teacher', 'view_paid_salary_teacher', 'edit_paid_salary_teacher', 'delete_paid_salary_teacher',
                'add_loan_teacher', 'view_loan_teacher', 'edit_loan_teacher', 'delete_loan_teacher',
                'add_attendance_teacher', 'view_attendance_teacher', 'edit_attendance_teacher', 'delete_attendance_teacher',
                
                # Suppliers
                'add_supplier', 'view_supplier', 'edit_supplier', 'delete_supplier',
                'add_balance_supplier', 'paid_money_supplier',
                
                # Library
                'add_book', 'view_book', 'edit_book', 'delete_book', 'purchase_book',
                
                # Classes
                'add_class', 'view_class', 'edit_class', 'delete_class',
                
                # Income Expenses
                'add_income_expenses', 'view_income_expenses', 'edit_income_expenses', 'delete_income_expenses',
                'collect_income', 'collect_expenses',
                
                # Reports
                'student_report', 'teachers_report', 'income_expenses_report', 'library_report', 'supplier_report',
                
                # Settings & History
                'setting', 'history'
            ]
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set Persian labels for all fields
        labels = {
            # Students
            'add_student': 'افزودن دانش‌آموز',
            'view_student': 'مشاهده دانش‌آموزان',
            'edit_student': 'ویرایش دانش‌آموز',
            'delete_student': 'حذف دانش‌آموز',
            'active_deactive_student': 'فعال/غیرفعال کردن دانش‌آموز',
            'add_registeration_student': 'افزودن ثبت‌نام',
            'view_registration_student': 'مشاهده ثبت‌نام‌ها',
            'edit_registration_student': 'ویرایش ثبت‌نام',
            'delete_registration_student': 'حذف ثبت‌نام',
            'add_buybook_student': 'افزودن خرید کتاب',
            'view_buybook_student': 'مشاهده خرید کتاب',
            'edit_buybook_student': 'ویرایش خرید کتاب',
            'delete_buybook_student': 'حذف خرید کتاب',
            'add_improving_student': 'افزودن ارتقاء',
            'view_improving_student': 'مشاهده ارتقاء',
            'edit_improving_student': 'ویرایش ارتقاء',
            'delete_improving_student': 'حذف ارتقاء',
            'add_paid_remain_student': 'افزودن پرداخت باقی‌مانده',
            'view_paid_remain_student': 'مشاهده پرداخت‌های باقی‌مانده',
            'edit_paid_remain_student': 'ویرایش پرداخت باقی‌مانده',
            'delete_paid_remain_student': 'حذف پرداخت باقی‌مانده',
            
            # Teachers
            'add_teacher': 'افزودن استاد',
            'view_teacher': 'مشاهده اساتید',
            'edit_teacher': 'ویرایش استاد',
            'delete_teacher': 'حذف استاد',
            'active_deactive_teacher': 'فعال/غیرفعال کردن استاد',
            'add_paid_salary_teacher': 'افزودن پرداخت حقوق',
            'view_paid_salary_teacher': 'مشاهده پرداخت حقوق',
            'edit_paid_salary_teacher': 'ویرایش پرداخت حقوق',
            'delete_paid_salary_teacher': 'حذف پرداخت حقوق',
            'add_loan_teacher': 'افزودن قرض',
            'view_loan_teacher': 'مشاهده قرض‌ها',
            'edit_loan_teacher': 'ویرایش قرض',
            'delete_loan_teacher': 'حذف قرض',
            'add_attendance_teacher': 'افزودن حضور و غیاب',
            'view_attendance_teacher': 'مشاهده حضور و غیاب',
            'edit_attendance_teacher': 'ویرایش حضور و غیاب',
            'delete_attendance_teacher': 'حذف حضور و غیاب',
            
            # Suppliers
            'add_supplier': 'افزودن تامین‌کننده',
            'view_supplier': 'مشاهده تامین‌کنندگان',
            'edit_supplier': 'ویرایش تامین‌کننده',
            'delete_supplier': 'حذف تامین‌کننده',
            'add_balance_supplier': 'افزودن بیلانس',
            'paid_money_supplier': 'پرداخت به تامین‌کننده',
            
            # Library
            'add_book': 'افزودن کتاب',
            'view_book': 'مشاهده کتاب‌ها',
            'edit_book': 'ویرایش کتاب',
            'delete_book': 'حذف کتاب',
            'purchase_book': 'خرید کتاب',
            
            # Classes
            'add_class': 'افزودن کلاس',
            'view_class': 'مشاهده کلاس‌ها',
            'edit_class': 'ویرایش کلاس',
            'delete_class': 'حذف کلاس',
            
            # Income Expenses
            'add_income_expenses': 'افزودن درآمد/هزینه',
            'view_income_expenses': 'مشاهده درآمد/هزینه',
            'edit_income_expenses': 'ویرایش درآمد/هزینه',
            'delete_income_expenses': 'حذف درآمد/هزینه',
            'collect_income': 'وصول درآمد',
            'collect_expenses': 'پرداخت هزینه',
            
            # Reports
            'student_report': 'گزارش دانش‌آموزان',
            'teachers_report': 'گزارش اساتید',
            'income_expenses_report': 'گزارش درآمد/هزینه',
            'library_report': 'گزارش کتابخانه',
            'supplier_report': 'گزارش تامین‌کنندگان',
            
            # Settings & History
            'setting': 'تنظیمات سیستم',
            'history': 'تاریخچه سیستم',
        }
        
        for field, label in labels.items():
            if field in self.fields:
                self.fields[field].label = label
                self.fields[field].required = False