from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page, Task
from wagtail.search import index

from cdc.recipes.tasks import process_recipe_with_ai


class RecipeIndexPage(Page):
    intro = RichTextField(blank=True)
    subpage_types = [
        'recipes.RecipePage',
    ]
    content_panels = Page.content_panels + ['intro']

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        recipepages = self.get_children().live().order_by('-first_published_at')
        context['recipepages'] = recipepages
        return context


class RecipeTagIndexPage(Page):
    template = 'recipes/recipe_tag_index_page.html'

    def get_context(self, request):
        context = super().get_context(request)
        tag_name = request.GET.get('tag')

        if tag_name:
            # Filtrar receitas por tag específica
            recipepages = RecipePage.objects.live().filter(tags__name=tag_name)
            context['current_tag'] = tag_name
        else:
            # Mostrar todas as tags disponíveis com contagem
            from django.db.models import Count
            from taggit.models import Tag

            all_tags = (
                Tag.objects.annotate(num_items=Count('taggit_taggeditem_items') + 1)
                .filter(num_items__gt=0)
                .order_by('-num_items', 'name')
            )
            context['all_tags'] = all_tags
            recipepages = RecipePage.objects.none()

        context['recipepages'] = recipepages
        return context


class RecipePageTag(TaggedItemBase):
    content_object = ParentalKey('RecipePage', related_name='tagged_items', on_delete=models.CASCADE)


class RecipePage(Page):
    input_description = RichTextField(  # Tudo cru aqui: descrição, ingredientes, preparo, fonte
        verbose_name='Descrição completa (crua)',
        help_text='Escreva descrição, ingredientes, preparo e fonte. Será processado automaticamente.',
    )
    processed_description = RichTextField(  # Versão formatada pela IA
        verbose_name='Descrição processada', blank=True, help_text='Versão final após IA.'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('pending_review', 'Pending IA'),
            ('in_review', 'In Review'),
            ('published', 'Published'),
        ],
        default='draft',
        editable=False,
    )
    tags = ClusterTaggableManager(through=RecipePageTag, blank=True)
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.PROTECT, related_name='+')

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
        FieldPanel('input_description'),
        FieldPanel('processed_description'),
        FieldPanel('image'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('input_description'),
        index.SearchField('processed_description'),
    ]
    parent_page_types = ['recipes.RecipeIndexPage']
    subpage_types = []

    def save(self, *args, **kwargs):
        if self.status != 'published':
            self.live = False
        else:
            self.live = True
        super().save(*args, **kwargs)


class AIProcessingTask(Task):
    label = 'AI processing task'

    class Meta:
        verbose_name = 'AI Processing Task'
        verbose_name_plural = 'AI Processing Tasks'

    def start(self, workflow_state, user=None):
        task_state = super().start(workflow_state, user=user)

        # dispara processamento async
        process_recipe_with_ai.enqueue(task_state.id)

        return task_state

    def on_action(self, task_state, user, action_name, **kwargs):
        # Não queremos ação manual aqui
        pass
