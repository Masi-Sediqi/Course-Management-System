from django.urls import reverse
from django.shortcuts import render, redirect , get_object_or_404
from decimal import Decimal
from management.models import TotalIncome
from .forms import *
from django.db import transaction
from .models import *
from django.http import HttpResponse
from django.db.models import Sum
from django.contrib import messages
from itertools import chain
# Create your views here.

def students_registration(request):
    form = None
    students = None

    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == "student":
            form = StudentForm(request.POST, request.FILES)
            if form.is_valid():
                get_class_ids = request.POST.getlist('classs')
                # Add the student to classes and decrease capacity
                with transaction.atomic():  # ensures rollback if anything fails
                    for class_id in get_class_ids:
                        subclass = SubClass.objects.select_for_update().get(id=class_id)
                        
                        if subclass.capacity > 0:
                            subclass.capacity -= 1
                            subclass.save()
                        else:
                            return HttpResponse(f"صنف {subclass.name} گنجایش ندارد", status=400)
                student = form.save(commit=False)  # don't commit yet
                student.save()                     # save main instance
                form.save_m2m()         
                return redirect('students:students_registration')
        else:
            student_without_classForm = StudentWithoutClassForm(request.POST)
            if student_without_classForm.is_valid():
                jalali_str = student_without_classForm.cleaned_data.get('date_for_notification')  # "30/06/1404"

                # Parse the string (format: day/month/year)
                jalali_date = jdatetime.datetime.strptime(jalali_str, "%d/%m/%Y").date()

                # Convert Jalali to Gregorian
                gregorian_date = jalali_date.togregorian()
                instance = student_without_classForm.save(commit=False)
                instance.jalali_to_gregorian = gregorian_date
                instance.save()
                return redirect('students:students_registration')
    else:
        form = StudentForm()
        student_without_classForm = StudentWithoutClassForm()

    form = StudentForm()
    students = Student.objects.filter(is_active=True)

    context = {
        'students':students,
        'form':form,
        'student_without_classForm':student_without_classForm,
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

def delete_students_withoutclass(request, id):
    get_student_id = StudentWithoutClass.objects.get(id=id)
    if get_student_id:
        get_student_id.delete()
        messages.success(request, 'شاگرد موفقانه ذخیره شد')
        return redirect('students:students_registration')
    else:
        return HttpResponse('User Is Not in Detabase')

    
def edit_students(request, id):
    get_student_id = Student.objects.get(id=id)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=get_student_id)
        if form.is_valid():
            form.save()
            messages.success(request, f" دانش‌آموز{get_student_id.first_name} {get_student_id.last_name} موفقانه تغییرات آورده شد.")
            return redirect('students:edit_students', id=get_student_id.id)  # or render response
        else:
            return HttpResponse('مشکل در تغییر شاگرد آمده ...')

    form = StudentForm(instance=get_student_id)

    context = {
        'get_student_id':get_student_id,
        'form':form,
    }
    return render(request, 'students/students-without-class.html', context)

