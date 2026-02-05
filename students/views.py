from django.urls import reverse
from django.shortcuts import render, redirect , get_object_or_404
from decimal import Decimal
from management.models import *
from .forms import *
from django.db import transaction
from .models import *
from django.http import HttpResponse
from django.db.models import Sum
from django.contrib import messages
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
# Create your views here.

def students_registration(request):

    form = StudentForm()
    students = Student.objects.filter(is_active=True)

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, 'شاگرد موفقانه ثبت شد')
            return redirect('students:students_registration')
    else:
        form = StudentForm()

    form = StudentForm()
    students = Student.objects.filter(is_active=True)

    context = {
        'students':students,
        'form':form,
    }

    return render(request, 'students/students-registration.html', context)

def delete_students(request, id):
    get_student_id = Student.objects.get(id=id)
    if get_student_id:
        get_student_id.delete()
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

def student_bill(request, student_id, fees_id):
    get_student_fees = Student_fess_info.objects.get(id=fees_id)
    student = Student.objects.get(id=student_id)
    return render(request, 'students/student-bill.html', {
        'student': student,
        'get_student_fees':get_student_fees,
    })


def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student_balance = StudentBalance.objects.filter(student=student).last()
    if not student_balance:
        StudentBalance.objects.create(
            student=student,
            paid=0,
            remain=0,
        )

    if request.method == "POST":
        paid_amount = request.POST.get('paid_amount')
        remain_amount = request.POST.get('remain_amount')

        StudentBalance.objects.filter(student=student).delete()

        StudentBalance.objects.create(
            student=student,
            paid=paid_amount,
            remain=remain_amount,
        )
        messages.success(request, 'بیلانس موفقانه اضافه شد، و بیلانس گذشته حذف شد.')
        return redirect('students:student_detail', student.id)

    context = {
        'student': student,
        'student_balance': student_balance
    }
    return render(request, 'students/student-detail.html', context)


# Mapping Shamsi month numbers to names in Dari
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
    income_expenses = TotalBalance.objects.last()

    if request.method == "POST":
        form = Student_fess_infoForm(request.POST)
        if form.is_valid():
            get_date = form.cleaned_data.get('date')

            orginal_fess = float(request.POST.get('orginal_fees'))
            paid_fees = float(request.POST.get('paid_fees'))
            remaining = float(request.POST.get('remaining'))

            waive_remaining = request.POST.get('waive_remaining') == "on"

            student_balance.paid += paid_fees
            student_balance.remain += remaining
            student_balance.save()

            income_expenses.total_income += paid_fees
            income_expenses.total_receivable += remaining
            income_expenses.save()

            try:
                day, month, year = map(int, get_date.split('/'))

            except ValueError:
                messages.error(
                    request,
                    'فرمت تاریخ نادرست است. از قالب dd/mm/yyyy استفاده کنید.'
                )
                return redirect(request.path)

            shamsi_months = {
                1: "حمل",
                2: "ثور",
                3: "جوزا",
                4: "سرطان",
                5: "اسد",
                6: "سنبله",
                7: "میزان",
                8: "عقرب",
                9: "قوس",
                10: "جدی",
                11: "دلو",
                12: "حوت",
            }

            month_name = shamsi_months.get(month)

            if not month_name:
                messages.error(request, "ماه نامعتبر است")
                return redirect(request.path)

            fees_info = form.save(commit=False)
            fees_info.student = student 
            fees_info.st_class = stu_class 
            fees_info.month = month_name
            fees_info.orginal_fees = orginal_fess
            fees_info.give_fees = paid_fees
            fees_info.remain_fees = remaining
            fees_info.not_remain = waive_remaining
            fees_info.save()

            messages.success(request, 'فیس ذیل موفقانه ذخیره شد')
            return redirect('students:student_payments', student_id=student.id)
    else:
        form = Student_fess_infoForm(initial={"orginal_fees": stu_class.fees})

    context = {
        'student':student,
        'stu_class':stu_class,
        'form':form,
    }
    return render(request, 'students/student-paid-fees.html', context)

