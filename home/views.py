from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from students.models import *
from account.models import *
from management.models import *
from .forms import *
from django.utils import timezone
from settings.models import *
from django.db.models import Sum
from django.contrib import messages
import jdatetime
from decimal import Decimal
from django.db import transaction

# views.py
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from .forms import DateFilterForm
import jdatetime
# Create your views here.


@login_required
def dashboard(request):
    today = timezone.now().date()

    notifications = Notification.objects.all().order_by('is_read', '-created_at')

    visible_notifications = []
    unread_count = 0
    read_count = 0

    for n in notifications:
        obj = n.content_object
        show = False

        if obj:
            # Tuition fee notification (Jalali end_date)
            if hasattr(obj, "end_date") and obj.end_date:
                try:
                    # Convert Jalali string to Gregorian date
                    day, month, year = map(int, obj.end_date.split('/'))
                    jalali_date = jdatetime.date(year, month, day)
                    due_date = jalali_date.togregorian()

                    if due_date <= today:
                        show = True
                except Exception as e:
                    print("Date conversion error:", e)

            # Low stock notification
            elif hasattr(obj, "total_remain_item"):
                if obj.total_remain_item < 10:
                    show = True

        if show:
            visible_notifications.append(n)
            if not n.is_read:
                unread_count += 1
            else:
                read_count += 1

    context = {
        "notifications": visible_notifications,
        "unread_count": unread_count,
        "read_count": read_count,
        "total_count": len(visible_notifications),
    }

    return render(request, 'dashboard.html', context)


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    messages.success(request, 'اعلان با موفقیت به عنوان خوانده شده علامت خورد')
    return redirect('home:dashboard')


@login_required
def mark_as_unread(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = False
    notification.read_at = None
    notification.save()
    
    messages.success(request, 'اعلان با موفقیت به عنوان نخوانده علامت خورد')
    return redirect('home:dashboard')


@login_required
def mark_all_as_read(request):
    Notification.objects.filter(is_read=False).update(
        is_read=True, 
        read_at=timezone.now()
    )
    
    messages.success(request, 'همه اعلانات با موفقیت به عنوان خوانده شده علامت خوردند')
    return redirect('home:dashboard')

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
        'jdate_form1': jdate_form1,
        'only_one_balance': only_one_balance,
    }
    return render(request, 'home/detail-supplier.html', context)


@transaction.atomic
def delete_balance(request, id):
    record = ColculationWithSupplier.objects.get(id=id)
    supplier = record.supplier

    # Delete linked FinanceRecord
    content_type = ContentType.objects.get_for_model(ColculationWithSupplier)
    FinanceRecord.objects.filter(
        content_type=content_type,
        object_id=record.id
    ).delete()

    # Delete the selected record
    record.delete()

    # 🔥 Recalculate all remaining balances
    calculations = ColculationWithSupplier.objects.filter(
        supplier=supplier
    ).order_by('created_at')

    current_balance = 0

    for calc in calculations:

        if calc.colculation_type == 'بیلانس':
            # Starting balance
            current_balance = calc.remain_price or 0

        elif calc.colculation_type == 'پرداخت':
            current_balance -= calc.paid_price or 0

        elif calc.colculation_type == 'خریداری':
            current_balance += calc.total_price or 0

        calc.remain_balance = current_balance
        calc.save(update_fields=['remain_balance'])

    SystemLog.objects.create(
        section="تامین کننده‌ها",
        action="حذف رکورد و بروزرسانی بیلانس",
        description=f"رکورد تامین کننده {supplier.name} حذف شد و بیلانس‌ها بروزرسانی شد.",
        user=request.user if request.user.is_authenticated else None
    )

    messages.success(request, 'رکورد حذف شد و بیلانس‌ها بروزرسانی شدند')
    return redirect('home:supplier_detail', id=supplier.id)


