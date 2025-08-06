from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import *
from django.http import HttpResponse
# Create your views here.

def library_view(request):
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
                book_form.save()
                book_form = BooksForm()
                messages.success(request, "کتاب با موفقیت اضافه شد ")
                return redirect('library:library_view')
        else:
            form = StationeryItemForm(request.POST)
            if form.is_valid():
                form.save()
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
        record.delete()
        messages.success(request, 'جنس مذکور موفقانه حذف شد ....')
        return redirect('library:library_view')
    else:
        return HttpResponse('مشکل در آیدی کتگوری است')

def delete_book(request, id):
    record = get_object_or_404(Books, id=id)
    if record:
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
    if request.method == "POST":
        form = StationeryItemForm(request.POST, instance=record)
        if form.is_valid():
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
    if request.method == "POST":
        form = BooksForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'ریکارد ذیل موفقانه ایدیت شد ')
            return redirect('library:library_view')
    else:
        form = BooksForm(instance=record)

    context = {
        'form':form
    }
    return render(request, 'library/edit_main_library.html', context)