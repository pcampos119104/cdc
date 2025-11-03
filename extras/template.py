import marimo

__generated_with = '0.8.15'
app = marimo.App()


@app.cell
def __():
    import os
    import sys

    import django

    sys.path.insert(0, '/app')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cdc.settings')
    os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

    django.setup()

    def vdir(obj):
        return [x for x in dir(obj) if not x.startswith('__')]

    return django, os, sys, vdir


@app.cell
def __():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user, created = User.objects.get_or_create(username='Pedro', email='email@asdf.asdf')
    if created:
        user.set_password('password')
        user.save()

    print(user)
    return User, created, get_user_model, user


if __name__ == '__main__':
    app.run()
