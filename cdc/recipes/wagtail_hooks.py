# recipes/wagtail_hooks.py
from django.http import HttpResponseRedirect
from django.urls import reverse
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem, SubmitForModerationMenuItem

from .models import RecipeIndexPage, RecipePage


class AIActionMenuItem(ActionMenuItem):
    name = 'action-submit-to-ai'
    label = 'Submeter para IA'
    icon_name = 'cogs'
    order = 1


@hooks.register('construct_page_action_menu')
def custom_action_menu(menu_items, request, context):
    if not isinstance(context.get('parent_page'), RecipeIndexPage) \
            and not isinstance(context.get('page'), RecipePage):
        return
    menu_items[:] = [item for item in menu_items if not isinstance(item, SubmitForModerationMenuItem)]
    menu_items.append(AIActionMenuItem())


@hooks.register('after_create_page')
@hooks.register('after_edit_page')
def apply_action_after_create(request, page):
    if 'action-submit-to-ai' not in request.POST:
        return
    page.status = 'pending_review'
    page.live = False
    page.save_revision(log_action=True)
    # todo add to task framework
