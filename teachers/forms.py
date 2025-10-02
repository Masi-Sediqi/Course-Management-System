from django import forms
from .models import *
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget


class TeacherForm(forms.ModelForm):
    # birth_date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))

    class Meta:
        model = Teacher
        fields = ["name","last_name","phone","file","description","percentage","gender"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["last_name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

        self.fields["phone"].widget.attrs.update(
        {"class": "form-control", "placeholder": "در صورت نداشتن فیلد حالی گذاشته شود"}
        )
        self.fields["file"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

        self.fields["percentage"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["gender"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class TeacherPaidSalaryForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))

    class Meta:
        model = TeacherPaidSalary
        fields = ["amount","date","description","amount_of_fees_bell","paid_salary"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["amount_of_fees_bell"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["paid_salary"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class TeacherPaidRemainMoneyForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker12",'class': 'form-control' }))

    class Meta:
        model = TeacherPaidRemainMoney
        fields = ["amount","date","description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

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

        



