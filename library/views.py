from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import *
from home.models import *
from management.models import *
from django.http import HttpResponse
from account.models import *


def library_view(request):
    form = ItemForm()

    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "آیتم با موفقیت ثبت شد.")
            return redirect('library:library_view')

    items = Item.objects.all()

    context = {
        'form': form,
        'items': items,
    }
    return render(request, 'library/main_library.html', context)

def delete_item(request, id):

    record = get_object_or_404(Item, id=id)
    if record:
        record.delete()
        messages.success(request, 'جنس مذکور موفقانه حذف شد ....')
        return redirect('library:library_view')
    else:
        return HttpResponse('مشکل در آیدی کتگوری است')
    
def edit_item(request, id):
    item = Item.objects.get(id=id)

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "جنس با موفقیت ثبت شد.")
            return redirect('library:library_view')
    else:
        form = ItemForm(instance=item)

    context = {
        'form':form,
        'item':item,
    }
    return render(request, 'library/edit_main_library.html', context)

def item_info(request, id):
    item = Item.objects.get(id=id)
    purchages = item.purchases.all()  # دسترسی به خریدهای مرتبط با این آیتم
    total_item = TotalItem.objects.filter(item=item).last()
    if total_item:
        item_price = total_item.remain_item * total_item.per_price
    else:
        item_price = 0

    context = {
        'item':item,
        'purchages':purchages,
        'total_item':total_item,
        'item_price':item_price,
    }
    return render(request, 'library/item_info.html', context)


def buy_book_again(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    item = Item.objects.get(id=id)

    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            
            return redirect(referer)
    else:
        form = PurchaseForm()

    context = {
        'form':form,
    }
    return render(request, 'library/buy-book-again.html', context)

def delete_buy_again(request, id):

    record = get_object_or_404(BuyBookAgain, id=id)
    total_book = TotalBook.objects.get(book=record.book.id)
    total_book.total_book -= record.number_of_book
    total_book.total_amount -= record.number_of_book
    total_book.save()

    total_ex = TotalExpenses.objects.get(pk=1)
    total_ex.total_amount -= record.paid_price
    total_ex.save()
    messages.success(request, 'ریکارد موفقانه حذف شد')
    record.delete()
    return redirect("library:buy_book_again", id=record.book.id)  # change this to your list view name


def update_per_price(request, id):

    total_book = get_object_or_404(TotalBook, id=id)
    if request.method == "POST":
        per_price = request.POST.get("per_price")
        if per_price:
            total_book.per_price = per_price
            total_book.save()
            messages.success(request, "مقدار فی با موفقیت تغییر یافت.")
    return redirect("library:buy_book_again", id=total_book.book.id)  # change to your view name

