from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import *
from management.models import *
from django.db import transaction
from django.http import HttpResponse
# Create your views here.

def library_view(request):
    referer = request.META.get('HTTP_REFERER', '/')
    category_form = StationeryCategoryForm()
    form = StationeryItemForm()
    book_form=None
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == "category":
            category_form = StationeryCategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, "کتگوری با موفقیت ذخیره شد ")
                category_form = StationeryCategoryForm()  # Reset after saving
                return redirect('library:library_view')
        elif form_type == "book":
            book_form = BooksForm(request.POST)
            if book_form.is_valid():
                get_number_of_book_field = float(request.POST.get('number_of_book') or 0)
                get_per_book_price = float(request.POST.get('per_price') or 0)
                get_per_book_price_for_buy = float(request.POST.get('per_book_price_for_buy') or 0)
                get_price_field = float(request.POST.get('price') or 0)
                get_paid_price_field = float(request.POST.get('paid_price') or 0)

                multiplication = get_number_of_book_field * get_per_book_price
                if get_paid_price_field < multiplication:
                    messages.warning(request, 'مقدار پرداخت شده کمتر از مقدار است که باید پرداخت شود')
                    return redirect(referer)
                # subtraction_paid_price_collection = multiplication - get_paid_price_field

                with transaction.atomic():
                    # TotalExpenses
                    find_expenses_pk, created = TotalExpenses.objects.get_or_create(pk=1, defaults={'total_amount': 0})
                    find_expenses_pk.total_amount += get_paid_price_field
                    find_expenses_pk.save()

                    # Total_Stationery_Loan
                    # if subtraction_paid_price_collection > 0:
                    #     collect_loans, created = Total_Stationery_Loan.objects.get_or_create(pk=1, defaults={'total_amount': 0})
                    #     collect_loans.total_amount += subtraction_paid_price_collection
                    #     collect_loans.save()

                    # Save book
                book = book_form.save()

                # Create or update related TotalBook
                total_obj, created = TotalBook.objects.get_or_create(
                    book=book,
                    defaults={
                        "total_amount": get_number_of_book_field,
                        "total_book": get_number_of_book_field,
                        "per_price": get_per_book_price_for_buy,
                    },
                )

                if not created:  
                    # If it already exists, just update/collect totals
                    total_obj.total_amount += get_number_of_book_field
                    total_obj.total_book += get_number_of_book_field
                    total_obj.per_price = get_per_book_price_for_buy  # or maybe update only if needed
                    total_obj.save()

                messages.success(request, "کتاب با موفقیت اضافه شد")
                return redirect('library:library_view')
        else:
            form = StationeryItemForm(request.POST)
            if form.is_valid():

                number_of_stationery = float(request.POST.get('number_of_stationery') or 0)
                per_price_stationery = float(request.POST.get('per_price_stationery') or 0)
                per_price_for_buy = float(request.POST.get('per_price_for_buy') or 0)
                stationery_paid_price = float(request.POST.get('stationery_paid_price') or 0)

                multiplication = number_of_stationery * per_price_stationery
                if stationery_paid_price < multiplication:
                    messages.warning(request, 'مقدار پرداخت شده کمتر از مقدار است که باید پرداخت شود')
                    return redirect(referer)
                # subtraction_paid_price_collection = multiplication - stationery_paid_price

                with transaction.atomic():
                    # TotalExpenses
                    find_expenses_pk, created = TotalExpenses.objects.get_or_create(pk=1, defaults={'total_amount': 0})
                    find_expenses_pk.total_amount += stationery_paid_price
                    find_expenses_pk.save()
                stationery = form.save()

                # Create or update related TotalBook
                total_obj, created = TotalStationery.objects.get_or_create(
                    stationery=stationery,
                    defaults={
                        "total_amount": number_of_stationery,
                        "total_stationery": number_of_stationery,
                        "per_price": per_price_for_buy,
                    },
                )

                if not created:  
                    # If it already exists, just update/collect totals
                    total_obj.total_amount += number_of_stationery
                    total_obj.total_stationery += number_of_stationery
                    total_obj.per_price = per_price_for_buy  # or maybe update only if needed
                    total_obj.save()

                messages.success(request, "قرطاسیه جدید ذخیره شد ")
                form = StationeryItemForm()  # Reset after saving
                return redirect('library:library_view')

    categories = StationeryCategory.objects.all()
    stationeries = StationeryItem.objects.all()
    books = Books.objects.all()
    book_form = BooksForm()

    context = {
        'category_form': category_form,
        'form': form,
        'categories': categories,
        'stationeries': stationeries,
        'book_form': book_form,
        'books': books,
    }
    return render(request, 'library/main_library.html', context)

