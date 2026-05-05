"""URL patterns for the recipes app."""

from django.urls import path

from .views import PendingRecipesView

app_name = 'recipes'
urlpatterns = [
    # API endpoint for pending recipes
    path('api/pending/', PendingRecipesView.as_view(), name='pending'),
]
