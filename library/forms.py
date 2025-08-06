from django import forms
from .models import *
from django import forms
from jalali_date.widgets import AdminJalaliDateWidget

class StationeryCategoryForm(forms.ModelForm):
    class Meta:
        model = StationeryCategory
        fields = ["name"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class StationeryItemForm(forms.ModelForm):

    class Meta:
        model = StationeryItem
        fields = ["name","category","price","description"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["category"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class BooksForm(forms.ModelForm):

    class Meta:
        model = Books
        fields = ["name","price","description"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
