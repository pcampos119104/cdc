from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from cdc.pdrf.main import PdrFlow


def simple_page(request):
    """
    Página simples com um botão que faz GET para outra view
    """
    return render(request, 'base/simple_page.html')


@require_http_methods(['GET'])
def api_response(request):
    """
    View que recebe o GET do botão e retorna uma resposta JSON
    """
    pdrf = PdrFlow()
    result = pdrf.kickoff()


    data = {
        'message': result,
        'status': 'success',
        'timestamp': request.META.get('HTTP_DATE', 'N/A'),
    }
    return JsonResponse(data)
