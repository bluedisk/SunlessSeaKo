from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from .models import Noun


def nouns(requests):
    result = []

    for noun in Noun.objects.all():
        result.append({
            'uid': '%s:%s' % (noun.cate.name, noun.id),
            'value': noun.name,
        })

    return JsonResponse(result, safe=False)


def home(request):
    return render(request, "home.html")
