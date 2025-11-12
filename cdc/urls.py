from django.contrib import admin
from django.urls import include, path

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('cms/', include(wagtailadmin_urls)),
    path('', include(wagtail_urls)),
    path('documents/', include(wagtaildocs_urls)),
]
