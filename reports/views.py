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

        # 🔹 Active Students
        if filter_type == "active_students":
            students = Student.objects.filter(is_active=True)
            if start_date and end_date:
                students = students.filter(
                    date_of_registration__gte=start_date,
                    date_of_registration__lte=end_date
                )
                title = f"فلتر شاگردان فعال از تاریخ {start_date} الی {end_date}"
            else:
                title = "تمام شاگردان فعال"

            filter_active = True

        # 🔹 Deactive Students
        elif filter_type == "deactive_students":
            students = Student.objects.filter(is_active=False)
            if start_date and end_date:
                students = students.filter(
                    date_of_registration__gte=start_date,
                    date_of_registration__lte=end_date
                )
                title = f"فلتر شاگردان غیر فعال از تاریخ {start_date} الی {end_date}"
            else:
                title = "تمام شاگردان غیر فعال"

            filter_active = True

        # 🔹 Loan Students
        elif filter_type == "loan_students":
            students_with_loans = StudentRemailMoney.objects.filter(
                student__is_active=True,
                amount__gt=0
            )
            if start_date:
                students_with_loans = students_with_loans.filter(student__date_of_registration__gte=start_date)
            if end_date:
                students_with_loans = students_with_loans.filter(student__date_of_registration__lte=end_date)

            students = Student.objects.filter(student_remains__in=students_with_loans).distinct()
            title = f"شاگردان قرضدار {f'از تاریخ {start_date} الی {end_date}' if start_date and end_date else ''}"

            filter_active = True

        # 🔹 Students Without Class
        elif filter_type == "students_withoutclass":
            students = StudentWithoutClass.objects.all()
            if start_date and end_date:
                students = students.filter(
                    date__gte=start_date,
                    date__lte=end_date
                )
                title = f"شاگردان بدون صنف از تاریخ {start_date} الی {end_date}"
            else:
                title = "تمام شاگردان بدون صنف"

            filter_active = True

        if filter_type == "students_complete_fess":
            selected_date = start_date or end_date  # prefer start_date if both filled

            # Start with all fee records
            qs = Student_fess_info.objects.all()

            if selected_date:
                # Filter by selected end_date
                qs = qs.filter(end_date=selected_date)

            # Only keep completed fees if needed
            # qs = qs.filter(remain_fees=0)  # optional if you want only fully paid

            # Get the latest record per student
            latest_ids = qs.values('student').annotate(latest_id=Max('id')).values_list('latest_id', flat=True)
            students = Student_fess_info.objects.filter(id__in=latest_ids).order_by('student__first_name')

            title = f"شاگردانی که فیس شان پوره شده - تاریخ: {selected_date}" if selected_date else "شاگردانی که فیس شان پوره شده"
            filter_active = True

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
