from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def colculator(request):
    return render(request, 'colculator.html')

from django.shortcuts import render
from classes.models import SubClass
import jdatetime

def notification(request):
    sub_records = SubClass.objects.all()
    notifications = []

    for cls in sub_records:
        remaining = None
        try:
            end_jalali = jdatetime.datetime.strptime(cls.end_date, "%d/%m/%Y").date()
            start_jalali = jdatetime.datetime.strptime(cls.start_date, "%d/%m/%Y").date()
            today_jalali = jdatetime.date.today()
            remaining = max((end_jalali - today_jalali).days, 0)
        except Exception as e:
            print("DEBUG: Error parsing date:", cls.end_date, "| Exception:", e)

        if remaining is not None:
            if remaining == 0:
                notifications.append({
                    "name": cls.name,
                    "start_date": cls.start_date,
                    "remaining": remaining,
                    "type": "danger"
                })
            elif remaining <= 3:
                notifications.append({
                    "name": cls.name,
                    "start_date": cls.start_date,
                    "remaining": remaining,
                    "type": "warning"
                })
            else:
                notifications.append({
                    "name": cls.name,
                    "start_date": cls.start_date,
                    "remaining": remaining,
                    "type": "info"
                })

    context = {
        "notifications": notifications
    }
    return render(request, 'noti/notifications.html', context)
