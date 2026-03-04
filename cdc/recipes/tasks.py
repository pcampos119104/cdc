from django.tasks import task

from cdc.recipes.models import RecipePage


@task
def process_recipe_description(page: RecipePage):
    print('>>>>> process_recipe_description')
    # pegar a revisao
    latest_revision = page.get_latest_revision()
    current_draft_page = latest_revision.as_page_object()  # retorna uma instância "falsa" com campos da revisão
    current_draft_page.description = (
            current_draft_page.description + " [Processado pela IA: texto otimizado, adicionadas tags automáticas]"
    )

    # Avança o workflow automaticamente
    task = IATask.objects.get(id=task_id)
    task_state = TaskState.objects.get(task=task, workflow_state__page=page)
    task_state.finish(user=user, action='approve')  # avança para próxima task (review humana)