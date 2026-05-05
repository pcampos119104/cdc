import pytest
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker):
    """Ensure steady_queue tables exist before running tests."""
    with django_db_blocker.unblock():
        call_command('migrate', '--run-syncdb', verbosity=0)
