
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    
]+ i18n_patterns(
    # URLs localisées ...
    path('i18n/', include('django.conf.urls.i18n')),
)
