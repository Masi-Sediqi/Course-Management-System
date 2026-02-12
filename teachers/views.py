from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from students.models import *
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
from jdatetime import date as jdate
from django.contrib.contenttypes.models import ContentType
from home.models import *
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
            SystemLog.objects.create(
                section="اساتید",
                action=f"ثبت استاد جدید:",
                description=f"استاد با نام {form.cleaned_data.get('name')} ثبت شد.",
                user=request.user if request.user.is_authenticated else None
            )
            messages.success(request, 'استاد جدید با موفقیت ثبت شد.')
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
        SystemLog.objects.create(
            section="اساتید",
            action=f"غیرفعال کردن استاد:",
            description=f"استاد با نام {teacher.name} غیرفعال شد.",
            user=request.user if request.user.is_authenticated else None
        )
        messages.success(request, f"استاد {teacher.name} موفقانه غیر فعال شد.")
        return redirect(referer)

def active_teacher(request, id):

    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    if teacher:
        teacher.is_active = True
        teacher.save()
        SystemLog.objects.create(
            section="اساتید",
            action=f"فعال کردن استاد:",
            description=f"استاد با نام {teacher.name} فعال شد.",
            user=request.user if request.user.is_authenticated else None
        )
        messages.success(request, f"استاد {teacher.name} موفقانه فعال شد.")
        return redirect(referer)


def edit_teacher(request, id):

    get_student_id = Teacher.objects.get(id=id)
    if request.method == "POST":
        form = TeacherForm(request.POST,request.FILES, instance=get_student_id)
        if form.is_valid():
            form.save()
            SystemLog.objects.create(
                section="اساتید",
                action=f"ایدیت اطلاعات استاد:",
                description=f"اطلاعات استاد با نام {get_student_id.name} ایدیت شد.",
                user=request.user if request.user.is_authenticated else None
            )
            messages.success(request, f" دانش‌آموز{get_student_id.name} موفقانه تغییرات آورده شد.")
            return redirect('teachers:teacher_detail', id=id)  # or render response
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
    teacher_balance = TeacherBalance.objects.filter(teacher=teacher).last()

    lock_balance_btn = False
    if teacher_balance:
        if (
            teacher_balance.total_paid > 0 or
            teacher_balance.total_remain > 0 or
            teacher_balance.total_loan > 0
        ):
            lock_balance_btn = True

    return render(request, 'teachers/teacher-detail.html',{'teacher':teacher, 'teacher_balance':teacher_balance, 'lock_balance_btn':lock_balance_btn})


def teacher_paid_salary(request, id):

    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    teacher_balance = TeacherBalance.objects.filter(teacher=teacher).last()
    total_balance = TotalBalance.objects.last()
    if not total_balance:
        TotalBalance.objects.create(
            total_income=0,
            total_expenses=0
        )

    if request.method == "POST":
        form = TeacherPaidSalaryForm(request.POST)
        if form.is_valid():
            get_amount = form.cleaned_data.get('amount')
            get_paid_amount = form.cleaned_data.get('paid_salary')
            loan_deduction = form.cleaned_data.get('loan_amount') or 0

            if get_paid_amount > get_amount:
                messages.warning(request, 'مقدار پرداخت بیشتر از مقدار است که باید پرداخت شود')
                return redirect(referer)

            find_sub = loan_deduction + get_paid_amount
            get_sub = get_amount - find_sub

            # Teacher Balance 
            teacher_balance.total_paid += get_amount
            teacher_balance.total_remain += get_sub
            teacher_balance.total_loan -= loan_deduction
            teacher_balance.save()

            # Total Balance 

            total_balance.total_expenses += get_amount
            total_balance.save()

            instance = form.save(commit=False)
            instance.remain_salary = get_sub
            instance.teacher = teacher
            instance.save()

            FinanceRecord.objects.create(
                date=instance.date,
                title=f"پرداخت معاش استاد {teacher.name}",
                amount=get_paid_amount,
                description=f"پرداخت معاش استاد {teacher.name} به مبلغ {get_paid_amount} افغانی.",
                type='expense',
                content_type=ContentType.objects.get_for_model(Teacher),
                object_id=teacher.id,
            )

            SystemLog.objects.create(
                section="اساتید",
                action=f"پرداخت ماش استاد:",
                description=f"پرداخت ماش استاد {teacher.name} صورت گرفت",
                user=request.user if request.user.is_authenticated else None
            )

    else:
        form = TeacherPaidSalaryForm()

    paid_records = TeacherPaidSalary.objects.filter(teacher=teacher)

    context = {
        'teacher': teacher,
        'form': form,
        'paid_records': paid_records,
        'teacher_balance':teacher_balance
    }
    return render(request, 'teachers/teacher-paid-salary.html', context)


