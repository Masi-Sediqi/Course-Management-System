from django.contrib import messages
from django.http import HttpResponse
from.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from .models import MainClass, SubClass
from account.models import *
from django.utils import timezone

def main_classes(request):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    referer = request.META.get('HTTP_REFERER', '/')
    main_form = None
    sub_form = None
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == "class":
            sub_form = SubClassForm(request.POST)
            if sub_form.is_valid():
                instance = sub_form.save(commit=False)
                instance.save()
                sub_form.save_m2m()
                messages.success(request, 'صنف جدید موفقانه اضافه شد')
                print("DEBUG: SubClass created:", instance.name) 
                return redirect(referer)
        else:
            main_form = MainClassForm(request.POST)
            if main_form.is_valid():
                instance = main_form.save()
                messages.success(request, 'دوره جدید موفقانه اضافه شد')
                print("DEBUG: MainClass created:", instance.name) 
                return redirect(referer)
    else:
        sub_form = SubClassForm()
        main_form = MainClassForm()

    main_records = MainClass.objects.all()
    sub_records = SubClass.objects.all()

    context = {
        'main_form': main_form,
        'sub_form': sub_form,
        'main_records': main_records,
        'sub_records': sub_records,
    }
    return render(request, 'classes/class-main.html', context)

def edit_sub_class(request, pk):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
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
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    instance = get_object_or_404(SubClass, pk=pk)
    instance.active = False
    instance.save()
    messages.success(request, "صنف موفقانه غیر فعال شد")
    return redirect('classes:main_classes')

def active_sub_class(request, pk):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    instance = get_object_or_404(SubClass, pk=pk)
    instance.active = True
    instance.save()
    messages.success(request, "صنف موفقانه فعال شد")
    return redirect('classes:main_classes')


def delete_sub_class(request, pk):
    get_lisance_check_model = Licsanse_check.objects.get(pk=1)
    license_time = get_lisance_check_model.date
    # Get today's date in the same timezone
    today = timezone.localdate()

    if license_time.date() <= today:
        return redirect('management:hesabpay')
    else:
        print("❌ The license date is not today.")
    instance = get_object_or_404(SubClass, pk=pk)
    instance.delete()
    messages.success(request, "صنف موفقانه حذف شد")
    return redirect('classes:main_classes')

def edit_main_class(request, id):
    record = MainClass.objects.get(id=id)
    if request.method == "POST":
        main_form = MainClassForm(request.POST, instance=record)
        if main_form.is_valid():
            instance = main_form.save()
            messages.success(request, 'دوره موفقانه اضافه شد')
            print("DEBUG: MainClass created:", instance.name) 
            return redirect('classes:main_classes')
    else:
        main_form = MainClassForm(instance=record)

    return render(request, 'classes/edit_main_class.html', {'form':main_form, 'record':record})

def delete_main_class(request, id):
    record = MainClass.objects.get(id=id)
    record.delete()
    messages.success(request, 'دوره موفقانه حذف شد')
    return redirect('classes:main_classes')