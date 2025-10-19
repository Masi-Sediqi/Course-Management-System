from django.urls import reverse
from django.shortcuts import render, redirect , get_object_or_404
from decimal import Decimal
from management.models import TotalIncome
from .forms import *
from django.db import transaction
from .models import *
from account.models import Licsanse_check
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Sum
from django.contrib import messages
from itertools import chain
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
# Create your views here.

def students_registration(request):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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

def export_students_excel(request):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    # Create workbook and active sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Active Students"

    # Set the column headers
    headers = ["شماره", "نام", "تخلص", "نام پدر", "جنسیت", "صنف", "شماره تماس", "تاریخ ثبت"]
    ws.append(headers)

    # Header styling
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill("solid", fgColor="17a2b8")  # Bootstrap info color
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

    # Query active students
    students = Student.objects.filter(is_active=True).prefetch_related("classs")

    # Add student rows
    for idx, student in enumerate(students, start=1):
        # Join all class names
        class_names = "، ".join([c.name for c in student.classs.all()]) if student.classs.exists() else "—"

        gender_display = "مرد" if student.gender == "Male" else "زن"

        ws.append([
            idx,
            student.first_name,
            student.last_name,
            student.father_name,
            gender_display,
            class_names,
            student.phone if student.phone else "—",
            student.date_of_registration,
        ])

    # Apply styles to all data cells
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=ws.max_column):
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # Auto-size columns
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 3

    # Create HTTP response with Excel content
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Active_Students.xlsx"'

    wb.save(response)
    return response

