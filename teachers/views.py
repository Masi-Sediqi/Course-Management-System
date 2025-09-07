from django.shortcuts import render, redirect
from .forms import *
from .models import *
from students.models import *
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
# Create your views here.


def teacher_registration(request):
    referer = request.META.get('HTTP_REFERER', '/')
    teachers = None
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(referer)
    else:
        form = TeacherForm()
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
    except TeacherRemainMoney.DoesNotExist:
        total_paid_amount_for_teacher = None   # or 0 if you want numeric

    try:
        total_teacher_loan = TeacherTotalLoan.objects.get(teacher=teacher)
    except TeacherTotalLoan.DoesNotExist:
        total_teacher_loan = None   # or 0 if you want numeric

    if request.method == "POST":
        form = TeacherPaidSalaryForm(request.POST)
        if form.is_valid():
            get_amount = form.cleaned_data.get('amount')
            get_loan_amount = float(request.POST.get('loan_amount'))
            get_paid_amount = form.cleaned_data.get('paid_salary')

            if get_loan_amount > total_teacher_loan.total_loan_amount:
                messages.warning(request, 'مقدار قرض بیشتر از مقدار قرض است')
                return redirect(referer)

            if total_teacher_loan.total_loan_amount > 0:
                total_teacher_loan.total_loan_amount -= get_loan_amount
                total_teacher_loan.save()

            if get_paid_amount > get_amount:
                substracktion =  get_paid_amount - get_amount
                checking_if_any_remain_amount_for_teacher = total_paid_amount_for_teacher.total_amount
                if checking_if_any_remain_amount_for_teacher <= 0:
                    messages.warning(request, 'مقدار پرداخت بیشتر از مقدار است که باید پرداخت شود.')
                    return redirect(referer)
                else:
                    total_paid_amount_for_teacher.total_amount -= substracktion
                    if 0 > total_paid_amount_for_teacher.total_amount:
                        messages.warning(request, 'مقدار باقی مانده کمتر از صفر میشود.')
                        return redirect(referer)
                    else:
                        total_paid_amount_for_teacher.save()

            # Calculate remain if any
            substracktion = 0
            if get_paid_amount < get_amount:
                substracktion = get_amount - get_paid_amount

            instance = form.save()
            instance.remain_salary = substracktion
            instance.teacher = teacher
            instance.save()

            # Handle TeacherRemainMoney (one record per teacher)
            if substracktion > 0:
                remain_obj, created = TeacherRemainMoney.objects.get_or_create(
                    teacher=teacher,
                    defaults={'total_amount': substracktion}
                )
                if not created:  
                    # If already exists, add to it
                    remain_obj.total_amount += substracktion
                    remain_obj.save()

                remain_obj, created = TotalPaidMoneyForTeacher.objects.get_or_create(
                    teacher=teacher,
                    defaults={'total_amount': get_paid_amount}
                )
                if not created:  
                    # If already exists, add to it
                    remain_obj.total_amount += get_paid_amount
                    remain_obj.save()
            return redirect(referer)
    else:
        form = TeacherPaidSalaryForm()
    
    paid_records = TeacherPaidSalary.objects.filter(teacher=teacher)
    # Collect total remain salary
    total_remain_salary = TeacherRemainMoney.objects.get(teacher=teacher)

    context = {
        'teacher':teacher,
        'paid_records':paid_records,
        'form':form,
        'total_remain_salary':total_remain_salary,
        'total_paid_amount_for_teacher':total_paid_amount_for_teacher,
        'total_teacher_loan':total_teacher_loan,
    }
    return render(request, 'teachers/teacher-paid-salary.html', context)


def teacher_loan(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    if request.method == "POST":
        form = TeacherLoanForm(request.POST)
        if form.is_valid():
            get_amount_str = request.POST.get('amount')
            get_amount = int(get_amount_str)
            instance = form.save(commit=False)
            instance.teacher = teacher
            instance.save()

            # Update or create total loan for this teacher
            total_loan_obj, created = TeacherTotalLoan.objects.get_or_create(
                teacher=teacher,
                defaults={'total_loan_amount': 0}
            )
            total_loan_obj.total_loan_amount += get_amount
            total_loan_obj.save()

            messages.success(request, f"ریکارد قرض برای استاد {teacher.name} موفقانه اضافه شد.")
            return redirect(referer)
    else:
        form = TeacherLoanForm()
    
    records = TeacherLoan.objects.filter(teacher=teacher)

    context = {
       'teacher':teacher, 
       'form':form, 
       'records':records, 
    }
    return render(request, 'teachers/loan-page.html', context)

def teacher_leave_day(request,id):
    return render()

def teacher_paid_remain_money(request, id):
    teacher = Teacher.objects.get(id=id)
    try:
        remain_money = TeacherRemainMoney.objects.get(teacher=teacher)
    except TeacherRemainMoney.DoesNotExist:
        pass

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












import jdatetime
from django.shortcuts import render, get_object_or_404, redirect
from .models import Teacher, Attendance_and_Leaves
from .forms import Attendance_and_LeavesForm

def add_attendance(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == "POST":
        form = Attendance_and_LeavesForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.Teacher_id = teacher  # set teacher manually
            attendance.save()
            return redirect("teachers:add_attendance", teacher_id=teacher.id)
    else:
        form = Attendance_and_LeavesForm()

    # Query all attendance records for this teacher
    records = Attendance_and_Leaves.objects.filter(Teacher_id=teacher).order_by('-start_date')

    # Add a 'days' attribute to each record
    for r in records:
        try:
            # Parse DD/MM/YYYY format
            start_parts = [int(x) for x in r.start_date.split('/')]
            end_parts = [int(x) for x in r.end_date.split('/')]
            start_jdate = jdatetime.date(start_parts[2], start_parts[1], start_parts[0])
            end_jdate = jdatetime.date(end_parts[2], end_parts[1], end_parts[0])
            r.days = (end_jdate.togregorian() - start_jdate.togregorian()).days
        except Exception:
            r.days = 0

    return render(
        request,
        "teachers/add_attendance.html",
        {
            "form": form,
            "teacher": teacher,
            "records": records  # each record now has a 'days' attribute
        }
    )
