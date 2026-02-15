from django.shortcuts import render, redirect
from students.models import *
from .forms import *
from django.db.models import Sum
from teachers.models import *
from khayyam import JalaliDatetime  # for Jalali date conversion
from django.http import HttpResponse
from management.models import *
from account.models import *
from django.db.models import Max
from django.utils import timezone
# Create your views here.

def statndart(request):

    return render(request, "reports/standart.html")


def students_reports(request):
    form = StudentFilterForm(request.GET or None)
    students = Student.objects.filter(is_active=True)
    filter_type = request.GET.get('filter_type', 'active_students')
    filter_active = False
    title = "در حال حاضر شاگردان فعال نمایش داده می‌شوند"

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # Normalize blank strings to None
        start_date = start_date or None
        end_date = end_date or None

        # 🔹 Deactive Students
        if filter_type == "deactive_students":
            students = Student.objects.filter(is_active=False)

            if start_date and end_date:
                # پیدا کردن دانش‌آموزانی که در بازه تاریخ غیر فعال شده‌اند
                from datetime import datetime

                # تبدیل تاریخ فرم (d/m/Y) به date
                start_dt = datetime.strptime(start_date, "%d/%m/%Y").date()
                end_dt = datetime.strptime(end_date, "%d/%m/%Y").date()

                filtered_students = []
                for student in students:
                    if student.deactivated_at:
                        # تبدیل deactivated_at به date
                        student_dt = datetime.strptime(student.deactivated_at, "%d/%m/%Y").date()
                        if start_dt <= student_dt <= end_dt:
                            filtered_students.append(student.id)

                students = students.filter(id__in=filtered_students)

                title = f"فلتر شاگردان غیر فعال از تاریخ {start_date} الی {end_date}"
            else:
                title = "تمام شاگردان غیر فعال"

            filter_active = True

        # 🔹 Loan Students
        elif filter_type == "loan_students":
            # تمام رکوردهای StudentBalance که باقیمانده دارند
            balances_with_remain = StudentBalance.objects.filter(remain__gt=0)

            # فقط دانش‌آموزان مرتبط
            students = Student.objects.filter(id__in=balances_with_remain.values_list('student_id', flat=True))

            title = "شاگردانی که باقیمانده فیس دارند"
            filter_active = True


        elif filter_type == "finish_fees":
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            students_finish_feeses = Student_fess_info.objects.all()

            if start_date and end_date:
                from datetime import datetime

                # فرمت جدید: روز/ماه/سال
                start_dt = datetime.strptime(start_date, "%d/%m/%Y").date()
                end_dt = datetime.strptime(end_date, "%d/%m/%Y").date()

                # فقط فیس‌هایی که end_date بین start و end هستند
                filtered_fees = []
                for fee in students_finish_feeses:
                    if fee.end_date:
                        fee_end_dt = datetime.strptime(fee.end_date, "%d/%m/%Y").date()
                        if start_dt <= fee_end_dt <= end_dt:
                            filtered_fees.append(fee.id)
                
                students_finish_feeses = students_finish_feeses.filter(id__in=filtered_fees)
                title = f"شاگردانی که فیس آن‌ها بین {start_date} تا {end_date} تکمیل شده"
            else:
                # اگر start یا end نبود، همه فیس‌های تمام شده
                students_finish_feeses = students_finish_feeses.exclude(end_date__isnull=True).exclude(end_date__exact='')
                title = "تمام شاگردانی که فیس آن‌ها تکمیل شده"

            filter_active = True

            # فقط دانش‌آموزان مرتبط
            students = Student.objects.filter(id__in=students_finish_feeses.values_list('student_id', flat=True))

        elif filter_type == "improving":
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            # همه رکوردهای StudentImporvment
            improvements = StudentImporvment.objects.all()

            if start_date and end_date:
                from datetime import datetime

                start_dt = datetime.strptime(start_date, "%d/%m/%Y").date()
                end_dt = datetime.strptime(end_date, "%d/%m/%Y").date()

                filtered_improvements = []
                for imp in improvements:
                    if imp.date:
                        imp_dt = datetime.strptime(imp.date, "%d/%m/%Y").date()
                        if start_dt <= imp_dt <= end_dt:
                            filtered_improvements.append(imp.id)

                improvements = improvements.filter(id__in=filtered_improvements)
                title = f"شاگردانی که در بازه {start_date} تا {end_date} به کلاس ارتقاء یافته‌اند"
            else:
                # اگر تاریخ نبود، همه رکوردها
                title = "تمام شاگردانی که ارتقاء یافته‌اند"

            filter_active = True

            # فقط دانش‌آموزان مرتبط
            students = Student.objects.filter(id__in=improvements.values_list('student_id', flat=True))


    context = {
        'students': students,
        'form': form,
        'filter_type': filter_type,
        'filter_active': filter_active,
        'title': title,
    }
    return render(request, "reports/students_reports.html", context)


