from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from.forms import *



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


from django.contrib import messages
from .models import MainClass, SubClass
from .forms import MainClassForm, SubClassForm

def main_classes(request):
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
                print("DEBUG: SubClass created:", instance.name)  # ✅
                return redirect(referer)
        else:
            main_form = MainClassForm(request.POST)
            if main_form.is_valid():
                instance = main_form.save()
                messages.success(request, 'دوره جدید موفقانه اضافه شد')
                print("DEBUG: MainClass created:", instance.name)  # ✅
                return redirect(referer)
    else:
        sub_form = SubClassForm()
        main_form = MainClassForm()

    main_records = MainClass.objects.all()
    sub_records = SubClass.objects.all()
    print("DEBUG: Found", sub_records.count(), "SubClass records")  # ✅

    notifications = []
    for cls in sub_records:
        print("DEBUG: Checking SubClass:", cls.name, "Start:", cls.start_date, "End:", cls.end_date)  # ✅
        remaining = cls.get_remaining_days()
        print("DEBUG: Remaining days for", cls.name, "=", remaining)  # ✅
        if remaining is not None:
            if remaining == 0:
                msg = f"صنف {cls.name} امروز ختم شد!"
                print("DEBUG:", msg)
                notifications.append({"message": msg, "type": "danger"})
            elif remaining <= 3:
                msg = f"از صنف {cls.name} فقط {remaining} روز باقی مانده است!"
                print("DEBUG:", msg)
                notifications.append({"message": msg, "type": "warning"})
            else:
                msg = f"از صنف {cls.name} {remaining} روز باقی مانده است."
                print("DEBUG:", msg)
                notifications.append({"message": msg, "type": "info"})
        else:
            print("DEBUG: Could not calculate remaining days for", cls.name)  # ✅

    context = {
        'main_form': main_form,
        'sub_form': sub_form,
        'main_records': main_records,
        'sub_records': sub_records,
        'notifications': notifications,
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




def delete_sub_class(request, pk):
    instance = get_object_or_404(SubClass, pk=pk)
    instance.delete()
    messages.success(request, "صنف موفقانه حذف شد")
    return redirect('classes:main_classes')





