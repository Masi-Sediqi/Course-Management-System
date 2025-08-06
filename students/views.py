from django.shortcuts import render, redirect , get_object_or_404
from decimal import Decimal
from management.models import TotalIncome
from .forms import *
from .models import *
from django.http import HttpResponse
from django.contrib import messages
# Create your views here.

def students_registration(request):
    form = None
    students = None

    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)  # don't commit yet
            student.save()                     # save main instance
            form.save_m2m()         
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

    context = {
        'student': student,
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
            g_form = StudentGiveRemainMoneyForm(request.POST)
            if g_form.is_valid():
                get_Amount = g_form.cleaned_data.get('amount')
                get_remain_money.amount -= get_Amount
                instance = g_form.save(commit=False)
                get_remain_money.save()
                instance.studnet = student
                instance.save()
                return redirect(referer)
            return redirect('students:student_fees_detail', student_id=student.id)
    else:
        form = Student_fess_infoForm(initial={
            'orginal_fees': student.orginal_fees
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