from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from students.models import *
from account.models import *
from django.utils import timezone
from .forms import *
from django.db.models import Sum
from django.contrib import messages
# Create your views here.

@login_required
def dashboard(request):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")

    return render(request, 'dashboard.html')

def colculator(request):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    supplier_books = Books.objects.filter(supplier=supplier)
    # 💰 Collect total paid amount for this supplier
    total_book_paid = supplier_books.aggregate(total_paid=Sum('paid_price'))['total_paid'] or 0
    total_book_remain = supplier_books.aggregate(total_remain=Sum('remain_price'))['total_remain'] or 0

    supplier_Stationery = StationeryItem.objects.filter(supplier=supplier)
    # 💰 Collect total paid amount for this supplier
    total_paid = supplier_Stationery.aggregate(total_paid=Sum('stationery_paid_price'))['total_paid'] or 0
    total_remain = supplier_Stationery.aggregate(total_remain=Sum('stationery_remain_price'))['total_remain'] or 0

    total_book_stationary_paid = total_book_paid + total_paid
    total_book_stationary_remain = total_book_remain + total_remain

    context = {
        'supplier':supplier,
        'supplier_Stationery':supplier_Stationery,
        'supplier_books':supplier_books,
        'total_book_stationary_paid':total_book_stationary_paid,
        'total_book_stationary_remain':total_book_stationary_remain,
    }
    return render(request, 'home/detail-supplier.html', context)