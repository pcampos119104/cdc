from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


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
    description = models.TextField('descrição', help_text='Breve descrição da receita.')
    directions = RichTextField(verbose_name='preparo', help_text='Passos para o preparo.', blank=True)
    tags = ClusterTaggableManager(through=RecipePageTag, blank=True)
    font = models.CharField('fonte', max_length=200, help_text='Livro de receita, link do youtube e etc.')
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.PROTECT, related_name='+')

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
        FieldPanel('description'),
        FieldPanel('directions'),
        FieldPanel('font'),
        FieldPanel('image'),
        InlinePanel('ingredients', label='Ingredientes'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('description'),
        index.SearchField('directions'),
    ]
    parent_page_types = ['recipes.RecipeIndexPage']
    subpage_types = []


class RecipeIngredient(ClusterableModel):
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
        return f'{self.quantity or "?"} {getattr(self.metric, "abbr", "?")} de {getattr(self.ingredient, "name", "?")}'

    @property
    def qualifier_list(self):
        """Usado no template se precisar mostrar os qualifiers"""
        return [iq.qualifier.name for iq in self.detailed_qualifiers.all()]


class Ingredient(models.Model):
    name = models.CharField('Nome', max_length=64, unique=True)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Metric(models.Model):
    name = models.CharField('Nome', max_length=30)
    abbr = models.CharField('Abreviação', max_length=10, help_text='Ex: g, ml, xíc., colher')

    panels = [
        FieldPanel('name'),
        FieldPanel('abbr'),
    ]

    def __str__(self):
        return self.abbr or self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Métrica'
        verbose_name_plural = 'Métricas'


class Qualifier(models.Model):
    name = models.CharField('Nome', max_length=64, help_text='Ex: picado, ralado, em cubos, opcional')

    panels = [FieldPanel('name')]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class RecipeIngredientQualifier(ClusterableModel):
    ingredient = ParentalKey('RecipeIngredient', related_name='ingredient_qualifiers', on_delete=models.CASCADE)
    qualifier = models.ForeignKey('recipes.Qualifier', on_delete=models.PROTECT)

    panels = [
        FieldPanel('qualifier'),
    ]

    def __str__(self):
        return str(self.qualifier)


class IngredientViewSet(SnippetViewSet):
    model = Ingredient
    icon = 'snippet'
    list_display = ['name']
    search_fields = ['name']


class MetricViewSet(SnippetViewSet):
    model = Metric
    icon = 'snippet'
    list_display = ['abbr', 'name']
    search_fields = ['name', 'abbr']


class QualifierViewSet(SnippetViewSet):
    model = Qualifier
    icon = 'snippet'
    list_display = ['name']
    search_fields = ['name']


# Registre assim:
register_snippet(Ingredient, viewset=IngredientViewSet)
register_snippet(Metric, viewset=MetricViewSet)
register_snippet(Qualifier, viewset=QualifierViewSet)
