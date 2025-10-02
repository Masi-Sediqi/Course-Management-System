from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls', namespace="home")),
    path('account/', include('account.urls', namespace="account")),
    path('students/', include('students.urls', namespace="students")),
    path('management/', include('management.urls', namespace="management")),
    path('teachers/', include('teachers.urls', namespace="teachers")),
    path('library/', include('library.urls', namespace="library")),
    path('classes/', include('classes.urls', namespace="classes")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)