def delete_teacher_salary_record(request, salary_id):
    referer = request.META.get('HTTP_REFERER', '/')

    salary = get_object_or_404(TeacherPaidSalary, id=salary_id)
    teacher = salary.teacher

    teacher_balance = TeacherBalance.objects.filter(teacher=teacher).last()
    total_balance = TotalBalance.objects.last()

    amount = salary.amount  
    paid_amount = salary.paid_salary or 0
    remain_amount = salary.remain_salary
    loan_deduction = getattr(salary, "loan_amount", 0) or 0

    if teacher_balance:
        teacher_balance.total_paid -= amount
        teacher_balance.total_remain -= remain_amount
        if teacher_balance.total_paid < 0:
            teacher_balance.total_paid = 0
        teacher_balance.save()

    if total_balance:
        total_balance.total_expenses -= amount
        if total_balance.total_expenses < 0:
            total_balance.total_expenses = 0
        total_balance.save()

    content_type = ContentType.objects.get_for_model(teacher)

    FinanceRecord.objects.filter(
        content_type=content_type,
        object_id=teacher.id,
        amount=paid_amount + loan_deduction,
        type='expense'
    ).delete()

    salary.delete()

    messages.success(request, 'ریکارد پرداخت معاش موفقانه حذف شد')
    return redirect(referer)


def teacher_remain_loan_caluculating(request, id):
    teacher = Teacher.objects.get(id=id)
    teacher_balance = TeacherBalance.objects.filter(teacher=teacher).last()

    if not teacher_balance:
        return

    loan = teacher_balance.total_loan or 0
    remain = teacher_balance.total_remain or 0

    # خنثی کردن loan و remain
    if loan > remain:
        teacher_balance.total_loan = loan - remain
        teacher_balance.total_remain = 0

    elif remain > loan:
        teacher_balance.total_remain = remain - loan
        teacher_balance.total_loan = 0

    else:
        # اگر برابر باشند
        teacher_balance.total_loan = 0
        teacher_balance.total_remain = 0

    teacher_balance.save()
    messages.success(request, 'محاسبه مقدار باقی مانده و مقدار قرض موفقانه صورت گرفت')
    return redirect('teachers:teacher_detail', id=id)


def edit_teacher_salary_record(request, salary_id):
    referer = request.META.get('HTTP_REFERER', '/')
    salary_instance = get_object_or_404(TeacherPaidSalary, id=salary_id)
    teacher = salary_instance.teacher

    # Teacher balance and total balance
    teacher_balance, _ = TeacherBalance.objects.get_or_create(teacher=teacher)
    total_balance, _ = TotalBalance.objects.get_or_create(pk=1)

    # Get existing finance record
    finance_record, _ = FinanceRecord.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(TeacherPaidSalary),
        object_id=salary_instance.id,
        defaults={
            "date": salary_instance.date,
            "title": f"پرداخت معاش استاد {teacher.name}",
            "amount": salary_instance.paid_salary,
            "type": "expense",
        }
    )

    if request.method == "POST":
        form = TeacherPaidSalaryForm(request.POST, instance=salary_instance)
        if form.is_valid():
            new_total = form.cleaned_data.get('amount')
            new_paid = form.cleaned_data.get('paid_salary')
            new_loan = float(request.POST.get('loan_amount', 0))

            # Validation
            if new_paid + new_loan > new_total:
                messages.warning(request, "جمع پرداخت و قرض نمی‌تواند بیشتر از مقدار کل باشد")
                return redirect(referer)

            # Save updated salary record
            instance = form.save(commit=False)
            instance.remain_salary = new_total - new_paid - new_loan
            instance.loan_amount = new_loan
            instance.save()

            # --- Recalculate teacher_balance from all salary records ---
            all_salaries = TeacherPaidSalary.objects.filter(teacher=teacher)
            total_paid = all_salaries.aggregate(total=Sum('paid_salary'))['total'] or 0
            total_remain = all_salaries.aggregate(total=Sum('remain_salary'))['total'] or 0
            total_loan = all_salaries.aggregate(total=Sum('loan_amount'))['total'] or 0

            teacher_balance.total_paid = total_paid
            teacher_balance.total_remain = total_remain
            teacher_balance.total_loan = total_loan
            teacher_balance.save()

            # --- Update TotalBalance ---
            total_expenses = TeacherPaidSalary.objects.aggregate(total=Sum('paid_salary'))['total'] or 0
            total_balance.total_expenses = total_expenses
            total_balance.save()

            # --- Update FinanceRecord ---
            finance_record.date = instance.date
            finance_record.amount = new_paid
            finance_record.title = f"پرداخت معاش استاد {teacher.name}"
            finance_record.save()

            messages.success(request, "ریکارد پرداخت معاش با موفقیت ویرایش شد")
            return redirect('teachers:teacher_paid_salary', id=teacher.id)

        else:
            return HttpResponse("فرم معتبر نیست")

    else:
        form = TeacherPaidSalaryForm(instance=salary_instance)

    context = {
        'form': form,
        'salary_id': salary_instance,
        'teacher_balance': teacher_balance,
        'total_balance': total_balance,
        'finance_record': finance_record,
    }
    return render(request, 'teachers/edit-teacher-paid-salary.html', context)


