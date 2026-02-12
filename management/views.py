from django.shortcuts import render, redirect, get_object_or_404
from management.forms import *
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
# Create your views here.

def Total_income(request):
    referer = request.META.get('HTTP_REFERER', '/')

    if request.method == "POST":
        form = FinanceRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.save()

            messages.success(request, "ریکارد با موفقیت ثبت شد.")
            return redirect(referer)
    else:
        form = FinanceRecordForm()

    all_records = FinanceRecord.objects.all()
    income_records = all_records.filter(type='income')
    expense_records = all_records.filter(type='expense') 

    total_income = FinanceRecord.objects.filter(type='income').aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_expense = FinanceRecord.objects.filter(type='expense').aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        "form": form,
        "income_records":income_records,
        "expense_records":expense_records,
        "total_income":total_income,
        "total_expense":total_expense,
    }
    return render(request, "management/total-income.html", context)


def delete_record(request, record_id):
    referer = request.META.get('HTTP_REFERER', '/')

    record = get_object_or_404(FinanceRecord, id=record_id)

    record.delete()

    messages.success(request, "ریکارد با موفقیت حذف شد.")
    return redirect(referer)


def edit_record(request, record_id):
    record = get_object_or_404(FinanceRecord, id=record_id)

    if request.method == "POST":
        form = FinanceRecordForm(request.POST, instance=record)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.save()

            messages.success(request, "ریکارد با موفقیت ویرایش شد.")
            return redirect("management:Total_income")
    else:
        form = FinanceRecordForm(instance=record)

    return render(request, "management/edit-record.html", {
        "form": form,
        "record": record
    })