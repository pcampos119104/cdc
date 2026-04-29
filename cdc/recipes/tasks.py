from django.tasks import task
from wagtail.models import TaskState


@task
def process_recipe_with_ai(task_state_id):
    print('>>>>> process_recipe_with_ai')
    task_state = TaskState.objects.get(id=task_state_id)
    page = task_state.workflow_state.content_object.specific
    print('>>>>> Processing page', page.id)

    # Mock AI response JSON
    mock_ai_response = {
        'description': 'Descrição extraída da receita por IA.',
        'directions': 'Passos do preparo extraídos por IA.',
        'ingredients': [{'ingredient': 'Ingrediente Exemplo', 'quantity': '1', 'metric': 'xícara', 'qualifiers': []}],
        'font': 'Fonte extraída por IA.',
    }

    # Store raw AI response
    page.raw_ai_response = mock_ai_response

    # Populate structured fields from mock data
    page.description = mock_ai_response['description']
    page.directions = mock_ai_response['directions']
    page.font = mock_ai_response['font']

    # Create basic ingredients (for mock, create new snippets if needed)
    from cdc.recipes.models import Ingredient, Metric, RecipeIngredient

    for ing_data in mock_ai_response['ingredients']:
        # Create or get ingredient
        ingredient, _ = Ingredient.objects.get_or_create(name=ing_data['ingredient'])
        # Create or get metric
        metric, _ = Metric.objects.get_or_create(name=ing_data['metric'], defaults={'abbr': ing_data['metric'][:3]})
        # Create RecipeIngredient
        RecipeIngredient.objects.create(page=page, ingredient=ingredient, metric=metric, quantity=ing_data['quantity'])

    page.save_revision()

    # avança o workflow automaticamente
    task_state.approve(user=None)
