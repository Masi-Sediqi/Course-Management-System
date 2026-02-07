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
        item_price = total_item.total_item * total_item.per_price
    else:
        item_price = 0

    context = {
        'item':item,
        'purchages':purchages,
        'total_item':total_item,
        'item_price':item_price,
    }
    return render(request, 'library/item_info.html', context)


def purchase_item(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    item = Item.objects.get(id=id)
    item_balance = TotalItem.objects.filter(item=item).last()
    if not item_balance:
        item_balance = TotalItem.objects.create(item=item, total_item=0, total_remain_item=0, per_price=0)

    total_balance = TotalBalance.objects.last()
    if not total_balance:
        total_balance = TotalBalance.objects.create(total_income=0, total_expenses=0, total_receivable=0, total_payable=0)

    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data.get('date')
            number = float(request.POST.get('number'))
            per_price = request.POST.get('per_price')
            total_price = request.POST.get('total_price')
            paid_price = request.POST.get('paid_price')
            remain_price = request.POST.get('remain_price')

            instance = form.save(commit=False)
            instance.item = item
            instance.number = number
            instance.per_price = per_price
            instance.total_price = total_price
            instance.paid_price = paid_price
            instance.remain_price = remain_price
            instance.save()

            # Update TotalItem
            item_balance.total_item += int(number)
            item_balance.per_price = float(per_price)
            item_balance.total_remain_item += int(number)
            item_balance.save()

            # Update TotalBalance
            total_balance.total_expenses += float(paid_price)
            total_balance.total_payable += float(remain_price)
            total_balance.save()

            latest_col = ColculationWithSupplier.objects.filter(supplier=instance.supplier).last()
            if latest_col:
                remain_balance = latest_col.remain_balance + float(remain_price)
            else:
                remain_balance = remain_price

            ColculationWithSupplier.objects.create(
                supplier=instance.supplier,
                colculation_type='خریداری',
                total_price=float(total_price),
                paid_price=float(paid_price),
                remain_price=float(remain_price),
                remain_balance=remain_balance,
                purchase_item=instance,
                date=date
            )

            messages.success(request, "خرید با موفقیت ثبت شد.")
            return redirect('library:item_info', id=item.id)
    else:
        form = PurchaseForm()

    context = {
        'form':form,
        'item':item,
    }
    return render(request, 'library/buy-book-again.html', context)

def delete_purchase_item(request, id):
    purchase = get_object_or_404(Purchase, id=id)
    item = purchase.item

    item_balance = TotalItem.objects.filter(item=item).last()
    total_balance = TotalBalance.objects.last()

    # Update TotalItem
    item_balance.total_item -= purchase.number
    item_balance.total_remain_item -= purchase.number
    item_balance.save()

    # Update TotalBalance
    total_balance.total_expenses -= purchase.paid_price
    total_balance.total_payable -= purchase.remain_price
    total_balance.save()

    messages.success(request, 'ریکارد موفقانه حذف شد')
    purchase.delete()
    return redirect("library:item_info", id=item.id)  

def edit_purchase_item(request, id):
    purchase = get_object_or_404(Purchase, id=id)
    item = purchase.item
    item_balance = TotalItem.objects.filter(item=item).last()
    total_balance = TotalBalance.objects.get(pk=1)


    if request.method == "POST":
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            old_number = purchase.number
            old_paid_price = purchase.paid_price
            old_remain_price = purchase.remain_price

            updated_purchase = form.save(commit=False)
            new_number = int(request.POST.get('number'))
            new_paid_price = float(request.POST.get('paid_price'))
            new_remain_price = float(request.POST.get('remain_price'))

            updated_purchase.number = new_number
            updated_purchase.paid_price = new_paid_price
            updated_purchase.remain_price = new_remain_price
            updated_purchase.save()

            # Update TotalItem
            item_balance.total_item += (new_number - old_number)
            item_balance.total_remain_item += (new_number - old_number)
            item_balance.save()

            # Update TotalBalance
            total_balance.total_expenses += (new_paid_price - old_paid_price)
            total_balance.total_payable += (new_remain_price - old_remain_price)
            total_balance.save()

            delete_old_colculation = ColculationWithSupplier.objects.get(purchase_item=purchase)
            delete_old_colculation.delete()

            # Update ColculationWithSupplier
            latest_col = ColculationWithSupplier.objects.filter(supplier=updated_purchase.supplier).last()
            if latest_col:
                remain_balance = latest_col.remain_balance - old_remain_price + new_remain_price
            else:
                remain_balance = new_remain_price

            ColculationWithSupplier.objects.create(
                supplier=updated_purchase.supplier,
                colculation_type='خریداری',
                total_price=float(updated_purchase.total_price),
                paid_price=float(updated_purchase.paid_price),
                remain_price=float(updated_purchase.remain_price),
                remain_balance=remain_balance,
                purchase_item=updated_purchase,
                date=updated_purchase.date
            )

            messages.success(request, "خرید با موفقیت ویرایش شد.")
            return redirect('library:item_info', id=item.id)
    else:
        form = PurchaseForm(instance=purchase)

    context = {
        'form':form,
        'purchase':purchase,
        'item':item,
    }
    return render(request, 'library/edit-purchase-item.html', context)