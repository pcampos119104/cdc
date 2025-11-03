from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


class HomeView(View):
    """
    Simple Home page, to show that it's working.
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'base/home.html')


def htmx(request):
    """
    A simple htmx view that return a partial html.
    """
    return HttpResponse('<span id="click-test">HTMX is working</span>')
