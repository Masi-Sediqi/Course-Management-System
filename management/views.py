from django.shortcuts import render, redirect
from decimal import Decimal
from management.forms import *
from .models import *
from django.contrib import messages
from django.http import HttpResponse
# Create your views here.

def Total_income(request):
    form = None
    x_form = None
    referer = request.META.get('HTTP_REFERER', '/')
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == "income":
            form = OtherIncomeForm(request.POST)
            if form.is_valid():
                get_amount = form.cleaned_data.get('amount')
                total_income_obj, created = TotalIncome.objects.get_or_create(pk=1)

                if get_amount:
                    # Update the total amount properly
                    total_income_obj.total_amount = Decimal(str(total_income_obj.total_amount)) + Decimal(get_amount)
                    total_income_obj.save()

                    # If you have another income model being saved (e.g., record of each income), you can do:
                    income_instance = form.save(commit=False)
                    income_instance.total_income = total_income_obj  # if related
                    income_instance.save()
                    return redirect(referer)
        else:
            x_form = ExpensesForm(request.POST)
            if x_form.is_valid():
                get_amount = x_form.cleaned_data.get('amount')
                total_income = TotalIncome.objects.last()
                total_expenses_obj, created = TotalExpenses.objects.get_or_create(pk=1)
                total_expenses_obj.total_amount = Decimal(str(total_expenses_obj.total_amount)) + Decimal(get_amount)
                total_income.total_amount -= get_amount
                total_expenses_obj.save()
                total_income.save() 
                x_form.save()
                return redirect(referer)
    else:
        form = OtherIncomeForm()
        x_form = ExpensesForm()

    # Reload total income after saving
    get_total_income = TotalIncome.objects.last()
    get_total_expenses = TotalExpenses.objects.last()
    get_total_otherinceom = OtherIncome.objects.all()
    get_total_expens = Expenses.objects.all()

    context = {
        'get_total_income': get_total_income,
        'form': form,
        'get_total_otherinceom':get_total_otherinceom,
        'x_form':x_form,
        'get_total_expenses':get_total_expenses,
        'get_total_expens':get_total_expens,
    }
    return render(request, 'management/total-income.html', context)

def delete_income(request, income_id):
    referer = request.META.get('HTTP_REFERER', '/')
    try:
        income_instance = OtherIncome.objects.get(id=income_id)
        total_income = TotalIncome.objects.last()
        if income_instance and total_income:
            total_income.total_amount -= income_instance.amount
            total_income.save()
            messages.success(request, f"ریکارد هزینه با موفقیت حذف شد.") 
            income_instance.delete()
    except OtherIncome.DoesNotExist:
        pass
    return redirect(referer)

def edit_income(request, income_id):
    income_instance = OtherIncome.objects.get(id=income_id)
    total_income = TotalIncome.objects.last()
    previous_amount = income_instance.amount
    if request.method == "POST":
        form = OtherIncomeForm(request.POST, instance=income_instance)
        if form.is_valid():
            
            updated_income = form.save(commit=False)
            
            # Adjust the total income by removing the previous amount and adding the new amount
            if form.cleaned_data.get('amount') > previous_amount:
                difference = form.cleaned_data.get('amount') - previous_amount
                total_income.total_amount += difference
            elif form.cleaned_data.get('amount') < previous_amount:
                difference = previous_amount - form.cleaned_data.get('amount')
                total_income.total_amount -= difference
            else:
                pass  # No change in amount
            total_income.save() 
            updated_income.save()
            messages.success(request, f"ریکارد با موفقیت ایدیت شد.")
            return redirect('management:Total_income')
    else:
        form = OtherIncomeForm(instance=income_instance)
    context = {
        'form': form,
        'income_instance': income_instance,
    }   
    return render(request, 'management/edit-income.html', context)

def delete_expense(request, expense_id):
    referer = request.META.get('HTTP_REFERER', '/')
    try:
        expense_instance = Expenses.objects.get(id=expense_id)
        total_expenses = TotalExpenses.objects.last()
        if expense_instance and total_expenses:
            total_expenses.total_amount -= expense_instance.amount
            total_expenses.save()
            messages.success(request, f"ریکارد هزینه با موفقیت حذف شد.") 
            expense_instance.delete()
    except Expenses.DoesNotExist:
        pass
    return redirect(referer)

def edit_expense(request, expense_id):
    expense_instance = Expenses.objects.get(id=expense_id)
    total_expenses = TotalExpenses.objects.last()
    previous_amount = expense_instance.amount  # Store the previous amount before updating

    if request.method == "POST":
        form = ExpensesForm(request.POST, instance=expense_instance)
        if form.is_valid():
            update_expenses = form.save(commit=False)
# Adjust the total income by removing the previous amount and adding the new amount
            if form.cleaned_data.get('amount') > previous_amount:
                difference = form.cleaned_data.get('amount') - previous_amount
                total_expenses.total_amount += difference
            elif form.cleaned_data.get('amount') < previous_amount:
                difference = previous_amount - form.cleaned_data.get('amount')
                total_expenses.total_amount -= difference
            else:
                pass  # No change in amount
            update_expenses.save()
            total_expenses.save()
            messages.success(request, f"ریکارد با موفقیت ایدیت شد.")
            return redirect('management:Total_income')
    else:
        form = ExpensesForm(instance=expense_instance)
    context = {
        'form': form,   
        'expense_instance': expense_instance,
    } 
    return render(request, 'management/edit-expense.html', context)