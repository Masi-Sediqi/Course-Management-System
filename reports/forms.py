# forms.py
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget


class StudentFilterForm(forms.Form):
    start_date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker20",'class': 'form-control' }))

    end_date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker21",'class': 'form-control' }))