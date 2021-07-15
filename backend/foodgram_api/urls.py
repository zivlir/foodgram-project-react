from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.flatpages import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
]
