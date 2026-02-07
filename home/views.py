from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from students.models import *
from account.models import *
from .forms import *
from django.db.models import Sum
from django.contrib import messages
# Create your views here.

@login_required
def dashboard(request):


    return render(request, 'dashboard.html')

def colculator(request):

    return render(request, 'colculator.html')

def supplier(request):
    if request.method == "POST":
        form = suppliersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تامین کننده جدید اضافه شد')
            return redirect('home:supplier')
        else:
            form.errors()
    else:
        form = suppliersForm()
        records = suppliers.objects.all()
    context = {
        'form':form,
        'records':records,
    }
    return render(request, 'home/supplier.html', context)

def delete_supplier(request, id):
    supplier = suppliers.objects.get(id=id)
    supplier.delete()
    messages.success(request, 'تامین کننده موفقانه حذف شد')
    return redirect('home:supplier')

def edit_supplier(request, id):
    supplier = suppliers.objects.get(id=id)
    if request.method == "POST":
        form = suppliersForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
        else:
            form.errors()
    else:
        form = suppliersForm(instance=supplier)
    
    context = {
        'form':form,
        'supplier':supplier,
    }
    return render(request, 'home/edit-supplier.html', context)

def supplier_detail(request, id):
    supplier = suppliers.objects.get(id=id)
    supplier_colculation = ColculationWithSupplier.objects.filter(supplier=supplier)
    latest_supplier_colculation = ColculationWithSupplier.objects.filter(supplier=supplier).last()

    supplier_colculation = ColculationWithSupplier.objects.filter(supplier=supplier).order_by('created_at')

    latest_record = supplier_colculation.last()
    latest_payment = supplier_colculation.filter(colculation_type='پرداخت').last()
    only_one_balance = (
        supplier_colculation.count() == 1 and
        latest_record and
        latest_record.colculation_type == 'بیلانس'
    )

    total_paid = supplier_colculation.aggregate(Sum('paid_price'))['paid_price__sum'] or 0
    total_remain = supplier_colculation.aggregate(Sum('remain_price'))['remain_price__sum'] or 0
    total = total_paid + total_remain

    jdate_form = JDateForm()

    if request.method == "POST":
        jdate_form = JDateForm(request.POST)
        if jdate_form.is_valid():
            date = jdate_form.cleaned_data.get('date')
            last_paid = float(request.POST.get('last_paid'))
            latest_col = ColculationWithSupplier.objects.filter(supplier=supplier).last()
            if latest_col:
                remain_balance = latest_col.remain_balance - last_paid
            else:
                remain_balance = 0

        form_type = request.POST.get('form_type')
        if form_type == "payment":
            
            ColculationWithSupplier.objects.create(
                supplier=supplier,
                colculation_type='پرداخت',
                total_price=0,
                paid_price=last_paid,
                remain_price=0,
                remain_balance=remain_balance,
                date=date
            )
        else:
            last_paid = float(request.POST.get('last_paid'))
            last_remain = float(request.POST.get('last_remain'))
            ColculationWithSupplier.objects.create(
                supplier=supplier,
                colculation_type='بیلانس',
                total_price=0,
                paid_price=last_paid,
                remain_price=last_remain,
                remain_balance=last_remain,
                date=date
            )
            messages.success(request, 'بیلانس تامین کننده با موفقیت ثبت شد')
        return redirect('home:supplier_detail', id=id)

    context = {
        'supplier':supplier,
        'total_paid':total_paid,
        'total_remain':total_remain,
        'total':total,
        'supplier_colculation':supplier_colculation,
        'jdate_form':jdate_form,
        'latest_supplier_colculation':latest_supplier_colculation,
        'latest_payment': latest_payment,
        'only_one_balance': only_one_balance,
    }
    return render(request, 'home/detail-supplier.html', context)

def delete_balance(request, id):
    balance = ColculationWithSupplier.objects.get(id=id)
    balance.delete()
    messages.success(request, 'بیلانس تامین کننده با موفقیت حذف شد')
    return redirect('home:supplier_detail', id=balance.supplier.id)

def edit_balance(request, id):
    balance = ColculationWithSupplier.objects.get(id=id)
    if request.method == "POST":
        form = JDateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data.get('date')
            last_paid = float(request.POST.get('last_paid'))
            last_remain = float(request.POST.get('last_remain'))

            balance.paid_price = last_paid
            balance.remain_price = last_remain
            balance.remain_balance = last_remain
            balance.date = date
            balance.save()
            messages.success(request, 'تاریخ بیلانس تامین کننده با موفقیت ویرایش شد')
            return redirect('home:supplier_detail', id=balance.supplier.id)
    else:
        form = JDateForm(initial={'date': balance.date})
    
    context = {
        'form':form,
        'balance':balance,
    }

    return render(request, 'home/edit-balance.html', context)