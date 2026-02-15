from django.shortcuts import render, redirect , get_object_or_404
from home.models import *
from .forms import *
from .models import *
from django.contrib.contenttypes.models import ContentType
from management.models import *
from django.http import HttpResponse
from django.contrib import messages
import jdatetime
# Create your views here.

def students_registration(request):

    form = StudentForm()
    students = Student.objects.all()

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, 'شاگرد موفقانه ثبت شد')

            SystemLog.objects.create(
                section="شاگردان",
                action=f"ثبت شاگرد جدید:",
                description=f"یک شاگرد جدید با نام {form.cleaned_data.get('first_name')} ثبت شد.",
                user=request.user if request.user.is_authenticated else None
            )
            return redirect('students:students_registration')

    else:
        form = StudentForm()

    form = StudentForm()
    students = Student.objects.all()
    
    context = {
        'students':students,
        'form':form,
    }

    return render(request, 'students/students-registration.html', context)

def delete_students(request, id):
    get_student_id = Student.objects.get(id=id)
    if get_student_id:
        get_student_id.delete()

        SystemLog.objects.create(
            section="شاگردان",
            action=f"حذف شاگرد:",
            description=f"شاگرد با نام {get_student_id.first_name} حذف شد.",
            user=request.user if request.user.is_authenticated else None
        )

        messages.success(request, 'شاگرد موفقانه ذخیره شد')
        return redirect('students:students_registration')
    else:
        return HttpResponse('User Is Not in Detabase')


    
