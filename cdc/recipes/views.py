import json

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import RecipePage


class PendingRecipesView(View):
    @method_decorator(csrf_exempt)
    def get(self, request):
        # Verifique auth (ex: API key simples)
        api_key = request.headers.get('X-API-Key')
        if api_key != settings.RECIPE_API_KEY:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        pendings = RecipePage.objects.filter(status='pending_review')
        data = [
            {
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.input_description,
            }
            for recipe in pendings
        ]
        return JsonResponse({'pendings': data})

    @method_decorator(csrf_exempt)
    def post(self, request):
        # Verifique auth
        api_key = request.headers.get('X-API-Key')
        if api_key != settings.RECIPE_API_KEY:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        recipe_id = data.get('id')
        processed_desc = data.get('processed_description')
        tags_str = data.get('tags', '')

        try:
            recipe = RecipePage.objects.get(id=recipe_id)
            recipe.processed_description = processed_desc
            recipe.status = 'final_review'
            if tags_str:
                tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                recipe.tags.set(tags_list)
            recipe.save()
            return JsonResponse({'status': 'updated'})
        except RecipePage.DoesNotExist:
            return JsonResponse({'error': 'Recipe not found'}, status=404)