def teacher_loan(request, id):

    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    teacher_balance = TeacherBalance.objects.filter(teacher=teacher).last()

    if request.method == "POST":
        form = TeacherLoanForm(request.POST)
        if form.is_valid():
            get_amount_str = request.POST.get('amount' ,0)
            get_amount_float = float(get_amount_str or 0)

            if teacher_balance.total_remain > 0:
                if get_amount_float >= teacher_balance.total_remain:
                    deffrence = get_amount_float - teacher_balance.total_remain
                    teacher_balance.total_loan += deffrence
                    teacher_balance.total_remain = 0
                    teacher_balance.total_paid += deffrence
                    teacher_balance.save()
                    
                else:
                    teacher_balance.total_remain -= get_amount_float
                    teacher_balance.save()

            else:
                teacher_balance.total_paid += get_amount_float
                teacher_balance.total_loan += get_amount_float
                teacher_balance.save()

      
            messages.success(request, 'مقدار قرض موفقانه ثبت شد')
            instance = form.save(commit=False)
            instance.teacher = teacher
            instance.save()

            FinanceRecord.objects.create(
                date=instance.date,
                title=f"قرض برای استاد {teacher.name}",
                amount=get_amount_float,
                type="expense",
                description=f"پرداخت قرض به استاد {teacher.name} به مبلغ {get_amount_float}.",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
            )

            SystemLog.objects.create(
                section="اساتید",
                action=f"برداشت پول جدید:",
                description=f"برداشت پول به مبلغ {get_amount_float} برای استاد {teacher.name} ثبت شد.",
                user=request.user if request.user.is_authenticated else None
            )

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
       'teacher_balance':teacher_balance, 
    }
    return render(request, 'teachers/loan-page.html', context)

def delete_loan_request(request, loan_id):
    loan_record = TeacherLoan.objects.get(id=loan_id)
    teacher = loan_record.teacher
    teacher_balance = TeacherBalance.objects.filter(teacher=teacher).last()

    amount = loan_record.amount

    if teacher_balance.total_loan >= amount:
        teacher_balance.total_loan -= amount
    else:
        remain_part = amount - teacher_balance.total_loan
        teacher_balance.total_remain += remain_part
        teacher_balance.total_loan = 0

    teacher_balance.total_paid -= amount

    teacher_balance.save()

    content_type = ContentType.objects.get_for_model(TeacherLoan)
    FinanceRecord.objects.filter(
        content_type=content_type,
        object_id=loan_record.id
    ).delete()

    loan_record.delete()

    SystemLog.objects.create(
        section="اساتید",
        action=f"حذف برداشت پول:",
        description=f"برداشت پول به مبلغ {amount} برای استاد {teacher.name} حذف شد.",
        user=request.user if request.user.is_authenticated else None
    )

    messages.success(request, 'ریکارد درخواست قرض حذف شد')
    return redirect(request.META.get('HTTP_REFERER', '/'))


