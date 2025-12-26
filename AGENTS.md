# Build/Lint/Test Commands

## Full Test Suite
just test

## Single Test File
pytest cdc/base/tests/test_view.py

## Single Test Method
pytest cdc/base/tests/test_view.py::TestBaseViews::test_home

## Linting & Formatting
just format

## Django Management Commands
just mng makemigrations
just mng migrate
just mng collectstatic

# Code Style Guidelines

## Python
- Line length: 120 characters
- Quote style: single quotes
- Imports: isort (I) rules via ruff
- Code style: pycodestyle (E) rules via ruff
- Exclude: tests/ and **/migrations/** from linting

## Django/Wagtail
- Use snake_case for variables and functions
- Use PascalCase for classes and models
- Follow Django model conventions with verbose_name in Portuguese
- Use RichTextField for HTML content
- Use ClusterTaggableManager for tags
- Follow Wagtail Page patterns for CMS pages
- RecipeTagIndexPage template: 'recipes/recipe_tag_index_page.html'
- Page hierarchy: RecipeTagIndexPage should be child of Home page (not RecipeIndexPage)

## Testing
- Use pytest with django_db fixture for database access
- Wagtail pages are tested via URL paths, not named URLs