def students_edit_withoutclass(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    student = get_object_or_404(StudentWithoutClass, id=id)
    if request.method == "POST":
        form = StudentWithoutClassForm(request.POST, instance=student)
        if form.is_valid():
            jalali_str = form.cleaned_data.get('date_for_notification')
            if jalali_str:
                jalali_date = jdatetime.datetime.strptime(jalali_str, "%d/%m/%Y").date()
                gregorian_date = jalali_date.togregorian()
                instance = form.save(commit=False)
                instance.jalali_to_gregorian = gregorian_date
                instance.save()
            else:
                form.save()
            messages.success(request, "معلومات شاگرد موفقانه ویرایش شد ✅")
            return redirect(referer)
    else:
        form = StudentWithoutClassForm(instance=student)

    return render(request, "students/student_edit_modal.html", {"form": form, "student": student})

def student_bill(request, student_id, fees_id):
    get_student_fees = Student_fess_info.objects.get(id=fees_id)
    student = Student.objects.get(id=student_id)
    return render(request, 'students/student-bill.html', {
        'student': student,
        'get_student_fees':get_student_fees,
    })


def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    remain_amount = StudentRemailMoney.objects.filter(student=student).last()

    context = {
        'student': student,
        'remain_amount': remain_amount,
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
    g_form=None
    form=None
    referer = request.META.get('HTTP_REFERER', '/')
    student = get_object_or_404(Student, id=student_id)
    get_remain_money = StudentRemailMoney.objects.filter(student=student).first()

    fees_record_related_student = Student_fess_info.objects.filter(student=student)
    # remain_money_records = StudentGiveRemainMoney.objects.filter(studnet=student)

    # Add a type field to each record (so we know قرض or پرداخت in template)
    # for record in fees_record_related_student:
    #     record.record_type = "قرض"
    #     record.amount_paid = record.give_fees
    #     record.remain = record.remain_fees
    #     record.month_display = record.month
    #     record.model_type = "fees"
    #     record.student_obj = record.student  # unify field name
    #     # 🔴 Flag for remain_fees
    #     record.is_red = record.remain_fees and record.remain_fees > 0
    #     record.is_green = False

    # for record in remain_money_records:
    #     record.record_type = "پرداخت"
    #     record.orginal_fees = "-"
    #     record.give_fees = record.amount
    #     record.remain_fees = "-"
    #     record.month_display = "-"
    #     record.model_type = "remain"
    #     record.student_obj = record.studnet  # unify field name
    #     # 🟢 Always green
    #     record.is_red = False
    #     record.is_green = True

    # Merge them into one list
    # all_records = list(chain(fees_record_related_student, remain_money_records))
    # all_records.sort(key=lambda r: r.created_at)

    if request.method == "POST":
        get_form_type = request.POST.get('form_type')
        if get_form_type == "givefees":
            form = Student_fess_infoForm(request.POST)
            if form.is_valid():
                get_date = form.cleaned_data.get('date')
                get_orginal_fess = form.cleaned_data.get('orginal_fees')
                get_give_money = form.cleaned_data.get('give_fees')
                # Extract month part
                try:
                    parts = get_date.split('/')
                    month_number = parts[1].zfill(2)  # Ensures "4" becomes "04"
                    month_name = shamsi_months.get(month_number, "")
                except:
                    month_name = ""
                fees_info = form.save(commit=False)
                fees_info.student = student  # Link to the correct student
                fees_info.month = month_name  # Save the month name
                # Handle total income safely
                total_income_obj, created = TotalIncome.objects.get_or_create(pk=1)  # Ensure single row

                # Add the new fee to existing total
                if get_give_money:
                    total_income_obj.total_amount = Decimal(str(total_income_obj.total_amount)) + Decimal(get_give_money)
                
                if get_give_money < get_orginal_fess:
                    substrack_values = get_orginal_fess - get_give_money
                    fees_info.remain_fees = substrack_values
                    try:
                        record = StudentRemailMoney.objects.get(student=student)
                        record.amount += substrack_values
                        record.save()
                    except StudentRemailMoney.DoesNotExist:
                        StudentRemailMoney.objects.create(
                            student=student,
                            amount=substrack_values
                        )

                total_income_obj.save()
                fees_info.save()
                return redirect(referer)
    else:
        form = Student_fess_infoForm()
        g_form = StudentGiveRemainMoneyForm()

    context = {
        'student': student,
        'g_form': g_form,
        'form': form,
        'fees_record_related_student': fees_record_related_student,
        'get_remain_money': get_remain_money,
    }
    return render(request, 'students/student-fees-detail.html', context)

def student_activate(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_active = False
    student.save()
    return redirect(request.META.get('HTTP_REFERER'))

def students_without_class(request):
    get_students = StudentWithoutClass.objects.all()
    form = StudentWithoutClassForm()
    return render(request, 'students/students-without-class.html', {'get_students':get_students,'form':form,})
    
def off_students(request):
    get_students = Student.objects.filter(is_active=False)
    return render(request, 'students/do-not-active-students.html', {'get_students':get_students})

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
            messages.success(request, '')
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


def buy_book(request, id):
    total_book = TotalBook.objects.all()
    student = Student.objects.get(id=id)
    allStationeryItem = TotalStationery.objects.all()
    # HTMX request to update total price
    if request.headers.get("HX-Request"):
        # Check which form was submitted
        if "books" in request.POST:
            book_ids = request.POST.getlist("books")
            total_price = Books.objects.filter(id__in=book_ids).aggregate(total=Sum("per_book_price_for_buy"))["total"] or 0
            return HttpResponse(f"<div class='alert alert-card alert-info'>مجموع قیمت: {total_price} AFN</div>")
        
        elif "stationeries" in request.POST:
            stationery_ids = request.POST.getlist("stationeries")
            total_price = StationeryItem.objects.filter(id__in=stationery_ids).aggregate(total=Sum("per_price_for_buy"))["total"] or 0
            return HttpResponse(f"<div class='alert alert-card alert-info'>مجموع قیمت: {total_price} AFN</div>")

        else:
            return HttpResponse("<div class='alert alert-card alert-warning'>هیچ موردی انتخاب نشده است</div>")
    
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
            "more_info": reverse('students:student_buyed_book', args=[rec.student.id, rec.id])
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
            "more_info_stationery": reverse('students:student_buyed_stationery', args=[rec.student.id, rec.id])
        })

    # optional: sort all records (by id or date)
    all_records = sorted(all_records, key=lambda x: x["id"], reverse=True)

    context = {
        'student':student,
        'buy_book_form':buy_book_form,
        'total_book':total_book,
        'buy_stationery_form':buy_stationery_form,
        'allStationeryItem':allStationeryItem,
        'all_records':all_records,
    }
    return render(request, 'students/student-buy-book.html', context)


def student_paid_Remain_money(request, id):
    referer = request.META.get('HTTP_REFERER', '/')

    student = Student.objects.get(id=id)
    get_remain_money = StudentRemailMoney.objects.filter(student=student).first()

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
            instance.studnet = student
            instance.save()
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