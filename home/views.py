from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from students.models import *
from account.models import *
from management.models import *
from .forms import *
from django.db.models import Sum
from django.contrib import messages
# Create your views here.

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def supplier(request):
    if request.method == "POST":
        form = suppliersForm(request.POST)
        if form.is_valid():
            form.save()
            SystemLog.objects.create(
                section="تامین کننده‌ها",
                action=f"ایجاد تامین کننده جدید:",
                description=f"تامین کننده {form.cleaned_data.get('name')} ایجاد شد.",
                user=request.user if request.user.is_authenticated else None
            )
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
    SystemLog.objects.create(
        section="تامین کننده‌ها",
        action=f"حذف تامین کننده:",
        description=f"تامین کننده {supplier.name} حذف شد.",
        user=request.user if request.user.is_authenticated else None
    )
    messages.success(request, 'تامین کننده موفقانه حذف شد')
    return redirect('home:supplier')

def edit_supplier(request, id):
    supplier = suppliers.objects.get(id=id)
    if request.method == "POST":
        form = suppliersForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            SystemLog.objects.create(
                section="تامین کننده‌ها",
                action=f"ایدیت تامین کننده:",
                description=f"تامین کننده {supplier.name} ایدیت شد.",
                user=request.user if request.user.is_authenticated else None
            )
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


    if request.method == "POST":
        jdate_form = JDateForm(request.POST)
        jdate_form1 = JDateForm1(request.POST)
        if jdate_form.is_valid() or jdate_form1.is_valid():
            date = jdate_form.cleaned_data.get('date') or jdate_form1.cleaned_data.get('date')
            last_paid = float(request.POST.get('last_paid'))
            latest_col = ColculationWithSupplier.objects.filter(supplier=supplier).last()
            if latest_col:
                remain_balance = latest_col.remain_balance - last_paid
            else:
                remain_balance = 0

        form_type = request.POST.get('form_type')
        if form_type == "payment":
            
            col = ColculationWithSupplier.objects.create(
            supplier=supplier,
            colculation_type='پرداخت',
            total_price=0,
            paid_price=last_paid,
            remain_price=0,
            remain_balance=remain_balance,
            date=date
            )

            # Create Finance Record (EXPENSE)
            FinanceRecord.objects.create(
                date=date,
                title=f"پرداخت به تامین کننده {supplier.name}",
                description=f"پرداخت مبلغ {last_paid} به تامین کننده {supplier.name}",
                amount=last_paid,
                type="expense",
                content_type=ContentType.objects.get_for_model(ColculationWithSupplier),
                object_id=col.id,
            )

        else:
            last_paid = float(request.POST.get('last_paid'))
            last_remain = float(request.POST.get('last_remain'))

            col = ColculationWithSupplier.objects.create(
                supplier=supplier,
                colculation_type='بیلانس',
                total_price=0,
                paid_price=last_paid,
                remain_price=last_remain,
                remain_balance=last_remain,
                date=date
            )

            # Optional: create finance record for starting balance (only if you want)
            FinanceRecord.objects.create(
                date=date,
                title=f"ثبت بیلانس اولیه تامین کننده {supplier.name}",
                description=f"ثبت بیلانس اولیه برای تامین کننده {supplier.name}",
                amount=last_paid,
                type="expense",
                content_type=ContentType.objects.get_for_model(ColculationWithSupplier),
                object_id=col.id,
            )

        SystemLog.objects.create(
            section="تامین کننده‌ها",
            action=f"ثبت بیلانس تامین کننده:",
            description=f"بیلانس تامین کننده {supplier.name} ثبت شد.",
            user=request.user if request.user.is_authenticated else None
        )
        messages.success(request, 'بیلانس تامین کننده با موفقیت ثبت شد')
        return redirect('home:supplier_detail', id=id)
    else:
        jdate_form = JDateForm()
        jdate_form1 = JDateForm1()

    context = {
        'supplier':supplier,
        'total_paid':total_paid,
        'total_remain':total_remain,
        'total':total,
        'supplier_colculation':supplier_colculation,
        'jdate_form':jdate_form,
        'latest_supplier_colculation':latest_supplier_colculation,
        'latest_payment': latest_payment,
        'jdate_form1': jdate_form1,
        'only_one_balance': only_one_balance,
    }
    return render(request, 'home/detail-supplier.html', context)


