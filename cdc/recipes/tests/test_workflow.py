from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import Group
from wagtail.models import Page, Workflow, WorkflowPage
from wagtail.test.utils import WagtailPageTestCase

from cdc.recipes.models import (
    AIProcessingTask,
    RecipeIndexPage,
    RecipePage,
)


class TestWorkflowSetup(WagtailPageTestCase):
    """Testes de configuração inicial do workflow"""

    def setUp(self):
        self.root_page = Page.objects.get(slug='home')

    def test_workflow_created(self):
        """Verifica que workflow foi criado na migration"""
        workflow = Workflow.objects.filter(name='Recipe Workflow').first()
        self.assertIsNotNone(workflow)
        self.assertTrue(workflow.active)

    def test_workflow_has_two_tasks(self):
        """Verifica que workflow tem 2 tasks na ordem correta"""
        workflow = Workflow.objects.get(name='Recipe Workflow')
        tasks = workflow.workflow_tasks.order_by('sort_order')

        self.assertEqual(tasks.count(), 2)
        self.assertEqual(tasks[0].task.name, 'AI Processing Task')
        self.assertEqual(tasks[1].task.name, 'Revisão Final de Receitas')

    def test_ai_task_is_ai_processing_task(self):
        """Verifica que a task de IA é a AIProcessingTask"""
        from cdc.recipes.models import AIProcessingTask

        ai_task = AIProcessingTask.objects.first()
        self.assertIsNotNone(ai_task)

    def test_workflow_assigned_to_index(self):
        """Verifica que workflow está atribuído ao RecipeIndexPage"""
        workflow = Workflow.objects.get(name='Recipe Workflow')
        index = RecipeIndexPage.objects.filter(slug='receitas').first()

        self.assertIsNotNone(index)

        wp = WorkflowPage.objects.filter(page=index).first()
        self.assertIsNotNone(wp)
        self.assertEqual(wp.workflow, workflow)

    def test_editors_group_exists(self):
        """Verifica que grupo Editors foi criado"""
        group = Group.objects.filter(name='Editors').first()
        self.assertIsNotNone(group)

    def test_review_task_has_group(self):
        """Verifica que task de revisão tem grupo Editors associado"""
        from wagtail.models import GroupApprovalTask

        task = GroupApprovalTask.objects.filter(name='Revisão Final de Receitas').first()
        self.assertIsNotNone(task)
        self.assertTrue(task.groups.exists())

    def test_recipe_index_page_created(self):
        """Verifica que RecipeIndexPage foi criada"""
        index = RecipeIndexPage.objects.filter(slug='receitas').first()
        self.assertIsNotNone(index)
        self.assertEqual(index.title, 'Receitas')


