from django.urls import path

from cdc.base.views import simple_page, api_response

app_name = 'base'

urlpatterns = [
    path('simple/', simple_page, name='simple_page'),
    path('api/response/', api_response, name='api_response'),
]