def teachers_reports(request):
    form = StudentFilterForm(request.GET or None)
    teachers = Teacher.objects.filter(is_active=True)
    filter_type = request.GET.get('filter_type', 'active_teachers')
    filter_active = False
    title = "در حال حاضر استادان فعال نمایش داده می‌شوند"

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date') or None
        end_date = form.cleaned_data.get('end_date') or None

        # 🔹 Deactive Teachers
        if filter_type == "deactive_teachers":
            teachers = Teacher.objects.filter(is_active=False)

            if start_date and end_date:
                from datetime import datetime

                start_dt = datetime.strptime(start_date, "%d/%m/%Y").date()
                end_dt = datetime.strptime(end_date, "%d/%m/%Y").date()

                filtered_ids = []
                for teacher in teachers:
                    if teacher.deactivate_at:
                        teacher_dt = datetime.strptime(teacher.deactivate_at, "%d/%m/%Y").date()
                        if start_dt <= teacher_dt <= end_dt:
                            filtered_ids.append(teacher.id)

                teachers = teachers.filter(id__in=filtered_ids)
                title = f"فلتر استادان غیر فعال از تاریخ {start_date} الی {end_date}"
            else:
                title = "تمام استادان غیر فعال"

            filter_active = True

        # 🔹 Loan Teachers (FIXED)
        elif filter_type == "loan_teachers":
            teachers = Teacher.objects.filter(
                teacherbalance__total_loan__gt=0
            ).distinct()

            title = (
                f"فلتر استادان قرضدار از تاریخ {start_date} الی {end_date}"
                if start_date and end_date
                else "تمام استادان قرضدار"
            )
            filter_active = True

        # 🔹 Teachers with Remaining Salary (FIXED)
        elif filter_type == "teachers_remain":
            teachers = Teacher.objects.filter(
                teacherbalance__total_remain__gt=0
            ).distinct()

            title = (
                f"فلتر استادان دارای باقی‌مانده از تاریخ {start_date} الی {end_date}"
                if start_date and end_date
                else "تمام استادان دارای باقی‌مانده"
            )
            filter_active = True

    context = {
        'teachers': teachers,
        'form': form,
        'filter_type': filter_type,
        'filter_active': filter_active,
        'title': title,
    }
    return render(request, "reports/teachers_reports.html", context)


