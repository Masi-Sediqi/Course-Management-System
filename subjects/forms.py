from django import forms
from .models import *
from jalali_date.widgets import AdminJalaliDateWidget


class SubjectsForm(forms.ModelForm):

    class Meta:
        model = Subjects
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )