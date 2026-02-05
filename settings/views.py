from django.shortcuts import render, redirect
from students.models import *
from teachers.models import *
from library.models import *
from classes.models import *
from management.models import *
from django.contrib import messages
from .models import *
from account.models import *
from django.utils import timezone
# Create your views here.

def settings(request):

    setting_instance = Setting.objects.first()  # Get the single existing record (if any)

    if request.method == "POST":
        title = request.POST.get("title")
        logo = request.FILES.get("logo")

        if setting_instance:
            # ✅ Update only provided fields
            if title:
                setting_instance.title = title
            if logo:
                setting_instance.logo = logo
            setting_instance.save()
        else:
            # ✅ Create a new record if none exists
            if title or logo:  # Only create if at least one field is provided
                Setting.objects.create(
                    title=title if title else "",
                    logo=logo if logo else None
                )

        return redirect('settings:settings')  # Refresh after save

    return render(request, 'settings/setting-main.html', {
        'setting': setting_instance
    })


def delete_database(request):

    delete_all_student = Student.objects.all().delete()
    delete_all_teacher = Teacher.objects.all().delete()
    delete_all_book = Books.objects.all().delete()
    delete_all_category = StationeryCategory.objects.all().delete()
    delete_all_stationery = StationeryItem.objects.all().delete()
    delete_all_mainclasses = MainClass.objects.all().delete()
    delete_all_classes = SubClass.objects.all().delete()
    delete_all_income = TotalIncome.objects.all().delete()
    delete_all_expense = TotalExpenses.objects.all().delete()
    delete_all_other_income = OtherIncome.objects.all().delete()
    delete_all_other_expense = Expenses.objects.all().delete()
    messages.success(request, 'تمام معلومات دیتابیس موفقانه حذف گردید')
    return redirect('settings:settings')