from django.shortcuts import render, redirect , get_object_or_404
from .forms import *
from .models import *
from django.http import HttpResponse
from django.contrib import messages
# Create your views here.

def students_registration(request):
    form = None
    students = None

    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students:students_registration')
    else:
        form = StudentForm()
    
    form = StudentForm()
    students = Student.objects.all()

    context = {
        'students':students,
        'form':form,
    }

    return render(request, 'students/students-registration.html', context)

def delete_students(request, id):
    get_student_id = Student.objects.get(id=id)
    if get_student_id:
        get_student_id.delete()
        messages.success(request, 'شاگرد موفقانه ذخیره شد')
        return redirect('students:students_registration')
    else:
        return HttpResponse('User Is Not in Detabase')

def edit_students(request, id):
    get_student_id = Student.objects.get(id=id)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=get_student_id)
        if form.is_valid():
            form.save()
            messages.success(request, f" دانش‌آموز{get_student_id.first_name} {get_student_id.last_name} موفقانه تغییرات آورده شد.")
            return redirect('students:edit_students', id=get_student_id.id)  # or render response
        else:
            return HttpResponse('مشکل در تغییر شاگرد آمده ...')

    form = StudentForm(instance=get_student_id)

    context = {
        'get_student_id':get_student_id,
        'form':form,
    }
    return render(request, 'students/student-edit.html', context)

def student_bill(request, id):
    student = Student.objects.get(id=id)
    return render(request, 'students/student-bill.html', {
        'student': student,
    })


def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    context = {
        'student': student,
    }
    return render(request, 'students/student-detail.html', context)


def student_fees_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        form = Student_fess_infoForm(request.POST)
        if form.is_valid():
            fees_info = form.save(commit=False)
            fees_info.student = student  # Link to the correct student
            fees_info.save()
            return redirect('students:student_fees_detail', student_id=student.id)
    else:
        form = Student_fess_infoForm(initial={
            'orginal_fees': student.orginal_fees
        })

    context = {
        'student': student,
        'form': form,
    }
    return render(request, 'students/student-fees-detail.html', context)