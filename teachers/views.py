from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from students.models import *
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
from jdatetime import date as jdate
# Create your views here.
from management.models import *


def teacher_registration(request):
    referer = request.META.get('HTTP_REFERER', '/')
    teachers = None
    # Get today's Jalali date
    today_jalali = jdatetime.date.today()

    # Format it as "DD/MM/YYYY"
    formatted_date = today_jalali.strftime("%d/%m/%Y")

    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(referer)
    else:
        form = TeacherForm(initial={'date': formatted_date})
        teachers = Teacher.objects.filter(is_active=True)
    context = {
        'teachers':teachers,
        'form':form,
    }
    return render(request, 'teachers/teacher-registration.html', context)

def deactive_teacher(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    if teacher:
        teacher.is_active = False
        teacher.save()
        messages.success(request, f"استاد {teacher.name} موفقانه غیر فعال شد.")
        return redirect(referer)

def active_teacher(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    if teacher:
        teacher.is_active = True
        teacher.save()
        messages.success(request, f"استاد {teacher.name} موفقانه فعال شد.")
        return redirect(referer)

def off_teachers(request):
    get_teachers = Teacher.objects.filter(is_active=False)
    return render(request, 'teachers/do-not-active-teacher.html', {'get_teachers':get_teachers})

def edit_teacher(request, id):
    get_student_id = Teacher.objects.get(id=id)
    if request.method == "POST":
        form = TeacherForm(request.POST,request.FILES, instance=get_student_id)
        if form.is_valid():
            form.save()
            messages.success(request, f" دانش‌آموز{get_student_id.name} {get_student_id.last_name} موفقانه تغییرات آورده شد.")
            return redirect('teachers:teacher_registration')  # or render response
        else:
            return HttpResponse('مشکل در تغییر شاگرد آمده ...')

    form = TeacherForm(instance=get_student_id)

    context = {
        'get_student_id':get_student_id,
        'form':form,
    }
    return render(request, 'teachers/teacher-edit.html', context)

def teacher_detail(request, id):
    teacher = Teacher.objects.get(id=id)
    try:
        get_total_remain_money = TeacherRemainMoney.objects.get(teacher=teacher)
    except TeacherRemainMoney.DoesNotExist:
        get_total_remain_money = None   # or 0 if you want numeric
    try:
        total_paid_amount_for_teacher = TotalPaidMoneyForTeacher.objects.get(teacher=teacher)
    except TotalPaidMoneyForTeacher.DoesNotExist:
        total_paid_amount_for_teacher = None   # or 0 if you want numeric
    total_students = 0
    try:
        total_students = Student.objects.filter(teacher=teacher)
    except Exception:
        total_students = 0
    try:
        total_students_count = Student.objects.filter(teacher=teacher).count()
    except Exception:
        total_students_count = 0

    total_loan_amount = TeacherTotalLoan.objects.filter(teacher=teacher).last()

    return render(request, 'teachers/teacher-detail.html', 
    {'teacher':teacher,'total_students':total_students,'total_students_count':total_students_count,'total_loan_amount':total_loan_amount,
            'get_total_remain_money':get_total_remain_money,'total_paid_amount_for_teacher':total_paid_amount_for_teacher})

def teacher_paid_salary(request,id):
    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    try:
        total_paid_amount_for_teacher = TeacherRemainMoney.objects.get(teacher=teacher)
        total_paid_amount_for_teacher_amount = total_paid_amount_for_teacher.total_amount
    except TeacherRemainMoney.DoesNotExist:
        total_paid_amount_for_teacher = None
        total_paid_amount_for_teacher_amount = 0

    try:
        total_teacher_loan = TeacherTotalLoan.objects.get(teacher=teacher)
        total_teacher_loan_amount = total_teacher_loan.total_loan_amount
    except TeacherTotalLoan.DoesNotExist:
        total_teacher_loan = None   # or 0 if you want numeric
        total_teacher_loan_amount = 0

    if request.method == "POST":
        form = TeacherPaidSalaryForm(request.POST)
        if form.is_valid():
            get_amount = form.cleaned_data.get('amount')
            get_paid_amount = form.cleaned_data.get('paid_salary')
            get_remain_amount = float(request.POST.get('remain_amount', 0))

            if get_paid_amount > get_amount:
                messages.warning(request, 'مقدار پرداخت بیشتر از مقدار است که باید پرداخت شود')
                return redirect(referer)
            # Collect Remain Amounts 

            sub_paid_with_amount = get_amount - get_paid_amount

            # save paid amount in expenses model 
            try:
                expenses_base = TotalExpenses.objects.get(pk=1)
            except TotalExpenses.DoesNotExist:
                expenses_base = TotalExpenses.objects.create(
                    total_amount=0
                )
            expenses_base.total_amount += get_paid_amount
            expenses_base.save()

            instance = form.save(commit=False)
            instance.remain_salary = sub_paid_with_amount
            instance.teacher = teacher
            instance.save()
         
            remain_obj, created = TeacherRemainMoney.objects.get_or_create(
                teacher=teacher,
                defaults={'total_amount': sub_paid_with_amount}
            )
            if not created:  
                # If already exists, add to it
                remain_obj.total_amount += sub_paid_with_amount
                remain_obj.save()

            total_paid, created = TotalPaidMoneyForTeacher.objects.get_or_create(
                teacher=teacher,
                defaults={'total_amount': get_paid_amount}
            )
            if not created:  
                # If already exists, add to it
                total_paid.total_amount += get_paid_amount
                total_paid.save()

    else:
        form = TeacherPaidSalaryForm()
    paid_records = TeacherPaidSalary.objects.filter(teacher=teacher)

    context = {
        'total_teacher_loan':total_teacher_loan,
        'total_paid_amount_for_teacher':total_paid_amount_for_teacher,
        'teacher':teacher,
        'form':form,
        'paid_records':paid_records,
    }
    return render(request, 'teachers/teacher-paid-salary.html', context)


def delete_teacher_salary_record(request, salary_id):
    referer = request.META.get('HTTP_REFERER', '/')
    salary_id = TeacherPaidSalary.objects.get(id=salary_id)
    try:
        expenses_base = TotalExpenses.objects.get(pk=1)
    except TotalExpenses.DoesNotExist:
        expenses_base = TotalExpenses.objects.create(
            total_amount=0
        )
    expenses_base.total_amount -= salary_id.paid_salary

    remain = TeacherRemainMoney.objects.get(teacher=salary_id.teacher)
    remain.total_amount -= salary_id.remain_salary

    total_paid = TotalPaidMoneyForTeacher.objects.get(teacher=salary_id.teacher)
    total_paid.total_amount -= salary_id.paid_salary

    expenses_base.save()
    remain.save()
    total_paid.save()
    salary_id.delete()

    messages.success(request, 'ریکارد پرداخت ماش موفقانه حذف شد')
    return redirect(referer)

def edit_teacher_salary_record(request, salary_id):
    referer = request.META.get('HTTP_REFERER', '/')
    salary_id = TeacherPaidSalary.objects.get(id=salary_id)
    past_remain = salary_id.remain_salary
    past_paid = salary_id.paid_salary

    if request.method == "POST":
        form = TeacherPaidSalaryForm(request.POST, instance=salary_id)
        if form.is_valid():
            get_total_amount = form.cleaned_data.get('amount')
            get_paid_amount = form.cleaned_data.get('paid_salary')
            get_remain_amount = form.cleaned_data.get('remain_salary')

            try:
                expenses_base = TotalExpenses.objects.get(pk=1)
            except TotalExpenses.DoesNotExist:
                expenses_base = TotalExpenses.objects.create(
                    total_amount=0)      
            expenses_base.total_amount -= past_paid

            remain = TeacherRemainMoney.objects.get(teacher=salary_id.teacher)
            remain.total_amount -= past_remain

            new_remain = get_total_amount - get_paid_amount 

            remain.total_amount += new_remain
            expenses_base.total_amount += get_paid_amount

            expenses_base.save()
            remain.save()
            instance = form.save(commit=False)
            instance.remain_salary = new_remain
            instance.save()
            messages.success(request, 'ریکارد پرداخت ماش موفقانه ایدیت شد')
            return redirect('teachers:teacher_paid_salary', id=salary_id.teacher.id)
        else:
            return HttpResponse('FORM IS NOT VALID')
                   
    else:
        form = TeacherPaidSalaryForm(instance=salary_id)

    context = {
        'form':form,
        'salary_id':salary_id,
    }
    return render(request, 'teachers/edit-teacher-paid-salary.html', context)


def teacher_loan(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    total_paid = TotalPaidMoneyForTeacher.objects.get(teacher=teacher)

    try:
        expenses_base = TotalExpenses.objects.get(pk=1)
    except TotalExpenses.DoesNotExist:
        expenses_base = TotalExpenses.objects.create(
            total_amount=0) 
            
    total = TeacherTotalLoan.objects.get(teacher=teacher)     

    if request.method == "POST":
        form = TeacherLoanForm(request.POST)
        if form.is_valid():
            get_amount_str = request.POST.get('amount' ,0)
            get_amount_float = float(get_amount_str or 0)

    
            total.total_loan_amount += get_amount_float
            total.save()                
    
            total_paid.total_amount += get_amount_float
            total_paid.save()                

            expenses_base.total_amount += get_amount_float
            expenses_base.save()


            messages.success(request, 'مقدار قرض موفقانه ثبت شد')
            instance = form.save(commit=False)
            instance.teacher = teacher
            instance.save()
            return redirect(referer)

        else:
            return HttpResponse("FORM IS NOT VALID SORRY TRY AGAIN LETTER")
    else:
        form = TeacherLoanForm()
    
    records = TeacherLoan.objects.filter(teacher=teacher)

    context = {
       'teacher':teacher, 
       'form':form, 
       'records':records, 
    }
    return render(request, 'teachers/loan-page.html', context)

def delete_loan_request(request, loan_id):
    loan_record = TeacherLoan.objects.get(id=loan_id)
    total_loan = TeacherTotalLoan.objects.get(teacher=loan_record.teacher)
    expenses_base = TotalExpenses.objects.get(pk=1)
    total_paid = TotalPaidMoneyForTeacher.objects.get(teacher=loan_record.teacher)

    loan_amount = loan_record.amount

    # Subtract the loan amount from teacher total loan
    total_loan.total_loan_amount -= loan_amount
    if total_loan.total_loan_amount < 0:
        total_loan.total_loan_amount = 0
    total_loan.save()

    # Subtract the loan amount from total expenses
    expenses_base.total_amount -= loan_amount
    if expenses_base.total_amount < 0:
        expenses_base.total_amount = 0
    expenses_base.save()

    total_paid.total_amount -= loan_amount
    total_paid.save()

    # Delete the loan record
    loan_record.delete()
    messages.success(request, 'ریکارد درخواست قرض حذف شد')
    return redirect(request.META.get('HTTP_REFERER', '/'))

def edit_loan_request(request, loan_id):
    loan_record = TeacherLoan.objects.get(id=loan_id)
    past_paid = loan_record.amount  # the old loan amount
    total_loan_obj = TeacherTotalLoan.objects.get(teacher=loan_record.teacher)
    total_paid = TotalPaidMoneyForTeacher.objects.get(teacher=loan_record.teacher)

    if request.method == "POST":
        form = TeacherLoanForm(request.POST, instance=loan_record)
        if form.is_valid():
            new_amount = form.cleaned_data.get('amount')

            # Update TotalExpenses
            expenses_base = TotalExpenses.objects.get(pk=1)
            expenses_base.total_amount = expenses_base.total_amount - past_paid + new_amount
            if expenses_base.total_amount < 0:
                expenses_base.total_amount = 0
            expenses_base.save()

            # Update TeacherTotalLoan
            total_loan_obj.total_loan_amount = total_loan_obj.total_loan_amount - past_paid + new_amount
            if total_loan_obj.total_loan_amount < 0:
                total_loan_obj.total_loan_amount = 0
            total_loan_obj.save()

            # Update TeacherTotalPaid
            total_paid.total_amount = total_paid.total_amount - past_paid + new_amount
            if total_paid.total_amount < 0:
                total_paid.total_amount = 0
            total_paid.save()

            # Save the updated loan record
            form.save()

            messages.success(request, 'مقدار قرض موفقانه ویرایش شد')
            return redirect('teachers:teacher_loan', id=loan_record.teacher.id)
    else:
        form = TeacherLoanForm(instance=loan_record)

    context = {
        'loan_record': loan_record,
        'form': form,
    }
    return render(request, 'teachers/edit-loan-page.html', context)

def teacher_leave_day(request,id):
    return render()

def teacher_paid_remain_money(request, id):
    teacher = Teacher.objects.get(id=id)
    try:
        remain_money = TeacherRemainMoney.objects.get(teacher=teacher)
    except TeacherRemainMoney.DoesNotExist:
        remain_money = None

    if request.method == "POST":
        form = TeacherPaidRemainMoneyForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            get_amount = form.cleaned_data.get('amount')
            get_remain_amount = remain_money.total_amount

            if get_amount > get_remain_amount:
                messages.warning(request, 'مقدار برای پرداخت بیشتر از مقدار باقی مانده است')
                return redirect('teachers:teacher_paid_remain_money', id=teacher.id)
            elif get_amount <= get_remain_amount:
                remain_money.total_amount -= get_amount
                remain_money.save()
            instance.teacher = teacher
            instance.save()   
    else:
        form = TeacherPaidRemainMoneyForm()
    records = TeacherPaidRemainMoney.objects.filter(teacher=teacher)

    context = {
        'teacher':teacher,
        'form':form,
        'records':records,
        'remain_money':remain_money,
    }
    return render(request, 'teachers/teahcer-paid-remain-money.html', context)


def delete_paid_remain_money(request, paid_id):
    paid_record = TeacherPaidRemainMoney.objects.get(id=paid_id)
    remain_money = TeacherRemainMoney.objects.get(teacher=paid_record.teacher)
    remain_money.total_amount += paid_record.amount
    remain_money.save()
    paid_record.delete()
    return HttpResponse(paid_record)

def edit_paid_remain_money(request, paid_id):
    paid_record = TeacherPaidRemainMoney.objects.get(id=paid_id)
    past_paid_money = paid_record.amount

    if request.method == "POST":
        form = TeacherPaidRemainMoneyForm(request.POST, instance=paid_record)
        if form.is_valid():
            instance = form.save(commit=False)
            get_amount = form.cleaned_data.get('amount')

            remain_money = TeacherRemainMoney.objects.get(teacher=paid_record.teacher)
            remain_money.total_amount += past_paid_money
            remain_money.total_amount -= get_amount
            remain_money.save()
            instance.save()
            messages.success(request, 'ریکارد پرداخت پول موفقانه ایدیت شد')
            return redirect('teachers:teacher_paid_remain_money', id=paid_record.teacher.id)
    else:
        form = TeacherPaidRemainMoneyForm(instance=paid_record)

    context = {
        'paid_record':paid_record,
        'form':form,
    }
    return render(request, 'teachers/edit-teahcer-paid-remain-money.html', context)

def add_attendance(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == "POST":
        form = AttendanceAndLeavesForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.teacher = teacher
            attendance.save()
            return redirect("teachers:add_attendance", teacher_id=teacher.id)
    else:
        form = AttendanceAndLeavesForm()

    records = AttendanceAndLeaves.objects.filter(teacher=teacher).order_by('-start_date')

    return render(request, "teachers/add_attendance.html", {
        "form": form,
        "teacher": teacher,
        "records": records
    })

def delete_attendance(request, attendance_id):
    attendance = get_object_or_404(AttendanceAndLeaves, id=attendance_id)
    teacher_id = attendance.teacher.id
    attendance.delete()
    messages.success(request, "ریکارد حضور و غیاب حذف شد")
    return redirect("teachers:add_attendance", teacher_id=teacher_id)

def edit_attendance(request, attendance_id):
    attendance = get_object_or_404(AttendanceAndLeaves, id=attendance_id)
    teacher = attendance.teacher

    if request.method == "POST":
        form = AttendanceAndLeavesForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, "ریکارد حضور و غیاب موفقانه ویرایش شد")
            return redirect("teachers:add_attendance", teacher_id=teacher.id)
    else:
        form = AttendanceAndLeavesForm(instance=attendance)

    return render(request, "teachers/edit_attendance.html", {
        "form": form,
        "teacher": teacher,
        "attendance": attendance
    })