@transaction.atomic
def edit_balance(request, id):
    balance = ColculationWithSupplier.objects.get(id=id)
    supplier = balance.supplier

    if request.method == "POST":
        form = JDateForm(request.POST)
        if form.is_valid():

            date = form.cleaned_data.get('date')
            last_paid = Decimal(request.POST.get('last_paid') or 0)
            last_remain = Decimal(request.POST.get('last_remain') or 0)

            old_total = (balance.paid_price or 0) + (balance.remain_price or 0)

            # --- Update current record values only ---
            balance.paid_price = last_paid
            balance.remain_price = last_remain
            balance.date = date
            balance.save()

            # --- Recalculate ALL balances from start ---
            calculations = ColculationWithSupplier.objects.filter(
                supplier=supplier
            ).order_by('created_at')

            current_balance = Decimal('0')

            for calc in calculations:

                if calc.colculation_type == 'بیلانس':
                    current_balance = Decimal(calc.remain_price or 0)

                elif calc.colculation_type == 'پرداخت':
                    current_balance -= Decimal(calc.paid_price or 0)

                elif calc.colculation_type == 'خریداری':
                    current_balance += Decimal(calc.total_price or 0)

                calc.remain_balance = current_balance
                calc.save(update_fields=['remain_balance'])

            # --- Update linked FinanceRecord ---
            content_type = ContentType.objects.get_for_model(ColculationWithSupplier)
            finance_record = FinanceRecord.objects.filter(
                content_type=content_type,
                object_id=balance.id
            ).first()

            if finance_record:
                finance_record.amount = last_paid
                finance_record.date = date
                finance_record.description = f"ویرایش رکورد تامین کننده {supplier.name}"
                finance_record.save()

            # --- Log ---
            new_total = last_paid + last_remain

            SystemLog.objects.create(
                section="تامین کننده‌ها",
                action="ویرایش رکورد تامین کننده",
                description=f"رکورد {supplier.name} از {old_total} به {new_total} تغییر یافت.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'رکورد با موفقیت ویرایش شد و بیلانس‌ها بروزرسانی شدند')
            return redirect('home:supplier_detail', id=supplier.id)

    else:
        form = JDateForm(initial={'date': balance.date})

    context = {
        'form': form,
        'balance': balance,
    }
    return render(request, 'home/edit-balance.html', context)


def history(request):
    from django.utils import timezone
    from datetime import timedelta
    
    logs = SystemLog.objects.all().select_related('user')
    form = DateFilterForm(request.GET or None)
    
    # Get filter type from request
    filter_type = request.GET.get('filter_type', 'all')
    start_date = None
    end_date = None
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Apply filters based on type
    if filter_type == 'today':
        logs = logs.filter(timestamp__date=today)
        start_date = today
        end_date = today
        
    elif filter_type == 'yesterday':
        logs = logs.filter(timestamp__date=yesterday)
        start_date = yesterday
        end_date = yesterday
        
    elif filter_type == 'last_week':
        logs = logs.filter(timestamp__date__gte=week_ago)
        start_date = week_ago
        end_date = today
        
    elif filter_type == 'last_month':
        logs = logs.filter(timestamp__date__gte=month_ago)
        start_date = month_ago
        end_date = today
        
    elif filter_type == 'custom' and form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        
        if start_date:
            logs = logs.filter(timestamp__date__gte=start_date)
        if end_date:
            logs = logs.filter(timestamp__date__lte=end_date)
    
    # Order by latest first
    logs = logs.order_by('-timestamp')
    
    context = {
        'logs': logs,
        'form': form,
        'filter_type': filter_type,
        'start_date': start_date,
        'end_date': end_date,
        'total_count': logs.count(),
        'today': today,
        'yesterday': yesterday,
        'week_ago': week_ago,
        'month_ago': month_ago,
    }
    return render(request, 'home/logs.html', context)

def about_us(request):
    return render(request, 'home/about-us.html')