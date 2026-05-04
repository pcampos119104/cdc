from django.contrib.auth.models import Group
from django.db import migrations
from wagtail.models import GroupApprovalTask, Page, Workflow, WorkflowPage, WorkflowTask


def create_recipe_workflow(apps, schema_editor):
    editors_group, _ = Group.objects.get_or_create(name='Editors')

    review_task, created = GroupApprovalTask.objects.get_or_create(
        name='Revisão Final de Receitas', defaults={'active': True}
    )
    if created:
        review_task.save()
        review_task.groups.add(editors_group)
        review_task.save()
    else:
        if editors_group not in review_task.groups.all():
            review_task.groups.add(editors_group)

    root_page = Page.objects.filter(slug='home').first()
    if not root_page:
        root_page = Page.objects.filter(depth=1).first()

    if root_page:
        from cdc.recipes.models import RecipeIndexPage

        recipe_index = RecipeIndexPage.objects.filter(slug='receitas').first()
        if not recipe_index:
            recipe_index = RecipeIndexPage.objects.filter(slug='recipes', content_type__model='recipeindexpage').first()
        if not recipe_index:
            recipe_index = RecipeIndexPage(title='Receitas', slug='receitas')
            root_page.add_child(instance=recipe_index)
    else:
        recipe_index = None

    workflow, _ = Workflow.objects.get_or_create(name='Recipe Workflow', defaults={'active': True})

    from cdc.recipes.models import AIProcessingTask

    ai_task, ai_created = AIProcessingTask.objects.get_or_create(
        name='AI Processing Task', defaults={'active': True}
    )

    if ai_created:
        ai_task.save()

    if workflow:
        workflow.workflow_tasks.all().delete()

        WorkflowTask.objects.create(workflow=workflow, task=ai_task, sort_order=1)
        WorkflowTask.objects.create(workflow=workflow, task=review_task, sort_order=2)

    if recipe_index and workflow:
        WorkflowPage.objects.get_or_create(page=recipe_index, defaults={'workflow': workflow})


def reverse_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0011_make_image_nullable'),
        ('steady_queue', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_recipe_workflow, reverse_migration),
    ]
