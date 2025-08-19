from django import forms
from .models import *
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget


class MainClassForm(forms.ModelForm):

    class Meta:
        model = MainClass
        fields = ["name","description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )


class SubClassForm(forms.ModelForm):
    start_date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))
    end_date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker4",'class': 'form-control' }))

    class Meta:
        model = SubClass
        fields = ["main_class","name","start_date","teacher","capacity","room","schedule","time","books","fees","subjects","end_date"]

        widgets = {
            'teacher': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '2'}),
            'books': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '2'}),
            'subjects': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["main_class"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["start_date"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["teacher"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["capacity"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["room"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["schedule"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["time"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["fees"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )