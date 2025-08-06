from django import forms
from .models import *
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget


class StudentForm(forms.ModelForm):
    date_of_registration = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))

    class Meta:
        model = Student
        fields = ["first_name","last_name","father_name","phone","date_of_registration","gender","orginal_fees","time","subject","teacher","books"]

        # In forms.py
        widgets = {
            'books': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["last_name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["father_name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["phone"].widget.attrs.update(
        {"class": "form-control", "placeholder": "در صورت نداشتن فیلد حالی گذاشته شود"}
        )
        self.fields["gender"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["orginal_fees"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["time"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["subject"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["teacher"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )


class Student_fess_infoForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))

    class Meta:
        model = Student_fess_info
        fields = ["orginal_fees","give_fees","description","date"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["orginal_fees"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["give_fees"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )


class StudentGiveRemainMoneyForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker21",'class': 'form-control' }))

    class Meta:
        model = StudentGiveRemainMoney
        fields = ["amount","description","date"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class StudentImporvmentForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker21",'class': 'form-control' }))

    class Meta:
        model = StudentImporvment
        fields = ["date","description","file","change_book","past_book"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["file"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["change_book"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["past_book"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )