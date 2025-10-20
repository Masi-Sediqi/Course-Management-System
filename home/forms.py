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