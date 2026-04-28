from django.tasks import task
from wagtail.models import TaskState


@task
def process_recipe_with_ai(task_state_id):
    print('>>>>> process_recipe_description')
    task_state = TaskState.objects.get(id=task_state_id)
    page = task_state.workflow_state.content_object.specific
    print('>>>>> Processing page', page.id)
    page.processed_description = page.input_description + (
        ' [Processado pela IA: texto otimizado, adicionadas tags automáticas]'
    )
    page.save_revision()

    # avança o workflow automaticamente
    task_state.approve(user=None)