def edit_students(request, id):
    get_student_id = Student.objects.get(id=id)
    if request.method == "POST":
        form = StudentForm(request.POST,request.FILES, instance=get_student_id)
        if form.is_valid():
            form.save()

            SystemLog.objects.create(
                section="شاگردان",
                action=f"تغییر اطلاعات شاگرد:",
                description=f"اطلاعات شاگرد با نام {form.cleaned_data.get('first_name')} تغییر داده شد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, f" دانش‌آموز{get_student_id.first_name} موفقانه تغییرات آورده شد.")
            return redirect('students:students_registration')  # or render response
        else:
            return HttpResponse('مشکل در تغییر شاگرد آمده ...')

    form = StudentForm(instance=get_student_id)

    context = {
        'get_student_id':get_student_id,
        'form':form,
    }
    return render(request, 'students/edit_student.html', context)

def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student_balance = StudentBalance.objects.filter(student=student).last()

    if not student_balance:
        StudentBalance.objects.create(
            student=student,
            paid=0,
            remain=0,
        )

    context = {
        'student': student,
        'student_balance': student_balance,
    }
    return render(request, 'students/student-detail.html', context)


shamsi_months = {
    "01": "حمل",
    "02": "ثور",
    "03": "جوزا",
    "04": "سرطان",
    "05": "اسد",
    "06": "سنبله",
    "07": "میزان",
    "08": "عقرب",
    "09": "قوس",
    "10": "جدی",
    "11": "دلو",
    "12": "حوت",
}

def student_fees_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    classes = SubClass.objects.all()

    context = {
        'student': student,
        'classes': classes,
    }
    return render(request, 'students/student-fees-detail.html', context)

def student_payments(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    payments = Student_fess_info.objects.filter(student=student)

    context = {
        'student': student,
        'payments': payments,
    }
    return render(request, 'students/student-payments.html', context)


def student_paid_fees(request, stu_id, cla_id):
    referer = request.META.get('HTTP_REFERER', '/')
    student = Student.objects.get(id=stu_id)
    stu_class = SubClass.objects.get(id=cla_id)
    student_balance = StudentBalance.objects.filter(student=student).last()

    if request.method == "POST":
        form = Student_fess_infoForm(request.POST)
        if form.is_valid():
            get_date = form.cleaned_data.get('date')

            orginal_fees = float(request.POST.get('orginal_fees', 0))
            paid_fees = float(request.POST.get('paid_fees', 0))
            remaining = float(request.POST.get('remaining', 0))
            waive_remaining = request.POST.get('waive_remaining') == "on"

            # Update StudentBalance
            if student_balance:
                student_balance.paid += paid_fees
                student_balance.remain += remaining
                student_balance.save()
            else:
                student_balance = StudentBalance.objects.create(
                    student=student,
                    paid=paid_fees,
                    remain=remaining
                )

            # Parse date
            try:
                day, month, year = map(int, get_date.split('/'))
            except ValueError:
                messages.error(
                    request,
                    'فرمت تاریخ نادرست است. از قالب dd/mm/yyyy استفاده کنید.'
                )
                return redirect(request.path)

            shamsi_months = {
                1: "حمل", 2: "ثور", 3: "جوزا", 4: "سرطان", 5: "اسد", 6: "سنبله",
                7: "میزان", 8: "عقرب", 9: "قوس", 10: "جدی", 11: "دلو", 12: "حوت",
            }
            month_name = shamsi_months.get(month)
            if not month_name:
                messages.error(request, "ماه نامعتبر است")
                return redirect(request.path)

            # Save Student Fees Record
            fees_info = form.save(commit=False)
            fees_info.student = student
            fees_info.st_class = stu_class
            fees_info.month = month_name
            fees_info.orginal_fees = orginal_fees
            fees_info.give_fees = paid_fees
            fees_info.remain_fees = remaining
            fees_info.not_remain = waive_remaining
            fees_info.save()

            # --- Create FinanceRecord for this payment ---
            FinanceRecord.objects.create(
                date=fees_info.date,  
                title=f"پرداخت فیس توسط {student.first_name}",
                description=f"پرداخت فیس به مبلغ {paid_fees} توسط شاگرد {student.first_name} برای صنف {stu_class.name}",
                amount=paid_fees,
                type="income",
                content_type=ContentType.objects.get_for_model(fees_info),
                object_id=fees_info.id
            )

            SystemLog.objects.create(
                section="شاگردان",
                action=f"پرداخت فیس:",
                description=f"فیس {paid_fees} برای شاگرد {student.first_name} ثبت شد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'فیس ذیل موفقانه ذخیره شد')
            return redirect('students:student_payments', student_id=student.id)
    else:
        form = Student_fess_infoForm(initial={"orginal_fees": stu_class.fees})

    context = {
        'student': student,
        'stu_class': stu_class,
        'form': form,
    }
    return render(request, 'students/student-paid-fees.html', context)


def delete_paid_fess(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    fees_record = get_object_or_404(Student_fess_info, id=id)
    student = fees_record.student
    amount = fees_record.give_fees
    remaining_amount = fees_record.remain_fees

    # Update StudentBalance
    student_balance = StudentBalance.objects.filter(student=student).last()
    if student_balance:
        student_balance.paid -= amount
        student_balance.remain -= remaining_amount
        student_balance.save()

    # Delete linked FinanceRecord (if exists)
    content_type = ContentType.objects.get_for_model(Student_fess_info)
    FinanceRecord.objects.filter(
        content_type=content_type,
        object_id=fees_record.id
    ).delete()

    # Delete the Student Fee record
    fees_record.delete()

    # Log the action
    SystemLog.objects.create(
        section="شاگردان",
        action="حذف ریکارد فیس پرداخت شده",
        description=f"ریکارد فیس پرداخت شده به مقدار {amount} برای شاگرد {student.first_name} حذف شد.",
        user=request.user if request.user.is_authenticated else None
    )

    messages.success(request, 'ریکارد پرداخت موفقانه حذف شد')
    return redirect(referer)


def edit_paid_fees(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    fess_record = get_object_or_404(Student_fess_info, id=id)
    student = fess_record.student

    student_balance = StudentBalance.objects.filter(student=student).last()
    old_paid_fees = fess_record.give_fees

    if request.method == "POST":
        form = Student_fess_infoForm(request.POST, instance=fess_record)
        if form.is_valid():
            get_date = form.cleaned_data.get('date')

            orginal_fees = float(request.POST.get('orginal_fees', 0))
            paid_fees = float(request.POST.get('paid_fees', 0))
            remaining = float(request.POST.get('remaining', 0))
            waive_remaining = request.POST.get('waive_remaining') == "on"

            try:
                day, month, year = map(int, get_date.split('/'))
            except ValueError:
                messages.error(request, 'فرمت تاریخ نادرست است. از قالب dd/mm/yyyy استفاده کنید.')
                return redirect(request.path)

            shamsi_months = {
                1: "حمل", 2: "ثور", 3: "جوزا", 4: "سرطان",
                5: "اسد", 6: "سنبله", 7: "میزان", 8: "عقرب",
                9: "قوس", 10: "جدی", 11: "دلو", 12: "حوت",
            }
            month_name = shamsi_months.get(month)

            # Update Student Balance
            diff = paid_fees - old_paid_fees
            if student_balance:
                student_balance.paid += diff
                student_balance.remain += (remaining - fess_record.remain_fees)
                student_balance.save()

            # Update FinanceRecord linked to this fee
            content_type = ContentType.objects.get_for_model(Student_fess_info)
            finance_record = FinanceRecord.objects.filter(
                content_type=content_type,
                object_id=fess_record.id
            ).first()

            if finance_record:
                finance_record.amount = paid_fees
                finance_record.description = f"فیس پرداخت شده برای شاگرد {student.first_name}"
                finance_record.save()

            # Update the fee record
            fess_record.give_fees = paid_fees
            fess_record.remain_fees = remaining
            fess_record.orginal_fees = orginal_fees
            fess_record.month = month_name
            fess_record.not_remain = waive_remaining
            fess_record.save()

            # Log the edit
            SystemLog.objects.create(
                section="شاگردان",
                action="تغییر ریکارد فیس پرداخت شده",
                description=f"ریکارد فیس پرداخت شده برای شاگرد {student.first_name} به مقدار {paid_fees} تغییر داده شد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'ریکارد فیس موفقانه ایدیت شد')
            return redirect("students:student_payments", student_id=student.id)
        else:
            return HttpResponse('فرم معتبر نیست')

    else:
        form = Student_fess_infoForm(instance=fess_record)

    context = {
        'fess_id': fess_record,
        'form': form,
    }
    return render(request, 'students/edit-student-paid-fees.html', context)


def student_activate(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_active = False

    jalali_now = jdatetime.datetime.now().strftime("%d/%m/%Y")
    student.deactivated_at = jalali_now
    
    student.save()
    SystemLog.objects.create(
        section="شاگردان",
        action=f"غیرفعال کردن شاگرد:",
        description=f"شاگرد با نام {student.first_name} غیرفعال شد.",
        user=request.user if request.user.is_authenticated else None
    )
    return redirect(request.META.get('HTTP_REFERER'))


def student_activate_on(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_active = True
    student.save()
    SystemLog.objects.create(
        section="شاگردان",
        action=f"فعال کردن شاگرد:",
        description=f"شاگرد با نام {student.first_name} فعال شد.",
        user=request.user if request.user.is_authenticated else None
    )
    return redirect(request.META.get('HTTP_REFERER'))

def student_improvment(request, id):
    student = get_object_or_404(Student, id=id)
    paid_fess_classes = Student_fess_info.objects.filter(student=student)

    if request.method == "POST":
        form = StudentImporvmentForm(request.POST, request.FILES)
        if form.is_valid():
            past_class = request.POST.get('past_class')
            past_class_instance = SubClass.objects.get(id=past_class)

            instance = form.save(commit=False)
            instance.student = student
            instance.past_class = past_class_instance
            instance.save()
            SystemLog.objects.create(
                section="شاگردان",
                action=f"ارتقاع شاگرد:",
                description=f"یک رکارد ارتقاع برای شاگرد {student.first_name} ثبت شد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, f'ارتقاع جدید برای شاگرد {student.first_name} اضافه شد')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = StudentImporvmentForm()
    
    records = StudentImporvment.objects.filter(student=student)

    context = {
        'student':student,
        'records':records,
        'form':form,
        'paid_fess_classes':paid_fess_classes,
    }
    return render(request, 'students/student-improve.html', context)

def delete_student_improvment(request, id):
    student_improvement = StudentImporvment.objects.get(id=id)
    student_improvement.delete()
    messages.success(request, f'ریکارد ارتقاع شاگرد {student_improvement.student.first_name} موفقانه حذف شد')
    SystemLog.objects.create(
        section="شاگردان",
        action=f"حذف رکارد ارتقاع شاگرد:",
        description=f"ریکارد ارتقاع برای شاگرد {student_improvement.student.first_name} حذف شد.",
        user=request.user if request.user.is_authenticated else None
    )
    return redirect(request.META.get('HTTP_REFERER'))

def edit_student_improvement(request, id):
    student_improvement = StudentImporvment.objects.get(id=id)
    if request.method == "POST":
        form = StudentImporvmentForm(request.POST, request.FILES, instance = student_improvement)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.student = student_improvement.student
            instance.save()
            messages.success(request, f'ریکارد ارتقاع شاگرد {student_improvement.student.first_name} موفقانه ایدیت شد.')
            SystemLog.objects.create(
                section="شاگردان",
                action=f"ایدیت رکارد ارتقاع شاگرد:",
                description=f"ریکارد ارتقاع برای شاگرد {student_improvement.student.first_name} ایدیت شد.",
                user=request.user if request.user.is_authenticated else None
            )
            return redirect('students:student_improvment', id=student_improvement.student.id)
        else:
            form.errors()
    else:
        form = StudentImporvmentForm(instance=student_improvement)
    
    context = {
        'form':form,
        'student_improvement':student_improvement,
    }
    return render(request, 'students/edit-student-improve.html', context)


def buy_book(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    student = Student.objects.get(id=id)
    items = Item.objects.all()

    context = {
        'student':student,
        'items':items
    }
    return render(request, 'students/student-buy-book.html', context)


def student_purchased_items(request, student_id, item_id):
    student = get_object_or_404(Student, id=student_id)
    item = get_object_or_404(Item, id=item_id)
    total_item = TotalItem.objects.filter(item=item).last()
    book_exists = BuyBook.objects.filter(student=student, item=item).exists()
    student_balance = StudentBalance.objects.filter(student=student).last()
    
    if request.method == 'POST':
        form = BuyBookForm(request.POST)
        if form.is_valid():
            try:
                amount = int(request.POST.get('amount', 1))
                per_price = float(request.POST.get('per_price', 0))
                total_price = float(request.POST.get('total_price', 0))
                paid_price = float(request.POST.get('paid_price', 0))
                remain_price = float(request.POST.get('remain_price', 0))
                
                # Save BuyBook record
                buy_book = form.save(commit=False)
                buy_book.student = student
                buy_book.item = item
                buy_book.number_of_book = amount
                buy_book.per_price = per_price
                buy_book.total_amount = total_price
                buy_book.paid_amount = paid_price
                buy_book.remain_amount = remain_price
                buy_book.save()

                # --- Create FinanceRecord ---
                content_type = ContentType.objects.get_for_model(BuyBook)

                finance_record = FinanceRecord.objects.create(
                    date=buy_book.date, 
                    title=f"خرید کتاب: {item.name} توسط {student.first_name}",
                    amount=paid_price,
                    description=f"خرید {amount} کتاب {item.name} توسط {student.first_name}.",
                    type='income',  # because student is paying money
                    content_type=content_type,
                    object_id=buy_book.id,
                )

                # Update TotalItem
                if total_item:
                    total_item.total_remain_item -= amount
                    total_item.save()

                    # 🔔 اگر موجودی کم شد → ساخت Notification
                    if total_item.total_remain_item <= 4:

                        content_type = ContentType.objects.get_for_model(TotalItem)

                        # جلوگیری از ثبت چندباره
                        notif_exists = Notification.objects.filter(
                            content_type=content_type,
                            object_id=total_item.id,
                            is_read=False
                        ).exists()

                        if not notif_exists:
                            Notification.objects.create(
                                title="کمبود موجودی کتاب",
                                message=f"موجودی {item.name} به {total_item.total_remain_item} عدد رسید",
                                notification_date=jdatetime.date.today().strftime("%Y/%m/%d"),
                                content_type=content_type,
                                object_id=total_item.id   # 👈 ذخیره آیتم در Generic FK
                            )


                # Update StudentBalance
                if student_balance:
                    student_balance.paid += paid_price
                    student_balance.remain += remain_price
                    student_balance.save()

                SystemLog.objects.create(
                    section="شاگردان",
                    action=f"خرید کتاب:",
                    description=f"شاگرد {student.first_name} کتاب {item.name} را به تعداد {amount} خریداری کرد.",
                    user=request.user if request.user.is_authenticated else None
                )

                messages.success(request, 'خرید کتاب با موفقیت ثبت شد و در مالی ثبت شد.')
                return redirect('students:student_detail', student_id=student.id)
                
            except Exception as e:
                messages.error(request, f'خطا در ثبت خرید: {str(e)}')
    else:
        form = BuyBookForm()
    
    context = {
        'student': student,
        'item_id': item,
        'total_item': total_item,
        'form': form,
        'total_item_balance': total_item.total_remain_item if total_item else 0,
        'book_exists': book_exists,
    }
    return render(request, 'students/student-purchased-items.html', context)


def delete_student_purchased_items(request, purchase_id):
    purchased_record = BuyBook.objects.get(id=purchase_id)

    # Update TotalItem
    total_item = TotalItem.objects.filter(item=purchased_record.item).last()
    if total_item:
        total_item.total_remain_item += purchased_record.number_of_book
        total_item.save()

    # Update StudentBalance
    student_balance = StudentBalance.objects.filter(student=purchased_record.student).last()
    if student_balance:
        student_balance.paid -= purchased_record.paid_amount
        student_balance.remain -= purchased_record.remain_amount
        student_balance.save()

    # Delete related FinanceRecord
    content_type = ContentType.objects.get_for_model(BuyBook)
    FinanceRecord.objects.filter(
        content_type=content_type,
        object_id=purchase_id
    ).delete()

    # Log the deletion
    SystemLog.objects.create(
        section="شاگردان",
        action="حذف ریکارد خرید کتاب",
        description=f"ریکارد خرید کتاب {purchased_record.item.name} برای شاگرد {purchased_record.student.first_name} حذف شد.",
        user=request.user if request.user.is_authenticated else None
    )

    purchased_record.delete()
    messages.success(request, 'ریکارد خرید موفقانه حذف شد')
    return redirect(request.META.get('HTTP_REFERER'))


def edit_student_purchased_items(request, purchase_id):
    purchase = BuyBook.objects.get(id=purchase_id)
    old_amount = purchase.number_of_book
    old_paid = purchase.paid_amount
    old_remain = purchase.remain_amount

    if request.method == 'POST':
        form = BuyBookForm(request.POST, instance=purchase)
        if form.is_valid():
            amount = int(request.POST.get('amount', 1))
            per_price = float(request.POST.get('per_price', 0))
            total_price = float(request.POST.get('total_price', 0))
            paid_price = float(request.POST.get('paid_price', 0))
            remain_price = float(request.POST.get('remain_price', 0))

            instance = form.save(commit=False)

            # Update TotalItem
            total_item = TotalItem.objects.filter(item=purchase.item).last()
            if total_item:
                difference = amount - old_amount
                total_item.total_remain_item -= difference
                total_item.save()

            # Update StudentBalance
            student_balance = StudentBalance.objects.filter(student=purchase.student).last()
            if student_balance:
                student_balance.paid += (paid_price - old_paid)
                student_balance.remain += (remain_price - old_remain)
                student_balance.save()

            # --- Update linked FinanceRecord ---
            content_type = ContentType.objects.get_for_model(BuyBook)
            finance_record = FinanceRecord.objects.filter(
                content_type=content_type,
                object_id=purchase.id
            ).last()
            if finance_record:
                # Update the amount
                finance_record.amount = total_price
                finance_record.title = f"خرید کتاب توسط {purchase.student.first_name}"
                finance_record.description = f"خرید {amount} عدد از کتاب {purchase.item.name} توسط شاگرد {purchase.student.first_name}"
                finance_record.save()

            # Update purchase instance
            instance.number_of_book = amount
            instance.per_price = per_price
            instance.total_amount = total_price
            instance.paid_amount = paid_price
            instance.remain_amount = remain_price
            instance.save()

            SystemLog.objects.create(
                section="شاگردان",
                action="تغییر ریکارد خرید کتاب",
                description=f"ریکارد خرید کتاب {purchase.item.name} برای شاگرد {purchase.student.first_name} تغییر داده شد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'ریکارد خرید موفقانه ایدیت شد')
            return redirect('students:student_purchased', student_id=purchase.student.id)
    else:
        form = BuyBookForm(instance=purchase)

    context = {
        'form': form,
        'purchase': purchase,
        'student': purchase.student,
    }
    return render(request, 'students/edit-student-purchased-item.html', context)


def student_purchased(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    purchased_books = BuyBook.objects.filter(student=student)

    context = {
        'student': student,
        'purchased_books': purchased_books,
    }
    return render(request, 'students/student-purchased.html', context)


def student_paid_remain_money(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student_balance = StudentBalance.objects.filter(student=student).last()
    current_remain = student_balance.remain if student_balance else 0

    if request.method == "POST":
        form = StudentPaidRemainAmountForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.student = student
            instance.save()

            paid_amount = instance.paid

            # Update Student Balance
            if student_balance:
                student_balance.paid += paid_amount
                student_balance.remain -= paid_amount
                student_balance.save()

            # Create Finance Record (Income)
            FinanceRecord.objects.create(
                date=instance.date,
                title=f"پرداخت باقی‌مانده شاگرد {student.first_name}",
                amount=paid_amount,
                type="income",
                description=instance.description or f"پرداخت باقی‌مانده توسط شاگرد {student.first_name}",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
            )

            # System Log
            SystemLog.objects.create(
                section="شاگردان",
                action="پرداخت باقی‌مانده",
                description=f"شاگرد {student.first_name} مبلغ {paid_amount} از باقی‌مانده خود را پرداخت کرد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, "پرداخت باقی‌مانده موفقانه ثبت شد")
            return redirect("students:student_paid_remain_money", student_id=student.id)
    else:
        form = StudentPaidRemainAmountForm()
    
    paid_remain_records = StudentPaidRemainAmount.objects.filter(student=student)

    context = {
        'student': student,
        'form': form,
        'student_balance': student_balance,
        'current_remain': current_remain,
        'paid_remain_records':paid_remain_records
    }
    return render(request, 'students/student-paid-remain.html', context)


def delete_student_paid_remain(request, id):
    referer = request.META.get('HTTP_REFERER', '/')

    remain_record = get_object_or_404(StudentPaidRemainAmount, id=id)
    student = remain_record.student
    paid_amount = remain_record.paid

    # Update student balance
    student_balance = StudentBalance.objects.filter(student=student).last()
    if student_balance:
        student_balance.paid -= paid_amount
        student_balance.remain += paid_amount

        # prevent negative values
        student_balance.paid = max(student_balance.paid, 0)
        student_balance.remain = max(student_balance.remain, 0)

        student_balance.save()

    # Delete linked finance record
    content_type = ContentType.objects.get_for_model(StudentPaidRemainAmount)
    FinanceRecord.objects.filter(
        content_type=content_type,
        object_id=remain_record.id
    ).delete()

    # Log
    SystemLog.objects.create(
        section="شاگردان",
        action="حذف پرداخت باقی‌مانده:",
        description=f"پرداخت باقی‌مانده به مقدار {paid_amount} برای شاگرد {student.first_name} حذف شد.",
        user=request.user if request.user.is_authenticated else None
    )

    remain_record.delete()
    messages.success(request, "ریکارد پرداخت باقی‌مانده حذف شد")

    return redirect(referer)


def edit_student_paid_remain(request, id):
    remain_record = get_object_or_404(StudentPaidRemainAmount, id=id)
    student = remain_record.student
    student_balance = StudentBalance.objects.filter(student=student).last()

    old_paid = remain_record.paid

    if request.method == "POST":
        form = StudentPaidRemainAmountForm(request.POST, instance=remain_record)
        if form.is_valid():
            new_paid = float(form.cleaned_data.get("paid") or 0)
            diff = new_paid - old_paid

            # Prevent over payment
            if student_balance and diff > student_balance.remain:
                messages.error(request, "مقدار پرداخت بیشتر از باقی‌مانده شاگرد است")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # Update student balance
            if student_balance:
                student_balance.paid += diff
                student_balance.remain -= diff

                # prevent negative values
                student_balance.paid = max(student_balance.paid, 0)
                student_balance.remain = max(student_balance.remain, 0)

                student_balance.save()

            # Save record
            instance = form.save(commit=False)
            instance.student = student
            instance.save()

            # Update linked finance record
            content_type = ContentType.objects.get_for_model(StudentPaidRemainAmount)
            finance_record = FinanceRecord.objects.filter(
                content_type=content_type,
                object_id=remain_record.id
            ).last()

            if finance_record:
                finance_record.amount = new_paid
                finance_record.description = f"پرداخت باقی‌مانده توسط شاگرد {student.first_name}"
                finance_record.date = instance.date
                finance_record.save()

            SystemLog.objects.create(
                section="شاگردان",
                action="تغییر پرداخت باقی‌مانده:",
                description=f"پرداخت باقی‌مانده شاگرد {student.first_name} از {old_paid} به {new_paid} تغییر کرد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, "پرداخت باقی‌مانده موفقانه ویرایش شد")
            return redirect("students:student_detail", student_id=student.id)

    else:
        form = StudentPaidRemainAmountForm(instance=remain_record)

    return render(request, "students/edit-student-paid-remain.html", {
        "form": form,
        "record": remain_record,
        "student": student,
    })
