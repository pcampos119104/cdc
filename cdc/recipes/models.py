from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index


class RecipeIndexPage(Page):
    intro = RichTextField(blank=True)
    subpage_types = ['recipes.RecipePage',]
    content_panels = Page.content_panels + ['intro']

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        recipepages = self.get_children().live().order_by('-first_published_at')
        context['recipepages'] = recipepages
        return context


class RecipeTagIndexPage(Page):
    template = 'recipe/recipe_index_page.html'

    def get_context(self, request):
        tag = request.GET.get('tag')
        recipepages = RecipePage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['recipepages'] = recipepages
        return context


class RecipePageTag(TaggedItemBase):
    content_object = ParentalKey('RecipePage', related_name='tagged_items', on_delete=models.CASCADE)


class RecipePage(Page):
    description = models.TextField('descrição', help_text='Breve descrição da receita.')
    directions = RichTextField(verbose_name='preparo', help_text='Passos para o preparo.', blank=True)
    tags = ClusterTaggableManager(through=RecipePageTag, blank=True)
    font = models.CharField('fonte', max_length=200, help_text='Livro de receita, link do youtube e etc.')
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.CASCADE, related_name='+')

    content_panels = Page.content_panels + [
        'tags',
        'description',
        'directions',
        'font',
        'image',
    ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('description'),
        index.SearchField('body'),
    ]
