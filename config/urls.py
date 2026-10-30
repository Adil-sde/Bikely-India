from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bikes.urls')),  # Isse seedha http://127.0.0.1:8000/ par landing page khulega
    path('api/bikes/', include('bikes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)