def delete_students(request, id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    get_student_id = Student.objects.get(id=id)
    if get_student_id:
        get_student_id.delete()
        messages.success(request, 'شاگرد موفقانه ذخیره شد')
        return redirect('students:students_registration')
    else:
        return HttpResponse('User Is Not in Detabase')

def delete_students_withoutclass(request, id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    get_student_id = StudentWithoutClass.objects.get(id=id)
    if get_student_id:
        get_student_id.delete()
        messages.success(request, 'شاگرد موفقانه حذف شد')
        return redirect('students:students_without_class')
    else:
        return HttpResponse('User Is Not in Detabase')

    
def edit_students(request, id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    get_student_id = Student.objects.get(id=id)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=get_student_id)
        if form.is_valid():
            form.save()
            messages.success(request, f" دانش‌آموز{get_student_id.first_name} {get_student_id.last_name} موفقانه تغییرات آورده شد.")
            return redirect('students:students_registration')  # or render response
        else:
            return HttpResponse('مشکل در تغییر شاگرد آمده ...')

    form = StudentForm(instance=get_student_id)

    context = {
        'get_student_id':get_student_id,
        'form':form,
    }
    return render(request, 'students/edit_student.html', context)

def students_edit_withoutclass(request, id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
            return redirect('students:students_without_class')
    else:
        form = StudentWithoutClassForm(instance=student)

    return render(request, "students/student_edit_modal.html", {"form": form, "student": student})

def student_bill(request, student_id, fees_id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    get_student_fees = Student_fess_info.objects.get(id=fees_id)
    student = Student.objects.get(id=student_id)
    return render(request, 'students/student-bill.html', {
        'student': student,
        'get_student_fees':get_student_fees,
    })


def student_detail(request, student_id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    g_form=None
    form=None
    referer = request.META.get('HTTP_REFERER', '/')
    student = get_object_or_404(Student, id=student_id)
    student_classes = student.classs.all()

    context = {
        'student': student,
        'g_form': g_form,
        'form': form,
        'student_classes': student_classes,
    }
    return render(request, 'students/student-fees-detail.html', context)

def student_paid_fees(request, stu_id, cla_id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    referer = request.META.get('HTTP_REFERER', '/')
    student = Student.objects.get(id=stu_id)
    stu_class = SubClass.objects.get(id=cla_id)

    if request.method == "POST":
        get_form_type = request.POST.get('form_type')
        if get_form_type == "givefees":
            form = Student_fess_infoForm(request.POST)
            if form.is_valid():
                get_date = form.cleaned_data.get('date')
                get_orginal_fess = form.cleaned_data.get('orginal_fees')
                get_give_money = form.cleaned_data.get('give_fees')

                # --- Extract Jalali month name ---
                try:
                    parts = get_date.split('/')
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])

                    # Add 1 month to the Jalali date safely
                    date_obj = jdatetime.date(year, month, day)
                    try:
                        next_month_date = date_obj.replace(month=month + 1)
                    except ValueError:
                        # When month > 12, roll over to next year
                        next_month_date = date_obj.replace(year=year + 1, month=1)

                    # Convert to string again in same format
                    end_date_str = f"{next_month_date.day:02d}/{next_month_date.month:02d}/{next_month_date.year}"
                except Exception as e:
                    end_date_str = ""

                # --- Get month name ---
                shamsi_months = {
                    "01": "حمل", "02": "ثور", "03": "جوزا", "04": "سرطان",
                    "05": "اسد", "06": "سنبله", "07": "میزان", "08": "عقرب",
                    "09": "قوس", "10": "جدی", "11": "دلو", "12": "حوت",
                }
                month_name = shamsi_months.get(f"{month:02d}", "")

                fees_info = form.save(commit=False)
                fees_info.student = student 
                fees_info.st_class = stu_class 
                fees_info.month = month_name  # Save the month name
                fees_info.end_date = end_date_str
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
                messages.success(request, 'فیس ذیل موفقانه ذخیره شد')
                return redirect(referer)
    else:
        form = Student_fess_infoForm(initial={"orginal_fees": stu_class.fees})
        records = Student_fess_info.objects.filter(student=student, st_class=stu_class)


    context = {
        'student':student,
        'stu_class':stu_class,
        'form':form,
        'records':records,
    }
    return render(request, 'students/student-paid-fees.html', context)

def delete_paid_fess(request, id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    referer = request.META.get('HTTP_REFERER', '/')
    fess_id = Student_fess_info.objects.get(id=id)
    income = TotalIncome.objects.get(pk=1)
    income.total_amount -= fess_id.give_fees
    # Sub Track Amount From Remain Money
    subtrack_remain_money = fess_id.orginal_fees - fess_id.give_fees
    get_student_remain_money_model = StudentRemailMoney.objects.get(student=fess_id.student.id)
    get_student_remain_money_model.amount -= subtrack_remain_money 
    get_student_remain_money_model.save()
    income.save()
    messages.success(request, 'ریکارد پرداخت موفقانه حذف شد')
    fess_id.delete()
    return redirect(referer)

def edit_paid_fees(request, id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    referer = request.META.get('HTTP_REFERER', '/')
    fess_id = Student_fess_info.objects.get(id=id)
    past_paid_amount = fess_id.give_fees
    if request.method == "POST":
        form = Student_fess_infoForm(request.POST, instance=fess_id)
        if form.is_valid():
            get_date = form.cleaned_data.get('date')
            get_orginal_fess = form.cleaned_data.get('orginal_fees')
            get_give_money = form.cleaned_data.get('give_fees')
            try:
                parts = get_date.split('/')
                month_number = parts[1].zfill(2)  # Ensures "4" becomes "04"
                month_name = shamsi_months.get(month_number, "")
            except:
                month_name = ""
            fees_info = form.save(commit=False)
            fees_info.student = fess_id.student 
            fees_info.st_class = fess_id.st_class
            fees_info.month = month_name  # Save the month name

            total_income_obj, created = TotalIncome.objects.get_or_create(pk=1)  # Ensure single row

            try:
                record = StudentRemailMoney.objects.get(student=fess_id.student)
            except StudentRemailMoney.DoesNotExist:
                StudentRemailMoney.objects.create(
                    student=fess_id.student,
                    amount=0
                )

            if get_give_money > past_paid_amount:
                # Student paid more now
                extra_paid = get_give_money - past_paid_amount
                new_remain = get_orginal_fess - get_give_money

                record.amount = new_remain  # student's remaining balance
                total_income_obj.total_amount = Decimal(str(total_income_obj.total_amount)) + Decimal(str(extra_paid))

                fees_info.remain_fees = new_remain
                record.save()

            elif get_give_money < past_paid_amount:
                # Student paid less now
                reduced_paid = past_paid_amount - get_give_money
                new_remain = get_orginal_fess - get_give_money

                record.amount = new_remain
                total_income_obj.total_amount = Decimal(str(total_income_obj.total_amount)) - Decimal(str(reduced_paid))

                fees_info.remain_fees = new_remain
                record.save()

            total_income_obj.save()
            fees_info.save()
            messages.success(request, 'ریکارد ذیل موفقانه ایدیت شد')
            return redirect("students:student_paid_fees", stu_id=fess_id.student.id, cla_id=fess_id.st_class.id)
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    student = get_object_or_404(Student, id=student_id)
    student.is_active = False
    student.save()
    return redirect(request.META.get('HTTP_REFERER'))

def students_without_class(request):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    get_students = StudentWithoutClass.objects.all()
    return render(request, 'students/students-without-class.html', {'get_students':get_students,})


def off_students(request):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    get_students = Student.objects.filter(is_active=False)
    return render(request, 'students/do-not-active-students.html', {'get_students':get_students})

def student_activate_on(request, student_id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    student = get_object_or_404(Student, id=student_id)
    student.is_active = True
    student.save()
    return redirect(request.META.get('HTTP_REFERER'))

def student_improvment(request, id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    student = Student.objects.get(id=id)
    student_classes = student.classs.all()
    return render(request, 'students/student-class-improvemtn.html')

def buy_book(request, id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    referer = request.META.get('HTTP_REFERER', '/')
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
        'total_book':total_book,
        'buy_stationery_form':buy_stationery_form,
        'allStationeryItem':allStationeryItem,
        'all_records':all_records,
    }
    return render(request, 'students/student-buy-book.html', context)

def delete_student_buy_book(request, id):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    student = Student.objects.get(id=stu_id)
    stationery_id = BuyStationery.objects.get(id=stationery_id)

    buyed_stationeyies = StationeryRecord.objects.filter(buy_stationery=stationery_id)

    context = {
        'student':student,
        'stationery_id':stationery_id,
        'buyed_stationeyies':buyed_stationeyies,
    }
    return render(request, 'students/student-buyed-stationeries.html', context)