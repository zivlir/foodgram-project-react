from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),
    path('admin/', admin.site.urls),
    path(r'auth/', include('djoser.urls')),
    path(r'^auth/', include('djoser.urls.authtoken')),
    # path('auth/', include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
]