def delete_category(request, id):
    record = get_object_or_404(StationeryCategory, id=id)
    if record:
        record.delete()
        messages.success(request, 'کتگوری ذیل موفقانه حذف شد ....')
        return redirect('library:library_view')
    else:
        return HttpResponse('مشکل در آیدی کتگوری است')


def delete_station(request, id):
    record = get_object_or_404(StationeryItem, id=id)
    if record:
        expenses_base = TotalExpenses.objects.get(pk=1)
        expenses_base.total_amount -= record.stationery_paid_price
        expenses_base.save()
        record.delete()
        messages.success(request, 'جنس مذکور موفقانه حذف شد ....')
        return redirect('library:library_view')
    else:
        return HttpResponse('مشکل در آیدی کتگوری است')

def delete_book(request, id):
    record = get_object_or_404(Books, id=id)
    if record:
        expenses_base = TotalExpenses.objects.get(pk=1)
        expenses_base.total_amount -= record.paid_price
        expenses_base.save()
        record.delete()
        messages.success(request, 'کتاب مذکور موفقانه حذف شد ....')
        return redirect('library:library_view')
    else:
        return HttpResponse('مشکل در آیدی کتگوری است')


def edit_category(request, id):
    record = get_object_or_404(StationeryCategory, id=id)
    if request.method == "POST":
        form = StationeryCategoryForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'ریکارد ذیل موفقانه ایدیت شد ')
            return redirect('library:library_view')
    else:
        form = StationeryCategoryForm(instance=record)

    context = {
        'form':form
    }
    return render(request, 'library/edit_main_library.html', context)

def edit_station(request, id):
    record = get_object_or_404(StationeryItem, id=id)
    past_paid = record.stationery_paid_price
    past_number_of_stationery = record.number_of_stationery

    if request.method == "POST":
        form = StationeryItemForm(request.POST, instance=record)
        if form.is_valid():
            new_past_number_of_stationery = form.cleaned_data.get('number_of_stationery')
            new_per_price_stationery = form.cleaned_data.get('per_price_stationery')
            new_stationery_paid_price = form.cleaned_data.get('stationery_paid_price')

            multiply = new_past_number_of_stationery * new_per_price_stationery
            if new_stationery_paid_price > multiply or new_stationery_paid_price < multiply:
                messages.error(request, 'مقدار پرداخت نباید کوچکتر ویا بزرگتر از مقدار پرداخت باشد')
                return redirect('library:library_view')
            
            if new_past_number_of_stationery > past_number_of_stationery:
                total = TotalStationery.objects.get(stationery=record)
                find_new_count_book = new_past_number_of_stationery - total.total_amount
                total.total_stationery += find_new_count_book
                total.total_amount += find_new_count_book
                total.save()
                find_new_paid = new_stationery_paid_price - past_paid
                get_expenses = TotalExpenses.objects.get(pk=1)
                get_expenses.total_amount += find_new_paid
                get_expenses.save()
            elif new_past_number_of_stationery < past_number_of_stationery:
                total = TotalStationery.objects.get(stationery=record)
                find_new_count_book = total.total_amount - new_past_number_of_stationery
                total.total_stationery -= find_new_count_book
                total.total_amount -= find_new_count_book
                total.save()
                find_new_paid = past_paid - new_stationery_paid_price
                get_expenses = TotalExpenses.objects.get(pk=1)
                get_expenses.total_amount -= find_new_paid
                get_expenses.save()
            else:
                return redirect('library:library_view')
            form.save()
            messages.success(request, 'ریکارد ذیل موفقانه ایدیت شد ')
            return redirect('library:library_view')
    else:
        form = StationeryItemForm(instance=record)

    context = {
        'form':form,
        'record':record,
    }
    return render(request, 'library/edit_station.html', context)


