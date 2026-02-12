from .models import *
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ["first_name","father_name","phone","gender","image"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update(
        {"class": "form-control ", "placeholder": ""}
        )
        self.fields["father_name"].widget.attrs.update(
        {"class": "form-control ", "placeholder": ""}
        )
        self.fields["phone"].widget.attrs.update(
        {"class": "form-control ", "placeholder": "در صورت نداشتن فیلد حالی گذاشته شود"}
        )
        self.fields["gender"].widget.attrs.update(
        {"class": "form-control ", "placeholder": ""}
        )
        self.fields["image"].widget.attrs.update(
        {"class": "form-control ", "placeholder": ""}
        )


class Student_fess_infoForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker3",'class': 'form-control' }))
    end_date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker4",'class': 'form-control' }))

    class Meta:
        model = Student_fess_info
        fields = ["description","date","end_date"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )


class StudentImporvmentForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker21",'class': 'form-control' }))

    class Meta:
        model = StudentImporvment
        fields = ["date","description","file","after_class","number"]
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
        self.fields["after_class"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["number"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class BuyBookForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker21",'class': 'form-control' }))

    class Meta:
        model = BuyBook
        fields = ["date","description"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class StudentPaidRemainAmountForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker21",'class': 'form-control' }))

    class Meta:
        model = StudentPaidRemainAmount
        fields = ["date","description","paid"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["paid"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )