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
            SystemLog.objects.create(
                section="کتابخانه",
                action=f"ایجاد کتاب جدید:",
                description=f"کتاب {form.cleaned_data.get('name')} ایجاد شد.",
                user=request.user if request.user.is_authenticated else None
            )
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
        SystemLog.objects.create(
            section="کتابخانه",
            action=f"حذف کتاب:",
            description=f"کتاب {record.name} حذف شد.",
            user=request.user if request.user.is_authenticated else None
        )

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
            SystemLog.objects.create(
                section="کتابخانه",
                action=f"ایدیت کتاب:",
                description=f"کتاب {item.name} ایدیت شد.",
                user=request.user if request.user.is_authenticated else None
            )
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

            # Create finance expense record
            FinanceRecord.objects.create(
                date=date,
                title=f"خرید کتاب {item.name}",
                description=f"خرید کتاب از تامین‌کننده {instance.supplier.name} | تعداد: {number}",
                amount=float(paid_price),   # only the paid amount is expense
                type="expense",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
            )

            SystemLog.objects.create(
                section="کتابخانه",
                action=f"خریداری کتاب:",
                description=f"خریداری کتاب {item.name} از تامین کننده به اسم {instance.supplier.name}",
                user=request.user if request.user.is_authenticated else None
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


def recalc_supplier_balances(supplier):
    records = ColculationWithSupplier.objects.filter(
        supplier=supplier
    ).order_by('created_at')

    current_balance = 0

    for r in records:
        if r.colculation_type == "بیلانس":
            current_balance = r.remain_price

        elif r.colculation_type == "پرداخت":
            current_balance -= r.paid_price

        elif r.colculation_type == "خریداری":
            current_balance += r.remain_price

        r.remain_balance = current_balance
        r.save()


def delete_purchase_item(request, id):
    purchase = get_object_or_404(Purchase, id=id)
    item = purchase.item
    supplier = purchase.supplier

    item_balance = TotalItem.objects.filter(item=item).last()

    # Update stock
    item_balance.total_item -= purchase.number
    item_balance.total_remain_item -= purchase.number
    item_balance.save()

    # Delete finance record
    content_type = ContentType.objects.get_for_model(Purchase)
    FinanceRecord.objects.filter(
        content_type=content_type,
        object_id=purchase.id
    ).delete()

    # Delete supplier calculation linked to this purchase
    ColculationWithSupplier.objects.filter(
        purchase_item=purchase
    ).delete()

    # 🔥 Recalculate ALL balances for this supplier
    recalc_supplier_balances(supplier)

    SystemLog.objects.create(
        section="کتابخانه",
        action="حذف خریداری کتاب:",
        description=f"خریداری کتاب {item.name} حذف شد",
        user=request.user if request.user.is_authenticated else None
    )

    purchase.delete()

    messages.success(request, 'ریکارد موفقانه حذف شد')
    return redirect("library:item_info", id=item.id)


def edit_purchase_item(request, id):
    purchase = get_object_or_404(Purchase, id=id)
    item = purchase.item
    supplier = purchase.supplier
    item_balance = TotalItem.objects.filter(item=item).last()

    if request.method == "POST":
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():

            old_number = purchase.number

            updated = form.save(commit=False)

            new_number = int(request.POST.get('number'))
            updated.number = new_number
            updated.save()

            # Update stock
            item_balance.total_item += (new_number - old_number)
            item_balance.total_remain_item += (new_number - old_number)
            item_balance.save()

            # Update finance
            content_type = ContentType.objects.get_for_model(Purchase)
            finance = FinanceRecord.objects.filter(
                content_type=content_type,
                object_id=purchase.id
            ).first()

            if finance:
                finance.amount = float(updated.paid_price)
                finance.date = updated.date
                finance.save()

            # Delete old supplier calculation
            ColculationWithSupplier.objects.filter(
                purchase_item=purchase
            ).delete()

            # Create new calculation
            ColculationWithSupplier.objects.create(
                supplier=updated.supplier,
                colculation_type='خریداری',
                total_price=float(updated.total_price),
                paid_price=float(updated.paid_price),
                remain_price=float(updated.remain_price),
                purchase_item=updated,
                date=updated.date
            )

            # 🔥 Recalculate ALL balances
            recalc_supplier_balances(updated.supplier)

            SystemLog.objects.create(
                section="کتابخانه",
                action="ایدیت خریداری کتاب:",
                description=f"خریداری کتاب {item.name} ایدیت شد",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, "خرید با موفقیت ویرایش شد.")
            return redirect('library:item_info', id=item.id)
    else:
        form = PurchaseForm(instance=purchase)

    return render(request, 'library/edit-purchase-item.html', {
        'form': form,
        'purchase': purchase,
        'item': item,
    })