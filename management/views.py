from django.shortcuts import render, redirect
from decimal import Decimal
from management.forms import *
from .models import *
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