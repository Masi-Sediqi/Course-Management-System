from django.contrib import messages
from django.http import HttpResponse
from.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from .models import SubClass
from account.models import *

def main_classes(request):

    referer = request.META.get('HTTP_REFERER', '/')
    main_form = None
    sub_form = None
    if request.method == "POST":
        sub_form = SubClassForm(request.POST)
        if sub_form.is_valid():
            instance = sub_form.save(commit=False)
            instance.save()
            sub_form.save_m2m()
            messages.success(request, 'صنف جدید موفقانه اضافه شد')
            print("DEBUG: SubClass created:", instance.name) 
            return redirect(referer)
    else:
        sub_form = SubClassForm()

    sub_records = SubClass.objects.all()

    context = {
        'main_form': main_form,
        'sub_form': sub_form,
        'sub_records': sub_records,
    }
    return render(request, 'classes/class-main.html', context)

def edit_sub_class(request, pk):

    instance = get_object_or_404(SubClass, pk=pk)
    if request.method == "POST":
        form = SubClassForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "صنف موفقانه ویرایش شد")
            return redirect('classes:main_classes')
    else:
        form = SubClassForm(instance=instance)
    return render(request, 'classes/edit_sub_class.html', {'form': form, 'instance': instance})


def deactive_sub_class(request, pk):

    instance = get_object_or_404(SubClass, pk=pk)
    instance.active = False
    instance.save()
    messages.success(request, "صنف موفقانه غیر فعال شد")
    return redirect('classes:main_classes')

def active_sub_class(request, pk):

    instance = get_object_or_404(SubClass, pk=pk)
    instance.active = True
    instance.save()
    messages.success(request, "صنف موفقانه فعال شد")
    return redirect('classes:main_classes')


def delete_sub_class(request, pk):

    instance = get_object_or_404(SubClass, pk=pk)
    instance.delete()
    messages.success(request, "صنف موفقانه حذف شد")
    return redirect('classes:main_classes')