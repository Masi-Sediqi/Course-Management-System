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

        # 🔹 Active Teachers
        if filter_type == "active_teachers":
            teachers = Teacher.objects.filter(is_active=True)
            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)
                title = f"فلتر استادان فعال از تاریخ {start_date} الی {end_date}"
            else:
                title = "تمام استادان فعال"
            filter_active = True

        # 🔹 Deactive Teachers
        elif filter_type == "deactive_teachers":
            teachers = Teacher.objects.filter(is_active=False)
            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)
                title = f"فلتر استادان غیر فعال از تاریخ {start_date} الی {end_date}"
            else:
                title = "تمام استادان غیر فعال"
            filter_active = True

        # 🔹 Loan Teachers
        elif filter_type == "loan_teachers":
            teachers_with_loans = TeacherTotalLoan.objects.filter(
                total_loan_amount__gt=0
            ).values_list('teacher_id', flat=True)

            teachers = Teacher.objects.filter(id__in=teachers_with_loans)
            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)
                title = f"فلتر استادان قرضدار از تاریخ {start_date} الی {end_date}"
            else:
                title = "تمام استادان قرضدار"
            filter_active = True

        # 🔹 Teachers with Remaining Money
        elif filter_type == "teachers_remain":
            teachers = Teacher.objects.filter(
                teacher_remains__total_amount__gt=0
            ).distinct()

            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)
                title = f"فلتر استادان دارای باقی‌مانده از تاریخ {start_date} الی {end_date}"
            else:
                title = "تمام استادان دارای باقی‌مانده"
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


    books = Books.objects.all()

    # Attach total_amount from TotalBook to each book
    for book in books:
        total_book = TotalBook.objects.filter(book=book).last()  # latest record
        book.total_amount_value = total_book.total_amount if total_book else 0

    form = StudentFilterForm(request.GET or None)
    filter_type = request.GET.get('filter_type', 'remain_books')
    filter_active = False
    title = "در حال حاضر تمام کتاب‌ها نمایش داده می‌شوند"

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date') or None
        end_date = form.cleaned_data.get('end_date') or None

        # Helper function
        def date_filter(qs):
            if start_date and end_date:
                return qs.filter(date__range=[start_date, end_date])
            elif start_date:
                return qs.filter(date__gte=start_date)
            elif end_date:
                return qs.filter(date__lte=end_date)
            return qs

        # 🔹 Remaining Books
        if filter_type == "remain_books":
            books = date_filter(Books.objects.all())
            filter_active = True
            title = f"کتاب‌های باقی‌مانده {f'از تاریخ {start_date} الی {end_date}' if (start_date or end_date) else ''}"

        # 🔹 Purchased Books
        elif filter_type == "buy_books":
            books = date_filter(BuyBook.objects.all())
            filter_active = True
            title = f"کتاب‌های خریداری‌شده {f'از تاریخ {start_date} الی {end_date}' if (start_date or end_date) else ''}"

    context = {
        'books': books,
        'form': form,
        'filter_type': filter_type,
        'filter_active': filter_active,
        'title': title,
    }
    return render(request, "reports/books_report.html", context)


def income_expenses(request):


    title = "در حال حاضر تمام عایدات و مصارفات نمایش داده می‌شوند"
    form = StudentFilterForm(request.GET or None)
    filter_type = request.GET.get('filter_type', 'income_expenses')
    filter_active = False
    income_data, expense_data = [], []

    # Helper for flexible date filtering
    def date_filter(qs, start_date, end_date):
        if start_date and end_date:
            return qs.filter(date__range=[start_date, end_date])
        elif start_date:
            return qs.filter(date__gte=start_date)
        elif end_date:
            return qs.filter(date__lte=end_date)
        return qs

    # Income sources
    income_sources = [
        ("عواید عمومی", OtherIncome),
        ("فیس شاگردان", Student_fess_info),
        ("فروش کتاب", BuyBook),
        ("فروش قرطاسیه", BuyStationery),
        ("پرداخت پول باقی مانده توسط شاگرد", StudentGiveRemainMoney),
    ]

    # Expense sources
    expense_sources = [
        ("مصارف عمومی", Expenses),
        ("ماش استادان", TeacherPaidSalary),
        ("قرض استادان", TeacherLoan),
        ("خرید قرطاسیه", StationeryItem),
        ("خرید دوباره قرطاسیه", BuyStationeryAgain),
        ("خرید کتاب", Books),
        ("خرید دوباره کتاب", BuyBookAgain),
    ]

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date') or None
        end_date = form.cleaned_data.get('end_date') or None

        # Apply filters dynamically
        if start_date or end_date:
            filter_active = True
            title = f"گزارش از تاریخ {start_date} تا {end_date}"
        else:
            title = "تمام عایدات و مصارفات"

    else:
        start_date = end_date = None

    # Build income and expense lists
    if filter_type in ["income_expenses", "income"]:
        for label, model in income_sources:
            qs = date_filter(model.objects.all(), start_date, end_date)
            for obj in qs:
                income_data.append({
                    'id': obj.id,
                    'type': label,
                    'date': getattr(obj, 'date', None),
                    'amount': getattr(obj, 'amount', getattr(obj, 'give_fees',
                               getattr(obj, 'paid_amount',
                               getattr(obj, 'paid_stationery_amount', 0)))),
                })

    if filter_type in ["income_expenses", "expenses"]:
        for label, model in expense_sources:
            qs = date_filter(model.objects.all(), start_date, end_date)
            for obj in qs:
                expense_data.append({
                    'id': obj.id,
                    'type': label,
                    'date': getattr(obj, 'date', None),
                    'amount': getattr(obj, 'amount', getattr(obj, 'paid_salary',
                               getattr(obj, 'stationery_paid_price',
                               getattr(obj, 'paid_price', 0)))),
                })

    # Smart title updates
    if filter_type == "income":
        title = f"تمام عواید {f'از تاریخ {start_date} الی {end_date}' if (start_date or end_date) else ''}"
    elif filter_type == "expenses":
        title = f"تمام مصارفات {f'از تاریخ {start_date} الی {end_date}' if (start_date or end_date) else ''}"

    income_data = sorted(income_data, key=lambda x: x['date'] or '', reverse=True)
    expense_data = sorted(expense_data, key=lambda x: x['date'] or '', reverse=True)

    context = {
        'title': title,
        'filter_active': filter_active,
        'form': form,
        'income_data': income_data,
        'expense_data': expense_data,
    }
    return render(request, 'reports/income-expenses.html', context)
