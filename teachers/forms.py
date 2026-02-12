from django import forms
from .models import *
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget


class TeacherForm(forms.ModelForm):

    class Meta:
        model = Teacher
        fields = ["name","phone","image","description","gender","percentage"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["phone"].widget.attrs.update(
        {"class": "form-control", "placeholder": "در صورت نداشتن فیلد حالی گذاشته شود"}
        )
        self.fields["image"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["gender"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["percentage"].widget.attrs.update(
        {"class": "form-control", "placeholder": "فیصدی"}
        )


class TeacherPaidSalaryForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))
    loan_amount = forms.FloatField(
    label='قرض قابل کسر',
    required=False,
    widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'loan_amount', 'placeholder': '0'})
)

    class Meta:
        model = TeacherPaidSalary
        fields = ["amount","date","description","paid_salary","loan_amount"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["paid_salary"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["loan_amount"].widget.attrs.update({"class": "form-control", "placeholder": "0"})


class TeacherLoanForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker12",'class': 'form-control' }))

    class Meta:
        model = TeacherLoan
        fields = ["amount","date","description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )


class AttendanceAndLeavesForm(forms.ModelForm):
    # Custom Jalali date widget for start_date
    start_date = forms.CharField(
        label='تاریخ شروع',
        widget=AdminJalaliDateWidget(
            attrs={"placeholder": "0/0/0000","id": "datepicker9","class": "form-control"
            }
        )
    )

    class Meta:
        model = AttendanceAndLeaves
        fields = [
            "start_date",
            "number_of_day",
            "description",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['number_of_day'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'تعداد روز های رخصتی'}
        )
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'توضیحات'}
        )