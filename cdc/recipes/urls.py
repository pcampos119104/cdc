from django.urls import path

from .views import PendingRecipesView

app_name = 'recipes'
urlpatterns = [
    path('api/pending/', PendingRecipesView.as_view(), name='pending'),
]