def edit_loan_request(request, loan_id):
    loan_record = TeacherLoan.objects.get(id=loan_id)
    teacher = loan_record.teacher
    teacher_balance = TeacherBalance.objects.filter(teacher=teacher).last()
    past_amount = loan_record.amount

    if request.method == "POST":
        form = TeacherLoanForm(request.POST, instance=loan_record)
        if form.is_valid():
            new_amount = form.cleaned_data.get('amount')
            difference = new_amount - past_amount

            # Update teacher balances only
            if difference > 0:
                # Increased loan
                if teacher_balance.total_remain > 0:
                    if difference >= teacher_balance.total_remain:
                        extra = difference - teacher_balance.total_remain
                        teacher_balance.total_paid += extra
                        teacher_balance.total_loan += extra
                        teacher_balance.total_remain = 0
                    else:
                        teacher_balance.total_remain -= difference
                else:
                    teacher_balance.total_paid += difference
                    teacher_balance.total_loan += difference
            elif difference < 0:
                # Decreased loan
                refund = abs(difference)
                if teacher_balance.total_loan >= refund:
                    teacher_balance.total_loan -= refund
                    teacher_balance.total_paid -= refund
                else:
                    remain_back = refund - teacher_balance.total_loan
                    teacher_balance.total_paid -= refund
                    teacher_balance.total_remain += remain_back
                    teacher_balance.total_loan = 0

            teacher_balance.save()

            # Save the loan record
            updated_loan = form.save(commit=False)
            updated_loan.amount = new_amount
            updated_loan.save()

            # Update only the linked FinanceRecord's amount
            content_type = ContentType.objects.get_for_model(TeacherLoan)
            finance_record = FinanceRecord.objects.filter(
                content_type=content_type,
                object_id=loan_record.id
            ).last()

            if finance_record:
                finance_record.amount = new_amount
                finance_record.description=f"پرداخت قرض به استاد {loan_record.teacher.name} به مبلغ {new_amount}.",
                finance_record.save()

            # Log
            SystemLog.objects.create(
                section="اساتید",
                action=f"ایدیت برداشت پول:",
                description=f"برداشت پول از {past_amount} به {new_amount} برای استاد {teacher.name} ایدیت شد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'مقدار قرض موفقانه ایدیت شد')
            return redirect('teachers:teacher_loan', id=teacher.id)
    else:
        form = TeacherLoanForm(instance=loan_record)

    context = {
        'loan_record': loan_record,
        'form': form,
    }
    return render(request, 'teachers/edit-loan-page.html', context)


def teacher_leave_day(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    referer = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        form = AttendanceAndLeavesForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.teacher = teacher
            leave.save()

            SystemLog.objects.create(
                section="اساتید",
                action=f"ثبت رخصتی جدید:",
                description=f"رخصتی از تاریخ {leave.start_date} تا {leave.end_date} برای استاد {teacher.name} ثبت شد.",
                user=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'درخواست رخصتی با موفقیت ثبت شد')
            return redirect(referer)
        else:
            messages.error(request, 'فورم درست نیست، لطفاً دوباره تلاش کنید')
            return redirect(referer)
    else:
        form = AttendanceAndLeavesForm()

    records = AttendanceAndLeaves.objects.filter(teacher=teacher).order_by('-start_date')

    return render(request, 'teachers/teacher-leave-day.html', {
        'teacher': teacher,
        'form': form,
        'records': records,
    })


def add_attendance(request, teacher_id):

    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == "POST":
        form = AttendanceAndLeavesForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.teacher = teacher
            attendance.save()
            SystemLog.objects.create(
                section="اساتید",
                action=f"ثبت رخصتی جدید:",
                description=f"رخصتی از تاریخ {attendance.start_date} تا {attendance.end_date} برای استاد {teacher.name} ثبت شد.",
                user=request.user if request.user.is_authenticated else None
            )
            messages.success(request, 'ریکارد رخصتی با موفقیت ثبت شد')
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
    SystemLog.objects.create(
        section="اساتید",
        action=f"حذف رخصتی:",
        description=f"رخصتی از تاریخ {attendance.start_date} تا {attendance.end_date} برای استاد {attendance.teacher.name} حذف شد.",
        user=request.user if request.user.is_authenticated else None
    )
    messages.success(request, "ریکارد حضور و غیاب حذف شد")
    return redirect("teachers:add_attendance", teacher_id=teacher_id)

def edit_attendance(request, attendance_id):
    attendance = get_object_or_404(AttendanceAndLeaves, id=attendance_id)
    teacher = attendance.teacher

    if request.method == "POST":
        form = AttendanceAndLeavesForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            SystemLog.objects.create(
                section="اساتید",
                action=f"ایدیت رخصتی:",
                description=f"رخصتی از تاریخ {attendance.start_date} تا {attendance.end_date} برای استاد {teacher.name} ایدیت شد.",
                user=request.user if request.user.is_authenticated else None
            )
            messages.success(request, "ریکارد حضور و غیاب موفقانه ایدیت شد")
            return redirect("teachers:add_attendance", teacher_id=teacher.id)
    else:
        form = AttendanceAndLeavesForm(instance=attendance)

    return render(request, "teachers/edit_attendance.html", {
        "form": form,
        "teacher": teacher,
        "attendance": attendance
    })