def delete_balance(request, id):
    balance = ColculationWithSupplier.objects.get(id=id)
    supplier = balance.supplier

    # Delete linked FinanceRecord(s)
    content_type = ContentType.objects.get_for_model(ColculationWithSupplier)
    FinanceRecord.objects.filter(content_type=content_type, object_id=balance.id).delete()

    balance.delete()

    SystemLog.objects.create(
        section="تامین کننده‌ها",
        action=f"حذف بیلانس تامین کننده:",
        description=f"بیلانس تامین کننده {supplier.name} حذف شد.",
        user=request.user if request.user.is_authenticated else None
    )
    messages.success(request, 'بیلانس تامین کننده با موفقیت حذف شد')
    return redirect('home:supplier_detail', id=supplier.id)


def edit_balance(request, id):
    balance = ColculationWithSupplier.objects.get(id=id)
    supplier = balance.supplier

    if request.method == "POST":
        form = JDateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data.get('date')
            last_paid = float(request.POST.get('last_paid'))
            last_remain = float(request.POST.get('last_remain', 0))

            # Store old values
            old_paid = balance.paid_price
            old_remain = balance.remain_price

            # --- Recalculate remain_balance like in create ---
            # Get the previous record (if exists)
            previous_record = ColculationWithSupplier.objects.filter(
                supplier=supplier,
                id__lt=balance.id
            ).order_by('-id').first()

            if balance.colculation_type == "پرداخت":
                prev_remain_balance = previous_record.remain_balance if previous_record else 0
                new_remain_balance = prev_remain_balance - last_paid
            else:  # بیلانس
                new_remain_balance = last_remain

            # Update balance
            balance.paid_price = last_paid
            balance.remain_price = last_remain
            balance.remain_balance = new_remain_balance
            balance.date = date
            balance.save()

            # Update linked FinanceRecord
            content_type = ContentType.objects.get_for_model(ColculationWithSupplier)
            finance_record = FinanceRecord.objects.filter(
                content_type=content_type,
                object_id=balance.id
            ).first()
            if finance_record:
                finance_record.amount = last_paid + last_remain
                finance_record.date = date
                finance_record.description = f"بیلانس تامین کننده {supplier.name} ایدیت شد"
                finance_record.save()

            # Update all following records remain_balance
            following_records = ColculationWithSupplier.objects.filter(
                supplier=supplier,
                id__gt=balance.id
            ).order_by('id')

            for record in following_records:
                prev_record = ColculationWithSupplier.objects.filter(
                    supplier=supplier,
                    id__lt=record.id
                ).order_by('-id').first()
                if record.colculation_type == "پرداخت":
                    record.remain_balance = (prev_record.remain_balance if prev_record else 0) - record.paid_price
                else:  # بیلانس
                    record.remain_balance = record.remain_price
                record.save()

            # Log
            SystemLog.objects.create(
                section="تامین کننده‌ها",
                action=f"ایدیت بیلانس تامین کننده",
                description=f"بیلانس تامین کننده {supplier.name} از {old_paid + old_remain} به {last_paid + last_remain} ایدیت شد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'بیلانس تامین کننده با موفقیت ایدیت شد')
            return redirect('home:supplier_detail', id=supplier.id)
    else:
        form = JDateForm(initial={'date': balance.date})

    context = {
        'form': form,
        'balance': balance,
    }
    return render(request, 'home/edit-balance.html', context)


def history(request):
    logs = SystemLog.objects.all()
    context = {
        'logs':logs
    }
    return render(request, 'home/logs.html', context)