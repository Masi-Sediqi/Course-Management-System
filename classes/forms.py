from django import forms
from .models import *
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget



class SubClassForm(forms.ModelForm):
    start_date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))

    class Meta:
        model = SubClass
        fields = ["name","start_date","capacity","room","schedule","time","fees"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": "صنف الجبر"}
        )
        self.fields["start_date"].widget.attrs.update(
        {"class": "form-control", "placeholder": "تاریخ شروع"}
        )
        self.fields["capacity"].widget.attrs.update(
        {"class": "form-control", "placeholder": "ظرفیت صنف"}
        )
        self.fields["room"].widget.attrs.update(
        {"class": "form-control", "placeholder": "صنف B-101"}
        )
        self.fields["schedule"].widget.attrs.update(
        {"class": "form-control", "placeholder": "توضیحات "}
        )
        self.fields["time"].widget.attrs.update(
        {"class": "form-control", "placeholder": "از 1 الی 3 بعد از ظهر"}
        )
        self.fields["fees"].widget.attrs.update(
        {"class": "form-control", "placeholder": "500 افغانی"}
        )