class TestFullWorkflow(WagtailPageTestCase):
    """Testes do fluxo completo de workflow"""

    def setUp(self):
        super().setUp()
        self.root_page = Page.objects.get(slug='home')

        self.index = RecipeIndexPage.objects.filter(slug='receitas').first()
        if not self.index:
            self.index = RecipeIndexPage(title='Receitas', slug='receitas')
            self.root_page.add_child(instance=self.index)

        self.superuser = self._create_superuser('superuser')

        self.author = self._create_user('author', is_superuser=False)
        self.editor_group, _ = Group.objects.get_or_create(name='Editors')
        self.editor = self._create_user('editor', is_superuser=False)
        self.editor.groups.add(self.editor_group)

    def _create_user(self, username, **kwargs):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_user(username=username, password='password', **kwargs)

    def _create_superuser(self, username):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_superuser(username=username, email=f'{username}@test.com', password='password')

    def create_user(self, username, **kwargs):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_user(username=username, password='password', **kwargs)

    def test_submit_to_workflow(self):
        """Autor submete receita para workflow"""
        recipe = RecipePage(title='Test Recipe', slug='test-workflow-submit', raw_input='Test input', owner=self.author)
        self.index.add_child(instance=recipe)

        revision = recipe.save_revision()
        workflow = Workflow.objects.get(name='Recipe Workflow')

        workflow_state = workflow.start(recipe, user=self.author)

        self.assertEqual(workflow_state.status, 'in_progress')

        lock = recipe.get_lock()
        self.assertIsNotNone(lock)

    @patch('cdc.recipes.tasks.process_recipe_with_ai')
    def test_ai_task_processes_and_advances(self, mock_ai):
        """Task de IA processa e avança automaticamente (mock)"""
        recipe = RecipePage(title='Test Recipe AI', slug='test-workflow-ai', raw_input='Test input', owner=self.author)
        self.index.add_child(instance=recipe)

        revision = recipe.save_revision()
        workflow = Workflow.objects.get(name='Recipe Workflow')
        workflow_state = workflow.start(recipe, user=self.author)

        task_state = workflow_state.current_task_state

        ai_task = AIProcessingTask.objects.first()
        self.assertIsNotNone(ai_task)

        task_state.approve(user=None)

        workflow_state.refresh_from_db()
        self.assertEqual(workflow_state.status, 'in_progress')

        current_task = workflow_state.current_task_state.task.specific
        self.assertEqual(current_task.name, 'Revisão Final de Receitas')

    def test_editor_approves_final_review(self):
        """Editor aprova a revisão final"""
        recipe = RecipePage(
            title='Test Recipe Editor', slug='test-workflow-editor', raw_input='Test input', owner=self.author
        )
        self.index.add_child(instance=recipe)

        revision = recipe.save_revision()
        workflow = Workflow.objects.get(name='Recipe Workflow')
        workflow_state = workflow.start(recipe, user=self.author)

        workflow_state.current_task_state.approve(user=None)

        final_task_state = workflow_state.current_task_state

        final_task_state.approve(user=self.superuser)

        workflow_state.refresh_from_db()
        self.assertEqual(workflow_state.status, 'approved')

    def test_publish_after_workflow_complete(self):
        """Página é publicada após aprovação final"""
        recipe = RecipePage(
            title='Test Recipe Publish', slug='test-workflow-publish', raw_input='Test input', owner=self.author
        )
        self.index.add_child(instance=recipe)

        revision = recipe.save_revision()
        workflow = Workflow.objects.get(name='Recipe Workflow')
        workflow_state = workflow.start(recipe, user=self.author)

        workflow_state.current_task_state.approve(user=None)

        workflow_state.current_task_state.approve(user=self.superuser)

        revision = recipe.get_latest_revision()
        recipe.publish(revision=revision, user=self.superuser)

        recipe.refresh_from_db()
        self.assertTrue(recipe.live)

    def test_full_workflow_flow(self):
        """Fluxo completo: submit -> IA -> Editor approve -> Publish"""
        recipe = RecipePage(
            title='Full Flow Recipe', slug='test-workflow-full', raw_input='Complete workflow test', owner=self.author
        )
        self.index.add_child(instance=recipe)

        revision = recipe.save_revision()
        workflow = Workflow.objects.get(name='Recipe Workflow')
        workflow_state = workflow.start(recipe, user=self.author)

        self.assertEqual(workflow_state.status, 'in_progress')

        task1 = workflow_state.current_task_state.task.specific
        self.assertIn('AI', task1.name)

        workflow_state.current_task_state.approve(user=None)

        workflow_state.refresh_from_db()
        task2 = workflow_state.current_task_state.task.specific
        self.assertEqual(task2.name, 'Revisão Final de Receitas')

        workflow_state.current_task_state.approve(user=self.superuser)

        workflow_state.refresh_from_db()
        self.assertEqual(workflow_state.status, 'approved')

        revision = recipe.get_latest_revision()
        recipe.publish(revision=revision, user=self.superuser)
        recipe.refresh_from_db()
        self.assertTrue(recipe.live)
