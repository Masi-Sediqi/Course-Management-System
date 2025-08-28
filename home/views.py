from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from students.models import *
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
    notifications_count = 0

    today = jdatetime.date.today().togregorian()
    students = StudentWithoutClass.objects.filter(jalali_to_gregorian=today)

    # 🔹 Student Notifications
    for s in students:
        notifications.append({
            "type": "warning",
            "name": f"{s.first_name} {s.last_name}",
            "start_date": s.date_for_notification,
            "phone": s.phone,        # ✅ add phone
            "remaining": 0,
            "source": "student"   # ✅ NEW
        })

    # 🔹 Class Notifications
    for cls in sub_records:
        try:
            end_jalali = jdatetime.datetime.strptime(cls.end_date, "%d/%m/%Y").date()
            today_jalali = jdatetime.date.today()
            remaining = (end_jalali - today_jalali).days
        except Exception as e:
            print("DEBUG: Error parsing date:", cls.end_date, "| Exception:", e)
            continue

        if remaining == 0:
            notifications.append({
                "name": cls.name,
                "start_date": cls.start_date,
                "remaining": remaining,
                "type": "danger",
                "source": "class"   # ✅ NEW
            })
            notifications_count += 1
        elif remaining <= 3:
            notifications.append({
                "name": cls.name,
                "start_date": cls.start_date,
                "remaining": remaining,
                "type": "warning",
                "source": "class"   # ✅ NEW
            })
            notifications_count += 1

    context = {
        "notifications": notifications,
        "notifications_count": notifications_count
    }
    return render(request, 'noti/notifications.html', context)
