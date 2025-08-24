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
    notifications_count = 0  # Count for the badge

    for cls in sub_records:
        remaining = None
        try:
            end_jalali = jdatetime.datetime.strptime(cls.end_date, "%d/%m/%Y").date()
            start_jalali = jdatetime.datetime.strptime(cls.start_date, "%d/%m/%Y").date()
            today_jalali = jdatetime.date.today()
            remaining = (end_jalali - today_jalali).days
        except Exception as e:
            print("DEBUG: Error parsing date:", cls.end_date, "| Exception:", e)
            continue

        if remaining is not None:
            if remaining == 0:
                # Class ended today → danger notification
                notifications.append({
                    "name": cls.name,
                    "start_date": cls.start_date,
                    "remaining": remaining,
                    "type": "danger"
                })
                notifications_count += 1
            elif remaining <= 3:
                # Only 1–3 days remaining → warning notification
                notifications.append({
                    "name": cls.name,
                    "start_date": cls.start_date,
                    "remaining": remaining,
                    "type": "warning"
                })
                notifications_count += 1
            # Classes with more than 3 days remaining → ignored

    context = {
        "notifications": notifications,
        "notifications_count": notifications_count  # For badge display
    }

    return render(request, 'noti/notifications.html', context)