def delete_paid_fess(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    fess_id = Student_fess_info.objects.get(id=id)
    student = fess_id.student
    amount = fess_id.give_fees

    student_balance = StudentBalance.objects.filter(student=student).last()

    student_balance.paid -= amount
    student_balance.remain -= fess_id.remain_fees
    student_balance.save()

    income_expenses = TotalBalance.objects.last()
    income_expenses.total_income -= amount
    income_expenses.total_receivable -= fess_id.remain_fees
    income_expenses.save()

    messages.success(request, 'ریکارد پرداخت موفقانه حذف شد')
    fess_id.delete()
    return redirect(referer)

def edit_paid_fees(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    fess_id = Student_fess_info.objects.get(id=id)
    student = fess_id.student

    student_balance = StudentBalance.objects.filter(student=student).last()
    income_expenses = TotalBalance.objects.last()

    old_paid_fess = fess_id.give_fees

    if request.method == "POST":
        form = Student_fess_infoForm(request.POST, instance=fess_id)
        if form.is_valid():
         
            get_date = form.cleaned_data.get('date')

            orginal_fess = float(request.POST.get('orginal_fees'))
            paid_fees = float(request.POST.get('paid_fees'))
            remaining = float(request.POST.get('remaining'))

            waive_remaining = request.POST.get('waive_remaining') == "on"

            try:
                day, month, year = map(int, get_date.split('/'))

            except ValueError:
                messages.error(
                    request,
                    'فرمت تاریخ نادرست است. از قالب dd/mm/yyyy استفاده کنید.'
                )
                return redirect(request.path)

            shamsi_months = {
                1: "حمل",
                2: "ثور",
                3: "جوزا",
                4: "سرطان",
                5: "اسد",
                6: "سنبله",
                7: "میزان",
                8: "عقرب",
                9: "قوس",
                10: "جدی",
                11: "دلو",
                12: "حوت",
            }

            instance = form.save(commit=False)

            month_name = shamsi_months.get(month)

            if paid_fees >= old_paid_fess:
                defference = paid_fees - old_paid_fess
                
                fess_id.give_fees += defference
                fess_id.remain_fees -= defference
                fess_id.save()

                student_balance.paid += defference
                student_balance.remain -= defference
                student_balance.save()

                income_expenses.total_income += defference
                income_expenses.total_receivable -= defference
                income_expenses.save()

            else:
                
                defference = old_paid_fess - paid_fees
                
                fess_id.give_fees -= defference
                fess_id.remain_fees += defference
                fess_id.save()

                student_balance.paid -= defference
                student_balance.remain += defference
                student_balance.save()

                income_expenses.total_income -= defference
                income_expenses.total_receivable += defference
                income_expenses.save()

            instance.student = student 
            instance.st_class = fess_id.st_class 
            instance.month = month_name
            instance.orginal_fees = orginal_fess
            instance.not_remain = waive_remaining
            instance.save()
           
            messages.success(request, 'ریکارد ذیل موفقانه ایدیت شد')
            return redirect("students:student_payments", student_id=student.id)
        else:
            return HttpResponse('Form Is Not Valid')

    else:
        form = Student_fess_infoForm(instance=fess_id)

    context = {
        'fess_id':fess_id,
        'form':form,
    }
    return render(request, 'students/edit-student-paid-fees.html', context)

def student_activate(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_active = False
    student.save()
    return redirect(request.META.get('HTTP_REFERER'))


def student_activate_on(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_active = True
    student.save()
    return redirect(request.META.get('HTTP_REFERER'))

def student_improvment(request, id):
    student = get_object_or_404(Student, id=id)
    if request.method == "POST":
        form = StudentImporvmentForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.student = student
            instance.save()
            messages.success(request, f'ارتقاع جدید برای شاگرد {student.first_name} اضافه شد')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = StudentImporvmentForm()
    
    records = StudentImporvment.objects.filter(student=student)

    context = {
        'student':student,
        'records':records,
        'form':form,
    }
    return render(request, 'students/student-improve.html', context)

def delete_student_improvment(request, id):
    student_improvement = StudentImporvment.objects.get(id=id)
    student_improvement.delete()
    messages.success(request, f'ریکارد ارتقاع شاگرد {student_improvement.student.first_name} موفقانه حذف شد')
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

def student_improvement_classes(request, id):
    student = Student.objects.get(id=id)
    student_classes = student.classs.all()
    return render(request, 'students/student-class-improvemtn.html')


def student_buy_item(request, student_id):
    student = Student.objects.get(id=id)
    return render(request, 'students/student-buy-item.html')


def buy_book(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    student = Student.objects.get(id=id)
    
    if request.method == "POST":
        boos = request.POST.getlist('books')
        form_type = request.POST.get('form_type')
        if form_type == "buy-book":
            buy_book_form = BuyBookForm(request.POST)
            if buy_book_form.is_valid():
                get_paid_amount = float(request.POST.get('paid_amount'))
                book_ids = request.POST.getlist('books')

                total_price = 0
                book_records = []

                with transaction.atomic():
                    for tb_id in book_ids:
                        qty = int(request.POST.get(f'quantity_{tb_id}', 0))
                        print(f"qty {qty}")
                        if qty <= 0:
                            continue

                        tb = TotalBook.objects.select_for_update().get(id=tb_id)

                        # price calculation
                        line_total = tb.per_price * qty
                        print(f"line_total {line_total}")
                        total_price += line_total
                        if get_paid_amount > total_price:
                            messages.error(request, 'مقدار پرداخت بیشتر از مقدار مجموعی است')
                            return redirect(referer)
                        print(f"total_price {total_price}")
                        # update stock
                        tb.total_amount -= qty
                        tb.save()

                        # prepare book record
                        book_records.append({
                            "book": tb,
                            "qty": qty,
                            "line_total": line_total
                        })

                    # Calculate remaining money
                    remain_amount = total_price - get_paid_amount
                    print(f"remain_amount {remain_amount}")
                    # Update TotalIncome
                    total_income, _ = TotalIncome.objects.get_or_create(pk=1, defaults={'total_amount': 0})
                    total_income.total_amount += get_paid_amount
                    total_income.save()

                    # Save remaining money if student didn't pay full
                    if remain_amount > 0:
                        student_remain, _ = StudentRemailMoney.objects.get_or_create(
                            student=student, defaults={'amount': 0}
                        )
                        student_remain.amount += remain_amount
                        student_remain.save()

                instance = buy_book_form.save(commit=False)
                instance.student = student
                instance.number_of_book = sum(b["qty"] for b in book_records)
                instance.total_amount = total_price
                instance.remain_amount = remain_amount
                instance.save()
                instance.book.set([b["book"].id for b in book_records])

                # Save BookRecords with correct total_amount
                for b in book_records:
                    # b["book"] is a TotalBook instance
                    book_instance = b["book"].book  # get the actual Books instance

                    per_price_for_buy = book_instance.per_book_price_for_buy
                    qty = b["qty"]
                    line_total = qty * per_price_for_buy  # calculate total amount correctly

                    BookRecord.objects.create(
                        student=student,
                        book=book_instance,
                        buy_book=instance,
                        date=instance.date,
                        number_of_book=qty,
                        total_amount=line_total
                    )

                return redirect('students:buy_book', id=student.id)
        else:
            # Stationery purchase
            buy_stationery_form = BuyStationeryForm(request.POST)
            if buy_stationery_form.is_valid():
                get_paid_amount = float(request.POST.get('paid_stationery_amount', 0))
                stationery_ids = request.POST.getlist('stationery')
                total_price = 0
                qty_dict = {}

                # First, calculate total price
                for ts_id in stationery_ids:
                    qty = int(request.POST.get(f'quantity_{ts_id}', 0)) or 1
                    ts = TotalStationery.objects.select_for_update().get(id=ts_id)
                    line_total = ts.per_price * qty
                    total_price += line_total
                    if get_paid_amount > total_price:
                        messages.error(request, 'مقدار پرداخت بیشتر از مقدار مجموعی است')
                        return redirect(referer)
                    qty_dict[ts_id] = qty

                remain_amount = total_price - get_paid_amount

                with transaction.atomic():
                    # Save BuyStationery instance first
                    instance = buy_stationery_form.save(commit=False)
                    instance.student = student
                    instance.number_of_stationery = sum(qty_dict.values())
                    instance.total_stationery_amount = total_price
                    instance.remain_amount = remain_amount
                    instance.paid_stationery_amount = get_paid_amount
                    instance.save()
                    instance.stationery.set(stationery_ids)

                    # Now create StationeryRecord
                    for ts_id in stationery_ids:
                        ts = TotalStationery.objects.select_for_update().get(id=ts_id)
                        qty = qty_dict[ts_id]
                        line_total = ts.per_price * qty

                        # Update stock
                        ts.total_stationery -= qty
                        ts.save()

                        StationeryRecord.objects.create(
                            student=student,
                            stationery=ts.stationery,  # must be StationeryItem instance
                            buy_stationery=instance,
                            date=instance.date,
                            number_of_stationery=qty,
                            total_amount=line_total
                        )

                    # Update TotalIncome
                    total_income, _ = TotalIncome.objects.get_or_create(pk=1, defaults={'total_amount': 0})
                    total_income.total_amount += get_paid_amount
                    total_income.save()

                    # Save remaining money
                    if remain_amount > 0:
                        student_remain, _ = StudentRemailMoney.objects.get_or_create(
                            student=student, defaults={'amount': 0}
                        )
                        student_remain.amount += remain_amount
                        student_remain.save()

                return redirect('students:buy_book', id=student.id)


    buy_book_form = BuyBookForm()
    buy_stationery_form = BuyStationeryForm()
    buy_book_records = BuyBook.objects.filter(student=id)
    buy_stationery_records = BuyStationery.objects.filter(student=id)

    all_records = []

    # append book records
    for rec in buy_book_records:
        all_records.append({
            "id": rec.id,
            "date": rec.date,
            "type": "کتاب",
            "names": [b.name for b in rec.book.all()],   # ✅ book names
            "total": rec.total_amount,
            "paid": rec.paid_amount,
            "remain": rec.remain_amount,
            "desc": rec.description,
            "more_info": reverse('students:student_buyed_book', args=[rec.student.id, rec.id]),
            "delete_link": reverse('students:delete_student_buy_book', args=[rec.id]),
            "edit_link": reverse('students:edit_student_buy_book', args=[rec.student.id, rec.id]),
        })

    # append stationery records
    for rec in buy_stationery_records:
        all_records.append({
            "id": rec.id,
            "date": rec.date,
            "type": "قرطاسیه",
            "names": [s.name for s in rec.stationery.all()],  # ✅ stationery names
            "total": rec.total_stationery_amount,
            "paid": rec.paid_stationery_amount,
            "remain": rec.remain_amount,
            "desc": rec.description,
            "more_info_stationery": reverse('students:student_buyed_stationery', args=[rec.student.id, rec.id]),
            "delete_link": reverse('students:delete_student_buy_stationery', args=[rec.id]),
            "edit_link": reverse('students:edit_student_buy_book', args=[rec.student.id, rec.id]),
        })

    # optional: sort all records (by id or date)
    all_records = sorted(all_records, key=lambda x: x["id"], reverse=True)

    context = {
        'student':student,
        'buy_book_form':buy_book_form,
        'buy_stationery_form':buy_stationery_form,
        'all_records':all_records,
    }
    return render(request, 'students/student-buy-book.html', context)

def delete_student_buy_book(request, id):
    referer = request.META.get("HTTP_REFERER", "/")
    buy_book = get_object_or_404(BuyBook, id=id)

    try:
        with transaction.atomic():
            # 1. Subtract paid amount from TotalIncome
            total_income, _ = TotalIncome.objects.get_or_create(pk=1, defaults={'total_amount': 0})
            total_income.total_amount -= buy_book.paid_amount
            total_income.save()

            # 2. Subtract remain_amount from student's remain money
            if buy_book.remain_amount > 0:
                student_remain, _ = StudentRemailMoney.objects.get_or_create(
                    student=buy_book.student, defaults={'amount': 0}
                )
                student_remain.amount -= buy_book.remain_amount
                if student_remain.amount < 0:
                    student_remain.amount = 0
                student_remain.save()

            # 3. Restore the book stock
            for book in buy_book.book.all():
                try:
                    # Find the BookRecord for qty
                    record = BookRecord.objects.filter(buy_book=buy_book, book=book).first()
                    if record:
                        total_book = TotalBook.objects.get(book=book)
                        total_book.total_amount += record.number_of_book
                        total_book.save()
                        record.delete()  # 4. delete BookRecord
                except TotalBook.DoesNotExist:
                    pass

            # 5. Delete BuyBook record
            buy_book.delete()

            messages.success(request, "خریداری کتاب موفقانه حذف شد ✅")

    except Exception as e:
        messages.error(request, f"خطا در حذف ریکارد: {e}")
    return redirect(referer)


def delete_student_buy_stationery(request, id):
    referer = request.META.get("HTTP_REFERER", "/")
    buy_book = get_object_or_404(BuyStationery, id=id)

    try:
        with transaction.atomic():
            # 1. Subtract paid amount from TotalIncome
            total_income, _ = TotalIncome.objects.get_or_create(pk=1, defaults={'total_amount': 0})
            total_income.total_amount -= buy_book.paid_stationery_amount
            total_income.save()

            # 2. Subtract remain_amount from student's remain money
            if buy_book.remain_amount > 0:
                student_remain, _ = StudentRemailMoney.objects.get_or_create(
                    student=buy_book.student, defaults={'amount': 0}
                )
                student_remain.amount -= buy_book.remain_amount
                if student_remain.amount < 0:
                    student_remain.amount = 0
                student_remain.save()

            # 3. Restore the book stock
            for book in buy_book.stationery.all():
                try:
                    # Find the BookRecord for qty
                    record = StationeryRecord.objects.filter(buy_stationery=buy_book, stationery=book).first()
                    if record:
                        total_book = TotalStationery.objects.get(stationery=book)
                        total_book.total_stationery += record.number_of_stationery
                        total_book.save()
                        record.delete()  # 4. delete BookRecord
                except TotalBook.DoesNotExist:
                    pass

            # 5. Delete BuyBook record
            buy_book.delete()

            messages.success(request, "خریداری قرطاسیه موفقانه حذف شد ✅")

    except Exception as e:
        messages.error(request, f"خطا در حذف ریکارد: {e}")
    return redirect(referer)


def edit_student_buy_book(request, student_id, buybook_id):
    student = get_object_or_404(Student, id=student_id)
    buy_book = get_object_or_404(BuyBook, id=buybook_id)
    total_book = TotalBook.objects.all()

    if request.method == "POST":
        form = BuyBookForm(request.POST, instance=buy_book)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # -------------------------------
                    # 1. Reverse old purchase
                    # -------------------------------
                    total_income, _ = TotalIncome.objects.get_or_create(pk=1, defaults={'total_amount': 0})
                    total_income.total_amount -= buy_book.paid_amount
                    total_income.save()

                    if buy_book.remain_amount > 0:
                        student_remain, _ = StudentRemailMoney.objects.get_or_create(
                            student=student, defaults={'amount': 0}
                        )
                        student_remain.amount -= buy_book.remain_amount
                        if student_remain.amount < 0:
                            student_remain.amount = 0
                        student_remain.save()

                    # restore old stock
                    for record in BookRecord.objects.filter(buy_book=buy_book):
                        try:
                            total_book = TotalBook.objects.get(book=record.book)
                            total_book.total_amount += record.number_of_book
                            total_book.save()
                        except TotalBook.DoesNotExist:
                            pass
                    # delete old BookRecords
                    BookRecord.objects.filter(buy_book=buy_book).delete()

                    # -------------------------------
                    # 2. Apply new purchase
                    # -------------------------------
                    # get_paid_amount = float(request.POST.get('paid_amount', 0))
                    get_paid_amount = Decimal(request.POST.get('paid_amount', 0) or 0)
                    old_paid_amount = Decimal(buy_book.paid_amount or 0)
                    difference = get_paid_amount - old_paid_amount
                    
                    book_ids = request.POST.getlist('books')
                    total_price = 0
                    book_records = []

                    for tb_id in book_ids:
                        qty = int(request.POST.get(f'quantity_{tb_id}', 0))
                        if qty <= 0:
                            continue
                        tb = TotalBook.objects.select_for_update().get(id=tb_id)
                        line_total = tb.per_price * qty
                        total_price += line_total

                        # reduce stock
                        tb.total_amount -= qty
                        tb.save()

                        book_records.append({
                            "book": tb.book,  # Books instance
                            "qty": qty,
                            "line_total": line_total,
                        })

                    remain_amount = total_price - get_paid_amount

                    # Update total income correctly
                    total_income.total_amount += difference
                    total_income.save(update_fields=['total_amount'])

                    if remain_amount > 0:
                        student_remain, _ = StudentRemailMoney.objects.get_or_create(
                            student=student, defaults={'amount': 0}
                        )
                        student_remain.amount += remain_amount
                        student_remain.save()

                    # save BuyBook instance
                    instance = form.save(commit=False)
                    instance.student = student
                    instance.number_of_book = qty
                    instance.total_amount = total_price
                    instance.remain_amount = remain_amount
                    instance.paid_amount = get_paid_amount
                    instance.save()
                    instance.book.set([b["book"].id for b in book_records])

                    # recreate BookRecords
                    for b in book_records:
                        BookRecord.objects.create(
                            student=student,
                            book=b["book"],
                            buy_book=instance,
                            date=instance.date,
                            number_of_book=b["qty"],
                            total_amount=b["line_total"]
                        )

                    messages.success(request, "خریداری کتاب موفقانه ویرایش شد ✅")
                    return redirect("students:buy_book", id=student.id)

            except Exception as e:
                messages.error(request, f"خطا در ویرایش: {e}")

    else:
        form = BuyBookForm(instance=buy_book)

    # show old BookRecords for this BuyBook
    records = BookRecord.objects.filter(buy_book=buy_book)

    return render(request, "students/edit-buy-book.html", {
        "form": form,
        "student": student,
        "buy_book": buy_book,
        "records": records,
        "total_book": total_book,
    })


def student_paid_Remain_money(request, id):
    referer = request.META.get('HTTP_REFERER', '/')

    student = Student.objects.get(id=id)
    get_remain_money = StudentRemailMoney.objects.filter(student=student).first()
    total = TotalIncome.objects.get(pk=1)
    remain_money_records = StudentGiveRemainMoney.objects.filter(studnet=student)

    if request.method == "POST":
        g_form = StudentGiveRemainMoneyForm(request.POST)
        if g_form.is_valid():
            get_Amount = g_form.cleaned_data.get('amount')
            if get_Amount > get_remain_money.amount:
                messages.error(request, 'مقدار برای پرداخت قرض بیشتر از مقدار قرض است')
                return redirect(referer)
            get_remain_money.amount -= get_Amount
            instance = g_form.save(commit=False)
            get_remain_money.save()
            total.total_amount += get_Amount
            total.save()
            instance.studnet = student
            instance.save()
            messages.success(request, 'ریکارد پرداخت قرض موفقانه اضافه شد')
            return redirect(referer)

    else:
        g_form = StudentGiveRemainMoneyForm()

    context = {
        'student':student,
        'g_form':g_form,
        'remain_money_records':remain_money_records,
        'get_remain_money':get_remain_money,
    }
    return render(request, 'students/student-remain-money.html', context)

def delete_paid_remain_money(request, id):
    remain_id = StudentGiveRemainMoney.objects.get(id=id)
    get_remain_money = StudentRemailMoney.objects.get(student=remain_id.studnet)
    total = TotalIncome.objects.get(pk=1)

    total.total_amount -= remain_id.amount
    get_remain_money.amount += remain_id.amount 

    total.save()
    get_remain_money.save()
    remain_id.delete()
    messages.success(request, 'ریکارد ذیل موفقانه حذف شد')
    return redirect(request.META.get('HTTP_REFERER', '/'))

def edit_paid_remain_money(request, id):
    remain_record = get_object_or_404(StudentGiveRemainMoney, id=id)
    student = remain_record.studnet  # keep your model spelling if "studnet"
    get_remain_money = get_object_or_404(StudentRemailMoney, student=student)
    total = TotalIncome.objects.get(pk=1)

    # Convert stored floats to Decimals safely
    past_amount = Decimal(str(remain_record.amount))
    total_amount = Decimal(str(total.total_amount))
    remain_amount = Decimal(str(get_remain_money.amount))

    if request.method == "POST":
        form = StudentGiveRemainMoneyForm(request.POST, instance=remain_record)
        if form.is_valid():
            new_amount = Decimal(str(form.cleaned_data.get("amount")))

            # Step 1: Undo old payment
            remain_amount += past_amount
            total_amount -= past_amount

            # Step 2: Check if new amount is valid
            if new_amount > remain_amount:
                messages.error(request, "مقدار پرداخت شده بیشتر از مقدار قرض باقی‌مانده است")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # Step 3: Apply new payment
            remain_amount -= new_amount
            total_amount += new_amount

            # Step 4: Save all changes
            get_remain_money.amount = remain_amount
            total.total_amount = total_amount

            get_remain_money.save()
            total.save()
            form.save()

            messages.success(request, "ریکارد پرداخت قرض موفقانه ویرایش شد")
            return redirect("students:student_paid_Remain_money", id=student.id)
    else:
        form = StudentGiveRemainMoneyForm(instance=remain_record)

    context = {
        "form": form,
        "remain_record": remain_record,
        "student": student,
        "get_remain_money": get_remain_money,
    }
    return render(request, "students/edit-remain-money.html", context)

def student_buyed_book(request, stu_id, book_id):
    student = Student.objects.get(id=stu_id)
    book_id = BuyBook.objects.get(id=book_id)
    buyed_books = BookRecord.objects.filter(buy_book=book_id)

    context = {
        'student':student,
        'book_id':book_id,
        'buyed_books':buyed_books,
    }
    return render(request, 'students/student-buyed-books.html', context)

def student_buyed_stationery(request, stu_id, stationery_id):
    student = Student.objects.get(id=stu_id)
    stationery_id = BuyStationery.objects.get(id=stationery_id)

    buyed_stationeyies = StationeryRecord.objects.filter(buy_stationery=stationery_id)

    context = {
        'student':student,
        'stationery_id':stationery_id,
        'buyed_stationeyies':buyed_stationeyies,
    }
    return render(request, 'students/student-buyed-stationeries.html', context)