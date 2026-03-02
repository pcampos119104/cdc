# recipes/wagtail_hooks.py
from django.http import HttpResponseRedirect
from django.urls import reverse
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem, SubmitForModerationMenuItem


class AIActionMenuItem(ActionMenuItem):
    name = 'action-submit-to-ai'
    label = 'Submeter para IA'
    icon_name = "cogs"
    order = 1

    def get_url(self, parent_context):
        request = parent_context["request"]
        return request.path + '?action=submit_to_ai'


@hooks.register('construct_page_action_menu')
def custom_action_menu(menu_items, request, context):
    menu_items[:] = [item for item in menu_items
                     if not isinstance(item, SubmitForModerationMenuItem)]

    menu_items.append(AIActionMenuItem())


@hooks.register('before_create_page')
def handle_custom_actions_create(request, parent_page, page_class):
    action = request.GET.get('action')
    if action:
        # Em add, retorna None para deixar o Wagtail salvar normal — after_create_page lida com a ação
        request.session['submit_action'] = action
        return None

    return None


@hooks.register('after_create_page')
def apply_action_after_create(request, page):
    action = request.session.pop('submit_action', None)

    if action == 'submit_to_ai':
        page.status = 'pending_review'
        page.live = False
        page.save_revision()

    if action:
        return HttpResponseRedirect(reverse('wagtailadmin_explore', args=[page.get_parent().id]))


# todo como atualizar o page.status na hora de salvar
@hooks.register('before_edit_page')
def handle_custom_actions_edit(request, page):
    action = request.GET.get('action')
    if action == 'draft':
        page.status = 'draft'
        page.live = False
        page.save_revision()
        return HttpResponseRedirect(reverse('wagtailadmin_pages:edit', args=(page.id,)))

    if action == 'submit_to_ai':
        page.status = 'pending_review'
        page.live = False
        page.save_revision()
        return HttpResponseRedirect(reverse('wagtailadmin_pages:edit', args=(page.id,)))

    if action == 'publish_direct':
        page.status = 'published'
        page.live = True
        page.save_revision()
        return HttpResponseRedirect(reverse('wagtailadmin_pages:edit', args=(page.id,)))

    return None