def edit_book(request, id):
    record = get_object_or_404(Books, id=id)
    past_number_of_book = record.number_of_book
    past_paid = record.paid_price

    if request.method == "POST":
        form = BooksForm(request.POST, instance=record)
        if form.is_valid():
            new_past_number_of_book = form.cleaned_data.get('number_of_book')
            new_price = form.cleaned_data.get('per_price')
            new_paid_price = form.cleaned_data.get('paid_price')

            multiply = new_past_number_of_book * new_price
            if new_paid_price > multiply or new_paid_price < multiply:
                messages.error(request, 'مقدار پرداخت نباید کوچکتر ویا بزرگتر از مقدار پرداخت باشد')
                return redirect('library:library_view')

            if new_past_number_of_book > past_number_of_book:
                total = TotalBook.objects.get(book=record)
                find_new_count_book = new_past_number_of_book - total.total_amount
                total.total_book += find_new_count_book
                total.total_amount += find_new_count_book
                total.save()
                find_new_paid = new_paid_price - past_paid
                get_expenses = TotalExpenses.objects.get(pk=1)
                get_expenses.total_amount += find_new_paid
                get_expenses.save()
            elif new_past_number_of_book < past_number_of_book:
                total = TotalBook.objects.get(book=record)
                find_new_count_book = total.total_amount - new_past_number_of_book
                total.total_book -= find_new_count_book
                total.total_amount -= find_new_count_book
                total.save()
                find_new_paid = past_paid - new_paid_price
                get_expenses = TotalExpenses.objects.get(pk=1)
                get_expenses.total_amount -= find_new_paid
                get_expenses.save()
            else:
                return redirect('library:library_view')

            form.save()
            messages.success(request, 'ریکارد ذیل موفقانه ایدیت شد ')
            return redirect('library:library_view')
    else:
        form = BooksForm(instance=record)

    context = {
        'form':form,
        'record':record,
    }
    return render(request, 'library/edit_main_library.html', context)

def find_category_item(request, id):
    find_Stationery = StationeryCategory.objects.get(id=id)
    find_Stationery_items = StationeryItem.objects.filter(category=find_Stationery)
    context = {
        'find_Stationery':find_Stationery,
        'find_Stationery_items':find_Stationery_items,
        }
    return render(request, 'library/category-item.html', context)

