from django import forms
from .models import *
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget


class TeacherForm(forms.ModelForm):
    birth_date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))

    class Meta:
        model = Teacher
        fields = ["name","last_name","subject","phone","birth_date","file","description","subject","percentage","gender"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["last_name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["subject"].widget.attrs.update(
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
        self.fields["subject"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["percentage"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["gender"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )