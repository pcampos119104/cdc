from django.urls import path

from cdc.base.views import HomeView, htmx

app_name = 'base'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('htmx/', htmx, name='htmx'),
]
