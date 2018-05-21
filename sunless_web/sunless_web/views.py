from django.http import JsonResponse
from django.shortcuts import render

from .models import Noun


def nouns(requests):
    result = []

    for noun in Noun.objects.all():
        result.append({
            'id': noun.id,
            'name': noun.name,
            'icon': noun.cate.icon,
            'type': 'noun'
        })

    return JsonResponse(result, safe=False)


def home(request):
    return render(request, "home.html")
