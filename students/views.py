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

    has_balance = False
    if student_balance:
        has_balance = True
    else:
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
        'student_balance': student_balance,
        'has_balance': has_balance,
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
            if income_expenses:
                income_expenses.total_income += paid_fees
                income_expenses.total_receivable += remaining
                income_expenses.save()
            else:
                TotalBalance.objects.create(
                    total_income=paid_fees,
                    total_receivable=remaining,
                    total_expenses=0,
                    total_payable=0,
                )

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

    # Get balances
    student_balance = StudentBalance.objects.filter(student=student).last()
    total_balance = TotalBalance.objects.last()
    
    if request.method == 'POST':
        form = BuyBookForm(request.POST)
        if form.is_valid():
            try:
                amount = int(request.POST.get('amount', 1))
                per_price = float(request.POST.get('per_price', 0))
                total_price = float(request.POST.get('total_price', 0))
                paid_price = float(request.POST.get('paid_price', 0))
                remain_price = float(request.POST.get('remain_price', 0))
                
                # Create BuyBook record
                buy_book = form.save(commit=False)
                buy_book.student = student
                buy_book.item = item
                buy_book.number_of_book = amount
                buy_book.per_price = per_price
                buy_book.total_amount = total_price
                buy_book.paid_amount = paid_price
                buy_book.remain_amount = remain_price
                buy_book.save()
                
                # Update TotalItem
                if total_item:
                    total_item.total_remain_item -= amount
                    total_item.save()

                # Update StudentBalance
                if student_balance:
                    student_balance.paid += paid_price
                    student_balance.remain += remain_price
                    student_balance.save()

                # Update TotalItem balance
                if total_balance:
                    total_balance.total_income += paid_price
                    total_balance.total_receivable += remain_price
                    total_balance.save()

                messages.success(request, 'خرید کتاب با موفقیت ثبت شد.')
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
    purchased_records = BuyBook.objects.get(id=purchase_id)

    # Update TotalItem
    total_item = TotalItem.objects.filter(item=purchased_records.item).last()
    if total_item:
        total_item.total_remain_item += purchased_records.number_of_book
        total_item.save()

    # update StudentBalance
    student_balance = StudentBalance.objects.filter(student=purchased_records.student).last()
    if student_balance:
        student_balance.paid -= purchased_records.paid_amount
        student_balance.remain -= purchased_records.remain_amount
        student_balance.save()

    # Update TotalBalance
    total_balance = TotalBalance.objects.last()
    if total_balance:
        total_balance.total_income -= purchased_records.paid_amount
        total_balance.total_receivable -= purchased_records.remain_amount
        total_balance.save()
    
    purchased_records.delete()
    messages.success(request, 'ریکارد خرید موفقانه حذف شد')
    return redirect(request.META.get('HTTP_REFERER'))

def edit_student_purchased_items(request, purchase_id):
    purchase = BuyBook.objects.get(id=purchase_id)
    old_amount = purchase.number_of_book

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
                if amount > old_amount:
                    difference = amount - old_amount
                    total_item.total_remain_item -= difference
                elif amount < old_amount:
                    difference = old_amount - amount
                    total_item.total_remain_item += difference
                total_item.save()

            # Update StudentBalance
            student_balance = StudentBalance.objects.filter(student=purchase.student).last()
            if student_balance:
                student_balance.paid += (paid_price - purchase.paid_amount)
                student_balance.remain += (remain_price - purchase.remain_amount)
                student_balance.save()
            
            # Update TotalBalance
            total_balance = TotalBalance.objects.last()
            if total_balance:
                total_balance.total_income += (paid_price - purchase.paid_amount)
                total_balance.total_receivable += (remain_price - purchase.remain_amount)
                total_balance.save()

            instance.amount = amount
            instance.per_price = per_price
            instance.total_amount = total_price
            instance.paid_amount = paid_price
            instance.remain_amount = remain_price
            instance.save()
            
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