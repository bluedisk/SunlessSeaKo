from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from .models import Noun, Patch


def nouns(requests):
    nouns_dict = Noun.make_dict()
    result = [{'uid': '%04d' % key, 'value': values[2]} for key, values in nouns_dict.items()]

    return JsonResponse(result, safe=False)


def home(request):
    return render(request, "home.html", {"patch": Patch.objects.order_by('-created_at').first()})


def download(request, patch_id):
    patch = Patch.objects.get(pk=patch_id)
    patch.download += 1
    patch.save()

    return HttpResponseRedirect(patch.file.url)
