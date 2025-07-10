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






# ________________________________ view for students registration ________________________________________ info 

def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    context = {
        'student': student,
    }
    return render(request, 'students/student-detail.html', context)