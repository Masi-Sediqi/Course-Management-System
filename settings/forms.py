# forms.py
from django import forms

class BackupForm(forms.Form):
    MODULE_CHOICES = [
        ('accounts', 'اکانت‌ها'),
        ('classes', 'کلاس‌ها'),
        ('suppliers', 'تامین‌کنندگان'),
        ('library', 'کتابخانه'),
        ('finance', 'عواید و مصارف'),
        ('students', 'دانش‌آموزان'),
        ('teachers', 'معلمان'),
    ]
    
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'توضیحات (اختیاری)'
        })
    )
    
    modules = forms.MultipleChoiceField(
        choices=MODULE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'module-check'}),
        initial=[choice[0] for choice in MODULE_CHOICES],
        required=True
    )