def books_reports(request):

    item_balance = TotalItem.objects.all()
    form = StudentFilterForm(request.GET or None)

    filter_active = False
    title = "همه کتاب‌ها"

    selected_item_id = request.GET.get('item_id')
    selected_item = None

    # default values (تا ارور ندهد)
    total_purchase = 0
    total_sale = 0

    total_purchase_amount = 0
    total_purchase_amount_paid = 0
    total_purchase_amount_remain = 0

    total_sale_amount = 0
    total_sale_amount_paid = 0
    total_sale_amount_remain = 0

    if form.is_valid():

        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # 🔴 تاریخ‌ها اجباری
        if not start_date or not end_date:
            form.add_error(None, "تاریخ شروع و پایان الزامی است")
        else:
            filter_active = True

            purchases = Purchase.objects.filter(date__range=[start_date, end_date])
            sales = BuyBook.objects.filter(date__range=[start_date, end_date])

            # ✅ اگر آیتم انتخاب شده باشد
            if selected_item_id:
                selected_item = Item.objects.get(id=selected_item_id)
                purchases = purchases.filter(item=selected_item)
                sales = sales.filter(item=selected_item)

            # ----------------- محاسبه -----------------

            total_purchase = purchases.aggregate(total=Sum('number'))['total'] or 0
            total_sale = sales.aggregate(total=Sum('number_of_book'))['total'] or 0
            total_purchase_amount = purchases.aggregate(total=Sum('total_price'))['total'] or 0
            total_purchase_amount_paid = purchases.aggregate(total=Sum('paid_price'))['total'] or 0
            total_purchase_amount_remain = purchases.aggregate(total=Sum('remain_price'))['total'] or 0

            total_sale_amount = sales.aggregate(total=Sum('total_amount'))['total'] or 0
            total_sale_amount_paid = sales.aggregate(total=Sum('paid_amount'))['total'] or 0
            total_sale_amount_remain = sales.aggregate(total=Sum('remain_amount'))['total'] or 0

            title = f"گزارش از تاریخ '{start_date}' الی '{end_date}' کتاب '{selected_item.name}'"

    context = {
        'items': item_balance,
        'form': form,
        'filter_active': filter_active,
        'title': title,
        'selected_item': selected_item,
        'selected_item_id': int(selected_item_id) if selected_item_id else None,

        "total_purchase": total_purchase,
        "total_sale": total_sale,

        "total_purchase_amount": total_purchase_amount,
        "total_purchase_amount_paid": total_purchase_amount_paid,
        "total_purchase_amount_remain": total_purchase_amount_remain,

        "total_sale_amount": total_sale_amount,
        "total_sale_amount_paid": total_sale_amount_paid,
        "total_sale_amount_remain": total_sale_amount_remain,
    }

    return render(request, "reports/books_report.html", context)


def income_expenses(request):
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    title = "تمام عواید و مصارف"
    form = StudentFilterForm(request.GET or None)
    filter_active = False
    start_date = None
    end_date = None
    
    # Quick filters
    date_filter = request.GET.get('date_filter')

    if date_filter == 'today':
        today = jdatetime.date.today()

        start_date = today.strftime('%d/%m/%Y')
        end_date = today.strftime('%d/%m/%Y')

        filter_active = True
        title = f"عواید و مصارف امروز ({start_date})"


    elif date_filter == 'yesterday_today':
        today = jdatetime.date.today()
        yesterday = today - jdatetime.timedelta(days=1)

        start_date = yesterday.strftime('%d/%m/%Y')
        end_date = today.strftime('%d/%m/%Y')

        filter_active = True
        title = f"عواید و مصارف امروز و دیروز ({start_date} تا {end_date})"
    
    # Check for date range filter from form
    if form.is_valid():
        form_start = form.cleaned_data.get('start_date')
        form_end = form.cleaned_data.get('end_date')
        
        if form_start and form_end:
            start_date = form_start
            end_date = form_end
            filter_active = True
            title = f"گزارش از تاریخ {start_date} تا {end_date}"
        elif form_start or form_end:
            # If only one date is provided, use it for both
            if form_start:
                start_date = form_start
                end_date = form_start
            else:
                start_date = form_end
                end_date = form_end
            filter_active = True
            title = f"گزارش برای تاریخ {start_date or end_date}"
    
    # Get finance records based on filters
    if filter_active and start_date and end_date:
        # Filter by date range
        income_data = FinanceRecord.objects.filter(
            type='income',
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
        
        expense_data = FinanceRecord.objects.filter(
            type='expense',
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
    else:
        # Get all records
        income_data = FinanceRecord.objects.filter(type='income').order_by('-date')
        expense_data = FinanceRecord.objects.filter(type='expense').order_by('-date')
    
    # Calculate totals
    total_income = income_data.aggregate(total=models.Sum('amount'))['total'] or 0
    total_expense = expense_data.aggregate(total=models.Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense
    
    context = {
        'title': title,
        'filter_active': filter_active,
        'form': form,
        'income_data': income_data,
        'expense_data': expense_data,
        'income_count': income_data.count(),
        'expense_count': expense_data.count(),
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
    }
    return render(request, 'reports/income-expenses.html', context)