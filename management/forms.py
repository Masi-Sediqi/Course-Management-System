from django import forms
from .models import *
from jalali_date.widgets import AdminJalaliDateWidget


class FinanceRecordForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))

    class Meta:
        model = FinanceRecord
        fields = ["amount","description","date","type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["amount"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["type"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )