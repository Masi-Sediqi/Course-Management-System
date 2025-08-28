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
    {'teacher':teacher,'total_students':total_students,'total_students_count':total_students_count,'total_loan_amount':total_loan_amount})

def teacher_paid_salary(request,id):
    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    if request.method == "POST":
        form = TeacherPaidSalaryForm(request.POST)
        if form.is_valid():
            get_amount = form.cleaned_data.get('amount')
            get_paid_amount = form.cleaned_data.get('paid_salary')

            if get_paid_amount > get_amount:
                messages.warning(request, 'مقدار پرداخت بیشتر از مقدار است که باید پرداخت شود.')
                return redirect(referer)
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
            return redirect(referer)
    else:
        form = TeacherPaidSalaryForm()
    
    paid_records = TeacherPaidSalary.objects.filter(teacher=teacher)
        # Collect total remain salary
    total_remain_salary = TeacherPaidSalary.objects.aggregate(
        total=Sum('remain_salary')
    )['total'] or 0

    context = {
        'teacher':teacher,
        'paid_records':paid_records,
        'form':form,
        'total_remain_salary':total_remain_salary,
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