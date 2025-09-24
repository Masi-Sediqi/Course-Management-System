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
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker7",'class': 'form-control' }))

    class Meta:
        model = StationeryItem
        fields = ["name","category","stationery_price","description","number_of_stationery","stationery_paid_price","per_price_stationery","per_price_for_buy","date"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["category"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["stationery_price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["stationery_paid_price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["number_of_stationery"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["per_price_stationery"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["per_price_for_buy"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class BuyStationeryAgainForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker7",'class': 'form-control' }))

    class Meta:
        model = BuyStationeryAgain
        fields = ["stationery_price","description","number_of_stationery","stationery_paid_price","per_price_stationery","per_price_for_buy","date"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["stationery_price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["stationery_paid_price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["number_of_stationery"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["per_price_stationery"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["per_price_for_buy"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )


class BooksForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker6",'class': 'form-control' }))

    class Meta:
        model = Books
        fields = ["name","price","description","number_of_book","paid_price","per_price","per_book_price_for_buy","date"]

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
        self.fields["number_of_book"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["paid_price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["per_price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["per_book_price_for_buy"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )

class BuyBookAgainForm(forms.ModelForm):
    date = forms.CharField(label='تاریخ',widget=AdminJalaliDateWidget(attrs={"placeholder": "0/0/0000", "id": "datepicker6",'class': 'form-control' }))

    class Meta:
        model = BuyBookAgain
        fields = ["price","description","number_of_book","paid_price","per_price","per_book_price_for_buy","date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["description"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["number_of_book"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["paid_price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["per_price"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )
        self.fields["per_book_price_for_buy"].widget.attrs.update(
        {"class": "form-control", "placeholder": ""}
        )