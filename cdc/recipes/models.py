"""Defines Django/Wagtail models for recipes, including pages, tasks,
and snippets for managing recipe content with AI processing."""

from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page, Task
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


class RecipeIndexPage(Page):
    """Index page for listing recipes, restricting subpages to RecipePage."""

    intro = RichTextField(blank=True)
    subpage_types = [
        'recipes.RecipePage',
    ]
    content_panels = Page.content_panels + ['intro']

    def get_context(self, request):
        """Updates context to include published recipe pages, ordered by publication date."""
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        recipepages = self.get_children().live().order_by('-first_published_at')
        context['recipepages'] = recipepages
        return context


class RecipeTagIndexPage(Page):
    """Page for filtering recipes by tags, displaying all tags or tag-specific recipes."""

    template = 'recipes/recipe_tag_index_page.html'

    def get_context(self, request):
        """Updates context with tag-filtered recipes or all available tags with counts."""
        context = super().get_context(request)
        tag_name = request.GET.get('tag')

        if tag_name:
            # Filter recipes by specific tag
            recipepages = RecipePage.objects.live().filter(tags__name=tag_name)
            context['current_tag'] = tag_name
        else:
            # Show all available tags with count
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
    """Through model for tagging RecipePage instances."""

    content_object = ParentalKey('RecipePage', related_name='tagged_items', on_delete=models.CASCADE)


class RecipePage(Page):
    """Core model for individual recipes with AI processing fields."""

    raw_input = RichTextField(
        verbose_name='Entrada bruta',
        help_text='Texto cru da receita para processamento por IA.',
        blank=True,
    )
    raw_ai_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Resposta bruta da IA',
        help_text='JSON retornado pela IA para aprendizado.',
    )

    # AI-populated fields for recipe details
    description = models.TextField('descrição', help_text='Breve descrição da receita.', blank=True)
    directions = RichTextField(verbose_name='preparo', help_text='Passos para o preparo.', blank=True)
    font = models.CharField('fonte', max_length=200, help_text='Livro de receita, link do youtube e etc.', blank=True)

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
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.PROTECT, related_name='+', null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
        FieldPanel('raw_input'),
        FieldPanel('description'),
        FieldPanel('directions'),
        FieldPanel('font'),
        FieldPanel('image'),
        InlinePanel('ingredients', label='Ingredientes'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('raw_input'),
        index.SearchField('description'),
        index.SearchField('directions'),
    ]
    parent_page_types = ['recipes.RecipeIndexPage']
    subpage_types = []

    def save(self, *args, **kwargs):
        """Sets live status based on status field before saving."""
        # Set live status based on publication status
        if self.status == 'published':
            self.live = True
        elif self._state.adding:
            self.live = False
        super().save(*args, **kwargs)


class AIProcessingTask(Task):
    """Task for AI-driven recipe processing in workflows."""

    label = 'AI processing task'

    class Meta:
        verbose_name = 'AI Processing Task'
        verbose_name_plural = 'AI Processing Tasks'

    def start(self, workflow_state, user=None):
        """Starts the task by enqueuing AI processing."""
        task_state = super().start(workflow_state, user=user)

        # Enqueue the AI processing task
        from cdc.recipes.tasks import process_recipe_with_ai

        process_recipe_with_ai.enqueue(task_state.id)

        return task_state

    def on_action(self, task_state, user, action_name, **kwargs):
        """Handles task actions, preventing manual approval."""
        # Manual actions are not allowed here
        pass


class RecipeIngredient(ClusterableModel):
    """Model representing ingredients in recipes with quantities and metrics."""

    page = ParentalKey('RecipePage', on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey('recipes.Ingredient', on_delete=models.PROTECT)
    metric = models.ForeignKey('recipes.Metric', on_delete=models.PROTECT)
    quantity = models.DecimalField('Quantidade', max_digits=6, decimal_places=2)

    panels = [
        FieldPanel('ingredient'),
        FieldPanel('metric'),
        FieldPanel('quantity'),
        MultiFieldPanel(
            [
                InlinePanel('ingredient_qualifiers', label='Qualificadores', min_num=0, max_num=5),
            ],
            heading='Detalhes do ingrediente',
            classname='collapsed',
        ),
    ]

    def __str__(self):
        """Returns a string representation of the ingredient quantity, metric, and name."""
        return f'{self.quantity or "?"} {getattr(self.metric, "abbr", "?")} de {getattr(self.ingredient, "name", "?")}'

    @property
    def qualifier_list(self):
        """Used in the template if needed to display qualifiers."""
        return [iq.qualifier.name for iq in self.ingredient_qualifiers.all()]


class Ingredient(models.Model):
    """Snippet model for recipe ingredients."""

    name = models.CharField('Nome', max_length=64, unique=True)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Métrica'
        verbose_name_plural = 'Métricas'


class Metric(models.Model):
    """Snippet model for measurement units."""

    name = models.CharField('Nome', max_length=30)
    abbr = models.CharField('Abreviação', max_length=10, help_text='Ex: g, ml, xíc., colher')

    panels = [
        FieldPanel('name'),
        FieldPanel('abbr'),
    ]

    def __str__(self):
        """Returns the metric abbreviation or name."""
        return self.abbr or self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Métrica'
        verbose_name_plural = 'Métricas'


class Qualifier(models.Model):
    """Snippet model for ingredient qualifiers."""

    name = models.CharField('Nome', max_length=64, help_text='Ex: picado, ralado, em cubos, opcional')

    panels = [FieldPanel('name')]

    def __str__(self):
        """Returns the qualifier name."""
        return self.name

    class Meta:
        ordering = ['name']


class RecipeIngredientQualifier(ClusterableModel):
    """Through model linking ingredients to qualifiers."""

    ingredient = ParentalKey('RecipeIngredient', related_name='ingredient_qualifiers', on_delete=models.CASCADE)
    qualifier = models.ForeignKey('recipes.Qualifier', on_delete=models.PROTECT)

    panels = [
        FieldPanel('qualifier'),
    ]

    def __str__(self):
        """Returns the qualifier name."""
        return str(self.qualifier)


class IngredientViewSet(SnippetViewSet):
    """Wagtail viewset for managing Ingredient snippets."""

    model = Ingredient


class MetricViewSet(SnippetViewSet):
    """Wagtail viewset for managing Metric snippets."""

    model = Metric


class QualifierViewSet(SnippetViewSet):
    """Wagtail viewset for managing Qualifier snippets."""

    model = Qualifier
    icon = 'snippet'
    list_display = ['name']
    search_fields = ['name']


# Registre assim:
register_snippet(Ingredient, viewset=IngredientViewSet)
register_snippet(Metric, viewset=MetricViewSet)
register_snippet(Qualifier, viewset=QualifierViewSet)
