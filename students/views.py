from django.shortcuts import render, redirect , get_object_or_404
from decimal import Decimal
from management.models import TotalIncome
from .forms import *
from django.db import transaction
from .models import *
from django.http import HttpResponse
from django.db.models import Sum
from django.contrib import messages
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
    return render(request, 'students/student-edit.html', context)

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
    remain_money_records = StudentGiveRemainMoney.objects.filter(studnet=student)

    if request.method == "POST":
        get_form_type = request.POST.get('form_type')
        if get_form_type == "givefees":
            form = Student_fess_infoForm(request.POST)
            if form.is_valid():
                get_date = form.cleaned_data.get('date')
                get_orginal_fess = 12
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
            # g_form = StudentGiveRemainMoneyForm(request.POST)
            # if g_form.is_valid():
            #     get_Amount = g_form.cleaned_data.get('amount')
            #     get_remain_money.amount -= get_Amount
            #     instance = g_form.save(commit=False)
            #     get_remain_money.save()
            #     instance.studnet = student
            #     instance.save()
            #     return redirect(referer)
            return redirect('students:student_fees_detail', student_id=student.id)
    else:
        form = Student_fess_infoForm(initial={
            'orginal_fees':12
        })
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
    return render(request, 'students/students-without-class.html', {'get_students':get_students})
    
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
    total_book = Books.objects.all()
    student = Student.objects.get(id=id)

    # HTMX request to update total price
    if request.headers.get("HX-Request"):  
        book_ids = request.POST.getlist("books")
        total_price = Books.objects.filter(id__in=book_ids).aggregate(total=Sum("price"))["total"] or 0
        return HttpResponse(f"<div class='alert alert-card alert-info'>مجموع قیمت: {total_price} AFN</div>")

    if request.method == "POST":
        boos = request.POST.getlist('books')
        form_type = request.POST.get('form_type')
        if form_type == "buy-book":
            buy_book_form = BuyBookForm(request.POST)
            if buy_book_form.is_valid():
                get_paid_amount = float(request.POST.get('paid_amount'))
                book_ids = list(map(int, request.POST.getlist('books')))
                total_price = Books.objects.filter(id__in=book_ids).aggregate(total=Sum("price"))["total"] or 0
                subtraction = total_price - get_paid_amount

                with transaction.atomic():
                    # TotalIncome
                    find_expenses_pk, created = TotalIncome.objects.get_or_create(pk=1, defaults={'total_amount': 0})
                    find_expenses_pk.total_amount += get_paid_amount
                    find_expenses_pk.save()

                    # Total_Stationery_Loan
                    if subtraction > 0:
                        collect_loans, created = StudentRemailMoney.objects.get_or_create(student=student, defaults={'amount': 0})
                        collect_loans.amount += subtraction
                        collect_loans.save()
                
                
                
                instance = buy_book_form.save()
                instance.student = student
                instance.remain_amount = subtraction

                instance.save()
                instance.book.set(boos)
                return redirect('students:buy_book', id=student.id)  # refresh after save
        else:
            pass

    buy_book_form = BuyBookForm()
    buy_book_records = BuyBook.objects.filter(student=id)

    context = {
        'student':student,
        'buy_book_form':buy_book_form,
        'buy_book_records':buy_book_records,
        'total_book':total_book,
    }
    return render(request, 'students/student-buy-book.html', context)