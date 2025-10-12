from django.shortcuts import render
from students.models import *
from .forms import *
from django.db.models import Sum
from teachers.models import *
from khayyam import JalaliDatetime  # for Jalali date conversion
from django.http import HttpResponse
from management.models import *
# Create your views here.

def statndart(request):
    return render(request, "reports/standart.html")


def students_reports(request):
    form = StudentFilterForm(request.GET or None)
    students = Student.objects.filter(is_active=True)
    filter_type = None
    filter_active = False
    title = "در حال حاضر شاگردان فعال نمایش داده می‌شوند"

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        filter_type = request.GET.get('filter_type', 'active_students')

        if filter_type == "active_students":
            students = Student.objects.filter(is_active=True)

            students = students.filter(
                date_of_registration__gte=start_date,
                date_of_registration__lte=end_date
            )
            filter_active = True
            title = f"فلتر شاگران فعال از تاریخ {start_date} الی {end_date}"

        elif filter_type == "deactive_students":
            students = Student.objects.filter(is_active=False)

            students = students.filter(
                date_of_registration__gte=start_date,
                date_of_registration__lte=end_date
            )
            filter_active = True
            title = f"فلتر شاگران غیر فعال از تاریخ {start_date} الی {end_date}"
            
        elif filter_type == "loan_students":
            students_with_loans = StudentRemailMoney.objects.filter(
                student__is_active=True,   
                amount__gt=0  
            )
            filter_active = True
            if start_date:
                students_with_loans = students_with_loans.filter(student__date_of_registration__gte=start_date)
            if end_date:
                students_with_loans = students_with_loans.filter(student__date_of_registration__lte=end_date)

            students = Student.objects.filter(student_remains__in=students_with_loans).distinct()

            title = f"فلتر شاگران قرضدار از تاریخ {start_date} الی {end_date}"


        elif filter_type == "students_withoutclass":
            students = StudentWithoutClass.objects.all()

            students = students.filter(
                date__gte=start_date,
                date__lte=end_date
            )
            filter_active = True

            title = f"فلتر شاگران بدون صنف از تاریخ {start_date} الی {end_date}"

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
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # 🔹 Active Teachers
        if filter_type == "active_teachers":
            teachers = Teacher.objects.filter(is_active=True)
            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)
            filter_active = True
            title = f"فلتر استادان فعال از تاریخ {start_date} الی {end_date}"

        # 🔹 Deactive Teachers
        elif filter_type == "deactive_teachers":
            teachers = Teacher.objects.filter(is_active=False)
            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)
            filter_active = True
            title = f"فلتر استادان غیر فعال از تاریخ {start_date} الی {end_date}"

        # 🔹 Loan Teachers
        elif filter_type == "loan_teachers":
            # find teachers with loan amount > 0
            teachers_with_loans = TeacherTotalLoan.objects.filter(total_loan_amount__gt=0).values_list('teacher_id', flat=True)
            teachers = Teacher.objects.filter(id__in=teachers_with_loans)

            # filter by date range (Shamsi string comparison)
            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)

            filter_active = True
            title = f"فلتر استادان قرضدار از تاریخ {start_date} الی {end_date}"

        # 🔹 Teachers with remaining money
        elif filter_type == "teachers_remain":
            teachers = Teacher.objects.filter(
                teacher_remains__total_amount__gt=0
            ).distinct()  # ✅ now shows teachers whose total_amount > 0

            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)

            filter_active = True
            title = f"فلتر استادان دارای باقی‌مانده از تاریخ {start_date} الی {end_date}"

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
    filter_type = request.GET.get('filter_type', 'active_teachers')
    filter_active = False
    title = "در حال حاضر تمام کتابها باقی مانده نمایش داده می‌شوند"
    

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # 🔹 Active Teachers
        if filter_type == "remain_books":
            teachers = Teacher.objects.filter(is_active=True)
            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)
            filter_active = True
            title = f"فلتر استادان فعال از تاریخ {start_date} الی {end_date}"

        # 🔹 Deactive Teachers
        elif filter_type == "buy_books":
            teachers = Teacher.objects.filter(is_active=False)
            if start_date and end_date:
                teachers = teachers.filter(date__gte=start_date, date__lte=end_date)
            filter_active = True
            title = f"فلتر استادان غیر فعال از تاریخ {start_date} الی {end_date}"

    context = {
        'books': books,
        'books':books,
        'title':title,
        'form':form,
        'filter_type':filter_type,
        'filter_active':filter_active,
    }
    return render(request, "reports/books_report.html", context)

def income_expenses(request):
    title = "در حال حاضر تمام عایدات و مصارفات نمایش داده می‌شوند"
    form = StudentFilterForm(request.GET or None)
    filter_type = request.GET.get('filter_type', 'income_expenses')

    # Default: show all
    filter_active = False
    income_data = []
    expense_data = []

    # helper filter for date range
    def date_filter(qs, start_date, end_date):
        if start_date and end_date:
            return qs.filter(date__range=[start_date, end_date])
        elif start_date:
            return qs.filter(date__gte=start_date)
        elif end_date:
            return qs.filter(date__lte=end_date)
        return qs

    # ========== INCOMES ==========
    income_sources = [
        ("عواید عمومی", OtherIncome),
        ("فیس شاگردان", Student_fess_info),
        ("فروش کتاب", BuyBook),
        ("فروش قرطاسیه", BuyStationery),
        ("پرداخت پول باقی مانده توسط شاگرد", StudentGiveRemainMoney),
    ]
    
    # ========== EXPENSES ==========
    expense_sources = [
        ("مصارف عمومی", Expenses),
        ("ماش استادان", TeacherPaidSalary),
        ("قرض استادان", TeacherLoan),
        ("خرید قرطاسیه", StationeryItem),
        ("خرید دوباره قرطاسیه", BuyStationeryAgain),
        ("خرید کتاب", Books),
        ("خرید دوباره کتاب", BuyBookAgain),
    ]

    # ========== FILTER BY DATE (if form valid) ==========
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if start_date or end_date:
            filter_active = True
            title = f"گزارش عواید و مصارف از تاریخ {start_date} تا {end_date}"
    else:
        start_date = end_date = None

    # ========== FETCH DATA ==========
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

    if filter_type == "income":
        title = f"نمایش تمام عواید از تاریخ {start_date} الی {end_date}"
    elif filter_type == "expenses":
        title = f"نمایش تمام مصارفات از تاریخ {start_date} الی {end_date}"
    # elif filter_type == "income_expenses":
    #     title = f"نمایش تمام عواید و مصارفات از تاریخ {start_date} الی {end_date}"

    # ========== SORT RESULTS ==========
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