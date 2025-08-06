from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib import messages
# Create your views here.


def teacher_registration(request):
    referer = request.META.get('HTTP_REFERER', '/')
    teachers = None
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(referer)
    else:
        form = TeacherForm()
        teachers = Teacher.objects.filter(is_active=True)
    context = {
        'teachers':teachers,
        'form':form,
    }
    return render(request, 'teachers/teacher-registration.html', context)

def deactive_teacher(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    if teacher:
        teacher.is_active = False
        teacher.save()
        messages.success(request, f"استاد {teacher.name} موفقانه غیر فعال شد.")
        return redirect(referer)

def active_teacher(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    teacher = Teacher.objects.get(id=id)
    if teacher:
        teacher.is_active = True
        teacher.save()
        messages.success(request, f"استاد {teacher.name} موفقانه فعال شد.")
        return redirect(referer)

def off_teachers(request):
    get_teachers = Teacher.objects.filter(is_active=False)
    return render(request, 'teachers/do-not-active-teacher.html', {'get_teachers':get_teachers})