from django.contrib import messages
from.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from .models import SubClass
from account.models import *
from home.models import SystemLog
from students.models import *
from teachers.models import *
from django.db import transaction
from django.http import HttpResponse


def main_classes(request):
    referer = request.META.get('HTTP_REFERER', '/')
    teachers = Teacher.objects.filter(is_active=True)
    books = Item.objects.all()
    
    if request.method == "POST":
        sub_form = SubClassForm(request.POST)
        
        if sub_form.is_valid():
            try:
                with transaction.atomic():
                    instance = sub_form.save(commit=False)
                    instance.save()
                    
                    # Get selected teachers
                    selected_teacher_ids = request.POST.getlist('selected_teachers')
                    if selected_teacher_ids:
                        selected_teachers = Teacher.objects.filter(id__in=selected_teacher_ids)
                        instance.teacher.set(selected_teachers)
                    
                    # Get selected books
                    selected_book_ids = request.POST.getlist('selected_books')
                    if selected_book_ids:
                        selected_books = Item.objects.filter(id__in=selected_book_ids)
                        instance.books.set(selected_books)
                    
                    # Save other ManyToMany fields if any
                    sub_form.save_m2m()
                    
                    SystemLog.objects.create(
                        section="صنف‌ها",
                        action=f"ایجاد صنف جدید: {instance.name}",
                        description=f"صنف {instance.name} ایجاد شد",
                        user=request.user if request.user.is_authenticated else None
                    )
                    
                    messages.success(request, f'صنف {instance.name} با موفقیت ایجاد شد')
                    return redirect(referer)
                    
            except Exception as e:
                messages.error(request, f'خطا در ایجاد صنف: {str(e)}')
                print(f"Error: {e}")  # Debug
        else:
            print("Form errors:", sub_form.errors)  # Debug
            messages.error(request, 'لطفاً فرم را به درستی پر کنید')
    else:
        sub_form = SubClassForm()

    sub_records = SubClass.objects.all()

    context = {
        'sub_form': sub_form,
        'sub_records': sub_records,
        'teachers': teachers,
        'books': books,
    }
    return render(request, 'classes/class-main.html', context)


def edit_sub_class(request, pk):
    instance = get_object_or_404(SubClass, pk=pk)
    teachers = Teacher.objects.filter(is_active=True)
    
    # Get existing teacher percentages
    existing_percentages = {}
    salary_records = TeacherColculationSalary.objects.filter(sub_class=instance)
    for record in salary_records:
        existing_percentages[record.teacher.id] = record.percentage
    
    if request.method == "POST":
        form = SubClassForm(request.POST, instance=instance)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save the class
                    updated_instance = form.save()
                    
                    # Get selected teachers and their percentages from POST data
                    selected_teachers = []
                    teacher_percentages = {}
                    
                    for teacher in teachers:
                        percentage_field = f'teacher_percentage_{teacher.id}'
                        percentage = request.POST.get(percentage_field, '').strip()
                        
                        if percentage:
                            try:
                                percentage_float = float(percentage)
                                if percentage_float > 0:
                                    selected_teachers.append(teacher)
                                    teacher_percentages[teacher.id] = percentage_float
                            except ValueError:
                                pass
                    
                    # Update ManyToMany field
                    updated_instance.teacher.set(selected_teachers)
                    
                    # Delete existing TeacherColculationSalary records for this class
                    TeacherColculationSalary.objects.filter(sub_class=updated_instance).delete()
                    
                    # Create new TeacherColculationSalary records
                    for teacher_id, percentage in teacher_percentages.items():
                        teacher = Teacher.objects.get(id=teacher_id)
                        TeacherColculationSalary.objects.create(
                            teacher=teacher,
                            sub_class=updated_instance,
                            percentage=percentage
                        )
                    
                    SystemLog.objects.create(
                        section="صنف‌ها",
                        action="ویرایش صنف",
                        description=f"صنف {updated_instance.name} ویرایش شد.",
                        user=request.user if request.user.is_authenticated else None
                    )
                    
                    messages.success(request, "صنف موفقانه ویرایش شد")
                    return redirect('classes:main_classes')
                    
            except Exception as e:
                messages.error(request, f'خطا در ویرایش صنف: {str(e)}')
                print(f"Error editing class: {e}")
        else:
            messages.error(request, "لطفاً فرم را به درستی پر کنید")
    else:
        form = SubClassForm(instance=instance)
    
    context = {
        'sub_form': form,
        'instance': instance,
        'teachers': teachers,
        'existing_percentages': existing_percentages,
    }
    return render(request, 'classes/edit_sub_class.html', context)


def deactive_sub_class(request, pk):

    instance = get_object_or_404(SubClass, pk=pk)
    instance.active = False
    instance.save()
    SystemLog.objects.create(
        section="صنف‌ها",
        action=f"غیر فعال کردن صنف:",
        description=f"صنف {instance.name} غیر فعال شد.",
        user=request.user if request.user.is_authenticated else None
    )
    messages.success(request, "صنف موفقانه غیر فعال شد")
    return redirect('classes:main_classes')

def active_sub_class(request, pk):

    instance = get_object_or_404(SubClass, pk=pk)
    instance.active = True
    instance.save()
    SystemLog.objects.create(
        section="صنف‌ها",
        action=f"فعال کردن صنف:",
        description=f"صنف {instance.name} فعال شد.",
        user=request.user if request.user.is_authenticated else None
    )
    messages.success(request, "صنف موفقانه فعال شد")
    return redirect('classes:main_classes')


def delete_sub_class(request, pk):

    instance = get_object_or_404(SubClass, pk=pk)
    instance.delete()
    SystemLog.objects.create(
        section="صنف‌ها",
        action=f"حذف صنف:",
        description=f"صنف {instance.name} حذف شد.",
        user=request.user if request.user.is_authenticated else None
    )
    messages.success(request, "صنف موفقانه حذف شد")
    return redirect('classes:main_classes')

def class_info(request, id):
    sub_class = get_object_or_404(SubClass, id=id)
    students = Student_fess_info.objects.filter(st_class=sub_class, student__is_active=True)
    total_paid = students.aggregate(total_paid=models.Sum('give_fees'))['total_paid'] or 0
    total_remain = students.aggregate(total_remain=models.Sum('remain_fees'))['total_remain'] or 0
    context = {
        'sub_class': sub_class,
        'students': students,
        'total_paid': total_paid,
        'total_remain': total_remain,
    }
    return render(request, 'classes/class-info.html', context)