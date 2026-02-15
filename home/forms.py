from django import forms
from .models import *
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget


class suppliersForm(forms.ModelForm):

    class Meta:
        model = suppliers
        fields = ["name","description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class JDateForm(forms.Form):
    date = forms.CharField(
        label='تاریخ',
        widget=AdminJalaliDateWidget(attrs={
            "placeholder": "0/0/0000", 
            "id": "datepicker3",
            'class': 'form-control'
        }),
        required=True
    )

class JDateForm1(forms.Form):
    date = forms.CharField(
        label='تاریخ',
        widget=AdminJalaliDateWidget(attrs={
            "placeholder": "0/0/0000", 
            "id": "datepicker4",
            'class': 'form-control'
        }),
        required=True
    )



class DateFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'placeholder': '۱۴۰۴/۰۱/۰۱',
            'autocomplete': 'off'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'placeholder': '۱۴۰۴/۱۲/۲۹',
            'autocomplete': 'off'
        })
    )