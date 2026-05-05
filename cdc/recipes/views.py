"""Views for recipe API interactions, handling pending recipes and AI responses."""

import json

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import RecipePage


class PendingRecipesView(View):
    """API view for retrieving and updating pending recipes with AI processing."""

    @method_decorator(csrf_exempt)
    def get(self, request):
        """Returns JSON list of pending recipes for authenticated users."""
        # Check auth (e.g., simple API key)
        api_key = request.headers.get('X-API-Key')
        if api_key != settings.RECIPE_API_KEY:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        pendings = RecipePage.objects.filter(status='pending_review')
        data = [
            {
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.raw_input,
            }
            for recipe in pendings
        ]
        # Return JSON with list of pending recipes
        return JsonResponse({'pendings': data})

    @method_decorator(csrf_exempt)
    def post(self, request):
        """Updates a recipe with AI response data and advances workflow state."""
        # Check auth
        api_key = request.headers.get('X-API-Key')
        if api_key != settings.RECIPE_API_KEY:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        recipe_id = data.get('id')
        ai_response = data.get('ai_response', {})  # Expect JSON with structured data
        tags_str = data.get('tags', '')

        try:
            recipe = RecipePage.objects.get(id=recipe_id)
            # Update recipe with AI response and set status
            # Store the raw AI response
            recipe.raw_ai_response = ai_response
            # Populate structured fields from AI response
            recipe.description = ai_response.get('description', '')
            recipe.directions = ai_response.get('directions', '')
            recipe.font = ai_response.get('font', '')
            recipe.status = 'final_review'
            if tags_str:
                tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                recipe.tags.set(tags_list)
            recipe.save()
            return JsonResponse({'status': 'updated'})
        except RecipePage.DoesNotExist:
            return JsonResponse({'error': 'Recipe not found'}, status=404)
