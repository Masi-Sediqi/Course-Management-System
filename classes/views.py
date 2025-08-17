from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from.forms import *
# Create your views here.

def main_classes(request):
    referer = request.META.get('HTTP_REFERER', '/')
    main_form=None
    sub_form=None
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == "class":
            sub_form = SubClassForm(request.POST)
            if sub_form.is_valid():
                instance = sub_form.save(commit=False)
                instance.save()
                sub_form.save_m2m() 
                messages.success(request, 'صنف جدید موفقانه اضافه شد')
                return redirect(referer)
        else:
            main_form = MainClassForm(request.POST)
            if main_form.is_valid():
                main_form.save()
                messages.success(request, 'دوره جدید موفقانه اضافه شد')
                return redirect(referer)
    else:
        sub_form = SubClassForm()
        main_form = MainClassForm()
    main_records = MainClass.objects.all()
    sub_records = SubClass.objects.all()
    
    context = {
        'main_form':main_form,
        'sub_form':sub_form,
        'main_records':main_records,
        'sub_records':sub_records,
    }
    return render(request, 'classes/class-main.html', context)