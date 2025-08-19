from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib import messages
# Create your views here.

def subjects(request):
    if request.method == "POST":
        form = SubjectsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'مضمون ذیل موفقانه اضافه شد')
            return redirect('subjects:subjects')
    else:
        form = SubjectsForm()
    datas = Subjects.objects.all()

    context = {
        'datas':datas,
        'form':form,
    }
    return render(request, 'subjects/subjects-main-page.html', context)