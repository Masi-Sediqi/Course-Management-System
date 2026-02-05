from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from students.models import *
from account.models import *
from django.utils import timezone
from .forms import *
from django.db.models import Sum
from django.contrib import messages
from itertools import chain
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
    supplier_books = Books.objects.filter(supplier=supplier)
    supplier_books_again = BuyBookAgain.objects.filter(supplier=supplier)

    supplier_books = Books.objects.filter(supplier=supplier)
    supplier_books_again = BuyBookAgain.objects.filter(supplier=supplier)

    combined_books = []

    # Append Books items
    for b in supplier_books:
        combined_books.append({
            'date': b.date,
            'name': b.name,
            'price': b.price,
            'paid_price': b.paid_price,
            'remain_price': b.remain_price,
        })

    # Append BuyBookAgain items
    for b in supplier_books_again:
        combined_books.append({
            'date': b.date,
            'name': b.book.name,  # comes from related field
            'price': b.price,
            'paid_price': b.paid_price,
            'remain_price': b.remain_price,
        })


    # 💰 Collect total paid amount for this supplier
    total_book_paid = supplier_books.aggregate(total_paid=Sum('paid_price'))['total_paid'] or 0
    total_book_paid_again = supplier_books_again.aggregate(total_paid=Sum('paid_price'))['total_paid'] or 0
    total_book_remain = supplier_books.aggregate(total_remain=Sum('remain_price'))['total_remain'] or 0
    total_book_remain_again = supplier_books_again.aggregate(total_remain=Sum('remain_price'))['total_remain'] or 0

    supplier_Stationery = StationeryItem.objects.filter(supplier=supplier)
    supplier_Stationery_again = BuyStationeryAgain.objects.filter(supplier=supplier)

    combined_stationery = []

    # Add original stationery purchases
    for s in supplier_Stationery:
        combined_stationery.append({
            'date': s.date,
            'name': s.name,
            'stationery_price': s.stationery_price,
            'stationery_paid_price': s.stationery_paid_price,
            'stationery_remain_price': s.stationery_remain_price,
        })

    # Add “buy again” stationery purchases
    for s in supplier_Stationery_again:
        combined_stationery.append({
            'date': s.date,
            'name': s.stationery.name,  # comes from foreign key
            'stationery_price': s.stationery_price,
            'stationery_paid_price': s.stationery_paid_price,
            'stationery_remain_price': s.stationery_remain_price,
        })

    # (optional) Sort by date if you want chronological order
    # Make sure date is in a sortable format (e.g., 'YYYY/MM/DD')
    combined_stationery.sort(key=lambda x: x['date'], reverse=True)

    # 💰 Collect total paid amount for this supplier
    total_paid = supplier_Stationery.aggregate(total_paid=Sum('stationery_paid_price'))['total_paid'] or 0
    total_remain = supplier_Stationery.aggregate(total_remain=Sum('stationery_remain_price'))['total_remain'] or 0

    total_book_stationary_paid = total_book_paid + total_paid + total_book_paid_again
    total_book_stationary_remain = total_book_remain + total_remain + total_book_remain_again

    context = {
        'supplier':supplier,
        'combined_stationery':combined_stationery,
        'total_book_stationary_paid':total_book_stationary_paid,
        'total_book_stationary_remain':total_book_stationary_remain,
        'combined_books':combined_books,
    }
    return render(request, 'home/detail-supplier.html', context)