def buy_book_again(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    book = Books.objects.get(id=id)
    total_book = TotalBook.objects.get(book=book)
    records = BuyBookAgain.objects.filter(book=book)

    if request.method == "POST":
        form = BuyBookAgainForm(request.POST)
        if form.is_valid():
            get_number_of_book_field = form.cleaned_data.get('number_of_book')
            get_per_book_price = form.cleaned_data.get('per_book_price_for_buy')

            multiply = get_number_of_book_field * form.cleaned_data.get('per_price')
            if form.cleaned_data.get('paid_price') > multiply or form.cleaned_data.get('paid_price') < multiply:
                messages.warning(request, 'مقدار پرداخت نباید کوچکتر یا بزرگتر از مقدار پرداخت باشد')
                return redirect(referer)
            
            instance = form.save(commit=False)
            instance.book = book
            instance.save()

            total_obj, created = TotalBook.objects.get_or_create(
                book=book,
                defaults={
                    "total_amount": get_number_of_book_field,
                    "total_book": get_number_of_book_field,
                    "per_price": get_per_book_price,
                },
            )

            if not created:  
                # If it already exists, just update/collect totals
                total_obj.total_amount += get_number_of_book_field
                total_obj.total_book += get_number_of_book_field
                total_obj.per_price = get_per_book_price  # or maybe update only if needed
                total_obj.save()

            total = TotalExpenses.objects.get(pk=1)
            total.total_amount += form.cleaned_data.get('paid_price')
            total.save()

            return redirect(referer)
    else:
        form = BuyBookAgainForm(initial={
            "per_price": book.per_price,
            "per_book_price_for_buy": book.per_book_price_for_buy,
        })

    context = {
        'book':book,
        'total_book':total_book,
        'form':form,
        'records':records,
    }
    return render(request, 'library/buy-book-again.html', context)

def delete_buy_again(request, id):
    record = get_object_or_404(BuyBookAgain, id=id)
    total_book = TotalBook.objects.get(book=record.book.id)
    total_book.total_book -= record.number_of_book
    total_book.total_amount -= record.number_of_book
    total_book.save()

    total_ex = TotalExpenses.objects.get(pk=1)
    total_ex.total_amount -= record.paid_price
    total_ex.save()
    messages.success(request, 'ریکارد موفقانه حذف شد')
    record.delete()
    return redirect("library:buy_book_again", id=record.book.id)  # change this to your list view name

def edit_buy_book_again(request, id):
    record = get_object_or_404(BuyBookAgain, id=id)
    past_number_of_book = record.number_of_book
    past_paid_price = record.paid_price

    if request.method == "POST":
        form = BuyBookAgainForm(request.POST, instance=record)
        if form.is_valid():
            get_new_number_of_book = form.cleaned_data.get('number_of_book')
            get_new_per_price = form.cleaned_data.get('per_price')


            multiply = get_new_number_of_book * get_new_per_price

            if form.cleaned_data.get('paid_price') > multiply or form.cleaned_data.get('paid_price') < multiply:
                messages.warning(request, 'مقدار پرداخت نباید کوچکتر یا بزرگتر از مقدار پرداخت باشد')
                return redirect("library:buy_book_again", id=record.book.id) 
            
            if get_new_number_of_book > past_number_of_book:
                total_book = TotalBook.objects.get(book=record.book.id)
                find_new_number_of_book = get_new_number_of_book - past_number_of_book
                total_book.total_amount += find_new_number_of_book
                total_book.total_book += find_new_number_of_book
                total_book.save()

                total_ex = TotalExpenses.objects.get(pk=1)
                find_new_paid = form.cleaned_data.get('paid_price') - past_paid_price
                total_ex.total_amount += find_new_paid
                total_ex.save()

            elif get_new_number_of_book < past_number_of_book:
                total_book = TotalBook.objects.get(book=record.book.id)
                find_new_number_of_book = past_number_of_book - get_new_number_of_book
                total_book.total_amount -= find_new_number_of_book
                total_book.total_book -= find_new_number_of_book
                total_book.save()

                total_ex = TotalExpenses.objects.get(pk=1)
                find_new_paid = past_paid_price - form.cleaned_data.get('paid_price')
                total_ex.total_amount -= find_new_paid
                total_ex.save()
            else:
                return redirect("library:buy_book_again", id=record.book.id) 
            form.save()
            messages.success(request, 'ریکارد ذیل موفقانه ایدیت شد')
            return redirect("library:buy_book_again", id=record.book.id) 
    else:
        form = BuyBookAgainForm(instance=record)

    context = {
        'record':record,
        'form':form,
    }
    return render(request, 'library/edit-buy-book-again.html', context)

def update_per_price(request, id):
    total_book = get_object_or_404(TotalBook, id=id)
    if request.method == "POST":
        per_price = request.POST.get("per_price")
        if per_price:
            total_book.per_price = per_price
            total_book.save()
            messages.success(request, "مقدار فی با موفقیت تغییر یافت.")
    return redirect("library:buy_book_again", id=total_book.book.id)  # change to your view name

def buy_stationery_again(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    stationery = StationeryItem.objects.get(id=id)
    total_book = TotalStationery.objects.get(stationery=stationery)
    records = BuyStationeryAgain.objects.filter(stationery=stationery)

    if request.method == "POST":
        form = BuyStationeryAgainForm(request.POST)
        if form.is_valid():
            number_of_stationery = form.cleaned_data.get('number_of_stationery')
            per_price_for_buy = form.cleaned_data.get('per_price_for_buy')

            instance = form.save(commit=False)
            instance.stationery = stationery
            instance.save()

            total_obj, created = TotalStationery.objects.get_or_create(
                stationery=stationery,
                defaults={
                    "total_amount": number_of_stationery,
                    "total_stationery": number_of_stationery,
                    "per_price": per_price_for_buy,
                },
            )
            if not created:  
                # If it already exists, just update/collect totals
                total_obj.total_amount += number_of_stationery
                total_obj.total_stationery += number_of_stationery
                total_obj.per_price = per_price_for_buy  # or maybe update only if needed
                total_obj.save()

            total = TotalExpenses.objects.get(pk=1)
            total.total_amount += form.cleaned_data.get('stationery_paid_price')    
            total.save()

            return redirect(referer)
    else:
        form = BuyStationeryAgainForm(initial={
            "per_price_stationery": stationery.per_price_stationery,
            "per_price_for_buy": stationery.per_price_for_buy,
        })

    context = {
        'stationery':stationery,
        'total_book':total_book,
        'form':form,
        'records':records,
    }
    return render(request, 'library/buy-stationery-again.html', context)


def update_stationery_per_price(request, id):
    total_book = get_object_or_404(TotalStationery, id=id)
    if request.method == "POST":
        per_price = request.POST.get("per_price_stationery")
        if per_price:
            total_book.per_price = per_price
            total_book.save()
            messages.success(request, "مقدار فی با موفقیت تغییر یافت.")
    return redirect("library:buy_stationery_again", id=total_book.book.id)  # change to your view name

def delete_buy_stationery_again(request, id):
    record = get_object_or_404(BuyStationeryAgain, id=id)
    total_book = TotalStationery.objects.get(stationery=record.stationery.id)
    total_book.total_stationery -= record.number_of_stationery
    total_book.total_amount -= record.number_of_stationery
    total_book.save()

    total_ex = TotalExpenses.objects.get(pk=1)
    total_ex.total_amount -= record.stationery_paid_price
    total_ex.save()
    messages.success(request, 'ریکارد موفقانه حذف شد')
    record.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))  # change this to your list view name

