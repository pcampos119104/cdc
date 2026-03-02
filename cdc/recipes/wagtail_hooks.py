# recipes/wagtail_hooks.py
from django.http import HttpResponseRedirect
from django.urls import reverse
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem, SubmitForModerationMenuItem

from .models import RecipePage, RecipeIndexPage


class AIActionMenuItem(ActionMenuItem):
    name = 'action-submit-to-ai'
    label = 'Submeter para IA'
    icon_name = 'cogs'
    order = 1

    # def get_url(self, parent_context):
    #   request = parent_context['request']
    #  return request.path + '?action=submit_to_ai'


@hooks.register('construct_page_action_menu')
def custom_action_menu(menu_items, request, context):
    print('@@@@@@@@@@@@@@@@@@@ construct_page_action_menu @@@@@@@@@@@@@@@@@@@@@@@@')
    if not isinstance(context.get('parent_page'), RecipeIndexPage) \
            and not isinstance(context.get('page'), RecipePage):
        return
    menu_items[:] = [item for item in menu_items if not isinstance(item, SubmitForModerationMenuItem)]
    menu_items.append(AIActionMenuItem())


@hooks.register('before_create_page')
def handle_custom_actions_create(request, parent_page, page_class):
    print('@@@@@@@@@@@@@@@@@@@ before_create_page @@@@@@@@@@@@@@@@@@@@@@@@')
    action = request.GET.get('action')
    if action:
        # Em add, retorna None para deixar o Wagtail salvar normal — after_create_page lida com a ação
        request.session['submit_action'] = action


@hooks.register('after_create_page')
@hooks.register('after_edit_page')
def apply_action_after_create(request, page):
    print('@@@@@@@@@@@@@@@@@@@ after_create_page @@@@@@@@@@@@@@@@@@@@@@@@')

    if bool(request.POST.get('action-submit-to-ai')):
        page.status = 'pending_review'
        page.live = False
        page.save_revision()
