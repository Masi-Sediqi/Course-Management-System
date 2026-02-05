from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from management.forms import *
from .models import *
from django.contrib import messages
from django.http import HttpResponse
# Create your views here.

def Total_income(request):
    referer = request.META.get('HTTP_REFERER', '/')

    total_balance, _ = TotalBalance.objects.get_or_create(pk=1)

    if request.method == "POST":
        form = FinanceRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)

            if record.type == "income":
                total_balance.total_income += float(record.amount)
            else:
                total_balance.total_expenses += float(record.amount)

            total_balance.save()
            record.save()

            messages.success(request, "ریکارد با موفقیت ثبت شد.")
            return redirect(referer)
    else:
        form = FinanceRecordForm()

    context = {
        "form": form,
        "total_balance": total_balance,
        "incomes_and_expenses": FinanceRecord.objects.all(),
    }
    return render(request, "management/total-income.html", context)


def delete_record(request, record_id):
    referer = request.META.get('HTTP_REFERER', '/')

    record = get_object_or_404(FinanceRecord, id=record_id)
    total_balance = TotalBalance.objects.first()

    if record.type == "income":
        total_balance.total_income -= record.amount
    else:
        total_balance.total_expenses -= record.amount

    total_balance.save()
    record.delete()

    messages.success(request, "ریکارد با موفقیت حذف شد.")
    return redirect(referer)


def edit_record(request, record_id):
    record = get_object_or_404(FinanceRecord, id=record_id)
    total_balance = TotalBalance.objects.first()
    previous_amount = record.amount
    previous_type = record.type

    if request.method == "POST":
        form = FinanceRecordForm(request.POST, instance=record)
        if form.is_valid():
            updated = form.save(commit=False)

            # rollback old value
            if previous_type == "income":
                total_balance.total_income -= previous_amount
            else:
                total_balance.total_expenses -= previous_amount

            # apply new value
            if updated.type == "income":
                total_balance.total_income += updated.amount
            else:
                total_balance.total_expenses += updated.amount

            total_balance.save()
            updated.save()

            messages.success(request, "ریکارد با موفقیت ویرایش شد.")
            return redirect("management:Total_income")
    else:
        form = FinanceRecordForm(instance=record)

    return render(request, "management/edit-record.html", {
        "form": form,
        "record": record
    })