def edit_buy_stationery_again(request, id):
    record = get_object_or_404(BuyStationeryAgain, id=id)
    past_number_of_stationery = record.number_of_stationery
    past_paid_price = record.stationery_paid_price

    if request.method == "POST":
        form = BuyStationeryAgainForm(request.POST, instance=record)
        if form.is_valid():
            get_new_number_of_stationery = form.cleaned_data.get('number_of_stationery')
            get_new_per_price = form.cleaned_data.get('per_price_stationery')


            multiply = get_new_number_of_stationery * get_new_per_price

            if form.cleaned_data.get('stationery_paid_price') > multiply or form.cleaned_data.get('stationery_paid_price') < multiply:
                messages.warning(request, 'مقدار پرداخت نباید کوچکتر یا بزرگتر از مقدار پرداخت باشد')
                return redirect("library:buy_stationery_again", id=record.stationery.id) 
            
            if get_new_number_of_stationery > past_number_of_stationery:
                total_book = TotalStationery.objects.get(stationery=record.stationery.id)
                find_new_number_of_stationery = get_new_number_of_stationery - past_number_of_stationery
                total_book.total_amount += find_new_number_of_stationery
                total_book.total_stationery += find_new_number_of_stationery
                total_book.save()

                total_ex = TotalExpenses.objects.get(pk=1)
                find_new_paid = form.cleaned_data.get('stationery_paid_price') - past_paid_price
                total_ex.total_amount += find_new_paid
                total_ex.save()

            elif get_new_number_of_stationery < past_number_of_stationery:
                total_book = TotalStationery.objects.get(stationery=record.stationery.id)
                find_new_number_of_stationery = past_number_of_stationery - get_new_number_of_stationery
                total_book.total_amount -= find_new_number_of_stationery
                total_book.total_stationery -= find_new_number_of_stationery
                total_book.save()

                total_ex = TotalExpenses.objects.get(pk=1)
                find_new_paid = past_paid_price - form.cleaned_data.get('stationery_paid_price')
                total_ex.total_amount -= find_new_paid
                total_ex.save()
            else:
                return redirect("library:buy_stationery_again", id=record.stationery.id) 
            form.save()
            messages.success(request, 'ریکارد ذیل موفقانه ایدیت شد')
            return redirect("library:buy_stationery_again", id=record.stationery.id) 
    else:        
        form = BuyStationeryAgainForm(instance=record)
    context = {
        'record':record,   
        'form':form,
    }
    return render(request, 'library/edit-buy-stationery-again.html', context)