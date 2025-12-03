from django import template
from wagtail.models import Page, Site

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context['request']).root_page


@register.simple_tag(takes_context=True)
def is_active_menuitem(context, menuitem):
    """
    Verifica se a página atual é o menuitem ou uma descendente dele.
    Retorna True se ativo, False caso contrário.
    """
    page = context.get('page')
    if isinstance(page, Page):
        return page.pk == menuitem.pk or page.is_descendant_of(menuitem)
    return False
